# RBR-0300: Replace the grouped-alternation and nested-group benchmark JSON manifests with Python modules

Status: ready
Owner: architecture-implementation
Created: 2026-03-14

## Goal
- Reduce tracked JSON and simplify the benchmark harness input path by replacing the next grouped/nested source-tree workload manifests with ordinary Python `MANIFEST` modules while preserving the shared scorecard and manifest-by-id flow.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/grouped_alternation_boundary.py`
- `benchmarks/workloads/grouped_alternation_replacement_boundary.py`
- `benchmarks/workloads/grouped_alternation_callable_replacement_boundary.py`
- `benchmarks/workloads/nested_group_boundary.py`
- Delete `benchmarks/workloads/grouped_alternation_boundary.json`
- Delete `benchmarks/workloads/grouped_alternation_replacement_boundary.json`
- Delete `benchmarks/workloads/grouped_alternation_callable_replacement_boundary.json`
- Delete `benchmarks/workloads/nested_group_boundary.json`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- `python/rebar_harness/benchmarks.py` continues to load benchmark manifests from both `.json` and `.py` paths through the existing shared validation path; do not add another family-specific loader, generator step, manifest registry, or package-discovery layer for these files.
- Each targeted benchmark manifest becomes a one-manifest-per-file Python module exposing the same manifest id, defaults, notes, workload ids, workload ordering, workload payloads, smoke tags, and workload counts that the deleted JSON file previously supplied, and no duplicate JSON copy of those four manifests remains in the tree.
- `DEFAULT_MANIFEST_PATHS` points at the new `.py` files for `grouped_alternation_boundary`, `grouped_alternation_replacement_boundary`, `grouped_alternation_callable_replacement_boundary`, and `nested_group_boundary` in the same ordering slots, so `tests/benchmarks/benchmark_expectations.py`, the combined-manifest helpers, and `load_manifest()` keep deriving this slice from one shared path list instead of another suffix-specific branch.
- The regenerated `reports/benchmarks/latest.json` preserves the current manifest ordering, manifest ids, workload ids, workload counts, representative grouped/nested measured rows, known-gap counts, and source-tree adapter metadata for the targeted families except for artifact path extensions changing from `.json` to `.py`.
- The existing verification surface still passes with the Python-backed manifests, including `tests.benchmarks.test_source_tree_benchmark_scorecards`, `tests.benchmarks.test_source_tree_combined_boundary_benchmarks`, and `tests.benchmarks.test_built_native_full_suite_benchmarks` under their existing skip conditions.
- The live JSON file count decreases by exactly 4 relative to the current checkout baseline; in this dirty worktree, `rg --files -g '*.json' | wc -l` should move from `64` to `60`.

## Constraints
- Keep the scope to `grouped_alternation_boundary`, `grouped_alternation_replacement_boundary`, `grouped_alternation_callable_replacement_boundary`, and `nested_group_boundary`; do not convert later nested, branch-local-backreference, optional-group, conditional, or correctness-manifest JSON in the same run.
- Do not change benchmark scorecard schema, workload semantics, or `reports/benchmarks/native_smoke.json` / `reports/benchmarks/native_full.json` in this task.
- Prefer simple Python `MANIFEST` modules and the existing path-based loader over generators, codegen, or another workload DSL.

## Notes
- `.rebar/runtime/dashboard.md` still reports `tracked_json_blob_count: 103` and `tracked_json_blob_delta: 0`, but the live working-tree JSON baseline in this dirty checkout is already `64`; verify reduction with `rg --files -g '*.json' | wc -l` rather than the lagging dashboard count until these deletions are committed.
- The current bottleneck is not loader capability: `python/rebar_harness/benchmarks.py` and `tests/benchmarks/benchmark_expectations.py` already handle mixed `.json`/`.py` manifests off `DEFAULT_MANIFEST_PATHS`, so this batch should delete suffix inertia rather than add new plumbing.
- A comparable correctness-fixture cleanup would currently sprawl into more suffix-specific test rewrites because several correctness tests still hard-code `.json` fixture paths; this benchmark batch is the smaller one-run JSON burn-down.
