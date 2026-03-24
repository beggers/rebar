# RBR-1186: Extract module and pattern keyword-window benchmark anchor support

Status: ready
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining module-workflow keyword and pattern-window anchor-support block that still lives inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by moving that bounded selector/signature logic into one dedicated benchmark-support module, so the giant combined benchmark suite stops owning another private anchor-support sublayer.

## Deliverables
- `tests/benchmarks/module_pattern_keyword_benchmark_anchor_support.py`
- `tests/benchmarks/test_module_pattern_keyword_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Add one bounded shared benchmark-support module at `tests/benchmarks/module_pattern_keyword_benchmark_anchor_support.py` for the current module-keyword and pattern-window anchor-support surface that is still embedded in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`:
  - move `_module_workflow_keyword_correctness_case_signature`;
  - move `_module_workflow_keyword_workload_args`;
  - move `_module_workflow_keyword_workload_signature`;
  - move `_is_module_workflow_keyword_flags_workload`;
  - move `_is_module_workflow_keyword_error_workload`;
  - move `_pattern_window_positional_indexlike_correctness_case_signature`;
  - move `_pattern_window_positional_indexlike_workload_args`;
  - move `_pattern_window_positional_indexlike_workload_signature`;
  - move `_is_pattern_window_positional_indexlike_workload`;
  - move `_pattern_keyword_window_correctness_case_signature`;
  - move `_pattern_keyword_window_workload_signature`; and
  - move `_is_pattern_keyword_window_workload`.
- Keep that extracted support pinned to the current live anchor-selection surface instead of widening it:
  - preserve the current module-boundary `flags` keyword success rows and `TypeError` keyword-error rows, including the present duplicate-argument and unexpected-keyword message-substring handling;
  - preserve the current pattern-boundary positional-window indexlike rows and keyword-window rows, including `pos`/`endpos` argument shaping, bool/indexlike payload handling, and `search`/`match`/`fullmatch`/`findall`/`finditer` coverage;
  - preserve the current `freeze_signature_value(...)`, `_module_workflow_keyword_kwargs_signature(...)`, `_module_workflow_positional_args_signature(...)`, and `_is_encoded_indexlike_payload(...)` based normalization behavior; and
  - keep the bounded wildcard helper path wired through the moved `_pattern_window_positional_indexlike_workload_args(...)` support instead of leaving a second local copy behind in the combined suite.
- Delete the duplicated inline support block from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` instead of leaving aliases or wrapper passthroughs behind.
- Add one focused support test file at `tests/benchmarks/test_module_pattern_keyword_benchmark_anchor_support.py` that pins the moved support without reintroducing another giant-suite dependency:
  - cover one module-workflow `flags` keyword success workload;
  - cover one module-workflow keyword-error workload;
  - cover one pattern positional-window indexlike workload; and
  - cover one pattern keyword-window workload.
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so it imports the moved support instead of defining that block inline:
  - keep the existing standard-benchmark anchor definitions on the same module-boundary and pattern-boundary rows and case ids;
  - keep the selected combined-suite keyword-normalization and pattern-window materialization tests on the same behavior after the extraction; and
  - do not widen this task into collection/replacement anchor support, compiled-pattern owner support, cache-contract support, or a broader breakup of the combined suite.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_module_pattern_keyword_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'keyword_kwargs_normalization_preserves_expected_exception_passthrough_rows or pattern_helper_keyword_kwargs_materialize_at_callback_time or standard_benchmark_keyword_kwargs_validation_matches_manifest_and_payload_entry_points or standard_benchmark_manifest_preserves_pattern_keyword_window_descriptors_until_helper_invocation or standard_benchmark_manifest_preserves_pattern_window_indexlike_descriptors_until_helper_invocation'`

## Constraints
- Keep this cleanup structural and limited to the support extraction above. Do not widen it into `python/rebar_harness/benchmarks.py`, benchmark manifests, correctness fixtures, reports, README text, or tracked ops state prose.
- Prefer one ordinary support module plus one focused support test file over another test-to-test import or another block of private inline helpers.
- Do not turn this into a larger source-tree combined-suite decomposition; this task is only the bounded module/pattern keyword-window anchor-support extraction above.

## Notes
- `RBR-1186` is the next available unreserved architecture task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run; and
  - `rg -n "RBR-1186|RBR-1187|RBR-1188" ops/tasks ops/state/backlog.md ops/state/current_status.md -g '*.md'` matched only a stale completion note mentioning future ids, not a live reservation for `RBR-1186`.
- No blocked architecture task exists to reopen or retire first in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining simplification is still concrete and bounded in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is `18020` lines in this run;
  - `rg -n "^def _module_workflow_keyword_correctness_case_signature\\(|^def _module_workflow_keyword_workload_args\\(|^def _module_workflow_keyword_workload_signature\\(|^def _is_module_workflow_keyword_flags_workload\\(|^def _is_module_workflow_keyword_error_workload\\(|^def _pattern_window_positional_indexlike_correctness_case_signature\\(|^def _pattern_window_positional_indexlike_workload_args\\(|^def _pattern_window_positional_indexlike_workload_signature\\(|^def _is_pattern_window_positional_indexlike_workload\\(|^def _pattern_keyword_window_correctness_case_signature\\(|^def _pattern_keyword_window_workload_signature\\(|^def _is_pattern_keyword_window_workload\\(" tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still shows the full inline support block at lines `8013`, `8030`, `8051`, `8072`, `8084`, `8105`, `8122`, `8145`, `8163`, `8183`, `8200`, and `8218`;
  - `rg -n "_is_pattern_keyword_window_workload|_is_pattern_window_positional_indexlike_workload" tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still shows the combined suite using those inline selectors both in workload-scope assertions around line `4682` and in standard benchmark anchor definitions around lines `9897` and `9960`; and
  - no repo-local support module currently owns this exact selector/signature surface.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_module_pattern_keyword_benchmark_anchor_support.py` currently fails with `ERROR: file or directory not found: tests/benchmarks/test_module_pattern_keyword_benchmark_anchor_support.py`, which belongs to the exact cleanup queued here.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'keyword_kwargs_normalization_preserves_expected_exception_passthrough_rows or pattern_helper_keyword_kwargs_materialize_at_callback_time or standard_benchmark_keyword_kwargs_validation_matches_manifest_and_payload_entry_points or standard_benchmark_manifest_preserves_pattern_keyword_window_descriptors_until_helper_invocation or standard_benchmark_manifest_preserves_pattern_window_indexlike_descriptors_until_helper_invocation'` returned `19 passed, 575 deselected` in this run.
