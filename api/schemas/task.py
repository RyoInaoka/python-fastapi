from typing import Optional
from pydantic import BaseModel, Field

class TaskBase(BaseModel):
  title: Optional[str] = Field(None, example="userAPIを作成する")

class TaskCreate(TaskBase):
  pass

class TaskCreateResponse(TaskCreate):
  id: int

  class Config:
    orm_mode = True

class Task(TaskBase):
  id: int
  is_done: bool = Field(False, description="完了したかどうか")

  class Config:
    orm_mode = True