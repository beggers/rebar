# RBR-1357: Delete source-tree shared compiled-pattern helper aliases

Status: done
Owner: architecture-implementation
Created: 2026-03-26
Completed: 2026-03-26

## Goal
- Delete the remaining source-tree re-export layer for shared compiled-pattern benchmark helpers so `tests/benchmarks/source_tree_benchmark_anchor_support.py` only owns source-tree-specific inventories/specs while shared helper behavior stays on `tests/benchmarks/benchmark_test_support.py`.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Remove these top-level alias assignments from `tests/benchmarks/source_tree_benchmark_anchor_support.py`:
  - `_assert_compiled_pattern_module_success_payload_round_trip`
  - `compiled_pattern_contract_expected_build_calls`
  - `_compiled_pattern_module_helper_route`
- Update the source-tree owner-surface inventories in `tests/benchmarks/source_tree_benchmark_anchor_support.py` so they no longer advertise those three shared helper names as part of the source-tree route.
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to call the shared helper functions from `tests.benchmarks.benchmark_test_support` directly instead of routing them through `source_tree_support`.
- Update `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` so the source-tree owner-surface assertions treat those three names as removed from the source-tree module while still requiring the remaining source-tree-specific compiled-pattern owner surface.
- Keep the cleanup bounded to alias deletion and consumer rerouting:
  - do not change workload payload semantics, benchmark manifest contents, or runtime behavior
  - do not move source-tree-specific owner specs or workload-selection logic out of `tests/benchmarks/source_tree_benchmark_anchor_support.py`
  - do not add a replacement wrapper, alias shim, or new helper module

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'test_source_tree_support_module_exposes_moved_combined_case_surface'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'test_compiled_pattern_wrong_text_model_callbacks_preserve_precompile_contract or test_run_internal_workload_probe_measures_compiled_pattern_module_success_contract_workloads'`
- `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/benchmark_test_support.py`
- `bash -lc "! rg -n '^(_assert_compiled_pattern_module_success_payload_round_trip|compiled_pattern_contract_expected_build_calls|_compiled_pattern_module_helper_route)\\s*=' tests/benchmarks/source_tree_benchmark_anchor_support.py"`
- `bash -lc "! rg -n 'source_tree_support\\.(compiled_pattern_contract_expected_build_calls|_compiled_pattern_module_helper_route|_assert_compiled_pattern_module_success_payload_round_trip)\\b' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Prefer deleting the source-tree alias layer over moving it sideways; the shared helper implementations already live on `tests/benchmarks/benchmark_test_support.py`.
- Keep `tests/benchmarks/source_tree_benchmark_anchor_support.py` focused on source-tree-owned specs, inventories, and workload selectors after the cleanup.

## Notes
- ID check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n 'RBR-1357|RBR-1358|RBR-1359|RBR-1360' ops/state/current_status.md ops/state/backlog.md ops/state/decision_log.md ops/tasks -g '*.md'` returned only historical mentions inside completed task notes, so no higher frontier ID in that range was reserved
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate probe that justified this task:
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` still assigns `_assert_compiled_pattern_module_success_payload_round_trip`, `compiled_pattern_contract_expected_build_calls`, and `_compiled_pattern_module_helper_route` directly from `benchmark_test_support`
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still reaches those shared helper implementations through `source_tree_support` at three call sites instead of importing them from shared support directly
  - the current source-tree owner-surface test still treats those alias assignments as present on the source-tree module, so deleting them cleanly requires one bounded cross-file refactor rather than a local assertion tweak
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'test_source_tree_support_module_exposes_moved_combined_case_surface'` passed with `1 passed, 98 deselected in 0.16s`
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'test_compiled_pattern_wrong_text_model_callbacks_preserve_precompile_contract or test_run_internal_workload_probe_measures_compiled_pattern_module_success_contract_workloads'` passed with `28 passed, 251 deselected in 0.13s`
  - `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/benchmark_test_support.py` passed
  - `bash -lc "! rg -n '^(_assert_compiled_pattern_module_success_payload_round_trip|compiled_pattern_contract_expected_build_calls|_compiled_pattern_module_helper_route)\\s*=' tests/benchmarks/source_tree_benchmark_anchor_support.py"` currently fails because those three alias assignments still exist, and that failure belongs exactly to this cleanup
  - `bash -lc "! rg -n 'source_tree_support\\.(compiled_pattern_contract_expected_build_calls|_compiled_pattern_module_helper_route|_assert_compiled_pattern_module_success_payload_round_trip)\\b' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` currently fails because the combined benchmark suite still routes those shared helpers through `source_tree_support`, and that failure belongs exactly to this cleanup

## Completion Note
- Deleted the three shared helper alias assignments from `tests/benchmarks/source_tree_benchmark_anchor_support.py`, removed them from the source-tree owner-surface inventory tuples, and rerouted the combined benchmark suite to call the shared helpers from `tests.benchmarks.benchmark_test_support` directly.
- Verified with:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'test_source_tree_support_module_exposes_moved_combined_case_surface'`
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'test_compiled_pattern_wrong_text_model_callbacks_preserve_precompile_contract or test_run_internal_workload_probe_measures_compiled_pattern_module_success_contract_workloads'`
  - `PYTHONPATH=python:. ./.venv/bin/python -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/benchmark_test_support.py`
  - `bash -lc "! rg -n '^(_assert_compiled_pattern_module_success_payload_round_trip|compiled_pattern_contract_expected_build_calls|_compiled_pattern_module_helper_route)\\s*=' tests/benchmarks/source_tree_benchmark_anchor_support.py"`
  - `bash -lc "! rg -n 'source_tree_support\\.(compiled_pattern_contract_expected_build_calls|_compiled_pattern_module_helper_route|_assert_compiled_pattern_module_success_payload_round_trip)\\b' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
