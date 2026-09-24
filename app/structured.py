import json
import re
from typing import Any
from pydantic import BaseModel, Field, model_validator


class RequestAnalysis(BaseModel):
    summary: str
    goal: str
    request_type: str = "general"
    complexity: str = "medium"
    requirements: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    requires_project_inspection: bool = True


class PlannedTask(BaseModel):
    title: str
    description: str
    dependencies: list[int] = Field(default_factory=list)
    suggested_capabilities: list[str] = Field(default_factory=list)
    relevant_files: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)
    validation_requirements: list[str] = Field(default_factory=list)
    risk: str = "low"


class PlanningOutput(BaseModel):
    objective: str
    strategy: str
    tasks: list[PlannedTask] = Field(min_length=1)

    @model_validator(mode="after")
    def valid_dependencies(self):
        for pos, task in enumerate(self.tasks):
            if pos in task.dependencies or any(i < 0 or i >= len(self.tasks) for i in task.dependencies):
                raise ValueError("invalid task dependency index")
        return self


class ProjectContext(BaseModel):
    root: str
    languages: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    important_files: list[str] = Field(default_factory=list)
    configuration: list[str] = Field(default_factory=list)
    test_directories: list[str] = Field(default_factory=list)
    build_files: list[str] = Field(default_factory=list)
    git_state: str = "UNVERIFIED"


class AgentExecutionResult(BaseModel):
    task_id: str
    agent: str
    status: str
    summary: str
    output: str = ""
    artifacts: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    started_at: str
    finished_at: str
    duration: float


class RoutingDecision(BaseModel):
    task_id: str
    selected_agent: str
    score: float
    reason: str
    alternatives: list[str] = Field(default_factory=list)


class FinalReport(BaseModel):
    request_summary: str
    plan_summary: str
    tasks_total: int
    tasks_completed: int
    tasks_failed: int
    tasks_blocked: int
    results: list[AgentExecutionResult]
    validation_summary: str
    limitations: list[str] = Field(default_factory=list)
    final_response: str


def extract_json(text: str) -> Any:
    """Extract one JSON object from plain text or a fenced markdown response."""
    cleaned = re.sub(r"```(?:json)?\s*", "", text, flags=re.I).replace("```", "").strip()
    decoder = json.JSONDecoder()
    for index, char in enumerate(cleaned):
        if char in "[{":
            try:
                return decoder.raw_decode(cleaned[index:])[0]
            except json.JSONDecodeError:
                continue
    raise ValueError("No valid JSON object found in model output")


def parse_model_output(text: str, schema: type[BaseModel]) -> BaseModel:
    value = extract_json(text)
    # Controlled repair for qwen3 responses that emit the first task object
    # instead of the requested PlanningOutput envelope. No arbitrary coercion.
    if schema is PlanningOutput and isinstance(value, dict) and "title" in value and "description" in value and "tasks" not in value:
        value = {"objective": "Model-generated plan", "strategy": "Execute the proposed task sequence", "tasks": [value]}
    return schema.model_validate(value)
