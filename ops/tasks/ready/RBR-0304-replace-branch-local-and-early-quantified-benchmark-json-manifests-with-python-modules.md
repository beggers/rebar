# RBR-0304: Replace the branch-local and early quantified benchmark JSON manifests with Python modules

Status: ready
Owner: architecture-implementation
Created: 2026-03-14

## Goal
- Reduce tracked JSON and simplify the benchmark harness input path by replacing the next smaller contiguous source-tree workload manifests with ordinary Python `MANIFEST` modules while preserving the shared scorecard and manifest-by-id flow.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/branch_local_backreference_boundary.py`
- `benchmarks/workloads/optional_group_boundary.py`
- `benchmarks/workloads/exact_repeat_quantified_group_boundary.py`
- `benchmarks/workloads/ranged_repeat_quantified_group_boundary.py`
- Delete `benchmarks/workloads/branch_local_backreference_boundary.json`
- Delete `benchmarks/workloads/optional_group_boundary.json`
- Delete `benchmarks/workloads/exact_repeat_quantified_group_boundary.json`
- Delete `benchmarks/workloads/ranged_repeat_quantified_group_boundary.json`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- `python/rebar_harness/benchmarks.py` continues to load benchmark manifests from both `.json` and `.py` paths through the existing shared validation path; do not add another family-specific loader, manifest registry, generator step, or package-discovery layer for these files.
- Each targeted benchmark manifest becomes a one-manifest-per-file Python module exposing the same manifest id, defaults, notes, workload ids, workload ordering, workload payloads, smoke tags, and workload counts that the deleted JSON file previously supplied, and no duplicate JSON copy of those four manifests remains in the tree.
- `DEFAULT_MANIFEST_PATHS` points at the new `.py` files for `branch_local_backreference_boundary`, `optional_group_boundary`, `exact_repeat_quantified_group_boundary`, and `ranged_repeat_quantified_group_boundary` in the same ordering slots, so `tests/benchmarks/benchmark_expectations.py`, the combined-manifest helpers, and `load_manifest()` keep deriving this slice from one shared path list instead of another suffix-specific branch.
- The regenerated `reports/benchmarks/latest.json` preserves the current manifest ordering, manifest ids, workload ids, workload counts, representative measured rows, known-gap counts, and source-tree adapter metadata for the targeted families except for artifact path extensions changing from `.json` to `.py`.
- The existing verification surface still passes with the Python-backed manifests, including `tests.benchmarks.test_source_tree_benchmark_scorecards`, `tests.benchmarks.test_source_tree_combined_boundary_benchmarks`, and `tests.benchmarks.test_built_native_full_suite_benchmarks` under their existing skip conditions.
- The live JSON file count decreases by exactly 4 relative to the current checkout baseline; in this dirty worktree, `rg --files -g '*.json' | wc -l` should move from `57` to `53`.

## Constraints
- Keep the scope to `branch_local_backreference_boundary`, `optional_group_boundary`, `exact_repeat_quantified_group_boundary`, and `ranged_repeat_quantified_group_boundary`; do not convert `wider_ranged_repeat_quantified_group_boundary`, `open_ended_quantified_group_boundary`, `quantified_alternation_boundary`, `optional_group_alternation_boundary`, conditional benchmark manifests, or correctness-manifest JSON in the same run.
- Do not change benchmark scorecard schema, workload semantics, or `reports/benchmarks/native_smoke.json` / `reports/benchmarks/native_full.json` in this task.
- Prefer simple Python `MANIFEST` modules and the existing path-based loader over generators, codegen, or another workload DSL.

## Notes
- `.rebar/runtime/dashboard.md` still reports `tracked_json_blob_count: 103` and `tracked_json_blob_delta: 0`, but the live working-tree JSON baseline in this dirty checkout is already `57`; verify reduction with `rg --files -g '*.json' | wc -l` rather than the lagging dashboard count until these deletions are committed.
- These four manifests are the next smaller contiguous JSON-only block inside `python/rebar_harness/benchmarks.py::DEFAULT_MANIFEST_PATHS`, and unlike the later `wider_ranged_repeat` or conditional families they do not carry a dedicated file-specific benchmark test that still hard-codes a `.json` path.
- Keep the architecture simple: reuse the existing mixed `.json`/`.py` loader and one shared manifest-path list rather than introducing another registry or benchmark-family wrapper just to finish this conversion batch.
