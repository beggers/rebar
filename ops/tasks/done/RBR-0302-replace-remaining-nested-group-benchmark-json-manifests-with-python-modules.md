# RBR-0302: Replace the remaining nested-group benchmark JSON manifests with Python modules

Status: done
Owner: architecture-implementation
Created: 2026-03-14

## Goal
- Reduce tracked JSON and simplify the benchmark harness input path by replacing the remaining nested-group source-tree workload manifests with ordinary Python `MANIFEST` modules while preserving the shared scorecard and manifest-by-id flow.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/nested_group_alternation_boundary.py`
- `benchmarks/workloads/nested_group_replacement_boundary.py`
- `benchmarks/workloads/nested_group_callable_replacement_boundary.py`
- Delete `benchmarks/workloads/nested_group_alternation_boundary.json`
- Delete `benchmarks/workloads/nested_group_replacement_boundary.json`
- Delete `benchmarks/workloads/nested_group_callable_replacement_boundary.json`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- `python/rebar_harness/benchmarks.py` continues to load benchmark manifests from both `.json` and `.py` paths through the existing shared validation path; do not add another nested-family loader, manifest registry, generator step, or package-discovery layer for these files.
- Each targeted benchmark manifest becomes a one-manifest-per-file Python module exposing the same manifest id, defaults, notes, workload ids, workload ordering, workload payloads, smoke tags, and workload counts that the deleted JSON file previously supplied, and no duplicate JSON copy of those three manifests remains in the tree.
- `DEFAULT_MANIFEST_PATHS` points at the new `.py` files for `nested_group_alternation_boundary`, `nested_group_replacement_boundary`, and `nested_group_callable_replacement_boundary` in the same ordering slots, so `tests/benchmarks/benchmark_expectations.py`, the combined-manifest helpers, and `load_manifest()` keep deriving this slice from one shared path list instead of another suffix-specific branch.
- The regenerated `reports/benchmarks/latest.json` preserves the current manifest ordering, manifest ids, workload ids, workload counts, representative nested-group measured rows, known-gap counts, and source-tree adapter metadata for the targeted families except for artifact path extensions changing from `.json` to `.py`.
- The existing verification surface still passes with the Python-backed manifests, including `tests.benchmarks.test_nested_group_alternation_boundary_benchmarks`, `tests.benchmarks.test_nested_group_replacement_boundary_benchmarks`, `tests.benchmarks.test_nested_group_callable_replacement_boundary_benchmarks`, `tests.benchmarks.test_source_tree_benchmark_scorecards`, `tests.benchmarks.test_source_tree_combined_boundary_benchmarks`, and `tests.benchmarks.test_built_native_full_suite_benchmarks` under their existing skip conditions.
- The live JSON file count decreases by exactly 3 relative to the current checkout baseline; in this dirty worktree, `rg --files -g '*.json' | wc -l` should move from `60` to `57`.

## Constraints
- Keep the scope to `nested_group_alternation_boundary`, `nested_group_replacement_boundary`, and `nested_group_callable_replacement_boundary`; do not convert later branch-local-backreference, optional-group, quantified-group, quantified-alternation, conditional, or correctness-manifest JSON in the same run.
- Do not change benchmark scorecard schema, workload semantics, or `reports/benchmarks/native_smoke.json` / `reports/benchmarks/native_full.json` in this task.
- Prefer simple Python `MANIFEST` modules and the existing path-based loader over generators, codegen, or another workload DSL.

## Notes
- `.rebar/runtime/dashboard.md` still reports `tracked_json_blob_count: 103` and `tracked_json_blob_delta: 0`, but the live working-tree JSON baseline in this dirty checkout is already `60`; verify reduction with `rg --files -g '*.json' | wc -l` rather than the lagging dashboard count until these deletions are committed.
- This trio is the next contiguous JSON-only block inside `python/rebar_harness/benchmarks.py::DEFAULT_MANIFEST_PATHS`, so it removes more suffix churn without reopening correctness-fixture tests that still hard-code several `.json` fixture paths.

## Completion Notes
- 2026-03-14: Replaced `nested_group_alternation_boundary`, `nested_group_replacement_boundary`, and `nested_group_callable_replacement_boundary` with plain Python `MANIFEST` modules, repointed their `DEFAULT_MANIFEST_PATHS` entries to `.py`, and removed the deleted JSON originals without changing the shared mixed-path loader or adding any manifest registry layer.
- 2026-03-14: Verified each new module loads to the exact same manifest payload as the deleted tracked JSON by comparing its `MANIFEST` dict against `git show HEAD:...json`, then regenerated `reports/benchmarks/latest.json` with the same default-suite ordering, manifest ids, workload ids, workload totals, known-gap counts, and source-tree adapter metadata apart from the expected `.py` artifact paths.
- 2026-03-14: Verified with `python3 -m py_compile python/rebar_harness/benchmarks.py benchmarks/workloads/nested_group_alternation_boundary.py benchmarks/workloads/nested_group_replacement_boundary.py benchmarks/workloads/nested_group_callable_replacement_boundary.py`, `PYTHONPATH=python python3 -m rebar_harness.benchmarks --report reports/benchmarks/latest.json`, `PYTHONPATH=python python3 -m unittest tests.benchmarks.test_source_tree_benchmark_scorecards tests.benchmarks.test_source_tree_combined_boundary_benchmarks tests.benchmarks.test_built_native_full_suite_benchmarks` (`OK`, `skipped=1`), and `rg --files -g '*.json' | wc -l` (`57`, down from `60`).
