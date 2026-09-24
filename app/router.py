from dataclasses import dataclass
from .agents import AgentRegistry, BaseAgent
from .structured import RoutingDecision
from .capabilities import normalize_capabilities


@dataclass
class RouteDecision:
    agent: BaseAgent
    score: float
    rationale: dict[str, int]


class Router:
    def __init__(self, registry: AgentRegistry):
        self.registry = registry

    def route(self, objective: str, context: dict | None = None) -> RouteDecision:
        text = objective.lower()
        scores = []
        for agent in self.registry.all():
            cap = set(agent.capabilities)
            rationale = {"context_awareness": int("refator" in text or "arquivo" in text),
                         "coding": int(any(x in text for x in ("implemente", "crie", "código", "endpoint"))),
                         "reasoning": int(any(x in text for x in ("debug", "investigue", "analise"))),
                         "terminal": int(any(x in text for x in ("build", "teste", "comando")))}
            score = sum(rationale[k] for k in rationale if {"context_awareness":"context", "coding":"coding", "reasoning":"reasoning", "terminal":"terminal"}[k] in cap)
            scores.append(RouteDecision(agent, score, rationale))
        if not scores:
            raise RuntimeError("No agents registered")
        return max(scores, key=lambda x: x.score)

    def route_task(self, task_id: str, required_capabilities: list[str], description: str = "") -> RoutingDecision:
        ranked = []
        normalized, unknown = normalize_capabilities(required_capabilities)
        required = set(normalized)
        for agent in self.registry.all():
            agent_capabilities, _ = normalize_capabilities(list(agent.capabilities))
            overlap = len(required.intersection(agent_capabilities))
            score = overlap / len(required) if required else (1.0 if agent.status == "AVAILABLE" else 0.0)
            ranked.append((score, agent))
        ranked.sort(key=lambda item: (-item[0], item[1].name))
        if not ranked or ranked[0][1].status != "AVAILABLE":
            raise RuntimeError("No available agent matches task capabilities")
        selected = ranked[0]
        if selected[0] <= 0: raise RuntimeError("NO_CAPABILITY_MATCH")
        return RoutingDecision(task_id=task_id, selected_agent=selected[1].name, score=round(selected[0], 3), reason=f"normalized capabilities: {normalized}; unknown: {unknown}", alternatives=[a.name for _, a in ranked[1:]])
