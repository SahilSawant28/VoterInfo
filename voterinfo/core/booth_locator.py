"""
core/booth_locator.py
----------------------
UNIT 2 - FUNCTIONS & MODULES.

A standalone, reusable module that contains the core "business logic"
functions for locating polling booths and calculating voter age. It is
imported by both the Django views (core/views.py) and the DRF API
views (core/api_views.py), so the logic is written exactly once.

Custom exceptions are used to keep error handling explicit and
readable, per the project requirements.
"""

import logging
from datetime import date, datetime

logger = logging.getLogger('core')


# ------------------------------------------------------------------
# CUSTOM EXCEPTIONS
# ------------------------------------------------------------------
class InvalidPincodeError(Exception):
    """Raised when a PIN code does not match the required 6-digit format."""
    pass


class BoothNotFoundError(Exception):
    """Raised when no polling booth is found for the given PIN code."""
    pass


class MissingRecordError(Exception):
    """Raised when a required record/field is missing from the datastore."""
    pass


class InvalidInputError(Exception):
    """Raised for generic invalid user input (dates, numbers, etc.)."""
    pass


# ------------------------------------------------------------------
# FUNCTIONS
# ------------------------------------------------------------------
def validate_pincode(pin_code: str) -> bool:
    """
    Validate that a PIN code is exactly 6 numeric digits.

    Raises:
        InvalidPincodeError: if the format is invalid.
    Returns:
        True if valid.
    """
    if pin_code is None:
        raise InvalidPincodeError("PIN Code cannot be empty.")

    pin_code = str(pin_code).strip()

    if not pin_code.isdigit() or len(pin_code) != 6:
        raise InvalidPincodeError(
            f"'{pin_code}' is not a valid PIN Code. It must be exactly 6 digits."
        )
    return True


def find_booth(pin_code: str, queryset=None):
    """
    Find a polling booth record by PIN code.

    Args:
        pin_code: 6-digit PIN code string.
        queryset: An iterable of booth-like objects/dicts to search
                   (dependency injected so this function stays testable
                   and does not hard-depend on MongoDB at import time).

    Raises:
        InvalidPincodeError: bad format.
        BoothNotFoundError: no matching booth.

    Returns:
        The matching booth record.
    """
    validate_pincode(pin_code)

    if queryset is None:
        # Lazy import to avoid circular imports / mongo connection at
        # module import time.
        from core.mongo_models import PollingBooth
        queryset = PollingBooth.objects.filter(pin_code=str(pin_code).strip())

    results = list(queryset)
    if not results:
        logger.warning("No booth found for PIN code %s", pin_code)
        raise BoothNotFoundError(
            f"No polling booth was found for PIN Code {pin_code}."
        )

    logger.info("Booth located for PIN code %s", pin_code)
    return results[0] if len(results) == 1 else results


def display_booth(booth) -> dict:
    """
    Normalize a booth record (MongoEngine document or dict) into a
    plain dictionary safe for template/API rendering.

    Raises:
        MissingRecordError: if the booth object has no usable fields.
    """
    if booth is None:
        raise MissingRecordError("Booth record is missing / empty.")

    if isinstance(booth, dict):
        data = booth
    else:
        # MongoEngine Document -> dict via to_mongo, fallback to getattr
        try:
            data = {
                "booth_name": booth.booth_name,
                "booth_number": booth.booth_number,
                "address": booth.address,
                "pin_code": booth.pin_code,
                "officer_name": booth.officer_name,
                "contact_number": getattr(booth, "contact_number", ""),
                "area_name": getattr(booth, "area_name", ""),
            }
        except AttributeError as exc:
            raise MissingRecordError(f"Booth record is incomplete: {exc}")

    required_fields = ["booth_name", "booth_number", "address", "pin_code"]
    for field in required_fields:
        if not data.get(field):
            raise MissingRecordError(f"Booth record is missing required field: '{field}'")

    return data


def calculate_age(dob) -> int:
    """
    Calculate a person's current age (in completed years) from their
    date of birth, using Python's datetime module.

    Args:
        dob: a `date`/`datetime` object OR a string in 'YYYY-MM-DD' format.

    Raises:
        InvalidInputError: if the date is invalid or is in the future.

    Returns:
        int: age in completed years.
    """
    if isinstance(dob, str):
        try:
            dob = datetime.strptime(dob.strip(), "%Y-%m-%d").date()
        except ValueError:
            raise InvalidInputError(
                f"'{dob}' is not a valid date. Expected format: YYYY-MM-DD."
            )
    elif isinstance(dob, datetime):
        dob = dob.date()
    elif not isinstance(dob, date):
        raise InvalidInputError("Date of Birth must be a date, datetime, or 'YYYY-MM-DD' string.")

    today = date.today()

    if dob > today:
        raise InvalidInputError("Date of Birth cannot be in the future.")

    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age
