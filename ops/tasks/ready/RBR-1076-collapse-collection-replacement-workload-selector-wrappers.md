## RBR-1076: Collapse collection/replacement workload-selector wrappers

Status: ready
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining thin collection/replacement workload-selector wrappers in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the measured-manifest checks, explicit-gap checks, and standard anchor definitions read directly from the canonical route owners or the existing generic literal-replacement selector instead of bouncing through seven one-line helper names.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines any of these thin selector wrappers:
  - `_is_collection_replacement_pattern_findall_bounded_workload`
  - `_is_collection_replacement_pattern_finditer_bounded_workload`
  - `_is_collection_replacement_pattern_split_workload`
  - `_is_collection_replacement_module_literal_replacement_workload`
  - `_is_collection_replacement_pattern_literal_replacement_workload`
  - `_is_any_collection_replacement_module_literal_replacement_workload`
  - `_is_any_collection_replacement_pattern_literal_replacement_workload`
- Replace that wrapper layer with direct use of the existing ownership surfaces, or a strictly smaller same-file equivalent:
  - `_COLLECTION_REPLACEMENT_PATTERN_COLLECTION_ROUTES["findall"].includes_workload`
  - `_COLLECTION_REPLACEMENT_PATTERN_COLLECTION_ROUTES["finditer"].includes_workload`
  - `_COLLECTION_REPLACEMENT_PATTERN_COLLECTION_ROUTES["split"].includes_workload`
  - `_is_collection_replacement_literal_replacement_workload(...)`
  - `functools.partial(...)` bindings of `_is_collection_replacement_literal_replacement_workload(...)` where a stable route-owned selector still improves readability
- Rewire these existing checks and definitions so they no longer depend on the deleted wrapper names:
  - the measured-manifest tests for `findall`, `finditer`, `split`, module literal replacement, and pattern literal replacement;
  - `test_collection_replacement_module_literal_replacement_benchmark_gap_stays_explicit`;
  - `test_collection_replacement_pattern_literal_replacement_benchmark_gap_stays_explicit`; and
  - the five `StandardBenchmarkAnchorContractDefinition(...)` entries for:
    - `collection-replacement-pattern-findall-bounded`
    - `collection-replacement-pattern-finditer-bounded`
    - `collection-replacement-pattern-split`
    - `collection-replacement-module-literal-replacement`
    - `collection-replacement-pattern-literal-replacement`
- Keep the current route-owned contracts intact after the cleanup:
  - the same workload ids remain selected for the five measured-manifest checks;
  - the two literal-replacement benchmark-gap checks still compare against the same all-route workload surface rather than the narrower anchor-owned subset;
  - the five standard anchor definitions keep the same expected anchor ids, workload ids, ordering, and callback-parity behavior; and
  - do not widen this task into correctness fixtures, workload manifests, reports, harness code, or unrelated benchmark sections.
- Keep the change file-local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_pattern_findall_bounded_rows_measured or collection_replacement_manifest_keeps_pattern_finditer_bounded_rows_measured or collection_replacement_manifest_keeps_pattern_split_rows_measured or collection_replacement_manifest_keeps_pattern_replacement_literal_rows_measured or collection_replacement_manifest_keeps_module_literal_replacement_rows_measured or test_collection_replacement_module_literal_replacement_benchmark_gap_stays_explicit or test_collection_replacement_pattern_literal_replacement_benchmark_gap_stays_explicit or collection-replacement-pattern-findall-bounded or collection-replacement-pattern-finditer-bounded or collection-replacement-pattern-split or collection-replacement-module-literal-replacement or collection-replacement-pattern-literal-replacement'`
- `bash -lc "! rg -n '^def (_is_collection_replacement_pattern_findall_bounded_workload|_is_collection_replacement_pattern_finditer_bounded_workload|_is_collection_replacement_pattern_split_workload|_is_collection_replacement_module_literal_replacement_workload|_is_collection_replacement_pattern_literal_replacement_workload|_is_any_collection_replacement_module_literal_replacement_workload|_is_any_collection_replacement_pattern_literal_replacement_workload)\\b' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Prefer deleting the seven wrappers over introducing another helper module, registry layer, or extra route abstraction.
- Keep the route tables and the existing generic literal-replacement selector as the ownership surface unless a strictly smaller same-file successor preserves the same behavior.
- Do not change implementation code, tests outside the targeted benchmark contract file, workload manifests, reports, README copy, or tracked project-state prose in this run.

## Notes
- `RBR-1076` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty before this file is added;
  - `ops/tasks/done/` currently runs through `RBR-1075`; and
  - `rg -n 'RBR-1076|RBR-1077|RBR-1078' ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done` returned no existing queued or reserved task for `RBR-1076` in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete and current in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest runtime cycle shows both task workers finishing `done`, with no inherited-dirty checkpoint churn or stalled post-task refresh path.
- The duplication target is concrete in the live checkout:
  - `sed -n '3740,3925p' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` shows the measured-manifest and benchmark-gap checks still routing through the seven wrapper names instead of the route owners or generic selector;
  - `sed -n '9780,9885p' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` shows the five standard anchor definitions still depending on the same wrapper layer; and
  - `rg -n '^def (_is_collection_replacement_pattern_findall_bounded_workload|_is_collection_replacement_pattern_finditer_bounded_workload|_is_collection_replacement_pattern_split_workload|_is_collection_replacement_module_literal_replacement_workload|_is_collection_replacement_pattern_literal_replacement_workload|_is_any_collection_replacement_module_literal_replacement_workload|_is_any_collection_replacement_pattern_literal_replacement_workload)\\b' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently returns the seven wrapper definitions in this run.
- The focused verification slice is green in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_pattern_findall_bounded_rows_measured or collection_replacement_manifest_keeps_pattern_finditer_bounded_rows_measured or collection_replacement_manifest_keeps_pattern_split_rows_measured or collection_replacement_manifest_keeps_pattern_replacement_literal_rows_measured or collection_replacement_manifest_keeps_module_literal_replacement_rows_measured or test_collection_replacement_module_literal_replacement_benchmark_gap_stays_explicit or test_collection_replacement_pattern_literal_replacement_benchmark_gap_stays_explicit or collection-replacement-pattern-findall-bounded or collection-replacement-pattern-finditer-bounded or collection-replacement-pattern-split or collection-replacement-module-literal-replacement or collection-replacement-pattern-literal-replacement'` returned `27 passed, 695 deselected, 47 subtests passed` in this run.
