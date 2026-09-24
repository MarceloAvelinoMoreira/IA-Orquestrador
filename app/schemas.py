from typing import Any
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    id: str | None = None
    title: str
    description: str = ""
    dependencies: list[str] = Field(default_factory=list)


class TaskResponse(TaskCreate):
    id: str
    status: str
    agent: str | None = None
    result: str | None = None


class OrchestrationRequest(BaseModel):
    request: str | None = None
    objective: str | None = None
    requirements: list[str] = Field(default_factory=list)
    context: dict[str, Any] = Field(default_factory=dict)
    execution_mode: str = "mock"

    @property
    def text(self) -> str: return self.request or self.objective or ""


class AgentResponse(BaseModel):
    name: str
    capabilities: list[str]
    available: bool
