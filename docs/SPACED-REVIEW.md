# Private spaced review — stage-level learning reminders

The offline `scripts/spaced_review.py` tool helps you revisit weak topics after a lesson. It tracks **stage IDs and review dates only**, not your responses, system profile, identity, or competence. Its schedule is not a grade or a certificate. You must still demonstrate independent work to pass an assessment.

## First use

From the repository root, with Python 3.11+:

```bash
python3 scripts/spaced_review.py add 07
python3 scripts/spaced_review.py due --all
```

After you actually revisit Stage 07 (for example, by redoing a quality-contract exercise without the reference solution), record how well you recalled it:

```bash
python3 scripts/spaced_review.py review 07 good
python3 scripts/spaced_review.py due --all
```

Ratings: `again` (could not recall), `hard` (needed effort), `good` (recalled), `easy` (recalled confidently). Review spacing progresses through 1, 3, 7, 14 and 30 days. `again` resets to the one-day interval; `hard` holds the current interval; `good` advances one step; `easy` advances two. The tool prevents repeated ratings on the same day and never changes `learner/progress.json`.

Use `--on YYYY-MM-DD` to simulate a date **without modifying the system clock** (e.g., `due --on 2026-12-01`). The date override also applies to `add` and `review`; avoid recording simulated reviews in your real learning history.

## Privacy and reliability

- State is written only to `learner/reviews.local.json`, which matches the repository's `learner/*.local.json` Git ignore rule. No external requests or GitHub API calls are made.
- The file is atomically replaced and restricted to mode 0600 on POSIX systems. Existing invalid data is rejected rather than silently reset, and symlink state files are refused.
- Keep the entire `learner/` directory private; never commit or screenshot local review state for public portfolio evidence. If you need to reset the tool, make a private backup before deleting the local file.
- This is a lightweight personal reminder, not a scientific individualized memory model or a substitute for independent assessment.

To run its isolated tests:

```bash
python3 -m unittest discover -s tests -p 'test_spaced_review.py' -v
```
