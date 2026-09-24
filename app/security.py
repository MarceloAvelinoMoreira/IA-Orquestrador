from pathlib import Path
from .config import settings


class SecurityError(PermissionError):
    pass


class SecurityLayer:
    def validate_command(self, command: str) -> None:
        if not command.strip(): raise SecurityError("Empty command")
        if not settings.allow_commands: raise SecurityError("Command execution is disabled by configuration")
        lowered = command.lower()
        if any(token in lowered for token in ("format ", "del /s", "rm -rf", "git reset --hard")):
            raise SecurityError("Potentially destructive command blocked")

    def validate_path(self, path: str | Path) -> Path:
        resolved = Path(path).resolve()
        workspace = settings.workspace.resolve()
        if workspace not in resolved.parents and resolved != workspace: raise SecurityError("Path outside workspace")
        return resolved

