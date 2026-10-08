from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field


# =========================
# USER SCHEMAS
# =========================

class UserCreate(BaseModel):

    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    email: EmailStr

    password: str = Field(
        ...,
        min_length=6
    )

    role: str = "User"


class UserResponse(BaseModel):

    id: int
    full_name: str
    email: EmailStr
    role: str
    created_date: datetime

    class Config:
        from_attributes = True


# =========================
# LOGIN SCHEMA
# =========================

class LoginRequest(BaseModel):

    email: EmailStr
    password: str


class TokenResponse(BaseModel):

    access_token: str
    token_type: str


# =========================
# TASK SCHEMAS
# =========================

class TaskCreate(BaseModel):

    task_title: str = Field(
        ...,
        min_length=2,
        max_length=200
    )

    description: Optional[str] = None

    status: str = "Pending"

    priority: str = "Medium"

    due_date: Optional[datetime] = None


class TaskUpdate(BaseModel):

    task_title: Optional[str] = Field(
        None,
        min_length=2,
        max_length=200
    )

    description: Optional[str] = None

    status: Optional[str] = None

    priority: Optional[str] = None

    due_date: Optional[datetime] = None


class TaskResponse(BaseModel):

    id: int
    task_title: str
    description: Optional[str]
    status: str
    priority: str
    assigned_to: int
    created_date: datetime
    due_date: Optional[datetime]

    class Config:
        from_attributes = True
