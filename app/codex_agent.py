import json
import hashlib
import subprocess
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from .agents import AgentResult, BaseAgent
from .config import settings


@dataclass
class TaskPacket:
    task_id: str
    role: str
    objective: str
    project_context: dict[str, Any]
    relevant_files: list[str]
    constraints: list[str]
    acceptance_criteria: list[str]
    expected_output: str
    validation_requirements: list[str]
    workspace_root: str
    allowed_scope: list[str]

    def to_prompt(self) -> str:
        return "Execute this task within the explicitly allowed workspace. Do not access files outside it. Return a concise summary of changes and validation.\nTASK_PACKET_JSON:\n" + json.dumps(asdict(self), ensure_ascii=False, indent=2)


class CodexAgent(BaseAgent):
    name = "codex"
    capabilities = ("coding", "debugging", "testing", "documentation", "repository_context")

    def __init__(self, executable: str = "codex", timeout: int | None = None):
        self.executable = executable
        self.timeout = timeout or settings.codex_timeout_seconds
        self.status = "NOT_CONFIGURED"
        self.version: str | None = None
        self.last_execution: dict[str, Any] = {}

    def health_check(self) -> dict[str, Any]:
        try:
            result = subprocess.run([self.executable, "login", "status"], capture_output=True, text=True, timeout=10, shell=False)
            version = subprocess.run([self.executable, "--version"], capture_output=True, text=True, timeout=10, shell=False)
            self.version = version.stdout.strip() or version.stderr.strip()
            authenticated = result.returncode == 0 and "logged in" in (result.stdout + result.stderr).lower()
            self.status = "AVAILABLE" if authenticated else "UNAVAILABLE"
            return {"status": self.status.lower(), "version": self.version, "authenticated": authenticated}
        except (OSError, subprocess.TimeoutExpired) as exc:
            self.status = "UNAVAILABLE"
            return {"status": "unavailable", "version": None, "authenticated": False, "error": type(exc).__name__}

    def _snapshot(self, root: Path, allowed_scope: list[str]) -> dict[str, str]:
        files = {}
        for item in root.rglob("*"):
            if item.is_file() and not any(part in {".git", ".venv", "__pycache__"} for part in item.relative_to(root).parts):
                rel = item.relative_to(root).as_posix()
                if not allowed_scope or rel in allowed_scope or any(rel.startswith(scope.rstrip("/") + "/") for scope in allowed_scope): files[rel] = hashlib.sha256(item.read_bytes()).hexdigest()
        return files

    def execute(self, task_packet: TaskPacket | dict[str, Any], context: dict[str, Any] | None = None) -> AgentResult:
        if isinstance(task_packet, dict): task_packet = TaskPacket(**task_packet)
        root = Path(task_packet.workspace_root).resolve()
        if not root.exists() or not root.is_dir(): raise ValueError("workspace_root must be an existing directory")
        if root == Path(root.anchor) or root == Path("C:/") or root == Path("C:\\"): raise ValueError("refusing broad workspace root")
        initial = self._snapshot(root, task_packet.allowed_scope)
        started = time.perf_counter(); started_at = datetime.now(timezone.utc).isoformat()
        args = [self.executable, "exec", "--ephemeral", "--skip-git-repo-check", "--sandbox", "workspace-write", "--json", "-C", str(root), task_packet.to_prompt()]
        try:
            completed = subprocess.run(args, capture_output=True, text=True, timeout=self.timeout, shell=False, cwd=root)
            output = completed.stdout.strip()
            messages = []
            for line in output.splitlines():
                try:
                    event = json.loads(line)
                    if event.get("type") == "item.completed" and event.get("item", {}).get("type") == "agent_message": messages.append(event["item"].get("text", ""))
                except json.JSONDecodeError: continue
            final = self._snapshot(root, task_packet.allowed_scope)
            changed = sorted(path for path in set(initial) | set(final) if initial.get(path) != final.get(path))
            status = "REVIEW" if completed.returncode == 0 else "FAILED"
            metadata = {"agent": self.name, "status": status, "stdout": output, "stderr": completed.stderr[-4000:], "changed_files": changed, "started_at": started_at, "finished_at": datetime.now(timezone.utc).isoformat(), "duration": round(time.perf_counter() - started, 3), "exit_code": completed.returncode, "execution_id": context.get("execution_id") if context else None, "task_id": task_packet.task_id}
            self.last_execution = metadata
            return AgentResult(output="\n".join(messages) or output, metadata=metadata)
        except subprocess.TimeoutExpired as exc:
            metadata = {"agent": self.name, "status": "FAILED", "error": "timeout", "task_id": task_packet.task_id, "duration": round(time.perf_counter() - started, 3), "stdout": str(exc.stdout or "")[-4000:], "stderr": str(exc.stderr or "")[-4000:]}
            self.last_execution = metadata
            return AgentResult(output="", metadata=metadata)
