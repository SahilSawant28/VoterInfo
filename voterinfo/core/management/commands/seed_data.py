"""
Management command: python manage.py seed_data

Seeds MongoDB with sample Polling Booth records so the Booth Locator
and API endpoints have data to demonstrate immediately after setup.
"""

from django.core.management.base import BaseCommand
from core.constants import SEED_BOOTHS
from core.mongo_models import PollingBooth


class Command(BaseCommand):
    help = "Seed MongoDB with sample polling booth records."

    def handle(self, *args, **options):
        created, updated = 0, 0
        for record in SEED_BOOTHS:
            booth, was_created = PollingBooth.objects.get_or_create(
                booth_number=record["booth_number"],
                defaults=record,
            )
            if was_created:
                created += 1
            else:
                for key, value in record.items():
                    setattr(booth, key, value)
                booth.save()
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seed complete. Created: {created}, Updated: {updated}, "
            f"Total booths in DB: {PollingBooth.objects.count()}"
        ))
