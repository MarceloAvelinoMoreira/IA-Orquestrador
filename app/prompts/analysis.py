from .system import SYSTEM_PROMPT


def analysis_prompt(request: str, context: str) -> str:
    return f"""{SYSTEM_PROMPT}\nAnalyze the request. Return ONLY compact JSON with exactly these fields: summary, goal, request_type, complexity, requirements, constraints, assumptions, risks, requires_project_inspection. Keep strings concise and lists short.\nREQUEST: {request}\nPROJECT CONTEXT: {context}"""
