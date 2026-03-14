# RBR-0308: Replace the remaining conditional benchmark JSON manifests with Python modules

Status: ready
Owner: architecture-implementation
Created: 2026-03-14

## Goal
- Reduce tracked JSON and finish the benchmark harness workload-input migration by replacing the five remaining `conditional_group_exists*.json` source-tree manifests with ordinary Python `MANIFEST` modules.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/conditional_group_exists_boundary.py`
- `benchmarks/workloads/conditional_group_exists_no_else_boundary.py`
- `benchmarks/workloads/conditional_group_exists_empty_else_boundary.py`
- `benchmarks/workloads/conditional_group_exists_empty_yes_else_boundary.py`
- `benchmarks/workloads/conditional_group_exists_fully_empty_boundary.py`
- Delete `benchmarks/workloads/conditional_group_exists_boundary.json`
- Delete `benchmarks/workloads/conditional_group_exists_no_else_boundary.json`
- Delete `benchmarks/workloads/conditional_group_exists_empty_else_boundary.json`
- Delete `benchmarks/workloads/conditional_group_exists_empty_yes_else_boundary.json`
- Delete `benchmarks/workloads/conditional_group_exists_fully_empty_boundary.json`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- Each targeted conditional benchmark manifest becomes a one-manifest-per-file Python module exposing the same manifest id, defaults, notes, workload ids, workload ordering, workload payloads, smoke tags, and workload counts that the deleted JSON file previously supplied, and no duplicate JSON copy of those five manifests remains in the tree.
- The converted manifests preserve the current checkout payload sizes and ids: `conditional-group-exists-boundary` with `50` workloads, `conditional-group-exists-no-else-boundary` with `27`, `conditional-group-exists-empty-else-boundary` with `27`, `conditional-group-exists-empty-yes-else-boundary` with `27`, and `conditional-group-exists-fully-empty-boundary` with `24`.
- `DEFAULT_MANIFEST_PATHS` points at the five new `.py` files in the same ordering slots, so `tests/benchmarks/benchmark_expectations.py`, the combined scorecard helpers, and the benchmark CLI keep deriving this family from one shared manifest-path list instead of another conditional-family registry or suffix branch.
- Because these are the last tracked benchmark workload JSON files under `benchmarks/workloads/`, `python/rebar_harness/benchmarks.py` no longer preserves a benchmark-manifest `.json` loading branch for deleted tracked artifacts; keep report JSON and subprocess JSON handling intact, but simplify benchmark-manifest loading to the ordinary Python-module path now that the benchmark workload surface is fully `.py`.
- The regenerated `reports/benchmarks/latest.json` preserves the current manifest ordering, manifest ids, workload ids, workload counts, representative measured rows, known-gap counts, and source-tree adapter metadata for the targeted families except for artifact path extensions changing from `.json` to `.py`.
- The existing verification surface still passes with the Python-backed conditional manifests, including `tests.benchmarks.test_source_tree_benchmark_scorecards`, `tests.benchmarks.test_source_tree_combined_boundary_benchmarks`, and `tests.benchmarks.test_built_native_full_suite_benchmarks` under their existing skip conditions.
- The live JSON file count decreases by exactly `5` relative to the current dirty-checkout baseline; `rg --files -g '*.json' | wc -l` should move from `49` to `44`.

## Constraints
- Keep the scope to the five `conditional_group_exists*_boundary` benchmark manifests listed above; do not convert correctness fixtures, agent/config JSON, or benchmark-report JSON in the same run.
- Do not change benchmark scorecard schema, workload semantics, `reports/benchmarks/native_smoke.json`, or `reports/benchmarks/native_full.json`.
- Prefer simple Python `MANIFEST` modules and the existing path-based manifest flow over generators, codegen, or another benchmark workload DSL.

## Notes
- `.rebar/runtime/dashboard.md` still reports `tracked_json_blob_count: 103` and `tracked_json_blob_delta: 0`, while `git ls-files '*.json' | wc -l` still reports `103`; in this dirty checkout the live workload-file baseline is already `49`, so verify reduction with `rg --files -g '*.json' | wc -l` until the deletions land in a commit.
- This is the final JSON-only block inside `python/rebar_harness/benchmarks.py::DEFAULT_MANIFEST_PATHS`; landing it should leave `benchmarks/workloads/` with no tracked JSON manifests and complete the benchmark harness shift to ordinary Python workload modules.
- There are no remaining manifest-specific benchmark tests for these five files; keep the coverage anchored in the existing shared scorecard and combined-boundary suites instead of inventing new per-manifest wrapper tests unless a current test actually needs a small path update.
