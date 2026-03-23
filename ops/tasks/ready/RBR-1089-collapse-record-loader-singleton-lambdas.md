## RBR-1089: Collapse record-loader singleton lambdas in harness manifests

Status: ready
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining singleton lambda adapters wrapped around `load_unique_record_collection(...)` in the two Python harness manifest loaders so the correctness and benchmark harnesses read through named same-file helpers or a strictly smaller equivalent instead of repeating one-off inline adapters for manifest ids, manifest paths, duplicate-error text, and nested-id extraction.

## Deliverables
- `python/rebar_harness/correctness.py`
- `python/rebar_harness/benchmarks.py`

## Acceptance Criteria
- `python/rebar_harness/correctness.py` no longer passes singleton lambdas into `load_unique_record_collection(...)` inside `load_fixture_manifests(...)` for:
  - `record_id`
  - `record_path`
  - `duplicate_record_error`
  - `nested_ids`
  - `duplicate_nested_error`
- `python/rebar_harness/benchmarks.py` no longer passes singleton lambdas into `load_unique_record_collection(...)` inside `load_manifests(...)` for:
  - `record_id`
  - `record_path`
  - `duplicate_record_error`
  - `nested_ids`
  - `duplicate_nested_error`
- Replace that wrapper layer with named same-file helpers, or a strictly smaller equivalent, while preserving the current loader behavior exactly:
  - `load_fixture_manifests(...)` still preserves requested path order;
  - correctness duplicate-manifest errors still include both conflicting paths;
  - correctness duplicate-case errors still include both conflicting paths;
  - `published_fixture_manifests()` still caches the loaded tuple over `DEFAULT_FIXTURE_PATHS`;
  - `load_manifests(...)` still preserves requested path order;
  - benchmark duplicate-manifest errors still remain `duplicate benchmark manifest id '<id>'`;
  - benchmark duplicate-workload errors still remain `duplicate benchmark workload id '<id>'`; and
  - neither cleanup changes `load_unique_record_collection(...)` in `python/rebar_harness/scorecard_io.py`.
- Keep the cleanup structural and local to the two harness loader files above.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py::test_fixture_manifest_loader_rejects_duplicate_ids tests/python/test_fixture_parity_support_contract.py::test_load_fixture_manifests_preserves_requested_path_order tests/python/test_fixture_parity_support_contract.py::test_published_fixture_manifests_cache_clear_reloads_current_default_fixture_paths tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::test_standard_benchmark_manifest_loader_rejects_duplicate_ids`
- `bash -lc "! rg -n 'record_id=lambda manifest: manifest\\.manifest_id|record_path=lambda manifest: manifest\\.path|duplicate_record_error=lambda manifest_id|nested_ids=lambda manifest: \\(case\\.case_id for case in manifest\\.cases\\)|nested_ids=lambda manifest: \\(|duplicate_nested_error=lambda case_id|duplicate_nested_error=lambda workload_id' python/rebar_harness/correctness.py python/rebar_harness/benchmarks.py"`

## Constraints
- Prefer deleting the singleton lambda layer over introducing another registry, helper module, or generic abstraction tier.
- Keep the exact duplicate-id error text stable in both harnesses.
- Do not broaden this task into `python/rebar_harness/scorecard_io.py`, benchmark workload files, correctness fixtures, reports, README copy, or tracked state prose.

## Notes
- `RBR-1089` is the next available unreserved task id in this checkout:
  - `ops/tasks/done/` currently runs through `RBR-1088`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contain no live `RBR-1089` task file; and
  - `rg -n 'RBR-1089|RBR-1090|RBR-1091|RBR-1092' ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` returned only historical mentions inside done-task notes, not a live reservation.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete and current in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest runtime cycle shows both task workers finishing `done`, with no inherited-dirty checkpoint churn or stalled task-refresh path.
- The simplification target is concrete in the live checkout:
  - `rg -n 'load_unique_record_collection\\(|record_id=lambda|record_path=lambda|duplicate_record_error=lambda|nested_ids=lambda|duplicate_nested_error=lambda' python/rebar_harness -g '*.py'` currently shows the ten singleton adapters at `python/rebar_harness/correctness.py:548-558` and `python/rebar_harness/benchmarks.py:1160-1173`.
- The focused verification slice is green in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py::test_fixture_manifest_loader_rejects_duplicate_ids tests/python/test_fixture_parity_support_contract.py::test_load_fixture_manifests_preserves_requested_path_order tests/python/test_fixture_parity_support_contract.py::test_published_fixture_manifests_cache_clear_reloads_current_default_fixture_paths tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::test_standard_benchmark_manifest_loader_rejects_duplicate_ids` returned `5 passed` in this run.
