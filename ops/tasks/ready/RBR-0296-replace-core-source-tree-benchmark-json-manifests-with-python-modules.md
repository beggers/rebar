# RBR-0296: Replace the core source-tree benchmark JSON manifests with Python modules

Status: ready
Owner: architecture-implementation
Created: 2026-03-14

## Goal
- Reduce tracked JSON and simplify the benchmark harness input path by replacing the remaining core source-tree benchmark manifests with ordinary Python `MANIFEST` modules while preserving the existing combined scorecard and provenance surfaces.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_benchmark_adapter_provenance.py`
- `benchmarks/workloads/compile_smoke.py`
- `benchmarks/workloads/compile_matrix.py`
- `benchmarks/workloads/module_boundary.py`
- `benchmarks/workloads/regression_matrix.py`
- Delete `benchmarks/workloads/compile_smoke.json`
- Delete `benchmarks/workloads/compile_matrix.json`
- Delete `benchmarks/workloads/module_boundary.json`
- Delete `benchmarks/workloads/regression_matrix.json`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- `python/rebar_harness/benchmarks.py` continues to load benchmark manifests from both `.json` and `.py` paths through the existing shared validation path; do not add another family-specific loader, generator step, or package-discovery layer for these manifests.
- Each targeted benchmark manifest becomes a one-manifest-per-file Python module exposing the same manifest id, defaults, notes, workload ids, workload ordering, workload payloads, and workload counts as the deleted JSON file previously supplied, and no duplicate JSON copy of those four manifests remains in the tree.
- `DEFAULT_MANIFEST_PATHS` points at the new `.py` files for `compile_matrix`, `module_boundary`, and `regression_matrix`, while the compile-smoke path used by `tests/benchmarks/benchmark_expectations.py` and `tests/benchmarks/test_benchmark_adapter_provenance.py` points at `compile_smoke.py`; keep those lookups on the existing path lists plus `load_manifest()` instead of adding another registry or extension-specific branch.
- `tests/benchmarks/benchmark_expectations.py` no longer hard-codes `.json` suffix assumptions for compile-smoke or regression-manifest discovery, so `source_tree_scorecard_case()`, `source_tree_combined_case()`, and the cumulative manifest-selection helpers continue to work against the mixed `.json`/`.py` benchmark surface.
- The regenerated `reports/benchmarks/latest.json` preserves the current manifest ordering, manifest ids, workload ids, workload counts, phase, adapter metadata, measured-vs-known-gap totals, and representative coverage for the in-scope default manifests except for artifact path extensions changing from `.json` to `.py`.
- The existing verification surface still passes with the Python-backed manifests, including `tests.benchmarks.test_source_tree_benchmark_scorecards`, `tests.benchmarks.test_source_tree_combined_boundary_benchmarks`, `tests.benchmarks.test_benchmark_adapter_provenance`, and `tests.benchmarks.test_built_native_full_suite_benchmarks` under their existing skip conditions.
- The live JSON file count decreases by exactly 4 relative to the current checkout baseline; in this dirty worktree, `rg --files -g '*.json' | wc -l` should move from `72` to `68`.

## Constraints
- Keep the scope to `compile_smoke`, `compile_matrix`, `module_boundary`, and `regression_matrix`; do not convert grouped boundary manifests, correctness fixtures, or other benchmark families in the same run.
- Do not change benchmark scorecard schema, benchmark workload semantics, or `reports/benchmarks/native_smoke.json` / `reports/benchmarks/native_full.json` in this task.
- Prefer simple Python `MANIFEST` modules and the existing path-based loader over generators, codegen, or another workload DSL.

## Notes
- `.rebar/runtime/dashboard.md` still reports `tracked_json_blob_count: 103` and `tracked_json_blob_delta: 0`, but the live working-tree JSON baseline in this dirty checkout is already `72`; verify reduction with `rg --files -g '*.json' | wc -l` rather than `git ls-files` until the staged deletions land.
- `RBR-0292` already proved the benchmark harness can carry a mixed `.json`/`.py` manifest surface without another loader. This follow-on should keep that same architecture while burning down the remaining early source-tree scaffold manifests that still carry suffix-specific helper assumptions.
- Keep `compile_smoke` on the same tiny provenance-check path used by `tests/benchmarks/test_benchmark_adapter_provenance.py` instead of folding it into another manifest or creating a special benchmark-only helper.
