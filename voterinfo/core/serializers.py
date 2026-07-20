"""
core/serializers.py
---------------------
Plain DRF Serializers (not ModelSerializer, since our models are
MongoEngine Documents, not Django ORM models). Each serializer
validates input using the regex validators from core/validators.py.
"""

from rest_framework import serializers
from core.validators import is_valid_pincode, is_valid_mobile, is_valid_aadhaar


class PollingBoothSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    booth_name = serializers.CharField(max_length=200)
    booth_number = serializers.CharField(max_length=50)
    address = serializers.CharField(max_length=500)
    pin_code = serializers.CharField(max_length=6)
    officer_name = serializers.CharField(max_length=150)
    contact_number = serializers.CharField(max_length=15, required=False, allow_blank=True)
    area_name = serializers.CharField(max_length=150, required=False, allow_blank=True)

    def validate_pin_code(self, value):
        if not is_valid_pincode(value):
            raise serializers.ValidationError("PIN Code must be exactly 6 digits.")
        return value

    def validate_contact_number(self, value):
        if value and not is_valid_mobile(value):
            raise serializers.ValidationError("Contact Number must be exactly 10 digits.")
        return value


class ComplaintSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    complaint_id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=150)
    mobile_number = serializers.CharField(max_length=10)
    booth_number = serializers.CharField(max_length=50)
    complaint_category = serializers.CharField(max_length=100)
    complaint_description = serializers.CharField(max_length=2000)
    status = serializers.ChoiceField(
        choices=["Pending", "In Progress", "Resolved", "Rejected"], required=False)
    date = serializers.CharField(read_only=True)
    time = serializers.CharField(read_only=True)

    def validate_mobile_number(self, value):
        if not is_valid_mobile(value):
            raise serializers.ValidationError("Mobile Number must be exactly 10 digits.")
        return value


class EligibilityRequestSerializer(serializers.Serializer):
    dob = serializers.DateField()
    aadhaar = serializers.CharField(max_length=12)

    def validate_aadhaar(self, value):
        if not is_valid_aadhaar(value):
            raise serializers.ValidationError("Aadhaar Number must be exactly 12 digits.")
        return value
