## RBR-1453: Localize harness record-loader helpers onto owners

Owner: architecture-implementation
Created: 2026-03-27

## Goal
- Remove the generic record-loader helper pair from `python/rebar_harness/scorecard_io.py`.
- Keep correctness fixture loading owned by `python/rebar_harness/correctness.py` and benchmark manifest loading owned by `python/rebar_harness/benchmarks.py`, so `scorecard_io.py` goes back to scorecard/report plumbing instead of carrying harness-specific record-ingestion glue.

## Deliverables
- `python/rebar_harness/scorecard_io.py`
- `python/rebar_harness/correctness.py`
- `python/rebar_harness/benchmarks.py`
- `tests/python/test_ops_harness.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `tests/benchmarks/test_benchmark_manifest_validation.py`
- `tests/benchmarks/test_benchmark_publication_runtime_contracts.py`

## Acceptance Criteria
- `python/rebar_harness/correctness.py` no longer imports `load_unique_record_collection(...)` or `load_python_dict_attribute(...)` from `rebar_harness.scorecard_io`; it owns the smallest local helper path needed to:
  - load Python fixture modules
  - reject duplicate fixture manifest ids
  - reject duplicate fixture case ids
  - preserve the current correctness-specific load and duplicate-id error text
- `python/rebar_harness/benchmarks.py` no longer imports `load_unique_record_collection(...)` or `load_python_dict_attribute(...)` from `rebar_harness.scorecard_io`; it owns the smallest local helper path needed to:
  - load Python benchmark manifest modules
  - reject duplicate benchmark manifest ids
  - reject duplicate benchmark workload ids
  - preserve the current benchmark-specific load and duplicate-id error text
- Delete these helper definitions from `python/rebar_harness/scorecard_io.py` instead of moving them to another shared harness-loader module:
  - `load_unique_record_collection(...)`
  - `load_python_dict_attribute(...)`
- `tests/python/test_ops_harness.py` stops owning direct unit tests for those two helpers as `scorecard_io` behavior; replace that coverage with the smallest negative smoke needed to assert that `scorecard_io.py` no longer exports the deleted loader helpers.
- `tests/conformance/test_combined_correctness_scorecards.py`, `tests/benchmarks/test_benchmark_manifest_validation.py`, and `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` own the structural loader coverage that currently lives under `tests/python/test_ops_harness.py`, validating duplicate-id and module-load failure behavior through the correctness and benchmark owners instead of importing loader helpers from `rebar_harness.scorecard_io`.
- Keep the run structural only:
  - do not change Rust sources, `python/rebar/__init__.py`, fixture/workload data files, published reports, README copy, scripts, or tracked project-state prose
  - do not add a replacement shared loader utility module under `python/rebar_harness/` or `tests/`

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/conformance/test_combined_correctness_scorecards.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_benchmark_publication_runtime_contracts.py`
- `./.venv/bin/python -m py_compile python/rebar_harness/scorecard_io.py python/rebar_harness/correctness.py python/rebar_harness/benchmarks.py tests/python/test_ops_harness.py tests/conformance/test_combined_correctness_scorecards.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_benchmark_publication_runtime_contracts.py`
- `bash -lc "! rg -n '^def (load_unique_record_collection|load_python_dict_attribute)\\(' python/rebar_harness/scorecard_io.py"`

## Notes
- Queue and JSON check in this planning run:
  - `.rebar/runtime/dashboard.md` reported `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the runtime JSON count was not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and identifier check in this planning run:
  - `ops/tasks/blocked/` contained no architecture task to reopen or normalize first.
  - `rg -n 'RBR-1453|RBR-1454|RBR-1455' ops/state/current_status.md ops/state/backlog.md ops/tasks -g '*.md'` returned no reserved future-task match for `RBR-1453`.
- Candidate selection in this planning run:
  - The first candidate, deleting the grouped-quantified direct-bytes helper layer from `tests/python/fixture_parity_support.py`, was rejected for this run because a focused verification slice against `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` is already red on unrelated wider-ranged-repeat direct-bytes expectation drift in the current checkout.
  - `python/rebar_harness/scorecard_io.py` still carries two record-loader helpers that are not scorecard/report I/O and are used only to bridge `python/rebar_harness/correctness.py`, `python/rebar_harness/benchmarks.py`, and scorecard-helper tests.
  - Localizing those two helpers back onto the two harness owners removes a remaining shared cross-file layer without depending on the already-drifting wider-ranged-repeat owner lane.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/conformance/test_combined_correctness_scorecards.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_benchmark_publication_runtime_contracts.py` passed (`287 passed, 3 skipped, 2468 subtests passed in 28.13s`).
  - `./.venv/bin/python -m py_compile python/rebar_harness/scorecard_io.py python/rebar_harness/correctness.py python/rebar_harness/benchmarks.py tests/python/test_ops_harness.py tests/conformance/test_combined_correctness_scorecards.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_benchmark_publication_runtime_contracts.py` passed.
  - `rg -n '^def (load_unique_record_collection|load_python_dict_attribute)\(' python/rebar_harness/scorecard_io.py` currently reports the two shared loader-helper definitions at lines `35` and `206`, so the negative `rg` verification above fails only on the exact cleanup this task queues.
