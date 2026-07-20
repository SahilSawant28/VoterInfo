"""
core/tests.py
--------------
Unit tests for the pure-Python logic (validators, booth_locator,
oop_models, constants). These do NOT require a live MongoDB connection,
since they test functions/classes in isolation using plain dicts and
dependency-injected data, keeping the test suite fast and self-contained.

Run with:  python manage.py test core
"""

from datetime import date, timedelta

from django.test import TestCase

from core.validators import is_valid_aadhaar, is_valid_pincode, is_valid_mobile
from core.booth_locator import (
    validate_pincode, find_booth, display_booth, calculate_age,
    InvalidPincodeError, BoothNotFoundError, MissingRecordError, InvalidInputError,
)
from core.constants import check_basic_eligibility
from core.oop_models import PollingBooth as PBClass, Voter, EligibilityChecker


class RegexValidatorTests(TestCase):
    def test_valid_aadhaar(self):
        self.assertTrue(is_valid_aadhaar("123456789012"))

    def test_invalid_aadhaar_length(self):
        self.assertFalse(is_valid_aadhaar("12345"))

    def test_invalid_aadhaar_letters(self):
        self.assertFalse(is_valid_aadhaar("12345678901A"))

    def test_valid_pincode(self):
        self.assertTrue(is_valid_pincode("422003"))

    def test_invalid_pincode(self):
        self.assertFalse(is_valid_pincode("4220"))

    def test_valid_mobile(self):
        self.assertTrue(is_valid_mobile("9876543210"))

    def test_invalid_mobile(self):
        self.assertFalse(is_valid_mobile("98765"))


class BoothLocatorFunctionTests(TestCase):
    def test_validate_pincode_ok(self):
        self.assertTrue(validate_pincode("400058"))

    def test_validate_pincode_bad_raises(self):
        with self.assertRaises(InvalidPincodeError):
            validate_pincode("12AB56")

    def test_find_booth_with_injected_queryset(self):
        fake_data = [{
            "booth_name": "Test School", "booth_number": "T-1",
            "address": "Test Address", "pin_code": "400058",
            "officer_name": "Test Officer",
        }]
        result = find_booth("400058", queryset=fake_data)
        self.assertEqual(result["booth_number"], "T-1")

    def test_find_booth_not_found_raises(self):
        with self.assertRaises(BoothNotFoundError):
            find_booth("400058", queryset=[])

    def test_display_booth_missing_field_raises(self):
        with self.assertRaises(MissingRecordError):
            display_booth({"booth_name": "Incomplete"})

    def test_calculate_age_from_string(self):
        eighteen_years_ago = date.today().replace(year=date.today().year - 18)
        age = calculate_age(eighteen_years_ago.isoformat())
        self.assertEqual(age, 18)

    def test_calculate_age_future_date_raises(self):
        future = (date.today() + timedelta(days=10)).isoformat()
        with self.assertRaises(InvalidInputError):
            calculate_age(future)


class EligibilityLogicTests(TestCase):
    def test_check_basic_eligibility_adult(self):
        self.assertEqual(check_basic_eligibility(20), "Eligible for Voter Registration")

    def test_check_basic_eligibility_minor(self):
        self.assertEqual(check_basic_eligibility(15), "Not Eligible Yet")

    def test_eligibility_checker_class(self):
        dob = date.today().replace(year=date.today().year - 20).isoformat()
        voter = Voter("Test Voter", dob, "123456789012", "Addr", "9876543210", "400058")
        checker = EligibilityChecker(voter)
        result = checker.display_result()
        self.assertTrue(result["is_eligible"])
        self.assertEqual(result["message"], "Eligible for Voter Registration")

    def test_eligibility_checker_underage(self):
        dob = date.today().replace(year=date.today().year - 10).isoformat()
        voter = Voter("Young Person", dob, "123456789012", "Addr", "9876543210", "400058")
        checker = EligibilityChecker(voter)
        result = checker.display_result()
        self.assertFalse(result["is_eligible"])


class OOPPollingBoothTests(TestCase):
    def test_update_and_display(self):
        booth = PBClass("Old School", "B-1", "Old Address", "Officer A", "400058")
        booth.update_booth(address="New Address")
        self.assertIn("New Address", booth.display_booth())

    def test_delete_booth(self):
        booth = PBClass("School", "B-2", "Addr", "Officer", "400058")
        self.assertTrue(booth.delete_booth())
        self.assertIsNone(booth.booth_name)
