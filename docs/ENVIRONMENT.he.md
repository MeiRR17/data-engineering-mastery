# Working environment, resource guidance and privacy

## Who runs which commands?

The learner runs tools **locally** in a terminal they control. An AI tutor cannot know a user's hardware inventory unless the user shares it or grants an authorized tool access.

~~~bash
python3 --version
python3 scripts/system_profile.py
python3 scripts/system_profile.py --write-local
~~~

The optional script summarizes operating-system class, architecture, logical CPU count, estimated RAM, free project storage and availability of Python/Git/Docker. It does not need network access, root privileges, disk-content scans, username or device serial number. Its saved `learner/system-profile.local.json` is private and gitignored.

**Do not upload the complete hardware profile to public GitHub.** Sharing only the `light` / `moderate` / `full` category is usually sufficient for selecting a suitable exercise.

## Resource modes

| Tier | Recommended exercises | Caution |
| --- | --- | --- |
| `light` | SQLite, small synthetic fixtures, Python, optional DuckDB | Memory/storage limited or unknown |
| `moderate` | Local Docker/PostgreSQL/dbt as the machine permits | Stop if memory pressure becomes excessive |
| `full` | Optional local PySpark and single-node Kafka | Still use explicit CPU/memory limits; not mandatory |

These are **conservative suggestions**, not official compatibility results. OS, architecture, Java version and Docker configuration matter. Do not interpret insufficient hardware as a knowledge failure: use Light mode, then document the full-mode lab as *deferred*.

## Learning progress versus system inventory

The private `learner/progress.json` contains personal reflection and evidence and stays on the learner's computer. You can explicitly create a **sanitized** progress summary:

~~~bash
python3 scripts/roadmap.py export-summary
~~~

Review `learner/learning-status.md` before optionally committing it in your own repository. A connected GitHub tool can access that public summary **only if authorized**; it should not receive the private system profile.

## Visual editor and notebook setup

Use [the VS Code setup guide](VS-CODE-LEARNING-SETUP.md) for recommended Markdown/Jupyter extensions, preview shortcuts, Python environments and kernel selection. Installing an extension, creating a virtual environment or using a cloud account requires your own deliberate action.
