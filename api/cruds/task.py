from typing import List, Tuple, Optional

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

import api.models.task as task_model
import api.schemas.task as task_schema

async def create_task(
  db: AsyncSession,
  task_create: task_schema.TaskCreate,
) -> task_model.Task:
  task = task_model.Task(**task_create.dict())
  db.add(task)
  await db.commit()
  await db.refresh(task)
  return task

async def get_tasks(db: AsyncSession) -> List[Tuple[task_model.Task]]:
  result: Result = await db.execute(select(task_model.Task))
  return result.scalars().all()

async def get_task(db: AsyncSession, task_id: int) -> Optional[task_model.Task]:
  result: Result = await db.execute(select(task_model.Task).where(task_model.Task.id == task_id))
  task: Optional[task_model.Task] = result.scalars().one_or_none()
  return task

async def update_task(
  db: AsyncSession,
  task_create: task_schema.TaskCreate,
  original: task_model.Task
) -> task_model.Task:
  original.title = task_create.title
  db.add(original)
  await db.commit()
  await db.refresh(original)
  return original

async def delete_task(db: AsyncSession, original: task_model.Task) -> None:
  await db.delete(original)
  await db.commit()