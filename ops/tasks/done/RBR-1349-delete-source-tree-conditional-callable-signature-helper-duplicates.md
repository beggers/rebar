## RBR-1349: Delete source-tree conditional callable signature helper duplicates

Status: done
Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the remaining nested and quantified conditional callable signature-helper duplicates from `tests/benchmarks/source_tree_benchmark_anchor_support.py` so the combined source-tree benchmark suite routes that owner surface through `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` instead of through a source-tree copy layer.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`

## Acceptance Criteria
- Remove these four local helper definitions from `tests/benchmarks/source_tree_benchmark_anchor_support.py`:
  - `_conditional_group_exists_nested_callable_correctness_case_signature(...)`
  - `_conditional_group_exists_nested_callable_workload_signature(...)`
  - `_conditional_group_exists_quantified_callable_correctness_case_signature(...)`
  - `_conditional_group_exists_quantified_callable_workload_signature(...)`
- Trim the source-tree owner-name inventory so those four helpers are no longer treated as source-tree-owned routed names:
  - update `SOURCE_TREE_ROUTED_COLLECTION_REPLACEMENT_SIGNATURE_HELPER_NAMES` in `tests/benchmarks/source_tree_benchmark_anchor_support.py`
  - update the corresponding ownership assertions in `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the combined suite reads those four helpers from `collection_replacement_support` instead of `source_tree_support`, while keeping the nested/quantified callable workload selectors and slice-expectation helpers on `source_tree_support`
- Expand the owner-boundary coverage in `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` so it proves the combined suite imports and uses the four signature helpers from `collection_replacement_support` without rebinding them locally or through `source_tree_support`
- Keep the cleanup structural only:
  - do not move the nested/quantified callable workload-selector helpers out of `source_tree_benchmark_anchor_support.py`
  - do not change benchmark manifests, harness behavior, scorecards, README text, or tracked `ops/state/` prose
  - do not add a new wrapper module, alias shim, or replacement helper surface

## Verification
- `./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists_nested_callable or conditional_group_exists_quantified_callable'`
- `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n '^def _conditional_group_exists_(nested|quantified)_callable_(correctness_case_signature|workload_signature)\\(' tests/benchmarks/source_tree_benchmark_anchor_support.py"`
- `bash -lc "! rg -n 'source_tree_support\\._conditional_group_exists_(nested|quantified)_callable_(correctness_case_signature|workload_signature)' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep the task bounded to deleting the duplicated signature-helper surface from the source-tree owner module and rerouting the combined suite to the existing collection-replacement owner module.
- Preserve the current nested/quantified conditional callable tuple shapes, exception/no-match bits, workload ordering, and anchored published-case behavior exactly.
- Leave the existing source-tree-owned slice-workload brokers and replacement-expectation helpers in place for a later follow-on.

## Notes
- `RBR-1349` is the next available unreserved task id in this checkout:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n 'RBR-1349|RBR-1350|RBR-1351|RBR-1352' ops/state/current_status.md ops/state/backlog.md` returned no matches in this run
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- This duplicate owner surface is live in the current checkout:
  - `rg -n '_conditional_group_exists_(nested|quantified)_callable_(correctness_case_signature|workload_signature)' tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py` reports the same four helper names in both owner modules
  - `rg -n 'source_tree_support\\._conditional_group_exists_(nested|quantified)_callable_(correctness_case_signature|workload_signature)' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` shows the combined suite still reading those four helpers through `source_tree_support`
- Verification status in this planning run:
  - `./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed with `243 passed in 2.77s`
  - `./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists_nested_callable or conditional_group_exists_quantified_callable'` passed with `12 passed, 267 deselected, 420 subtests passed in 1.62s`
  - `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed
  - `bash -lc "! rg -n '^def _conditional_group_exists_(nested|quantified)_callable_(correctness_case_signature|workload_signature)\\(' tests/benchmarks/source_tree_benchmark_anchor_support.py"` currently fails because those four duplicate helper definitions still live on the source-tree owner module, and that failure belongs exactly to this cleanup
  - `bash -lc "! rg -n 'source_tree_support\\._conditional_group_exists_(nested|quantified)_callable_(correctness_case_signature|workload_signature)' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` currently fails because the combined suite still routes those helper calls through `source_tree_support`, and that failure belongs exactly to this cleanup

## Completion
- Deleted the four nested/quantified conditional callable signature helpers from `tests/benchmarks/source_tree_benchmark_anchor_support.py` and cleared `SOURCE_TREE_ROUTED_COLLECTION_REPLACEMENT_SIGNATURE_HELPER_NAMES` so the source-tree owner no longer advertises them.
- Updated `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to keep the nested/quantified callable workload selectors on `source_tree_support` while reading the correctness/workload signature helpers from `collection_replacement_support`.
- Expanded owner-boundary coverage in `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` and `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` so the combined suite proves those four helpers come from the collection-replacement owner and are no longer exposed locally on `source_tree_support`.
- Verification in this run:
  - `./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed with `244 passed in 2.95s`
  - `./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists_nested_callable or conditional_group_exists_quantified_callable'` passed with `12 passed, 267 deselected, 420 subtests passed in 1.68s`
  - `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed
  - `bash -lc "! rg -n '^def _conditional_group_exists_(nested|quantified)_callable_(correctness_case_signature|workload_signature)\\(' tests/benchmarks/source_tree_benchmark_anchor_support.py"` passed
  - `bash -lc "! rg -n 'source_tree_support\\._conditional_group_exists_(nested|quantified)_callable_(correctness_case_signature|workload_signature)' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` passed
