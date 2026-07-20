"""
core/dashboard_views.py
-------------------------
UNIT 5 - ADMIN PANEL.

Django's built-in /admin/ site is backed by the relational ORM, but
VoterInfo's application data (Polling Booths, Complaints) lives in
MongoDB via MongoEngine, which Django admin does not manage out of the
box. This module provides a small, staff-only "Admin Dashboard" that
covers exactly what the spec asks for:

    - Manage Polling Booths (list, add, delete)
    - Manage Complaints (list, update status, delete)
    - Users (list Django auth users - staff/superuser accounts)
    - Statistics (counts, category breakdown)

Access is restricted with @staff_member_required, backed by Django's
normal auth/session system (create a superuser with `createsuperuser`
and log in at /admin/ or /dashboard/login/).
"""

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy

from core.mongo_models import PollingBooth, Complaint

User = get_user_model()


class DashboardLoginView(LoginView):
    template_name = "core/dashboard/login.html"
    redirect_authenticated_user = True


@staff_member_required
def dashboard_home(request):
    context = {
        "page_title": "Admin Dashboard",
        "booth_count": PollingBooth.objects.count(),
        "complaint_count": Complaint.objects.count(),
        "pending_count": Complaint.objects.filter(status="Pending").count(),
        "resolved_count": Complaint.objects.filter(status="Resolved").count(),
        "user_count": User.objects.count(),
    }
    return render(request, "core/dashboard/dashboard_home.html", context)


@staff_member_required
def dashboard_booths(request):
    if request.method == "POST" and request.POST.get("action") == "delete":
        booth_number = request.POST.get("booth_number")
        PollingBooth.objects.filter(booth_number=booth_number).delete()
        messages.success(request, f"Booth {booth_number} deleted.")
        return redirect("dashboard_booths")

    booths = [b.to_dict() for b in PollingBooth.objects.all()]
    context = {"page_title": "Manage Polling Booths", "booths": booths}
    return render(request, "core/dashboard/dashboard_booths.html", context)


@staff_member_required
def dashboard_complaints(request):
    if request.method == "POST":
        complaint_id = request.POST.get("complaint_id")
        action = request.POST.get("action")
        complaint = Complaint.objects.filter(complaint_id=complaint_id).first()
        if complaint:
            if action == "delete":
                complaint.delete()
                messages.success(request, f"Complaint {complaint_id} deleted.")
            elif action == "update_status":
                new_status = request.POST.get("status")
                if new_status in Complaint.STATUS_CHOICES:
                    complaint.status = new_status
                    complaint.save()
                    messages.success(request, f"Complaint {complaint_id} marked as {new_status}.")
        return redirect("dashboard_complaints")

    complaints = [c.to_dict() for c in Complaint.objects.all()]
    context = {
        "page_title": "Manage Complaints",
        "complaints": complaints,
        "status_choices": Complaint.STATUS_CHOICES,
    }
    return render(request, "core/dashboard/dashboard_complaints.html", context)


@staff_member_required
def dashboard_users(request):
    users = User.objects.all().order_by("-date_joined")
    context = {"page_title": "Manage Users", "users": users}
    return render(request, "core/dashboard/dashboard_users.html", context)


@staff_member_required
def dashboard_stats(request):
    from collections import Counter

    complaints = list(Complaint.objects.all())
    category_counts = Counter(c.complaint_category for c in complaints)
    status_counts = Counter(c.status for c in complaints)

    booths = list(PollingBooth.objects.all())
    area_counts = Counter(b.area_name for b in booths if b.area_name)

    context = {
        "page_title": "Statistics",
        "category_counts": dict(category_counts),
        "status_counts": dict(status_counts),
        "area_counts": dict(area_counts),
        "total_booths": len(booths),
        "total_complaints": len(complaints),
    }
    return render(request, "core/dashboard/dashboard_stats.html", context)
