import json
from uuid import uuid4
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import TaskRecord
from .schemas import TaskCreate


class TaskManager:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payload: TaskCreate) -> TaskRecord:
        task = TaskRecord(id=payload.id or f"TASK-{uuid4().hex[:8]}", title=payload.title,
                          description=payload.description, dependencies_json=json.dumps(payload.dependencies))
        self.db.add(task); self.db.commit(); self.db.refresh(task)
        return task

    def get(self, task_id: str) -> TaskRecord | None:
        return self.db.get(TaskRecord, task_id)

    def list(self) -> list[TaskRecord]:
        return list(self.db.scalars(select(TaskRecord).order_by(TaskRecord.created_at)))

    def dependencies(self, task: TaskRecord) -> list[str]:
        return json.loads(task.dependencies_json or "[]")

    def ready(self, task: TaskRecord) -> bool:
        return task.status in {"PENDING", "READY"} and all(
            (dep := self.get(dep_id)) is not None and dep.status == "DONE" for dep_id in self.dependencies(task)
        )

    TRANSITIONS = {"PENDING": {"READY", "BLOCKED"}, "READY": {"RUNNING", "BLOCKED"}, "RUNNING": {"REVIEW", "FAILED"}, "REVIEW": {"DONE", "FAILED"}, "BLOCKED": set(), "FAILED": set(), "DONE": set()}

    def transition(self, task: TaskRecord, target: str) -> TaskRecord:
        if target not in self.TRANSITIONS.get(task.status, set()): raise ValueError(f"invalid transition {task.status} -> {target}")
        task.status = target; self.db.commit(); self.db.refresh(task); return task
