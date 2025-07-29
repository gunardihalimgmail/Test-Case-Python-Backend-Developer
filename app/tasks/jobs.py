# app/tasks/jobs.py
from datetime import datetime
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.celery_app import celery
from app.db import AsyncSessionLocal
from app.models import Task
import logging

logger = logging.getLogger(__name__)

@celery.task(name="app.tasks.jobs.check_overdue_tasks")
def check_overdue_tasks():
    """
    Cek task yang overdue & kirim reminder (simulasi logging)
    """
    import asyncio
    asyncio.run(_check_overdue_tasks())

async def _check_overdue_tasks():
    async with AsyncSessionLocal() as db:
        now = datetime.utcnow()
        result = await db.execute(
            select(Task).where(Task.due_date != None, Task.due_date < now, Task.is_completed == False)
        )
        overdue_tasks = result.scalars().all()
        for task in overdue_tasks:
            logger.warning(f"TASK OVERDUE: {task.title} (ID: {task.id}) - Due {task.due_date}")
            # di sini bisa diubah jadi: kirim email, push notif, dsb.
