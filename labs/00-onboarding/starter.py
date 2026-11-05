
"""Stage 00 learner assignment — implement onboarding checks safely.

Use supplied synthetic flags; do not automatically collect a user's system
inventory, username, home directory or access tokens.
"""
def readiness(python_version,git_available,workspace_writable):
    raise NotImplementedError("Implement a privacy-preserving readiness report")

def pipeline_order(graph):
    raise NotImplementedError("Validate data-flow dependencies and detect cycles")

def safe_output_path(root,relative_name):
    raise NotImplementedError("Prevent traversal and never write to the workspace")

def evidence_check(evidence):
    raise NotImplementedError("Check a safe evidence template, not truth of results")
