
"""Stage 00 offline onboarding reference — synthetic input, no device inventory.

Never invokes system_profile or reads usernames, disk state or credentials.
Actual environment profiling requires deliberate learner action.
"""
from graphlib import CycleError, TopologicalSorter
from pathlib import Path


def readiness(python_version,git_available,workspace_writable):
    if (not isinstance(python_version,tuple) or len(python_version)!=3
        or any(type(n) is not int or n<0 for n in python_version)
        or type(git_available) is not bool or type(workspace_writable) is not bool):
        raise ValueError("invalid readiness inputs")
    issues=[]
    if python_version<(3,11,0):
        issues.append("PYTHON_TOO_OLD")
    if not git_available:
        issues.append("GIT_UNAVAILABLE")
    if not workspace_writable:
        issues.append("WORKSPACE_READ_ONLY")
    return {"ready":not issues,"issues":issues,
            "required_python":"3.11+",
            "real_device_inventory_collected":False}


def pipeline_order(graph):
    if not isinstance(graph,dict) or not graph:
        raise ValueError("graph must be nonempty")
    for key,dependencies in graph.items():
        if not isinstance(key,str) or not key:
            raise ValueError("invalid graph node")
        if not isinstance(dependencies,list) or len(dependencies)!=len(set(dependencies)):
            raise ValueError("invalid graph dependencies")
        if any(not isinstance(p,str) or p not in graph for p in dependencies):
            raise ValueError("unknown graph dependency")
    try:
        return list(TopologicalSorter(graph).static_order())
    except CycleError as exc:
        raise ValueError("pipeline dependency cycle") from exc


def safe_output_path(root,relative_name):
    """Compute safe path, but NEVER create, write or delete it."""
    root=Path(root)
    if not root.is_dir() or root.is_symlink():
        raise ValueError("root must be an ordinary existing directory")
    if not isinstance(relative_name,str) or not relative_name:
        raise ValueError("relative output name required")
    other=Path(relative_name)
    if other.is_absolute() or any(x in (".","..") for x in other.parts):
        raise ValueError("unsafe output path")
    candidate=root/other
    if not candidate.resolve().is_relative_to(root.resolve()):
        raise ValueError("path escapes workspace")
    if candidate.is_symlink():
        raise ValueError("output symlink forbidden")
    return candidate


def evidence_check(evidence):
    required={"commit","command","test_result","reflection"}
    if not isinstance(evidence,dict) or set(evidence)!=required:
        raise ValueError("evidence fields missing or unexpected")
    for field in required:
        value=evidence[field]
        if not isinstance(value,str) or not value.strip() or len(value)>500:
            raise ValueError("evidence must be short, nonempty text")
    # This only validates a learning template, not the truth of its claims.
    return {"structurally_complete":True,"independently_verified":False}
