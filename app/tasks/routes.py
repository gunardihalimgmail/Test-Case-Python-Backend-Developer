# app/tasks/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db import get_db
from app import models, schemas
from app.auth.utils import get_current_user
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/tasks", tags=["tasks"])

# CREATE
@router.post("/", response_model=schemas.TaskResponse)
async def create_task(task: schemas.TaskCreate, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    new_task = models.Task(
        title=task.title,
        description=task.description,
        due_date=task.due_date,
        is_completed=task.is_completed,
        created_by_user_id=current_user.id
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return new_task

# LIST (filter by is_completed, due_date)
@router.get("/", response_model=List[schemas.TaskResponse])
async def list_tasks(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    is_completed: Optional[bool] = None,
    due_date: Optional[datetime] = None
):
    query = select(models.Task).where(models.Task.created_by_user_id == current_user.id)
    if is_completed is not None:
        query = query.where(models.Task.is_completed == is_completed)
    if due_date is not None:
        query = query.where(models.Task.due_date <= due_date)
    result = await db.execute(query)
    return result.scalars().all()

# UPDATE
@router.patch("/{id}", response_model=schemas.TaskResponse)
async def update_task(id: int, task_update: schemas.TaskUpdate, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    result = await db.execute(select(models.Task).where(models.Task.id == id, models.Task.created_by_user_id == current_user.id))
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in task_update.dict(exclude_unset=True).items():
        setattr(task, key, value)
    await db.commit()
    await db.refresh(task)
    return task

# DELETE
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(id: int, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    result = await db.execute(select(models.Task).where(models.Task.id == id, models.Task.created_by_user_id == current_user.id))
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await db.delete(task)
    await db.commit()
    return None
