from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class AgentResult:
    output: str
    metadata: dict[str, Any]


class BaseAgent(ABC):
    name = "base"
    capabilities: tuple[str, ...] = ()
    status = "NOT_CONFIGURED"

    @abstractmethod
    def execute(self, objective: str, context: dict[str, Any] | None = None) -> AgentResult:
        raise NotImplementedError


class MockAgent(BaseAgent):
    name = "mock"
    capabilities = ("coding", "testing", "reasoning")
    status = "AVAILABLE"

    def execute(self, objective: str, context: dict[str, Any] | None = None) -> AgentResult:
        return AgentResult(output=f"Mock execution completed. Objective received: {objective}", metadata={"agent": self.name})


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> None:
        self._agents[agent.name] = agent

    def get(self, name: str) -> BaseAgent | None:
        return self._agents.get(name)

    def all(self) -> list[BaseAgent]:
        return list(self._agents.values())
