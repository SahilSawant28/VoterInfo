"""
core/mongo_models.py
----------------------
UNIT 4 - MONGODB.

MongoEngine Document classes that map to two MongoDB collections:

    1. polling_booths  -> PollingBooth
    2. complaints      -> Complaint

MongoEngine gives us a familiar, Django-model-like API
(`.objects.filter()`, `.save()`, `.delete()`, ...) while writing
directly to MongoDB, which keeps CRUD code clean and readable.
"""

import uuid
from datetime import datetime

from mongoengine import (
    Document,
    StringField,
    DateTimeField,
    IntField,
)


class PollingBooth(Document):
    """MongoDB collection: polling_booths"""

    booth_name = StringField(required=True, max_length=200)
    booth_number = StringField(required=True, max_length=50, unique=True)
    address = StringField(required=True, max_length=500)
    pin_code = StringField(required=True, max_length=6)
    officer_name = StringField(required=True, max_length=150)
    contact_number = StringField(max_length=15, default="")
    area_name = StringField(max_length=150, default="")
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "polling_booths",
        "indexes": ["pin_code", "booth_number", "area_name"],
        "ordering": ["booth_number"],
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "booth_name": self.booth_name,
            "booth_number": self.booth_number,
            "address": self.address,
            "pin_code": self.pin_code,
            "officer_name": self.officer_name,
            "contact_number": self.contact_number,
            "area_name": self.area_name,
        }

    def __str__(self):
        return f"{self.booth_number} - {self.booth_name}"


def _generate_complaint_id():
    return f"CMP-{uuid.uuid4().hex[:8].upper()}"


class Complaint(Document):
    """MongoDB collection: complaints"""

    STATUS_CHOICES = ("Pending", "In Progress", "Resolved", "Rejected")

    complaint_id = StringField(required=True, unique=True, default=_generate_complaint_id)
    name = StringField(required=True, max_length=150)
    mobile_number = StringField(required=True, max_length=10)
    booth_number = StringField(required=True, max_length=50)
    complaint_category = StringField(required=True, max_length=100)
    complaint_description = StringField(required=True, max_length=2000)
    status = StringField(choices=STATUS_CHOICES, default="Pending")
    date = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "complaints",
        "indexes": ["complaint_id", "booth_number", "status"],
        "ordering": ["-date"],
    }

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "complaint_id": self.complaint_id,
            "name": self.name,
            "mobile_number": self.mobile_number,
            "booth_number": self.booth_number,
            "complaint_category": self.complaint_category,
            "complaint_description": self.complaint_description,
            "status": self.status,
            "date": self.date.strftime("%Y-%m-%d"),
            "time": self.date.strftime("%H:%M:%S"),
        }

    def __str__(self):
        return f"{self.complaint_id} ({self.status})"
