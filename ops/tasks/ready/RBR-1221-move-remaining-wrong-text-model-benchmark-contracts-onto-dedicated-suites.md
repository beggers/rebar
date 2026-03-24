# RBR-1221: Move remaining wrong-text-model benchmark contracts onto dedicated suites

Status: ready
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the last wrong-text-model benchmark contract block that still lives inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by moving the manifest-measured selector checks onto the existing wrong-text-model anchor suite and the callback-time haystack materialization check onto the existing wrong-text-model owner-support suite, so the giant combined benchmark suite stops owning another dedicated helper surface.

## Deliverables
- `tests/benchmarks/test_wrong_text_model_benchmark_anchor_support.py`
- `tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Extend the existing wrong-text-model dedicated suites instead of creating another layer:
  - keep `tests/benchmarks/test_wrong_text_model_benchmark_anchor_support.py` as the owner for the wrong-text-model manifest-measured selector contract surface; and
  - keep `tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py` as the owner for the wrong-text-model callback-time materialization contract surface.
- Move these three manifest-measured tests out of `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and into `tests/benchmarks/test_wrong_text_model_benchmark_anchor_support.py` without widening their scope or changing their assertion surfaces:
  - `test_collection_replacement_manifest_keeps_compiled_pattern_wrong_text_model_rows_measured`
  - `test_collection_replacement_manifest_keeps_pattern_wrong_text_model_rows_measured`
  - `test_module_boundary_manifest_keeps_compiled_pattern_wrong_text_model_rows_measured`
- Keep the extracted manifest-measured surface pinned to current live behavior exactly:
  - preserve the current use of the live source-tree manifest helpers and wrong-text-model selectors;
  - preserve the current measured-row counts of `5` for compiled-pattern collection/replacement wrong-text-model rows, `3` for direct-`Pattern` collection/replacement wrong-text-model rows, and `3` for compiled-pattern module-boundary wrong-text-model rows; and
  - preserve the current zero-known-gap expectation for those selected measured workload ids on their existing manifests.
- Move `test_pattern_helper_collection_replacement_wrong_text_model_haystack_materializes_at_callback_time` out of `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and into `tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py` without widening its scope or changing its assertion surface.
- Keep the extracted callback-time materialization surface pinned to current live behavior exactly:
  - preserve the current `benchmarks.Workload.haystack_payload` monkeypatch pattern and the `observed_workload_ids == []` before callback invocation / `[workload.workload_id]` after invocation contract;
  - preserve the current `TypeError` assertion against `workload.expected_exception["message_substring"]`; and
  - keep the test anchored to the existing collection-replacement direct-`Pattern` wrong-text-model workload selection rather than inventing a new synthetic fixture path.
- Reuse existing shared helpers instead of inventing another architectural layer:
  - keep using the existing live manifest and workload helpers already in the benchmark test tree;
  - do not add a new `*_support.py` module, a new owner-spec file, or wrapper aliases in the combined suite; and
  - do not widen this cleanup into the mixed `pattern_boundary_manifest_keeps_keyword_and_positional_window_rows_measured` block, harness implementation code, benchmark workload manifests, correctness fixtures, reports, README text, or tracked ops/state prose.
- Delete the moved tests from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` instead of leaving wrappers, aliases, or duplicate copies behind.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_wrong_text_model_benchmark_anchor_support.py tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_compiled_pattern_wrong_text_model_rows_measured or collection_replacement_manifest_keeps_pattern_wrong_text_model_rows_measured or module_boundary_manifest_keeps_compiled_pattern_wrong_text_model_rows_measured or pattern_helper_collection_replacement_wrong_text_model_haystack_materializes_at_callback_time'`
- `bash -lc "! rg -n 'def test_(collection_replacement_manifest_keeps_compiled_pattern_wrong_text_model_rows_measured|collection_replacement_manifest_keeps_pattern_wrong_text_model_rows_measured|module_boundary_manifest_keeps_compiled_pattern_wrong_text_model_rows_measured|pattern_helper_collection_replacement_wrong_text_model_haystack_materializes_at_callback_time)' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Notes
- `RBR-1221` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run; and
  - `rg -n "RBR-1221|RBR-1222|RBR-1223|RBR-1224" ops/state/current_status.md ops/state/backlog.md ops/tasks -g '*.md'` matched only the historical note in `ops/tasks/done/RBR-1220-move-module-pattern-keyword-materialization-contracts-onto-dedicated-suite.md` and did not reveal a live reservation or sibling task at `RBR-1221`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Rule 10 does not block another architecture cleanup in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, `Dirty worktree: false`, and `Last Cycle Anomalies: none`; and
  - the last cycle completed `RBR-1219` and `RBR-1220` through the normal done path with no inherited-dirty or refresh/commit anomaly recorded.
- This simplification is concrete and still unfinished in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is `11836` lines in this run;
  - `rg -n "def test_(collection_replacement_manifest_keeps_compiled_pattern_wrong_text_model_rows_measured|collection_replacement_manifest_keeps_pattern_wrong_text_model_rows_measured|module_boundary_manifest_keeps_compiled_pattern_wrong_text_model_rows_measured|pattern_helper_collection_replacement_wrong_text_model_haystack_materializes_at_callback_time)" tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_wrong_text_model_benchmark_anchor_support.py tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py` currently matches only the combined-suite block at lines `4645`, `4663`, `4902`, and `11636`;
  - `tests/benchmarks/test_wrong_text_model_benchmark_anchor_support.py` and `tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py` already exist as the dedicated owners for the adjacent wrong-text-model selector and owner-support surfaces; and
  - this task removes one misplaced wrong-text-model contract block instead of creating another sibling suite.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_wrong_text_model_benchmark_anchor_support.py tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_compiled_pattern_wrong_text_model_rows_measured or collection_replacement_manifest_keeps_pattern_wrong_text_model_rows_measured or module_boundary_manifest_keeps_compiled_pattern_wrong_text_model_rows_measured or pattern_helper_collection_replacement_wrong_text_model_haystack_materializes_at_callback_time'` returned `6 passed, 189 deselected, 11 subtests passed in 0.72s`; and
  - the negative `rg` check named above currently fails exactly on this cleanup because those four tests still live in the combined suite.
