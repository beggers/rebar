## RBR-1388: Delete source-tree shape and slice wrapper helpers

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the three thin source-tree shape/slice wrappers from the shared benchmark owner layer, and have the affected tests read shape and slice data directly from `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS`, `SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS`, and the published manifest list instead of routing those reads through helper functions.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Remove these helper functions from `tests/benchmarks/source_tree_benchmark_anchor_support.py` without replacing them with another alias, wrapper, or shared helper layer:
  - `source_tree_combined_manifest_shape_expectation`
  - `source_tree_combined_slice_manifest_ids`
  - `source_tree_combined_slice_expectations`
- Rewrite `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the affected assertions keep the same behavior through direct reads of the existing owner data:
  - shape checks must read `shape_expectation` directly from `source_tree_support.SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]` and still assert that the stored value is present where the shared shape contract is required;
  - slice-manifest iteration must derive its ordered manifest ids directly from `source_tree_support.source_tree_combined_target_manifest_ids()` plus membership in `source_tree_support.SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS`, while preserving the current published-selector ordering and the current "slice expectations stay inside the combined selector" coverage;
  - per-manifest slice rows must filter `source_tree_support.SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS` directly by `manifest_id` and still preserve the current selected workload ids, representative measured row checks, and manifest-level slice grouping behavior.
- Update `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` so it treats the deleted wrappers as absent from the source-tree support module while keeping the remaining owner-surface and no-local-duplicate checks precise enough to catch regressions.
- Do not change benchmark manifests, workload ids, benchmark execution behavior, published row ids, or tracked project-state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'source_tree_combined_slice_manifest_ids or source_tree_combined_manifest_shape_expectation or source_tree_combined_slice_expectations or shape_expectation or slice_rows'`
- `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n '^(def source_tree_combined_(manifest_shape_expectation|slice_manifest_ids|slice_expectations)\\()|source_tree_support\\.source_tree_combined_(manifest_shape_expectation|slice_manifest_ids|slice_expectations)\\(|support\\.source_tree_combined_(manifest_shape_expectation|slice_manifest_ids|slice_expectations)\\(' tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Prefer direct reads of the stored manifest-definition and slice-expectation data over another shared helper.
- Keep the run bounded to deleting these three wrappers and rewiring their current benchmark-test consumers; do not reopen the broader `source_tree_combined_case(...)` or representative-workload helper stack in the same task.

## Notes
- Queue and JSON check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`.
  - `git status --short` was empty in this run, so the runtime counts were not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- ID and duplicate check in this run:
  - `rg -n 'RBR-1388|RBR-1389|RBR-1390|RBR-1391' ops/state/current_status.md ops/state/backlog.md` returned no reserved future id hits for `RBR-1388`.
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this checkout, so there was no ready or blocked duplicate to refine or reopen first.
  - No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate selection in this run:
  - With tracked and live JSON counts both at zero, I inspected the remaining public source-tree owner helpers for one bounded post-JSON simplification.
  - `source_tree_combined_manifest_shape_expectation(...)`, `source_tree_combined_slice_manifest_ids()`, and `source_tree_combined_slice_expectations(...)` are all thin wrappers over `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS`, `SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS`, and the published manifest order already available at the consuming test sites.
  - Their live consumers are bounded to the source-tree support module tests and the combined source-tree benchmark suite, so deleting them removes one more shared transit layer without touching runtime harness logic or published benchmark artifacts.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'source_tree_combined_slice_manifest_ids or source_tree_combined_manifest_shape_expectation or source_tree_combined_slice_expectations or shape_expectation or slice_rows'` passed with `6 passed, 384 deselected in 0.14s`.
  - `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed.
  - `rg -n '^(def source_tree_combined_(manifest_shape_expectation|slice_manifest_ids|slice_expectations)\\()|source_tree_support\\.source_tree_combined_(manifest_shape_expectation|slice_manifest_ids|slice_expectations)\\(|support\\.source_tree_combined_(manifest_shape_expectation|slice_manifest_ids|slice_expectations)\\(' tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently reports the exact wrapper definitions and test call sites this task is intended to delete.

## Completion Notes
- Deleted `source_tree_combined_manifest_shape_expectation`, `source_tree_combined_slice_manifest_ids`, and `source_tree_combined_slice_expectations` from `tests/benchmarks/source_tree_benchmark_anchor_support.py`.
- Rewired `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to read `shape_expectation` directly from `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS`, derive ordered slice-manifest ids from `source_tree_combined_target_manifest_ids()` plus `SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS`, and filter per-manifest slice rows directly from `SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS`.
- Updated `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` so the deleted wrappers are asserted absent and no longer part of the expected owner-local support surface.
- Verification in this run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'source_tree_combined_slice_manifest_ids or source_tree_combined_manifest_shape_expectation or source_tree_combined_slice_expectations or shape_expectation or slice_rows'` passed with `3 passed, 385 deselected in 0.34s`.
  - `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed.
  - `bash -lc "! rg -n '^(def source_tree_combined_(manifest_shape_expectation|slice_manifest_ids|slice_expectations)\\()|source_tree_support\\.source_tree_combined_(manifest_shape_expectation|slice_manifest_ids|slice_expectations)\\(|support\\.source_tree_combined_(manifest_shape_expectation|slice_manifest_ids|slice_expectations)\\(' tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` passed.
