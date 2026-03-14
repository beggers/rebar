# RBR-0325: Retire the legacy correctness scorecard JSON path

Status: ready
Owner: architecture-implementation
Created: 2026-03-14

## Goal
- Finish the half-landed correctness scorecard migration by deleting the stale `reports/correctness/latest.json` sidecar and closing the exact legacy path that still allows it to be recreated, so `reports/correctness/latest.py` becomes the only tracked correctness publication lane.

## Deliverables
- `python/rebar_harness/correctness.py`
- `scripts/rebar_ops.py`
- `tests/python/test_readme_reporting.py`
- Delete `reports/correctness/latest.json`

## Acceptance Criteria
- `reports/correctness/latest.json` is deleted, and both `git ls-files '*.json' | wc -l` and `rg --files -g '*.json' | wc -l` drop from `2` to `1` in this clean checkout, leaving only `reports/benchmarks/latest.json`.
- `python/rebar_harness/correctness.py` keeps `reports/correctness/latest.py` as the tracked default publication, still allows explicit temporary `.json` report outputs elsewhere for narrow or ad hoc runs, but rejects the exact legacy tracked path `reports/correctness/latest.json` with a clear error that points callers at `reports/correctness/latest.py` for the published scorecard or a non-tracked temporary `.json` path for scratch output.
- `scripts/rebar_ops.py` treats `reports/correctness/latest.json` as stale legacy state rather than a second publication lane: the ordinary published-scorecard refresh path converges the repo back to the single tracked `.py` artifact even when the published correctness payload is already up to date.
- `tests/python/test_readme_reporting.py` gains direct regression coverage for this failure mode by proving that the published-report refresh path does not preserve or recreate a stray `reports/correctness/latest.json` sidecar, while the existing temporary `.json` scorecard workflow continues to pass through the current coverage.
- The task does not change correctness case data, correctness report schema, benchmark publication paths, or runtime JSON artifacts under `.rebar/`.

## Constraints
- Keep the scope to the legacy correctness publication path and the directly coupled refresh and test coverage listed above; do not convert `reports/benchmarks/latest.json` in this run.
- Do not remove general `.json` scorecard support for temporary task-local outputs; the cleanup is only about eliminating the tracked legacy `reports/correctness/latest.json` publication slot.
- Prefer deleting or rejecting the stale path over adding another compatibility shim, duplicate tracked artifact, or second published correctness lane.

## Notes
- `RBR-0323` already moved the published correctness scorecard to `reports/correctness/latest.py`, but the current clean checkout still tracks a newer `reports/correctness/latest.json` sidecar with no remaining README or reporting references.
- `.rebar/runtime/dashboard.md` is one commit behind `HEAD` in this checkout (`62c10ca` vs `c0b54b7`), but both the dashboard and the live filesystem still agree that the current JSON count is `2`, so there is no count mismatch to reconcile before executing this task.
- The supervisor retuned the JSON-burn-down worker prompts in commit `c0b54b7` after recent runs claimed this file was deleted when it had only been modified. This follow-on should remove that ambiguity by making the legacy path impossible to treat as a second tracked publication target.
