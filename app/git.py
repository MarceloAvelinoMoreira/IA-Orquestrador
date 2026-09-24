from .runner import CommandRunner


class GitManager:
    def __init__(self, runner: CommandRunner | None = None): self.runner = runner or CommandRunner()

    def status(self) -> str:
        return self.runner.run("git status --short --branch").stdout

