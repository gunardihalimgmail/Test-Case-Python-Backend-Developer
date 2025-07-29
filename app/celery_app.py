# app/celery_app.py
import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery = Celery(
    "task_manager",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery.conf.beat_schedule = {
    "check-overdue-tasks": {
        "task": "app.tasks.jobs.check_overdue_tasks",
        "schedule": 30.0,  # tiap 30 detik
    }
}
celery.conf.timezone = "UTC"


# celery -A app.celery_app.celery worker --beat --loglevel=info
