import json
from typing import Dict, Any


def validate_workflow(workflow: Dict[str, Any]) -> bool:
    # Minimal validation: must have name and nodes (non-empty list), and each node must have id and type
    if not isinstance(workflow, dict):
        return False
    if "name" not in workflow:
        return False
    nodes = workflow.get("nodes")
    if not isinstance(nodes, list) or len(nodes) == 0:
        return False
    for n in nodes:
        if not isinstance(n, dict):
            return False
        if "id" not in n or "type" not in n:
            return False
    return True


def load_and_validate(path: str) -> bool:
    with open(path, "r", encoding="utf-8") as fh:
        wf = json.load(fh)
    return validate_workflow(wf)


if __name__ == "__main__":
    import sys
    ok = load_and_validate(sys.argv[1])
    print("VALID" if ok else "INVALID")
    sys.exit(0 if ok else 2)
