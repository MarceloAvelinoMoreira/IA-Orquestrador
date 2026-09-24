from pathlib import Path
from .structured import ProjectContext


class ProjectInspector:
    EXCLUDED = {".venv", ".git", "__pycache__", "node_modules", "dist", "build", ".pytest_cache"}
    IMPORTANT = {"README.md", "requirements.txt", "pyproject.toml", "package.json", "Dockerfile", "main.py"}

    def __init__(self, root: str | Path, max_files: int = 80): self.root = Path(root).resolve(); self.max_files = max_files

    def inspect(self) -> ProjectContext:
        files = []
        for path in self.root.rglob("*"):
            if len(files) >= self.max_files or not path.is_file() or any(part in self.EXCLUDED for part in path.parts): continue
            if path.suffix.lower() in {".py", ".toml", ".json", ".md", ".txt", ".yml", ".yaml"}: files.append(path.relative_to(self.root).as_posix())
        languages = sorted({"Python" if f.endswith(".py") else "Markdown" if f.endswith(".md") else "YAML" if f.endswith((".yml", ".yaml")) else "Configuration" for f in files})
        important = [f for f in files if Path(f).name in self.IMPORTANT]
        tests = sorted({str(Path(f).parent).replace(".", "") or "." for f in files if "test" in Path(f).name.lower() or "tests" in Path(f).parts})
        configs = [f for f in files if Path(f).suffix in {".toml", ".json", ".yml", ".yaml"} or Path(f).name == "requirements.txt"]
        builds = [f for f in files if Path(f).name in {"pyproject.toml", "setup.py", "Dockerfile", "package.json"}]
        return ProjectContext(root=str(self.root), languages=languages, frameworks=["FastAPI", "SQLAlchemy"], important_files=important, configuration=configs, test_directories=tests, build_files=builds, git_state="UNVERIFIED: repository not initialized")

