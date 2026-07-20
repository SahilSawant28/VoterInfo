"""
core/views.py
--------------
UNIT 5 - DJANGO APPLICATION (page views).

Implements: Home, Booth Locator, Eligibility Checker, Registration
Guide, Required Documents, Complaint Form, About — plus JSON endpoints
used by the frontend JS (search, CSV export, import status).
"""

import csv
import logging

from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from core.booth_locator import (
    find_booth, display_booth, calculate_age,
    InvalidPincodeError, BoothNotFoundError, MissingRecordError, InvalidInputError,
)
from core.constants import (
    VOTER_ELIGIBILITY_CRITERIA, REQUIRED_DOCUMENTS, REGISTRATION_STEPS,
    check_basic_eligibility,
)
from core.forms import BoothLocatorForm, EligibilityForm, ComplaintForm
from core.oop_models import Voter, EligibilityChecker
from core.mongo_models import PollingBooth, Complaint
from core.data_importer import import_booths_async, get_status

logger = logging.getLogger('core')


# ------------------------------------------------------------------
# HOME
# ------------------------------------------------------------------
def home(request):
    try:
        booth_count = PollingBooth.objects.count()
        complaint_count = Complaint.objects.count()
    except Exception as exc:
        logger.warning("MongoDB not reachable on home page: %s", exc)
        booth_count = complaint_count = 0

    context = {
        "page_title": "Home",
        "booth_count": booth_count,
        "complaint_count": complaint_count,
        "criteria": VOTER_ELIGIBILITY_CRITERIA,
    }
    return render(request, "core/home.html", context)


# ------------------------------------------------------------------
# BOOTH LOCATOR
# ------------------------------------------------------------------
def booth_locator(request):
    form = BoothLocatorForm(request.POST or None)
    booth_data = None
    error_message = None

    if request.method == "POST" and form.is_valid():
        pin_code = form.cleaned_data["pin_code"]
        try:
            booth = find_booth(pin_code)
            if isinstance(booth, list):
                booth = booth[0]
            booth_data = display_booth(booth)
        except InvalidPincodeError as exc:
            error_message = str(exc)
        except BoothNotFoundError as exc:
            error_message = str(exc)
        except MissingRecordError as exc:
            error_message = str(exc)

    context = {
        "page_title": "Booth Locator",
        "form": form,
        "booth_data": booth_data,
        "error_message": error_message,
    }
    return render(request, "core/booth_locator.html", context)


def search_booth_ajax(request):
    """JSON endpoint used by the live-search box in the navbar."""
    query = request.GET.get("q", "").strip()
    results = []

    if query:
        try:
            if query.isdigit():
                qs = PollingBooth.objects.filter(pin_code__icontains=query)
            else:
                qs = PollingBooth.objects.filter(area_name__icontains=query)
            results = [b.to_dict() for b in qs[:8]]
        except Exception as exc:
            logger.error("search_booth_ajax error: %s", exc)

    return JsonResponse({"results": results})


# ------------------------------------------------------------------
# ELIGIBILITY CHECKER
# ------------------------------------------------------------------
def eligibility_checker(request):
    form = EligibilityForm(request.POST or None)
    result = None

    if request.method == "POST" and form.is_valid():
        voter = Voter(
            name=form.cleaned_data["name"],
            dob=form.cleaned_data["dob"],
            aadhaar=form.cleaned_data["aadhaar"],
            address="",
            mobile_number="",
            pin_code="",
        )
        checker = EligibilityChecker(voter)
        result = checker.display_result()

    context = {
        "page_title": "Eligibility Checker",
        "form": form,
        "result": result,
    }
    return render(request, "core/eligibility_checker.html", context)


# ------------------------------------------------------------------
# REGISTRATION GUIDE
# ------------------------------------------------------------------
def registration_guide(request):
    context = {
        "page_title": "Registration Guide",
        "steps": REGISTRATION_STEPS,
    }
    return render(request, "core/registration_guide.html", context)


# ------------------------------------------------------------------
# REQUIRED DOCUMENTS
# ------------------------------------------------------------------
def required_documents(request):
    context = {
        "page_title": "Required Documents",
        "documents": REQUIRED_DOCUMENTS,
    }
    return render(request, "core/required_documents.html", context)


# ------------------------------------------------------------------
# COMPLAINT FORM
# ------------------------------------------------------------------
def complaint_form(request):
    form = ComplaintForm(request.POST or None)
    submitted_id = None

    if request.method == "POST" and form.is_valid():
        complaint = Complaint(
            name=form.cleaned_data["name"],
            mobile_number=form.cleaned_data["mobile_number"],
            booth_number=form.cleaned_data["booth_number"],
            complaint_category=form.cleaned_data["complaint_category"],
            complaint_description=form.cleaned_data["complaint_description"],
        )
        complaint.save()
        submitted_id = complaint.complaint_id
        messages.success(request, f"Complaint submitted successfully! Reference ID: {submitted_id}")
        return redirect("complaint_form")

    context = {
        "page_title": "Complaint Form",
        "form": form,
        "submitted_id": submitted_id,
    }
    return render(request, "core/complaint_form.html", context)


def export_complaints_csv(request):
    """Export all complaints to a downloadable CSV file."""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="complaints_export.csv"'

    writer = csv.writer(response)
    writer.writerow(["Complaint ID", "Name", "Mobile Number", "Booth Number",
                      "Category", "Description", "Status", "Date", "Time"])

    for c in Complaint.objects.all():
        d = c.to_dict()
        writer.writerow([d["complaint_id"], d["name"], d["mobile_number"],
                          d["booth_number"], d["complaint_category"],
                          d["complaint_description"], d["status"], d["date"], d["time"]])

    return response


# ------------------------------------------------------------------
# ABOUT
# ------------------------------------------------------------------
def about(request):
    context = {
        "page_title": "About",
        "tech_stack": [
            "Python 3", "Django 5", "MongoDB (MongoEngine)", "Django REST Framework",
            "Bootstrap 5", "HTML5 / CSS3", "JavaScript (ES6)",
        ],
    }
    return render(request, "core/about.html", context)


# ------------------------------------------------------------------
# BACKGROUND IMPORT (threading demo)
# ------------------------------------------------------------------
def trigger_import(request):
    import_booths_async()
    return JsonResponse({"message": "Import started in background.", "status": get_status()})


def import_status(request):
    return JsonResponse(get_status())


# ------------------------------------------------------------------
# CUSTOM ERROR PAGES
# ------------------------------------------------------------------
def error_404(request, exception=None):
    return render(request, "core/404.html", status=404)


def error_500(request):
    return render(request, "core/500.html", status=500)
