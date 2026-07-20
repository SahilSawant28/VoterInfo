"""
core/oop_models.py
--------------------
UNIT 3 - OBJECT ORIENTED PROGRAMMING.

Plain Python classes (PollingBooth, Voter, EligibilityChecker) as
required by the project spec. These are intentionally separate from
the MongoEngine `Document` classes in core/mongo_models.py:

    - mongo_models.py  -> persistence layer (talks to MongoDB)
    - oop_models.py    -> domain layer (pure Python OOP, easy to unit test)

Views convert between the two where needed. This separation is a
common, industry-standard practice (keeps business logic independent
of the database framework).
"""

from datetime import date
from core.validators import is_valid_aadhaar, is_valid_pincode
from core.booth_locator import calculate_age as _calculate_age, InvalidInputError


class PollingBooth:
    """Represents a single polling booth."""

    def __init__(self, booth_name, booth_number, address, officer_name, pin_code):
        self.booth_name = booth_name
        self.booth_number = booth_number
        self.address = address
        self.officer_name = officer_name
        self.pin_code = pin_code

    def display_booth(self) -> str:
        """Return a human-readable summary of the booth."""
        return (
            f"Booth {self.booth_number} - {self.booth_name}\n"
            f"Address: {self.address}\n"
            f"PIN Code: {self.pin_code}\n"
            f"Presiding Officer: {self.officer_name}"
        )

    def update_booth(self, **kwargs) -> "PollingBooth":
        """Update one or more attributes of the booth and return self."""
        allowed = {"booth_name", "booth_number", "address", "officer_name", "pin_code"}
        for key, value in kwargs.items():
            if key in allowed and value is not None:
                setattr(self, key, value)
        return self

    def delete_booth(self):
        """
        Clear the booth's fields (in-memory representation of a delete).
        Actual MongoDB deletion happens in the persistence layer.
        """
        self.booth_name = None
        self.booth_number = None
        self.address = None
        self.officer_name = None
        self.pin_code = None
        return True

    def __repr__(self):
        return f"<PollingBooth {self.booth_number}: {self.booth_name}>"


class Voter:
    """Represents a citizen/voter and their registration-relevant details."""

    def __init__(self, name, dob, aadhaar, address, mobile_number, pin_code):
        self.name = name
        self.dob = dob
        self.aadhaar = aadhaar
        self.address = address
        self.mobile_number = mobile_number
        self.pin_code = pin_code

    def calculate_age(self) -> int:
        """Calculate the voter's current age from their date of birth."""
        return _calculate_age(self.dob)

    def display_profile(self) -> dict:
        """Return the voter's profile as a dictionary, including computed age."""
        try:
            age = self.calculate_age()
        except InvalidInputError:
            age = None

        return {
            "name": self.name,
            "dob": str(self.dob),
            "age": age,
            "aadhaar_valid": is_valid_aadhaar(self.aadhaar),
            "address": self.address,
            "mobile_number": self.mobile_number,
            "pin_code": self.pin_code,
            "pincode_valid": is_valid_pincode(self.pin_code),
        }

    def __repr__(self):
        return f"<Voter {self.name}>"


class EligibilityChecker:
    """Encapsulates the voter-eligibility business rules."""

    MIN_VOTING_AGE = 18

    def __init__(self, voter: "Voter"):
        self.voter = voter
        self._age = None
        self._age_ok = False
        self._docs_ok = False

    def check_age(self) -> bool:
        """Return True if the voter meets the minimum voting age."""
        try:
            self._age = self.voter.calculate_age()
        except InvalidInputError:
            self._age = None
            self._age_ok = False
            return False

        self._age_ok = self._age >= self.MIN_VOTING_AGE
        return self._age_ok

    def verify_documents(self) -> bool:
        """Return True if the voter's Aadhaar number is a valid 12-digit number."""
        self._docs_ok = is_valid_aadhaar(self.voter.aadhaar)
        return self._docs_ok

    def display_result(self) -> dict:
        """Run all checks (if not already run) and return a result summary dict."""
        if self._age is None and self._age_ok is False:
            self.check_age()
        self.verify_documents()

        eligible = bool(self._age_ok and self._docs_ok)

        return {
            "name": self.voter.name,
            "age": self._age,
            "age_eligible": self._age_ok,
            "documents_valid": self._docs_ok,
            "is_eligible": eligible,
            "message": "Eligible for Voter Registration" if eligible else "Not Eligible Yet",
        }
