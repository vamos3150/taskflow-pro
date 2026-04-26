from __future__ import annotations
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel


class SubtaskOut(BaseModel):
    id: int
    task_id: int
    title: str
    done: bool
    model_config = {"from_attributes": True}


class SubtaskCreate(BaseModel):
    title: str
    done: bool = False


class SubtaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


class CommentOut(BaseModel):
    id: int
    task_id: int
    author: str
    content: str
    created_at: datetime
    model_config = {"from_attributes": True}


class CommentCreate(BaseModel):
    content: str
    author: str = "山田 太郎"


class TaskCreate(BaseModel):
    project_id: int
    title: str
    description: Optional[str] = None
    status: str = "未着手"
    priority: str = "中"
    assignee: Optional[str] = None
    labels: Optional[str] = None
    due_date: Optional[datetime] = None


class TaskUpdate(BaseModel):
    project_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee: Optional[str] = None
    labels: Optional[str] = None
    due_date: Optional[datetime] = None


class TaskSummary(BaseModel):
    id: int
    project_id: int
    title: str
    status: str
    priority: str
    assignee: Optional[str]
    labels: Optional[str]
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    subtask_count: int = 0
    done_subtask_count: int = 0
    model_config = {"from_attributes": True}


class TaskOut(TaskCreate):
    id: int
    created_at: datetime
    updated_at: datetime
    subtasks: List[SubtaskOut] = []
    comments: List[CommentOut] = []
    model_config = {"from_attributes": True}


class ProjectCreate(BaseModel):
    name: str
    color: str = "#6366f1"


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None


class ProjectOut(BaseModel):
    id: int
    name: str
    color: str
    created_at: datetime
    task_count: int = 0
    model_config = {"from_attributes": True}


class DashboardOut(BaseModel):
    total: int
    by_status: Dict[str, int]
    by_assignee: Dict[str, int]
    overdue: int
    completion_rate: float
