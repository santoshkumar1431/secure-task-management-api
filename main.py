from typing import Optional

from fastapi import FastAPI
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from sqlalchemy.orm import Session

from database import Base
from database import engine
from database import get_db

from models import User
from models import Task

from schemas import UserCreate
from schemas import UserResponse
from schemas import LoginRequest
from schemas import TokenResponse
from schemas import TaskCreate
from schemas import TaskUpdate
from schemas import TaskResponse

from auth import hash_password
from auth import authenticate_user
from auth import create_access_token
from auth import get_current_user


# =========================
# CREATE DATABASE TABLES
# =========================

Base.metadata.create_all(
    bind=engine
)


# =========================
# FASTAPI APP
# =========================

app = FastAPI(
    title="Secure Task Management API",
    description="FastAPI Task Management API with JWT Authentication",
    version="1.0.0"
)


# =========================================================
# REGISTER
# =========================================================

@app.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_user:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    if user_data.role not in [
        "Admin",
        "User"
    ]:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be Admin or User"
        )

    hashed_password = hash_password(
        user_data.password
    )

    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        password=hashed_password,
        role=user_data.role
    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    return new_user


# =========================================================
# LOGIN
# =========================================================

@app.post(
    "/login",
    response_model=TokenResponse
)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):

    user = authenticate_user(
        db,
        login_data.email,
        login_data.password
    )

    if not user:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    access_token = create_access_token(
        data={
            "sub": str(user.id)
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# =========================================================
# CURRENT USER
# =========================================================

@app.get(
    "/users/me",
    response_model=UserResponse
)
def get_current_user_details(
    current_user: User = Depends(
        get_current_user
    )
):

    return current_user


# =========================================================
# CREATE TASK
# =========================================================

@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED
)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    new_task = Task(

        task_title=task_data.task_title,

        description=task_data.description,

        status=task_data.status,

        priority=task_data.priority,

        assigned_to=current_user.id,

        due_date=task_data.due_date
    )

    db.add(new_task)

    db.commit()

    db.refresh(new_task)

    return new_task


# =========================================================
# GET TASKS + FILTER
# =========================================================

@app.get(
    "/tasks",
    response_model=list[TaskResponse]
)
def get_tasks(

    status_filter: Optional[str] = None,

    priority: Optional[str] = None,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    query = db.query(Task).filter(
        Task.assigned_to == current_user.id
    )

    if status_filter:

        query = query.filter(
            Task.status == status_filter
        )

    if priority:

        query = query.filter(
            Task.priority == priority
        )

    return query.all()


# =========================================================
# GET SINGLE TASK
# =========================================================

@app.get(
    "/tasks/{task_id}",
    response_model=TaskResponse
)
def get_task(

    task_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    task = db.query(Task).filter(

        Task.id == task_id,

        Task.assigned_to == current_user.id

    ).first()

    if not task:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


# =========================================================
# UPDATE TASK
# =========================================================

@app.put(
    "/tasks/{task_id}",
    response_model=TaskResponse
)
def update_task(

    task_id: int,

    task_data: TaskUpdate,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    task = db.query(Task).filter(

        Task.id == task_id,

        Task.assigned_to == current_user.id

    ).first()

    if not task:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    if task_data.task_title is not None:

        task.task_title = task_data.task_title

    if task_data.description is not None:

        task.description = task_data.description

    if task_data.status is not None:

        task.status = task_data.status

    if task_data.priority is not None:

        task.priority = task_data.priority

    if task_data.due_date is not None:

        task.due_date = task_data.due_date

    db.commit()

    db.refresh(task)

    return task


# =========================================================
# DELETE TASK
# =========================================================

@app.delete(
    "/tasks/{task_id}"
)
def delete_task(

    task_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    task = db.query(Task).filter(

        Task.id == task_id,

        Task.assigned_to == current_user.id

    ).first()

    if not task:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    db.delete(task)

    db.commit()

    return {
        "message": "Task deleted successfully"
    }


# =========================================================
# MY TASKS
# =========================================================

@app.get(
    "/my-tasks",
    response_model=list[TaskResponse]
)
def get_my_tasks(

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    return db.query(Task).filter(
        Task.assigned_to == current_user.id
    ).all()


# =========================================================
# COMPLETE TASK
# =========================================================

@app.patch(
    "/tasks/{task_id}/complete",
    response_model=TaskResponse
)
def complete_task(

    task_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    task = db.query(Task).filter(

        Task.id == task_id,

        Task.assigned_to == current_user.id

    ).first()

    if not task:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    task.status = "Completed"

    db.commit()

    db.refresh(task)

    return task
