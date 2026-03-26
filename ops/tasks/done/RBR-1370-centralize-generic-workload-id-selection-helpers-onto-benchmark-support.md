# RBR-1370: Centralize generic workload-id selection helpers onto benchmark support

Status: done
Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Move the generic workload-id selection helper trio out of `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` and onto `tests/benchmarks/benchmark_test_support.py` so the collection-replacement owner module stops carrying reusable selection logic that is consumed across multiple benchmark test suites.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_benchmark_test_support.py`

## Acceptance Criteria
- Add shared helper definitions to `tests/benchmarks/benchmark_test_support.py` for these currently owner-local utilities:
  - `_split_workload_ids_by_text_model(...)`
  - `_selected_workload_ids(...)`
  - `_mirrored_bytes_workload_ids(...)`
- Delete those three definitions from `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` instead of leaving forwarding aliases or re-export wrappers behind.
- Update the remaining callers in `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so they use `benchmark_test_support._split_workload_ids_by_text_model(...)`, `benchmark_test_support._selected_workload_ids(...)`, and `benchmark_test_support._mirrored_bytes_workload_ids(...)` directly rather than reaching through the collection owner module.
- Update the touched ownership/contract tests in `tests/benchmarks/test_benchmark_test_support.py` so they pin the new shared ownership and no longer expect the collection owner module to define those three generic helper names.
- Keep the bounded callable-conditional workload expectations, workload ids, manifest contents, and benchmark semantics unchanged; this is a support-layer ownership cleanup, not a workload-definition rewrite.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'moved_conditional_callable_workload_loaders_pin_expected_ids or split_workload_ids_by_text_model or mirrored_bytes_workload_ids or selected_workload_ids'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'split_workload_ids_by_text_model or mirrored_bytes_workload_ids or selected_workload_ids or conditional_group_exists_nested_callable_str_workloads_round_trip_preserves_outcomes or conditional_group_exists_nested_callable_bytes_workloads_round_trip_preserves_outcomes or conditional_group_exists_quantified_callable_str_workloads_round_trip_preserves_outcomes or conditional_group_exists_quantified_callable_bytes_workloads_round_trip_preserves_outcomes or conditional_group_exists_callable_str_slice_workloads_round_trip_preserves_outcomes or conditional_group_exists_callable_bytes_slice_workloads_round_trip_preserves_outcomes or conditional_group_exists_alternation_callable_bytes_workloads_round_trip_preserves_outcomes'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_test_support.py`
- `rg -n '^def (_split_workload_ids_by_text_model|_selected_workload_ids|_mirrored_bytes_workload_ids)\\b' tests/benchmarks/benchmark_test_support.py`
- `bash -lc \"! rg -n '^def (_split_workload_ids_by_text_model|_selected_workload_ids|_mirrored_bytes_workload_ids)\\b' tests/benchmarks/collection_replacement_benchmark_anchor_support.py\"`
- `bash -lc \"! rg -n 'collection_replacement_support\\._(split_workload_ids_by_text_model|selected_workload_ids|mirrored_bytes_workload_ids)\\b|collection_support\\._(split_workload_ids_by_text_model|selected_workload_ids|mirrored_bytes_workload_ids)\\b' tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_test_support.py\"`

## Constraints
- Prefer moving the helper logic once onto `tests/benchmarks/benchmark_test_support.py` over inventing another owner-specific broker or compatibility alias.
- Keep the run bounded to these three generic helper names and their direct consumers; do not widen into unrelated callable-slice expectation rewrites or broader benchmark support reshaping.

## Notes
- ID check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n 'RBR-1370|RBR-1371|RBR-1372' ops/state/current_status.md ops/state/backlog.md` returned no matches in this run
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate probe that justified this task:
  - `grep -n \"def _split_workload_ids_by_text_model\\|def _selected_workload_ids\\|def _mirrored_bytes_workload_ids\" tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/benchmark_test_support.py` shows the three helper definitions only on `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
  - `grep -n \"split_workload_ids_by_text_model\\|selected_workload_ids\\|mirrored_bytes_workload_ids\" tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py` shows the generic helper surface is consumed from multiple benchmark test files rather than only one owner-local path
  - the helper bodies operate on generic workload ids and category filters, so they fit the existing shared-support boundary better than the collection-replacement owner module
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'moved_conditional_callable_workload_loaders_pin_expected_ids or split_workload_ids_by_text_model or mirrored_bytes_workload_ids or selected_workload_ids'` passed with `1 passed, 105 deselected in 0.13s`
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'split_workload_ids_by_text_model or mirrored_bytes_workload_ids or selected_workload_ids or conditional_group_exists_nested_callable_str_workloads_round_trip_preserves_outcomes or conditional_group_exists_nested_callable_bytes_workloads_round_trip_preserves_outcomes or conditional_group_exists_quantified_callable_str_workloads_round_trip_preserves_outcomes or conditional_group_exists_quantified_callable_bytes_workloads_round_trip_preserves_outcomes or conditional_group_exists_callable_str_slice_workloads_round_trip_preserves_outcomes or conditional_group_exists_callable_bytes_slice_workloads_round_trip_preserves_outcomes or conditional_group_exists_alternation_callable_bytes_workloads_round_trip_preserves_outcomes'` passed with `7 passed, 272 deselected, 224 subtests passed in 0.19s`
  - `rg -n '^def (_split_workload_ids_by_text_model|_selected_workload_ids|_mirrored_bytes_workload_ids)\\b' tests/benchmarks/benchmark_test_support.py` currently fails because the shared support module does not own the helper trio yet, and that failure belongs exactly to this cleanup
  - `bash -lc \"! rg -n '^def (_split_workload_ids_by_text_model|_selected_workload_ids|_mirrored_bytes_workload_ids)\\b' tests/benchmarks/collection_replacement_benchmark_anchor_support.py\"` currently fails because the collection owner module still defines all three helpers, and that failure belongs exactly to this cleanup
  - `bash -lc \"! rg -n 'collection_replacement_support\\._(split_workload_ids_by_text_model|selected_workload_ids|mirrored_bytes_workload_ids)\\b|collection_support\\._(split_workload_ids_by_text_model|selected_workload_ids|mirrored_bytes_workload_ids)\\b' tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_test_support.py\"` currently fails because the touched benchmark tests still route through the collection owner module

## Completion
- Moved `_split_workload_ids_by_text_model(...)`, `_selected_workload_ids(...)`, and `_mirrored_bytes_workload_ids(...)` onto `tests/benchmarks/benchmark_test_support.py`, deleted their owner-local definitions from `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`, and updated direct benchmark-suite callers to use the shared support module.
- Trimmed `COLLECTION_REPLACEMENT_ROUTED_CONDITIONAL_CALLABLE_HELPER_NAMES` so the collection owner contract no longer advertises the generic selector trio, and added a support-contract test that pins the helper ownership on `benchmark_test_support`.
- Verified with:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'moved_conditional_callable_workload_loaders_pin_expected_ids or split_workload_ids_by_text_model or mirrored_bytes_workload_ids or selected_workload_ids'`
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'split_workload_ids_by_text_model or mirrored_bytes_workload_ids or selected_workload_ids or conditional_group_exists_nested_callable_str_workloads_round_trip_preserves_outcomes or conditional_group_exists_nested_callable_bytes_workloads_round_trip_preserves_outcomes or conditional_group_exists_quantified_callable_str_workloads_round_trip_preserves_outcomes or conditional_group_exists_quantified_callable_bytes_workloads_round_trip_preserves_outcomes or conditional_group_exists_callable_str_slice_workloads_round_trip_preserves_outcomes or conditional_group_exists_callable_bytes_slice_workloads_round_trip_preserves_outcomes or conditional_group_exists_alternation_callable_bytes_workloads_round_trip_preserves_outcomes'`
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'generic_workload_id_selector_helpers or collection_replacement_owner_surface_reaches_combined_suite_without_source_tree_workload_id_aliases or source_tree_support_module_exposes_moved_conditional_callable_helpers or source_tree_support_module_exposes_routed_collection_owner_surface'`
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_test_support.py`
  - `rg -n '^def (_split_workload_ids_by_text_model|_selected_workload_ids|_mirrored_bytes_workload_ids)\\b' tests/benchmarks/benchmark_test_support.py`
  - `bash -lc \"! rg -n '^def (_split_workload_ids_by_text_model|_selected_workload_ids|_mirrored_bytes_workload_ids)\\b' tests/benchmarks/collection_replacement_benchmark_anchor_support.py\"`
  - `bash -lc \"! rg -n 'collection_replacement_support\\._(split_workload_ids_by_text_model|selected_workload_ids|mirrored_bytes_workload_ids)\\b|collection_support\\._(split_workload_ids_by_text_model|selected_workload_ids|mirrored_bytes_workload_ids)\\b' tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_test_support.py\"`
