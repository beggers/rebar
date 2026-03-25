## RBR-1312: Centralize shared benchmark manifest-path constants

Status: ready
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Remove the remaining duplicate ownership of the shared `module_boundary` and `collection_replacement_boundary` manifest-path constants so `tests/benchmarks/benchmark_test_support.py` is the only benchmark support owner for those two paths, instead of leaving the same literals redefined across multiple benchmark support and benchmark test files.

## Deliverables
- `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Stop redefining the shared `MODULE_BOUNDARY_MANIFEST_PATH` and `COLLECTION_REPLACEMENT_MANIFEST_PATH` values in the surviving benchmark support owners that only consume those paths:
  - `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` should import and reuse the shared path constants from `tests.benchmarks.benchmark_test_support` instead of rebuilding those two paths locally; and
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` should import and reuse `MODULE_BOUNDARY_MANIFEST_PATH` from `tests.benchmarks.benchmark_test_support` instead of defining a second local copy.
- Remove the now-unnecessary duplicate local path assignments from the benchmark tests that currently mirror those same shared paths:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` should stop defining local `MODULE_BOUNDARY_MANIFEST_PATH` and `COLLECTION_REPLACEMENT_MANIFEST_PATH` assignments when it can import or reuse the existing shared owner paths directly; and
  - `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` should compare against the shared imported `MODULE_BOUNDARY_MANIFEST_PATH` constant instead of rebuilding that same repo path inline.
- Keep the ownership boundary narrow and explicit:
  - do not move the source-tree-specific manifest-path constants such as `OPTIONAL_GROUP_MANIFEST_PATH`, `NESTED_GROUP_MANIFEST_PATH`, `EXACT_REPEAT_MANIFEST_PATH`, `RANGED_REPEAT_MANIFEST_PATH`, `GROUPED_ALTERNATION_MANIFEST_PATH`, `GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH`, `NESTED_GROUP_REPLACEMENT_MANIFEST_PATH`, or `OPEN_ENDED_MANIFEST_PATH` off `tests/benchmarks/source_tree_benchmark_anchor_support.py`;
  - do not introduce a new helper/broker module or a forwarding alias layer for these two constants; and
  - preserve the current workload ids, manifest selection behavior, and support-surface identity checks.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py::test_collection_replacement_keyword_contract_surface_is_support_owned_without_local_duplicates tests/benchmarks/test_source_tree_benchmark_anchor_support.py::test_source_tree_owner_manifest_path_constants_point_to_current_workload_files`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n '^(MODULE_BOUNDARY_MANIFEST_PATH|COLLECTION_REPLACEMENT_MANIFEST_PATH) =' tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep this cleanup structural and bounded to the benchmark support/test ownership layer above. Do not change workload manifests, benchmark runtime behavior, README text, published reports, or tracked `ops/state/` prose.
- Prefer deleting duplicate assignments over adding compatibility aliases. The point is to leave one legible owner for the shared benchmark manifest paths, not another indirection layer.

## Notes
- `RBR-1312` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this run; and
  - `rg -n "RBR-1312|RBR-1313|RBR-1314|RBR-1315" ops/state/current_status.md ops/state/backlog.md ops/tasks -g '*.md'` matched only historical mentions inside older done-task notes, not a live reservation for `RBR-1312`.
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Queue/runtime state was not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reported a clean worktree, no ready tasks, no blocked tasks, and the most recent `architecture-implementation` run finished `done`; and
  - the latest runtime snapshot showed no inherited-dirty, refresh, or commit anomaly.
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/benchmark_test_support.py` already defines both shared constants;
  - `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` still defines local `COLLECTION_REPLACEMENT_MANIFEST_PATH` and `MODULE_BOUNDARY_MANIFEST_PATH` assignments;
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` still defines a second local `MODULE_BOUNDARY_MANIFEST_PATH`; and
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still carries unused local `MODULE_BOUNDARY_MANIFEST_PATH` and `COLLECTION_REPLACEMENT_MANIFEST_PATH` assignments even though the file already imports `MODULE_BOUNDARY_MANIFEST_PATH` from `tests.benchmarks.benchmark_test_support` for the compiled-pattern module-compile lane.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py::test_collection_replacement_keyword_contract_surface_is_support_owned_without_local_duplicates tests/benchmarks/test_source_tree_benchmark_anchor_support.py::test_source_tree_owner_manifest_path_constants_point_to_current_workload_files` passed with `2 passed in 0.11s`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed with `279 tests collected in 0.10s`; and
  - `bash -lc "! rg -n '^(MODULE_BOUNDARY_MANIFEST_PATH|COLLECTION_REPLACEMENT_MANIFEST_PATH) =' tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` currently fails because those files still define duplicate copies of the shared paths, and that failure belongs exactly to this cleanup.
