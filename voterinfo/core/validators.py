"""
core/validators.py
--------------------
UNIT 3 - REGEX VALIDATION.

Regex-based validators for Aadhaar Number, PIN Code, and Mobile Number,
as required by the project spec. Each validator returns True/False and
callers are expected to build user-facing error messages (see
core/forms_logic.py / views.py) so the same validators can be reused
by both Django forms and the DRF serializers.
"""

import re

AADHAAR_REGEX = re.compile(r'^\d{12}$')
PINCODE_REGEX = re.compile(r'^\d{6}$')
MOBILE_REGEX = re.compile(r'^\d{10}$')


def is_valid_aadhaar(value: str) -> bool:
    """Aadhaar Number must be exactly 12 digits."""
    if not value:
        return False
    return bool(AADHAAR_REGEX.match(str(value).strip()))


def is_valid_pincode(value: str) -> bool:
    """PIN Code must be exactly 6 digits."""
    if not value:
        return False
    return bool(PINCODE_REGEX.match(str(value).strip()))


def is_valid_mobile(value: str) -> bool:
    """Mobile Number must be exactly 10 digits."""
    if not value:
        return False
    return bool(MOBILE_REGEX.match(str(value).strip()))


def validate_all(aadhaar=None, pincode=None, mobile=None) -> dict:
    """
    Validate any combination of the three fields and return a dict of
    field_name -> error_message for any that fail. An empty dict means
    everything passed validation.
    """
    errors = {}
    if aadhaar is not None and not is_valid_aadhaar(aadhaar):
        errors['aadhaar'] = "Aadhaar Number must be exactly 12 digits."
    if pincode is not None and not is_valid_pincode(pincode):
        errors['pincode'] = "PIN Code must be exactly 6 digits."
    if mobile is not None and not is_valid_mobile(mobile):
        errors['mobile'] = "Mobile Number must be exactly 10 digits."
    return errors
