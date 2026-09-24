import pytest
from app.graph import DependencyError, validate_dependency_graph
from app.inspector import ProjectInspector
from app.providers import OllamaProvider
from app.structured import PlanningOutput, RequestAnalysis, extract_json, parse_model_output


def test_structured_schemas_and_markdown_json():
    analysis = parse_model_output('prefix ```json {"summary":"s","goal":"g"} ``` suffix', RequestAnalysis)
    assert analysis.goal == "g"
    plan = PlanningOutput(objective="x", strategy="s", tasks=[{"title":"t", "description":"d"}])
    assert plan.tasks[0].title == "t"


def test_invalid_json_is_rejected_without_eval():
    with pytest.raises(ValueError): extract_json("not json")


def test_dependency_graph_errors_and_order():
    assert validate_dependency_graph(["a", "b"], {"a": [], "b": ["a"]}) == ["a", "b"]
    with pytest.raises(DependencyError): validate_dependency_graph(["a"], {"a": ["missing"]})
    with pytest.raises(DependencyError): validate_dependency_graph(["a"], {"a": ["a"]})
    with pytest.raises(DependencyError): validate_dependency_graph(["a", "b"], {"a": ["b"], "b": ["a"]})


def test_project_inspector_excludes_virtual_environment(tmp_path):
    (tmp_path / "main.py").write_text("pass", encoding="utf-8")
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "secret.py").write_text("pass", encoding="utf-8")
    context = ProjectInspector(tmp_path).inspect()
    assert "main.py" in context.important_files
    assert all(".venv" not in item for item in context.important_files + context.configuration)


def test_provider_structured_retry(monkeypatch):
    responses = iter(["invalid", '{"summary":"s","goal":"g"}'])
    monkeypatch.setattr(OllamaProvider, "chat", lambda self, *args, **kwargs: next(responses))
    assert OllamaProvider().structured("x", RequestAnalysis).goal == "g"
