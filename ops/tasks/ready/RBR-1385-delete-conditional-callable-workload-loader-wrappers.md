## RBR-1385: Delete conditional callable workload loader wrappers

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the seven stored conditional-callable workload-loader helpers from the collection-replacement benchmark owner layer, and have the consuming benchmark test modules load the same live workloads directly from `conditional_group_exists_boundary.py` with the existing exported workload-id constants instead of routing through a test-only wrapper layer.

## Deliverables
- `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Remove these helpers from `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` without replacing them with another loader wrapper, registry, or alias layer:
  - `_conditional_group_exists_callable_str_slice_workloads()`
  - `_conditional_group_exists_callable_bytes_slice_workloads()`
  - `_conditional_group_exists_quantified_callable_str_workloads()`
  - `_conditional_group_exists_nested_callable_str_workloads()`
  - `_conditional_group_exists_nested_callable_bytes_workloads()`
  - `_conditional_group_exists_quantified_callable_bytes_workloads()`
  - `_conditional_group_exists_alternation_callable_bytes_workloads()`
- Keep the existing exported workload-id constants and expectation objects intact, including:
  - `_CONDITIONAL_GROUP_EXISTS_CALLABLE_REPLACEMENT_EXPECTATIONS`
  - `CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_STR_WORKLOAD_IDS`
  - `CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_BYTES_WORKLOAD_IDS`
  - `CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_STR_WORKLOAD_IDS`
  - `CONDITIONAL_GROUP_EXISTS_QUANTIFIED_CALLABLE_BYTES_WORKLOAD_IDS`
  - `CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_BYTES_WORKLOAD_IDS`
- Rewrite the affected assertions in `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so they call `benchmark_test_support.live_manifest_workloads(...)` directly against `benchmarks.BENCHMARK_WORKLOADS_ROOT / "conditional_group_exists_boundary.py"` with the existing workload-id tuples or the existing expectation-derived str/bytes id partitions.
- Update `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` so the owner/test surface proves the deleted helpers are absent and keeps the workload-id stability checks on the remaining exported constants and expectation objects rather than on stored loader functions.
- Preserve the current workload ordering, text-model partitions, round-trip payload checks, expected exception behavior, and benchmark/correctness row identities; this task is only about deleting the transit loader layer.
- Do not change benchmark manifests, workload ids, benchmark execution behavior, published row ids, or tracked project-state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional and callable and (nested or quantified or alternation or source_workloads)'`
- `python3 -m py_compile tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n '_conditional_group_exists_(callable_str_slice|callable_bytes_slice|nested_callable_str|nested_callable_bytes|quantified_callable_str|quantified_callable_bytes|alternation_callable_bytes)_workloads\\(' tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Prefer direct `benchmark_test_support.live_manifest_workloads(...)` calls at the consuming assertion sites over any new shared loader helper.
- Keep the run bounded to deleting these seven conditional-callable workload-loader wrappers and rewiring their current test consumers.

## Notes
- Queue and JSON check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`.
  - `git status --short` was empty in this run, so the dashboard counts were not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- ID and duplicate check in this run:
  - `rg -n 'RBR-1385|RBR-1386|RBR-1387|RBR-1388|RBR-1389' ops/state/current_status.md ops/state/backlog.md` returned no reserved future id hits for `RBR-1385`.
  - `rg --files ops/tasks/ready`, `rg --files ops/tasks/in_progress`, and `rg --files ops/tasks/blocked` returned no queued task files in this checkout.
  - No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate selection in this run:
  - I inspected the source-tree contract-builder stack first; its `_SourceTreeContractBuilderSpec` and manifest builder helpers are still wired into broader shared contract-spec ownership, so that cleanup would be larger than one bounded architecture-implementation run.
  - The seven conditional-callable workload-loader helpers are thin `benchmark_test_support.live_manifest_workloads(...)` wrappers over one manifest path plus already-exported workload-id tuples or already-exported expectation objects.
  - Their only remaining consumers are benchmark tests, so deleting them removes a shared owner/test transit layer without changing runtime harness code or benchmark publications.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed (`263 passed in 2.66s`).
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional and callable and (nested or quantified or alternation or source_workloads)'` passed (`17 passed, 262 deselected, 480 subtests passed in 1.89s`).
  - `python3 -m py_compile tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed.
  - `bash -lc "rg -n '_conditional_group_exists_(callable_str_slice|callable_bytes_slice|nested_callable_str|nested_callable_bytes|quantified_callable_str|quantified_callable_bytes|alternation_callable_bytes)_workloads\\(' tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` currently reports the seven helper definitions in the owner module plus their live test call sites, and that failure belongs exactly to this cleanup.
