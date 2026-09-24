import subprocess
from .config import settings
from .security import SecurityLayer


class CommandRunner:
    def __init__(self, security: SecurityLayer | None = None): self.security = security or SecurityLayer()

    def run(self, command: str) -> subprocess.CompletedProcess[str]:
        self.security.validate_command(command)
        return subprocess.run(command, shell=True, cwd=settings.workspace, capture_output=True, text=True, timeout=settings.command_timeout_seconds)

