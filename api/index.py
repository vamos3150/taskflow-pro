from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional, Dict
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func

from api import models, schemas
from api.database import engine, get_db
from api.seed import seed

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="TaskFlow Pro API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    db = next(get_db())
    try:
        seed(db)
    finally:
        db.close()


# ── Projects ──────────────────────────────────────────────────────────

@app.get("/api/projects", response_model=list[schemas.ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(models.Project).order_by(models.Project.created_at).all()
    result = []
    for p in projects:
        tc = db.query(func.count(models.Task.id)).filter(models.Task.project_id == p.id).scalar()
        result.append(schemas.ProjectOut(id=p.id, name=p.name, color=p.color, created_at=p.created_at, task_count=tc))
    return result


@app.post("/api/projects", response_model=schemas.ProjectOut, status_code=201)
def create_project(body: schemas.ProjectCreate, db: Session = Depends(get_db)):
    p = models.Project(name=body.name, color=body.color)
    db.add(p)
    db.commit()
    db.refresh(p)
    return schemas.ProjectOut(id=p.id, name=p.name, color=p.color, created_at=p.created_at, task_count=0)


@app.put("/api/projects/{project_id}", response_model=schemas.ProjectOut)
def update_project(project_id: int, body: schemas.ProjectUpdate, db: Session = Depends(get_db)):
    p = db.get(models.Project, project_id)
    if not p:
        raise HTTPException(404)
    if body.name is not None:
        p.name = body.name
    if body.color is not None:
        p.color = body.color
    db.commit()
    db.refresh(p)
    tc = db.query(func.count(models.Task.id)).filter(models.Task.project_id == p.id).scalar()
    return schemas.ProjectOut(id=p.id, name=p.name, color=p.color, created_at=p.created_at, task_count=tc)


@app.delete("/api/projects/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    p = db.get(models.Project, project_id)
    if not p:
        raise HTTPException(404)
    db.delete(p)
    db.commit()


# ── Tasks ─────────────────────────────────────────────────────────────

@app.get("/api/tasks", response_model=list[schemas.TaskSummary])
def list_tasks(
    project_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    assignee: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(models.Task)
    if project_id:
        query = query.filter(models.Task.project_id == project_id)
    if status:
        query = query.filter(models.Task.status == status)
    if priority:
        query = query.filter(models.Task.priority == priority)
    if assignee:
        query = query.filter(models.Task.assignee == assignee)
    if q:
        query = query.filter(models.Task.title.ilike(f"%{q}%"))
    tasks = query.order_by(models.Task.created_at.desc()).all()
    result = []
    for t in tasks:
        sc = len(t.subtasks)
        dc = sum(1 for s in t.subtasks if s.done)
        result.append(schemas.TaskSummary(
            id=t.id, project_id=t.project_id, title=t.title,
            status=t.status, priority=t.priority, assignee=t.assignee,
            labels=t.labels, due_date=t.due_date,
            created_at=t.created_at, updated_at=t.updated_at,
            subtask_count=sc, done_subtask_count=dc,
        ))
    return result


@app.post("/api/tasks", response_model=schemas.TaskOut, status_code=201)
def create_task(body: schemas.TaskCreate, db: Session = Depends(get_db)):
    if not db.get(models.Project, body.project_id):
        raise HTTPException(404, "Project not found")
    t = models.Task(**body.model_dump())
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


@app.get("/api/tasks/{task_id}", response_model=schemas.TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    t = db.get(models.Task, task_id)
    if not t:
        raise HTTPException(404)
    return t


@app.put("/api/tasks/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, body: schemas.TaskUpdate, db: Session = Depends(get_db)):
    t = db.get(models.Task, task_id)
    if not t:
        raise HTTPException(404)
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(t, k, v)
    t.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    db.commit()
    db.refresh(t)
    return t


@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    t = db.get(models.Task, task_id)
    if not t:
        raise HTTPException(404)
    db.delete(t)
    db.commit()


# ── Subtasks ──────────────────────────────────────────────────────────

@app.post("/api/tasks/{task_id}/subtasks", response_model=schemas.SubtaskOut, status_code=201)
def create_subtask(task_id: int, body: schemas.SubtaskCreate, db: Session = Depends(get_db)):
    if not db.get(models.Task, task_id):
        raise HTTPException(404)
    s = models.Subtask(task_id=task_id, **body.model_dump())
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


@app.put("/api/subtasks/{subtask_id}", response_model=schemas.SubtaskOut)
def update_subtask(subtask_id: int, body: schemas.SubtaskUpdate, db: Session = Depends(get_db)):
    s = db.get(models.Subtask, subtask_id)
    if not s:
        raise HTTPException(404)
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(s, k, v)
    db.commit()
    db.refresh(s)
    return s


@app.delete("/api/subtasks/{subtask_id}", status_code=204)
def delete_subtask(subtask_id: int, db: Session = Depends(get_db)):
    s = db.get(models.Subtask, subtask_id)
    if not s:
        raise HTTPException(404)
    db.delete(s)
    db.commit()


# ── Comments ──────────────────────────────────────────────────────────

@app.post("/api/tasks/{task_id}/comments", response_model=schemas.CommentOut, status_code=201)
def create_comment(task_id: int, body: schemas.CommentCreate, db: Session = Depends(get_db)):
    if not db.get(models.Task, task_id):
        raise HTTPException(404)
    c = models.Comment(task_id=task_id, **body.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@app.delete("/api/comments/{comment_id}", status_code=204)
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    c = db.get(models.Comment, comment_id)
    if not c:
        raise HTTPException(404)
    db.delete(c)
    db.commit()


# ── Dashboard ─────────────────────────────────────────────────────────

@app.get("/api/dashboard", response_model=schemas.DashboardOut)
def dashboard(project_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    query = db.query(models.Task)
    if project_id:
        query = query.filter(models.Task.project_id == project_id)
    tasks = query.all()
    total = len(tasks)
    by_status: Dict[str, int] = {"未着手": 0, "進行中": 0, "レビュー中": 0, "完了": 0}
    by_assignee: Dict[str, int] = {}
    overdue = 0
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    for t in tasks:
        by_status[t.status] = by_status.get(t.status, 0) + 1
        if t.assignee:
            by_assignee[t.assignee] = by_assignee.get(t.assignee, 0) + 1
        if t.due_date and t.due_date < now and t.status != "完了":
            overdue += 1
    done = by_status.get("完了", 0)
    return schemas.DashboardOut(
        total=total, by_status=by_status, by_assignee=by_assignee,
        overdue=overdue, completion_rate=round(done / total * 100, 1) if total else 0.0,
    )
