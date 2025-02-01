from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from api.db import Base


class Task(Base):
  __tablename__ = "tasks"

  id = Column(Integer, primary_key=True, index=True)
  title = Column(String(200), index=True)
  is_done = Column(Boolean, default=False)

  # user_id = Column(Integer, ForeignKey("users.id"))
  # user = relationship("User", back_populates="tasks")