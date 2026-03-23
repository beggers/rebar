# RBR-1074: Collapse collection/replacement route delegate wrappers

Status: ready
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining thin collection/replacement delegate wrappers in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the five collection/replacement anchor definitions read their correctness/workload signature logic directly from the canonical route owners instead of bouncing through ten one-line wrapper functions.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines any of these thin delegate wrappers:
  - `_pattern_collection_replacement_bounded_findall_correctness_case_signature`
  - `_pattern_collection_replacement_bounded_findall_workload_signature`
  - `_pattern_collection_replacement_bounded_finditer_correctness_case_signature`
  - `_pattern_collection_replacement_bounded_finditer_workload_signature`
  - `_pattern_collection_replacement_split_correctness_case_signature`
  - `_pattern_collection_replacement_split_workload_signature`
  - `_pattern_collection_replacement_literal_replacement_correctness_case_signature`
  - `_module_collection_replacement_literal_replacement_correctness_case_signature`
  - `_module_collection_replacement_literal_replacement_workload_signature`
  - `_pattern_collection_replacement_literal_replacement_workload_signature`
- Replace that wrapper layer with direct use of the existing canonical owners, or a strictly smaller same-file equivalent:
  - `_COLLECTION_REPLACEMENT_PATTERN_COLLECTION_ROUTES`
  - `_COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_ROUTES`
  - `_collection_replacement_literal_replacement_correctness_case_signature(...)`
  - `_collection_replacement_literal_replacement_workload_signature(...)`
- Rewire these five existing `StandardBenchmarkAnchorContractDefinition(...)` entries so they no longer depend on the deleted wrapper names:
  - `collection-replacement-pattern-findall-bounded`
  - `collection-replacement-pattern-finditer-bounded`
  - `collection-replacement-pattern-split`
  - `collection-replacement-module-literal-replacement`
  - `collection-replacement-pattern-literal-replacement`
- Keep the current route-owned contracts intact after the cleanup:
  - the expected anchor case ids for those five definitions stay exactly the same;
  - the bounded `Pattern.findall()` / `Pattern.finditer()` / `Pattern.split()` route methods still own the same workload ids, case ids, ordering, helper names, and window-bounds behavior;
  - the module/pattern literal replacement route owners still preserve the same workload ids, case ids, ordering, operation prefixes, and count-handling behavior; and
  - do not widen this task into `_any_collection_replacement_literal_replacement_workload_signature(...)`, the benchmark-gap tests, compiled-pattern module-helper routes, workload manifests, reports, or harness code.
- Keep the change file-local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_pattern_findall_bounded_rows_measured or collection_replacement_manifest_keeps_pattern_finditer_bounded_rows_measured or collection_replacement_manifest_keeps_pattern_split_rows_measured or collection_replacement_manifest_keeps_pattern_replacement_literal_rows_measured or collection-replacement-pattern-findall-bounded or collection-replacement-pattern-finditer-bounded or collection-replacement-pattern-split or collection-replacement-module-literal-replacement or collection-replacement-pattern-literal-replacement'`
- `bash -lc "! rg -n '^def (_pattern_collection_replacement_bounded_findall_(correctness_case_signature|workload_signature)|_pattern_collection_replacement_bounded_finditer_(correctness_case_signature|workload_signature)|_pattern_collection_replacement_split_(correctness_case_signature|workload_signature)|_module_collection_replacement_literal_replacement_(correctness_case_signature|workload_signature)|_pattern_collection_replacement_literal_replacement_(correctness_case_signature|workload_signature))\\b' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Prefer deleting the ten wrappers over introducing another support module, registry file, or extra abstraction layer.
- Keep the canonical route maps and the existing generic literal-replacement signature builders as the ownership surface unless a strictly smaller same-file successor preserves the same behavior.
- Do not change benchmark workload manifests, correctness fixtures, implementation code, reports, README copy, or tracked project-state prose in this run.

## Notes
- `RBR-1074` is the next available unreserved architecture-task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty before this file is added;
  - `ops/tasks/done/` currently runs through `RBR-1073`; and
  - `rg -n 'RBR-1074|RBR-1075|RBR-1076' ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done` returned no matches in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete and current in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-ready-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest runtime cycle shows both task workers finishing `done`, with no inherited-dirty checkpoint churn or stalled post-task refresh path.
- The duplication target is concrete in the live checkout:
  - `rg -n '^def (_pattern_collection_replacement_bounded_findall_(correctness_case_signature|workload_signature)|_pattern_collection_replacement_bounded_finditer_(correctness_case_signature|workload_signature)|_pattern_collection_replacement_split_(correctness_case_signature|workload_signature)|_module_collection_replacement_literal_replacement_(correctness_case_signature|workload_signature)|_pattern_collection_replacement_literal_replacement_(correctness_case_signature|workload_signature))\\b' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently returns the ten wrapper definitions in this run; and
  - `sed -n '9868,9965p' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` shows the five collection/replacement anchor definitions still consuming those wrapper names directly instead of the already-canonical route owners.
- The focused verification slice is green in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_pattern_findall_bounded_rows_measured or collection_replacement_manifest_keeps_pattern_finditer_bounded_rows_measured or collection_replacement_manifest_keeps_pattern_split_rows_measured or collection_replacement_manifest_keeps_pattern_replacement_literal_rows_measured or collection-replacement-pattern-findall-bounded or collection-replacement-pattern-finditer-bounded or collection-replacement-pattern-split or collection-replacement-module-literal-replacement or collection-replacement-pattern-literal-replacement'` returned `24 passed, 698 deselected, 29 subtests passed` in this run.
- One adjacent collection/replacement gap test is currently red for unrelated drift and should stay out of this cleanup's acceptance surface:
  - `test_collection_replacement_module_literal_replacement_benchmark_gap_stays_explicit` currently fails on `('module-subn-str-no-match',)` in the live checkout, so this wrapper-removal task should not claim that unrelated publication gap.
