# RBR-1367: Move callable signature normalizer onto collection support

Status: ready
Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the remaining collection-replacement callable-signature transit helper from `tests/benchmarks/source_tree_benchmark_anchor_support.py` so the combined source-tree benchmark suite reads that normalization helper from `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`, the same owner that already carries the adjacent conditional-callable signature helpers.

## Deliverables
- `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Move `def _text_model_agnostic_callable_match_group_signature(...)` out of `tests/benchmarks/source_tree_benchmark_anchor_support.py` and define it on `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` instead.
- Add that helper to the collection-owner routed callable-signature inventory so the ownership tests treat it as collection-owned surface alongside `_conditional_group_exists_nested_callable_*_signature` and `_conditional_group_exists_quantified_callable_*_signature`.
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the callable replacement slice checks read `_text_model_agnostic_callable_match_group_signature` through `collection_replacement_support`, not `source_tree_support`.
- Update the touched owner-boundary tests so `tests/benchmarks/source_tree_benchmark_anchor_support.py` no longer advertises `_text_model_agnostic_callable_match_group_signature` as local surface while the collection owner does.
- Preserve the current callable replacement benchmark semantics, workload ordering, and bytes-versus-str signature comparisons; this is an ownership cleanup, not a workload or scorecard change.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'combined_suite_uses_collection_owner_conditional_callable_signature_helpers or moved_collection_replacement_workload_ids_in_combined_suite_use_direct_owner_import'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_support_module_no_longer_exposes_collection_owned_signature_helpers or source_tree_support_module_exposes_routed_collection_owner_surface'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'alternation_callable_scorecards_keep_measured_rows_in_sync_with_scorecard_case or conditional_group_exists_nested_callable_scorecards_keep_bytes_rows_in_sync_with_str_slice or conditional_group_exists_quantified_callable_scorecards_keep_negative_count_follow_on_workloads_in_sync'`
- `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `rg -n '^def _text_model_agnostic_callable_match_group_signature\\b' tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `bash -lc "! rg -n '^def _text_model_agnostic_callable_match_group_signature\\b' tests/benchmarks/source_tree_benchmark_anchor_support.py"`
- `bash -lc "! rg -n 'source_tree_support\\._text_model_agnostic_callable_match_group_signature' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py"`

## Constraints
- Prefer deleting the source-tree transit helper over adding a new compatibility alias back onto `tests/benchmarks/source_tree_benchmark_anchor_support.py`.
- Keep the cleanup bounded to this callable-signature normalization helper and its ownership checks; do not widen into unrelated source-tree combined-case helpers or benchmark manifest edits in the same run.
- Do not change workload documents, report generation, or callable replacement semantics.

## Notes
- ID check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n 'RBR-1367|RBR-1368|RBR-1369' ops/state/current_status.md ops/state/backlog.md` returned no matches, so this ID range was not reserved in tracked planning state
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate probe that justified this task:
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` still defines `_text_model_agnostic_callable_match_group_signature` at line `1320`.
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still references `source_tree_support._text_model_agnostic_callable_match_group_signature` seven times, all inside collection-replacement callable slice checks.
  - `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` already owns the adjacent conditional callable correctness/workload signature helpers, so the normalization helper is the last obvious callable-signature transit surface still living on the source-tree owner.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'combined_suite_uses_collection_owner_conditional_callable_signature_helpers or moved_collection_replacement_workload_ids_in_combined_suite_use_direct_owner_import'` passed with `2 passed, 146 deselected in 0.30s`
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_support_module_no_longer_exposes_collection_owned_signature_helpers or source_tree_support_module_exposes_routed_collection_owner_surface'` passed with `2 passed, 103 deselected in 0.13s`
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'alternation_callable_scorecards_keep_measured_rows_in_sync_with_scorecard_case or conditional_group_exists_nested_callable_scorecards_keep_bytes_rows_in_sync_with_str_slice or conditional_group_exists_quantified_callable_scorecards_keep_negative_count_follow_on_workloads_in_sync'` passed with `3 passed, 276 deselected in 0.15s`
  - `bash -lc "! rg -n '^def _text_model_agnostic_callable_match_group_signature\\b' tests/benchmarks/source_tree_benchmark_anchor_support.py"` currently fails because the helper still lives on `tests/benchmarks/source_tree_benchmark_anchor_support.py`, and that failure belongs exactly to this cleanup
  - `rg -n '^def _text_model_agnostic_callable_match_group_signature\\b' tests/benchmarks/collection_replacement_benchmark_anchor_support.py` currently fails because the collection owner does not yet define the helper, and that failure belongs exactly to this cleanup
  - `bash -lc "! rg -n 'source_tree_support\\._text_model_agnostic_callable_match_group_signature' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py"` currently fails because the combined-suite tests still route that helper through `source_tree_support`, and that failure belongs exactly to this cleanup
