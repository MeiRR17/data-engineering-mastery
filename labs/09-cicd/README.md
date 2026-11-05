# Stage 09 — CI/CD, Reproducible Releases and Safe Rollback

[Stage 09 curriculum](../../curriculum/modules/09.md) · [Stage 08](../08-serving/README.md) · [Assessment rubric](../../docs/ASSESSMENT.md)

## Learning goal

A pipeline that passed tests is not necessarily safe to release. Here you learn the **Build → Verify → Promote → Health Gate → Rollback** lifecycle, how an immutable artifact differs from a mutable running environment, and why an audit-friendly release must be reproducible.

**Scope:** This is a local release-simulator implemented in the Python standard library. No Docker, cloud accounts, OIDC, repository secrets, real production environment or external calls. It does not deploy software to any server. Environments `dev`, `staging` and `prod-sim` are merely subfolders in a disposable directory, never real production.

~~~mermaid
flowchart LR
  S[Allowlisted synthetic source] --> B[Deterministic ZIP build]
  B --> M[SHA-256 manifest]
  M --> V{Verify archive and contract}
  V -->|failed| X[Reject release]
  V --> H{Health + quality gate}
  H -->|failed| X
  H -->|passed| P[Stage immutable version]
  P --> A[Atomic current pointer]
  A --> R[Rollback to verified prior version]
~~~

## Quickstart

Run from the root of the repository:

~~~bash
# Prove the reference implementation and test oracle work:
python3 labs/09-cicd/grade.py --reference

# See an end-to-end build, simulated promotion, rejection and rollback:
python3 labs/09-cicd/demo.py

# Learner implementation — expected to fail initially:
python3 labs/09-cicd/grade.py
~~~

The exercise source is [starter.py](starter.py). Implement five functions without copying [instructor/reference.py](instructor/reference.py) before trying on your own. The graded reference has **26 automated scenarios**, and CI also runs the demonstration.

## Exactly what you build

1. **Reproducible build:** Package only `README.txt` and `app.json` from a synthetic source directory into a deterministic ZIP. Fix timestamps, ordering and metadata so equal sources yield equal binary digests. Keep artifact versioned as `datapulse-vN.N.N.zip`.
2. **Manifest:** Record SHA-256 and exact byte size in a JSON file. Never embed credentials or machine-specific paths. Ensure the same version cannot be silently overwritten by different content.
3. **Verify before deploy:** Reject changed bytes, manifest mismatches, unexpected ZIP members, invalid paths, symlinked source files and unsupported application metadata.
4. **Environment isolation:** Each of `dev`, `staging`, `prod-sim` has its own current release pointer and archived release bundles. Switching staging cannot change dev.
5. **Health gate and atomic promotion:** Health and data-quality checks must pass before pointing to a new release. Use one atomic replacement of `current.json`; a simulated crash before this step must leave the previous release active.
6. **Rollback:** Confirm the previous bundle is still intact before reverting. A corrupted old artifact must **block** rollback rather than silently downgrade to an unknown state.
7. **Incident exercise:** Intentionally corrupt one artifact, observe rejection, restore a known-good build and explain the evidence you would need before a real release.
8. **Migration safety design:** Sketch an *expand → backfill → contract* database migration and a safe rollback policy. Describe why schema rollback may not be possible after destructive data changes. This planning task is required; **executable PostgreSQL migration rollback is not yet part of this lab**.

## The deployment state machine

| Initial state | Operation | Gate | Result |
|---|---|---|---|
| Empty | Deploy v1 | Valid artifact + healthy app | v1 active |
| v1 | Deploy v1 again | Same SHA | No change |
| v1 | Deploy v2 | Health and quality pass | v2 active, v1 rollback target |
| v1 | Deploy unhealthy v2 | Health fails | v1 remains active |
| v1 | Crash before pointer switch | Simulated fault | v1 remains active |
| v2 | Rollback | v1 checksum and health valid | v1 active |
| v2 | Rollback to corrupted v1 | Integrity check fails | v2 remains active |

### CI vs CD vs release

**Continuous Integration (CI)** verifies a proposed change; **Continuous Delivery** makes a verified release *ready* to deploy; **Continuous Deployment** promotes it automatically. This repository's GitHub Actions currently performs **CI and local release simulation**, not automatic deployment. Opening a PR does not grant environment secrets or production permissions. Real cloud environments require OIDC/short-lived identity, protected environments, approved deployments, telemetry, rollback runbooks, reliable migrations, cost bounds and disaster recovery.

### Key trust boundary

**SHA-256 provides integrity relative to a trusted manifest, not authenticity.** If an attacker can replace both ZIP and manifest, the checksum alone does not prove who built the artifact. Production delivery requires trusted provenance and artifact signing/attestation, and protected CI. This lab also does not guarantee power-loss durability or concurrent multi-process deployment safety.

## Assessment — no AI

Explain how to:
- Detect tampering even when a build's ZIP file can still be opened.
- Distinguish release rollback from schema/data rollback.
- Prevent untrusted PR code from accessing a deployment token.
- Recover if a service reports unhealthy after deployment, and preserve evidence.
- Ensure a release to staging does not change production and why a simple SHA does not prove authenticity.

**Exit gate:** Student-built `starter.py` passes all 26 scenarios; a deliberate failure is reproduced and fixed; the student supplies a red-to-green test log, a release note containing version and SHA, an ADR on migration trade-offs, and a personal PR. The public CI passing the instructor reference is not evidence that any student passed independently.
