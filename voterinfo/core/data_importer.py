"""
core/data_importer.py
-----------------------
UNIT 3 - THREADING.

Uses Python's `threading` module to import/seed polling-booth data into
MongoDB in the background, without blocking the request/response cycle.
A simple in-memory status dict is exposed so the frontend can poll
`/api/import-status/` and show a loading indicator until the background
thread finishes.
"""

import logging
import threading
import time

logger = logging.getLogger('core')

# Shared, thread-safe-enough status dict for a demo app (a single
# process). In a multi-worker production deployment you would back
# this with a cache (Redis) or a task queue (Celery) instead.
_status_lock = threading.Lock()
IMPORT_STATUS = {
    "running": False,
    "completed": False,
    "imported_count": 0,
    "error": None,
    "started_at": None,
    "finished_at": None,
}


def _set_status(**kwargs):
    with _status_lock:
        IMPORT_STATUS.update(kwargs)


def get_status() -> dict:
    with _status_lock:
        return dict(IMPORT_STATUS)


def _do_import(records):
    """The actual work performed on the background thread."""
    from core.mongo_models import PollingBooth

    _set_status(running=True, completed=False, error=None,
                imported_count=0, started_at=time.time(), finished_at=None)
    try:
        count = 0
        for record in records:
            # Simulate network/disk latency of a real bulk import.
            time.sleep(0.05)
            PollingBooth.objects(booth_number=record["booth_number"]).update_one(
                upsert=True,
                set__booth_name=record["booth_name"],
                set__address=record["address"],
                set__pin_code=record["pin_code"],
                set__officer_name=record["officer_name"],
                set__contact_number=record.get("contact_number", ""),
                set__area_name=record.get("area_name", ""),
            )
            count += 1
        _set_status(running=False, completed=True, imported_count=count,
                    finished_at=time.time())
        logger.info("Background import finished: %s records", count)
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Background import failed")
        _set_status(running=False, completed=False, error=str(exc),
                    finished_at=time.time())


def import_booths_async(records=None) -> threading.Thread:
    """
    Kick off booth-data import on a background daemon thread and
    immediately return the Thread object (non-blocking).
    """
    if records is None:
        from core.constants import SEED_BOOTHS
        records = SEED_BOOTHS

    thread = threading.Thread(target=_do_import, args=(records,), daemon=True)
    thread.start()
    return thread
