from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Text

from sqlalchemy.orm import relationship

from database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    full_name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(100),
        unique=True,
        index=True,
        nullable=False
    )

    password = Column(
        String(255),
        nullable=False
    )

    role = Column(
        String(20),
        default="User"
    )

    created_date = Column(
        DateTime,
        default=datetime.utcnow
    )

    tasks = relationship(
        "Task",
        back_populates="user"
    )


class Task(Base):

    __tablename__ = "tasks"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    task_title = Column(
        String(200),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    status = Column(
        String(50),
        default="Pending"
    )

    priority = Column(
        String(50),
        default="Medium"
    )

    assigned_to = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    created_date = Column(
        DateTime,
        default=datetime.utcnow
    )

    due_date = Column(
        DateTime,
        nullable=True
    )

    user = relationship(
        "User",
        back_populates="tasks"
    )
