import json
import os
import subprocess
import time
from pathlib import Path
from .agents import AgentResult, BaseAgent
from .codex_agent import TaskPacket
from .config import settings
from .codex_agent import CodexAgent


def discover_claude() -> list[str]:
    candidates = []
    launcher = Path(os.environ.get("LOCALAPPDATA", "")) / "pnpm" / "claude.CMD"
    if launcher.exists(): candidates.append(str(launcher))
    store = Path(os.environ.get("LOCALAPPDATA", "")) / "pnpm" / "store"
    if store.exists():
        candidates.extend(str(p) for p in store.rglob("claude.exe") if "claude-code-win32-x64" in str(p))
        candidates.extend(str(p) for p in store.rglob("claude.exe") if "claude-code-win32-x64" not in str(p))
    return list(dict.fromkeys(candidates))


class ClaudeAgent(BaseAgent):
    name = "claude"
    capabilities = ("debugging", "architecture", "terminal", "coding", "testing", "documentation", "repository_context")

    def __init__(self, executable: str | None = None, timeout: int = 180):
        self.executable = executable
        self.timeout = timeout
        self.status = "NOT_CONFIGURED"
        self.version = None
        self.authenticated = False

    def health_check(self) -> dict:
        selected = self.executable
        candidates = [selected] if selected else discover_claude()
        for candidate in candidates:
            if not candidate: continue
            try:
                result = subprocess.run([candidate, "--version"], capture_output=True, text=True, timeout=10, shell=False)
                if result.returncode == 0 and result.stdout.strip(): selected = candidate; break
            except (OSError, subprocess.TimeoutExpired): continue
        if not selected:
            self.status = "UNAVAILABLE"; return {"status":"unavailable","version":None,"authenticated":False}
        self.executable = selected
        try:
            version = subprocess.run([selected, "--version"], capture_output=True, text=True, timeout=10, shell=False)
            auth = subprocess.run([selected, "auth", "status"], capture_output=True, text=True, timeout=10, shell=False)
        except (OSError, subprocess.TimeoutExpired):
            self.status = "UNAVAILABLE"
            return {"status":"unavailable","version":None,"authenticated":False}
        self.version = version.stdout.strip().splitlines()[0] if version.stdout.strip() else None
        try: auth_data = json.loads(auth.stdout)
        except json.JSONDecodeError: auth_data = {}
        self.authenticated = auth_data.get("loggedIn") is True
        self.status = "AVAILABLE" if self.authenticated else "UNAVAILABLE"
        return {"status": self.status.lower(), "version": self.version, "authenticated": self.authenticated}

    def execute(self, task_packet: TaskPacket | dict, context: dict | None = None) -> AgentResult:
        if isinstance(task_packet, dict): task_packet = TaskPacket(**task_packet)
        root = Path(task_packet.workspace_root).resolve()
        if not self.executable or self.status != "AVAILABLE": return AgentResult("", {"agent":"claude","status":"FAILED","error":"unavailable"})
        if not root.is_dir() or root == Path(root.anchor): raise ValueError("invalid workspace")
        initial = CodexAgent()._snapshot(root, task_packet.allowed_scope)
        started = time.perf_counter()
        args = [self.executable, "-p", task_packet.to_prompt(), "--output-format", "json", "--input-format", "text", "--restricted", "--allowedTools", "Read,Edit", "--no-session-persistence"]
        try:
            completed = subprocess.run(args, cwd=root, capture_output=True, text=True, timeout=self.timeout, shell=False)
            final = CodexAgent()._snapshot(root, task_packet.allowed_scope)
            changed = sorted(path for path in set(initial) | set(final) if initial.get(path) != final.get(path))
            output = completed.stdout.strip()
            try: parsed = json.loads(output); output = parsed.get("result", output) if isinstance(parsed, dict) else output
            except json.JSONDecodeError: pass
            return AgentResult(output, {"agent":"claude","status":"REVIEW" if completed.returncode == 0 else "FAILED","exit_code":completed.returncode,"changed_files":changed,"stderr":completed.stderr[-4000:],"duration":round(time.perf_counter()-started,3)})
        except subprocess.TimeoutExpired:
            return AgentResult("", {"agent":"claude","status":"FAILED","error":"timeout","duration":round(time.perf_counter()-started,3)})
