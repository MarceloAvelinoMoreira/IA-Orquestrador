CANONICAL_CAPABILITIES = {"CODING", "DEBUGGING", "ARCHITECTURE", "TERMINAL", "REPOSITORY_CONTEXT", "LONG_CONTEXT", "MULTIMODAL", "DOCUMENTATION", "TESTING", "RESEARCH"}
ALIASES = {"code":"CODING", "coding":"CODING", "implementation":"CODING", "programming":"CODING", "debug":"DEBUGGING", "debugging":"DEBUGGING", "troubleshooting":"DEBUGGING", "tests":"TESTING", "testing":"TESTING", "unit_tests":"TESTING", "docs":"DOCUMENTATION", "documentation":"DOCUMENTATION", "repository":"REPOSITORY_CONTEXT", "repo_context":"REPOSITORY_CONTEXT", "codebase_context":"REPOSITORY_CONTEXT", "architecture":"ARCHITECTURE", "architectural_design":"ARCHITECTURE", "terminal":"TERMINAL", "command_line":"TERMINAL"}


def normalize_capability(value: str) -> str:
    key = value.strip().lower().replace("-", "_").replace(" ", "_")
    if key.endswith("s") and key[:-1] in ALIASES: key = key[:-1]
    return ALIASES.get(key, value.upper() if value.upper() in CANONICAL_CAPABILITIES else "UNKNOWN")


def normalize_capabilities(values: list[str]) -> tuple[list[str], list[str]]:
    normalized, unknown = [], []
    for value in values:
        result = normalize_capability(value)
        if result == "UNKNOWN": unknown.append(value)
        elif result not in normalized: normalized.append(result)
    return normalized, unknown


def infer_capabilities(text: str) -> list[str]:
    lowered = text.lower()
    rules = {"DEBUGGING": ("debug", "falha", "erro", "investigue", "causa raiz"), "TESTING": ("teste", "testes", "pytest"), "CODING": ("implemente", "crie", "função", "endpoint", "código"), "ARCHITECTURE": ("arquitetura", "design"), "TERMINAL": ("comando", "terminal", "shell"), "DOCUMENTATION": ("documentação", "readme")}
    return [capability for capability, keywords in rules.items() if any(keyword in lowered for keyword in keywords)]
