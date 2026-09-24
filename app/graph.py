class DependencyError(ValueError): pass


def validate_dependency_graph(task_ids: list[str], dependencies: dict[str, list[str]]) -> list[str]:
    known = set(task_ids)
    for task_id in task_ids:
        for dep in dependencies.get(task_id, []):
            if dep not in known: raise DependencyError(f"missing dependency: {dep}")
            if dep == task_id: raise DependencyError(f"self dependency: {task_id}")
    state: dict[str, int] = {}; order: list[str] = []
    def visit(node: str):
        if state.get(node) == 1: raise DependencyError(f"circular dependency at: {node}")
        if state.get(node) == 2: return
        state[node] = 1
        for dep in dependencies.get(node, []): visit(dep)
        state[node] = 2; order.append(node)
    for task_id in task_ids: visit(task_id)
    return order

