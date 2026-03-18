# RBR-0624: Collapse the correctness builder contract modules onto one suite

Status: ready
Owner: architecture-implementation
Created: 2026-03-18

## Goal
- Replace `tests/conformance/test_correctness_observation_contract.py` and `tests/conformance/test_correctness_summary_builder_contract.py` with one pure-Python pytest suite so the correctness-harness builder layer stops spreading closely related normalization, observation-summary, fixture-summary, and scorecard-aggregation coverage across two small modules.

## Deliverables
- `tests/conformance/test_correctness_builder_contracts.py`
- Delete `tests/conformance/test_correctness_observation_contract.py`
- Delete `tests/conformance/test_correctness_summary_builder_contract.py`

## Acceptance Criteria
- `tests/conformance/test_correctness_builder_contracts.py` covers exactly the current pure builder-layer contract surface and no broader harness/reporting behavior:
  - observation normalization and comparison coverage for `_normalize_value(...)`, `normalize_match_metadata(...)`, `normalize_warning_records(...)`, `normalize_exception(...)`, `compare_observations(...)`, and `build_observation_summary(...)`;
  - scorecard-construction coverage for `build_fixture_summary(...)` and `build_scorecard(...)`; and
  - the existing narrow synthetic-manifest / synthetic-case-result scorecard checks now live in the consolidated suite instead of a sibling module.
- The consolidation preserves the current behavioral assertions exactly:
  - bytes named-capture normalization, missing optional-group metadata, iterator exhaustion, warning payload normalization, exception payload normalization, unimplemented-preference, and mismatch-note ordering remain covered;
  - scorecard summary, diagnostics, layer fanout, suite fanout, representative fixture metadata, and narrow single-manifest fixture-summary assertions remain covered; and
  - no current builder-layer contract is dropped silently just because it moves into the new file.
- Keep the cleanup local and ordinary:
  - prefer one real pytest module with local helper builders over another support module, registry, or import-only wrapper;
  - keep `python/rebar_harness/correctness.py`, published reports, fixtures under `tests/conformance/fixtures/`, benchmark tests, and state/reporting files out of scope; and
  - do not broaden this run into `tests/conformance/test_correctness_scorecard_registry_contract.py` or `tests/conformance/test_combined_correctness_scorecards.py`.
- After the consolidation lands:
  - `bash -lc "! rg --files tests/conformance | rg 'test_correctness_(observation_contract|summary_builder_contract)\\.py$'"`
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_correctness_builder_contracts.py`
  - `bash -lc "! rg --files tests/conformance | rg 'test_correctness_(observation_contract|summary_builder_contract)\\.py$'"`

## Constraints
- Keep this cleanup structural only. Do not change correctness-harness behavior, fixture contents, published scorecards, benchmark expectations, queue/state prose, or README/reporting content.
- Do not replace the deleted files with import-only compatibility wrappers.
- Preserve readable test names so the builder-layer coverage still makes it obvious which normalization or scorecard contract failed.

## Notes
- `RBR-0624` is the next available task id:
  - `ops/state/backlog.md` and `ops/state/current_status.md` reserve `RBR-0623` only; and
  - no `RBR-0624` file exists in `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, or `ops/tasks/blocked/`.
- No blocked architecture task needed reopening first, and rule 10 does not apply in the current checkout:
  - `ops/tasks/blocked/` and `ops/tasks/in_progress/` are empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `blocked: 0`, and `Last Cycle Anomalies: none`;
  - the live checkout is clean (`git status --short --branch` returned only `## main...origin/main`); and
  - the latest dashboard cycle shows both task workers finishing at `done`, so the shared queue is not currently bottlenecked by inherited-dirty or post-commit refresh churn.
- JSON burn-down remains complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplicate builder-contract surface is concrete in the current checkout:
  - `tests/conformance/test_correctness_observation_contract.py` and `tests/conformance/test_correctness_summary_builder_contract.py` currently total `651` lines;
  - both modules import only correctness-harness builder helpers out of `rebar_harness.correctness` and stay on the same pure-Python contract layer rather than touching CLI/report publication flow; and
  - the split currently leaves closely related observation-summary and scorecard-builder assertions on two neighboring files even though they exercise one internal builder pipeline.
- 2026-03-18 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_correctness_observation_contract.py tests/conformance/test_correctness_summary_builder_contract.py` passes (`9 passed in 0.04s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_correctness_builder_contracts.py` currently fails exactly on this cleanup with `ERROR: file or directory not found: tests/conformance/test_correctness_builder_contracts.py`; and
  - `bash -lc "! rg --files tests/conformance | rg 'test_correctness_(observation_contract|summary_builder_contract)\\.py$'"` currently fails exactly on this cleanup because both superseded files still exist.
