"""
core/forms.py
--------------
Django forms for the Booth Locator, Eligibility Checker, and Complaint
Form pages. Uses RegexValidator so both server-side validation and
HTML5 pattern attributes stay in sync with core/validators.py.
"""

from django import forms
from django.core.validators import RegexValidator

pincode_validator = RegexValidator(r'^\d{6}$', 'PIN Code must be exactly 6 digits.')
aadhaar_validator = RegexValidator(r'^\d{12}$', 'Aadhaar Number must be exactly 12 digits.')
mobile_validator = RegexValidator(r'^\d{10}$', 'Mobile Number must be exactly 10 digits.')


class BoothLocatorForm(forms.Form):
    pin_code = forms.CharField(
        max_length=6,
        min_length=6,
        validators=[pincode_validator],
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter 6-digit PIN Code e.g. 422003',
            'pattern': r'\d{6}',
            'inputmode': 'numeric',
            'maxlength': '6',
        }),
        label="PIN Code",
    )


class EligibilityForm(forms.Form):
    name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
    )
    dob = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Date of Birth",
    )
    aadhaar = forms.CharField(
        max_length=12,
        min_length=12,
        validators=[aadhaar_validator],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '12-digit Aadhaar Number',
            'pattern': r'\d{12}',
            'inputmode': 'numeric',
            'maxlength': '12',
        }),
        label="Aadhaar Number",
    )


class ComplaintForm(forms.Form):
    name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
    )
    mobile_number = forms.CharField(
        max_length=10,
        min_length=10,
        validators=[mobile_validator],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '10-digit Mobile Number',
            'pattern': r'\d{10}',
            'inputmode': 'numeric',
            'maxlength': '10',
        }),
        label="Mobile Number",
    )
    booth_number = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. NSK-101'}),
        label="Booth Number",
    )
    complaint_category = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    complaint_description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4,
                                      'placeholder': 'Describe the issue in detail...'}),
        max_length=2000,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from core.constants import COMPLAINT_CATEGORIES
        self.fields['complaint_category'].choices = [(c, c) for c in COMPLAINT_CATEGORIES]
