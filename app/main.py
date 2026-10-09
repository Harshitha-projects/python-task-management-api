from datetime import datetime, timezone
from typing import Literal
from fastapi import FastAPI, Depends, HTTPException, Query
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import create_engine, Integer, String, DateTime, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, sessionmaker
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./tasks.db')
engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False} if DATABASE_URL.startswith('sqlite') else {})
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

class Task(Base):
    __tablename__ = 'tasks'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(String(1000), default='')
    status: Mapped[str] = mapped_column(String(20), default='todo')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

Base.metadata.create_all(bind=engine)
app = FastAPI(title='Task Management REST API', version='1.0')
Status = Literal['todo', 'in_progress', 'done']

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    description: str = Field(default='', max_length=1000)
    status: Status = 'todo'

class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = Field(default=None, max_length=1000)
    status: Status | None = None

class TaskOut(TaskCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime

def get_db():
    with SessionLocal() as db:
        yield db

@app.get('/health')
def health():
    return {'status':'ok'}

@app.post('/tasks', response_model=TaskOut, status_code=201)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    task = Task(**payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@app.get('/tasks', response_model=list[TaskOut])
def list_tasks(status: Status | None = None, limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    query = select(Task).order_by(Task.id)
    if status:
        query = query.where(Task.status == status)
    return db.scalars(query.offset(offset).limit(limit)).all()

@app.get('/tasks/{task_id}', response_model=TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(404, 'Task not found')
    return task

@app.patch('/tasks/{task_id}', response_model=TaskOut)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(404, 'Task not found')
    for key, value in payload.model_dump(exclude_unset=True).items():
        if value is None:
            raise HTTPException(422, f'{key} cannot be null')
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task

@app.delete('/tasks/{task_id}', status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(404, 'Task not found')
    db.delete(task)
    db.commit()
