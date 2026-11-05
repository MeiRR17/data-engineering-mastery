"""Implement these local release-simulator functions, without copying the oracle."""
def build_release(source, output, version):
    raise NotImplementedError("Build a reproducible, allowlisted artifact + SHA-256 manifest")

def verify_release(bundle, manifest):
    raise NotImplementedError("Verify integrity, schema and safe archive members")

def deploy_release(bundle, manifest, root, environment, *,
                   fail_health=False, crash_before_switch=False):
    raise NotImplementedError("Health gate, environment separation, atomic promotion")

def rollback_release(root, environment):
    raise NotImplementedError("Verify previous version and atomically roll back")

def deployment_status(root, environment):
    raise NotImplementedError("Report active version without mutating state")

