from .system import SYSTEM_PROMPT


def planning_prompt(analysis: str, context: str) -> str:
    return f"""{SYSTEM_PROMPT}\nReturn exactly ONE JSON OBJECT with top-level keys objective, strategy, tasks. tasks must be an ARRAY of 2-4 objects. Do not return a task object at the top level. Each task has title, description, dependencies as zero-based indexes, suggested_capabilities, relevant_files, acceptance_criteria, validation_requirements, risk. Keep lists short.\nANALYSIS: {analysis}\nPROJECT CONTEXT: {context}"""
