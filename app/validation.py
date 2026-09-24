from dataclasses import dataclass
from .runner import CommandRunner


@dataclass
class ValidationResult:
    name: str
    passed: bool
    output: str


class ValidationEngine:
    def __init__(self, runner: CommandRunner | None = None): self.runner = runner or CommandRunner()

    def run(self, command: str, name: str = "validation") -> ValidationResult:
        result = self.runner.run(command)
        return ValidationResult(name, result.returncode == 0, result.stdout + result.stderr)

    def validate_execution(self, result) -> ValidationResult:
        passed = result.status == "REVIEW" and bool(result.output) and not result.errors
        return ValidationResult("agent_execution", passed, "execution output present" if passed else "execution requires review")
