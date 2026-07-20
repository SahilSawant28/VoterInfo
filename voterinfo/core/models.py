# This app intentionally does NOT define Django ORM (SQL) models here.
#
# All application data (Polling Booths, Complaints) lives in MongoDB and
# is modelled with MongoEngine documents in core/mongo_models.py.
#
# Django's relational ORM (SQLite by default) is still used, but only
# for Django's own built-in auth/session/admin tables.
from django.db import models  # noqa: F401
