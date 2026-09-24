import json
import time
from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from .agents import AgentRegistry, MockAgent
from .config import settings
from .graph import validate_dependency_graph
from .inspector import ProjectInspector
from .router import Router
from .schemas import OrchestrationRequest
from .providers import OllamaProvider
from .prompts.analysis import analysis_prompt
from .prompts.planning import planning_prompt
from .structured import AgentExecutionResult, FinalReport, PlanningOutput, RequestAnalysis, PlannedTask
from .tasks import TaskManager
from .models import OrchestrationRecord
from .validation import ValidationEngine
from .codex_agent import CodexAgent
from .claude_agent import ClaudeAgent


class OrchestrationEngine:
    def __init__(self, registry: AgentRegistry | None = None, provider: OllamaProvider | None = None):
        self.registry = registry or AgentRegistry(); self.registry.register(MockAgent())
        self.codex = CodexAgent()
        self.codex.health_check()
        self.registry.register(self.codex)
        self.claude = ClaudeAgent(timeout=settings.claude_timeout_seconds)
        self.claude.health_check()
        self.registry.register(self.claude)
        self.router = Router(self.registry); self.provider = provider or OllamaProvider()

    def execute(self, request: OrchestrationRequest, db: Session | None = None, use_ollama: bool = True) -> dict:
        text = request.text
        execution_id = f"EXEC-{uuid4().hex[:10]}"
        context = ProjectInspector(settings.workspace).inspect()
        analysis = self.provider.structured(analysis_prompt(text, context.model_dump_json()), RequestAnalysis, retries=1) if use_ollama else RequestAnalysis(summary=text, goal=text, requirements=[text])
        plan = self.provider.structured(planning_prompt(analysis.model_dump_json(), context.model_dump_json()), PlanningOutput, retries=1) if use_ollama else PlanningOutput(
            objective=text,
            strategy="single local mock task",
            tasks=[PlannedTask(title=text[:120], description=text, acceptance_criteria=["Produce a non-empty mock result."])],
        )
        if not plan.tasks: raise RuntimeError("Planner returned no tasks")
        ids = [f"{execution_id}-TASK-{i+1:03d}" for i in range(len(plan.tasks))]
        deps = {ids[i]: [ids[d] for d in task.dependencies] for i, task in enumerate(plan.tasks)}
        order = validate_dependency_graph(ids, deps)
        routing = []; results = []
        for task_id in order:
            task = plan.tasks[ids.index(task_id)]
            if request.execution_mode == "mock":
                from .structured import RoutingDecision
                decision = RoutingDecision(task_id=task_id, selected_agent="mock", score=1.0, reason="explicit mock execution mode", alternatives=[a.name for a in self.registry.all() if a.name != "mock"])
            elif request.execution_mode == "external":
                decision = self.router.route_task(task_id, task.suggested_capabilities or ["coding"], task.description)
            else:
                decision = self.router.route_task(task_id, task.suggested_capabilities, task.description)
            routing.append(decision.model_dump())
            agent = self.registry.get(decision.selected_agent); started = time.perf_counter(); started_at = datetime.now(timezone.utc).isoformat()
            if agent.name in {"codex", "claude"} and request.execution_mode == "external":
                from .codex_agent import TaskPacket
                packet = TaskPacket(task_id=task_id, role="software engineer", objective=task.description, project_context=context.model_dump(), relevant_files=task.relevant_files, constraints=[], acceptance_criteria=task.acceptance_criteria, expected_output="summary and changed files", validation_requirements=task.validation_requirements, workspace_root=str(settings.workspace), allowed_scope=task.relevant_files)
                agent_result = agent.execute(packet, {"execution_id": execution_id})
                output = agent_result.output
                agent_metadata = agent_result.metadata
            else:
                output = agent.execute(task.description, {"acceptance_criteria": task.acceptance_criteria}).output
                agent_metadata = {}
            result = AgentExecutionResult(task_id=task_id, agent=agent.name, status="REVIEW", summary="Agent output produced", output=output, artifacts=agent_metadata.get("changed_files", []), errors=([agent_metadata.get("error")] if agent_metadata.get("error") else []), started_at=started_at, finished_at=datetime.now(timezone.utc).isoformat(), duration=round(time.perf_counter()-started, 4))
            validation = ValidationEngine().validate_execution(result)
            result.status = "DONE" if validation.passed else "FAILED"
            results.append(result)
        report = FinalReport(request_summary=analysis.summary, plan_summary=plan.strategy, tasks_total=len(results), tasks_completed=sum(r.status == "DONE" for r in results), tasks_failed=sum(r.status == "FAILED" for r in results), tasks_blocked=0, results=results, validation_summary="All execution results contained output and passed structural validation." if all(r.status == "DONE" for r in results) else "One or more results failed validation.", limitations=["MockAgent is the only configured executor."], final_response=f"Orchestration {execution_id} completed.")
        if db:
            record = OrchestrationRecord(id=execution_id, request=text, analysis_json=analysis.model_dump_json(), plan_json=plan.model_dump_json(), report_json=report.model_dump_json(), status="DONE" if report.tasks_failed == 0 else "FAILED")
            db.add(record); db.commit()
        return {"execution_id": execution_id, "status": "DONE" if report.tasks_failed == 0 else "FAILED", "analysis": analysis.model_dump(), "plan": plan.model_dump(), "tasks": [{"id": ids[i], **task.model_dump()} for i, task in enumerate(plan.tasks)], "routing": routing, "results": [r.model_dump() for r in results], "final_report": report.model_dump()}
