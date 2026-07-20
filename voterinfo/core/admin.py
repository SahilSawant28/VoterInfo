"""
core/admin.py
--------------
Django's default admin site is wired to SQL models, and our app data
lives in MongoDB (MongoEngine), so a lightweight custom admin dashboard
is provided instead at /booth-locator/, /complaint-form/, etc., plus a
dedicated statistics view. Django's own /admin/ still works for
managing Users/Groups (staff accounts that can log in to review
complaints, etc.).
"""

from django.contrib import admin  # noqa: F401

# Intentionally minimal: see core/views.py for the custom, MongoDB-aware
# "Admin Dashboard" pages that manage Polling Booths, Complaints, Users
# and Statistics as required by the project spec.
