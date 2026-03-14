# RBR-0323: Replace the tracked correctness scorecard JSON with a Python module

Status: ready
Owner: architecture-implementation
Created: 2026-03-14

## Goal
- Remove one of the final tracked JSON blobs by moving the published correctness scorecard from `reports/correctness/latest.json` to an ordinary Python report module, while keeping explicit temporary `.json` scorecard output available for narrow test runs and ad hoc harness checks.

## Deliverables
- `python/rebar_harness/correctness.py`
- `scripts/rebar_ops.py`
- `ops/reporting/readme.py`
- `README.md`
- `ops/agents/feature_implementation.md`
- `ops/agents/feature_planning.md`
- `ops/state/current_status.md`
- `ops/state/decision_log.md`
- `tests/conformance/scorecard_suite_support.py`
- `tests/conformance/test_correctness_*.py` that currently read the tracked published scorecard directly
- `tests/python/test_readme_reporting.py`
- `reports/correctness/latest.py`
- Delete `reports/correctness/latest.json`

## Acceptance Criteria
- `python/rebar_harness/correctness.py` changes the tracked default report path from `reports/correctness/latest.json` to `reports/correctness/latest.py`, and the tracked publication becomes a data-only Python module exposing one top-level report dict with the current correctness-report schema and payload.
- The published correctness payload is preserved through the format migration: the regenerated `reports/correctness/latest.py` keeps the same suite id, manifest ids and ordering, case ids and ordering, layer and suite summaries, baseline/candidate metadata, and aggregate totals as the deleted tracked JSON scorecard from the current checkout, aside from the path extension and regenerated timestamp.
- Explicit caller-selected `.json` report paths still work for temporary or task-local correctness runs. `python -m rebar_harness.correctness --report <temp>.json` continues emitting JSON with the existing schema so the narrow scorecard helpers and ad hoc local workflows do not need a second storage-format migration in this run.
- `scripts/rebar_ops.py` stops assuming the published correctness scorecard is JSON. `scorecard_from_config()`, `published_correctness_report_needs_refresh()`, and `refresh_published_correctness_scorecard()` load the new Python-backed correctness report while continuing to read the still-JSON benchmark report and runtime state through the existing JSON path.
- `ops/reporting/readme.py`, `README.md`, `ops/agents/feature_implementation.md`, `ops/agents/feature_planning.md`, `ops/state/current_status.md`, and `ops/state/decision_log.md` all point at `reports/correctness/latest.py` instead of the deleted JSON path, while `reports/benchmarks/latest.json` remains unchanged in this run.
- Active correctness-report tests no longer parse the tracked published scorecard with raw `json.loads(...read_text(...))`. Update the tracked-report readers under `tests/conformance/` plus `tests/python/test_readme_reporting.py` to use one shared helper or importlib-based loader for the Python-backed published scorecard, while leaving their temporary `.json` task-local reports alone.
- The existing verification surface still passes with the mixed-format publication model, including `tests.conformance.test_combined_correctness_scorecards`, `tests.conformance.test_correctness_smoke`, `tests.conformance.test_correctness_grouped_match_workflows`, `tests.conformance.test_correctness_quantified_alternation_open_ended_workflows`, and `tests.python.test_readme_reporting`.
- The live JSON count decreases by exactly `1`: both `git ls-files '*.json' | wc -l` and `rg --files -g '*.json' | wc -l` currently agree at `2` in this clean checkout and should finish at `1`, leaving only `reports/benchmarks/latest.json`. If the worker lands the deletion in a dirty tree where `git ls-files` lags, treat `rg --files -g '*.json' | wc -l` as the source of truth until the harness commit records the removal.

## Constraints
- Keep the scope to the published correctness scorecard, the directly coupled loader/writer code, the directly coupled README/state/prompt references, and the tests that currently hard-code the tracked correctness report path or file format.
- Do not convert `reports/benchmarks/latest.json`, runtime JSON artifacts under `.rebar/`, or temporary task-local correctness report outputs in the same run.
- Do not change correctness case data, fixture manifests, regex behavior, or the published correctness schema beyond the storage-format migration.
- Prefer one plain Python report module plus consolidated loaders over introducing another generator format, compatibility shim JSON file, or a second tracked correctness publication lane.

## Notes
- The ready queue already contains `RBR-0322`, which touches `reports/benchmarks/latest.json`, so this task intentionally targets only the correctness publication path to avoid invalidating the queued benchmark feature work.
- The dashboard and live checkout agree at `2` remaining JSON blobs right now: `reports/correctness/latest.json` and `reports/benchmarks/latest.json`.
- The tracked-file deletion is only half of the simplification here; the other half is removing the duplicated per-test assumption that the published correctness scorecard must be parsed from raw JSON text.
