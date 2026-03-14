# RBR-0306: Replace the wider-ranged/open-ended/alternation benchmark JSON manifests with Python modules

Status: done
Owner: architecture-implementation
Created: 2026-03-14

## Goal
- Reduce tracked JSON and simplify the benchmark harness input path by replacing the next contiguous counted-repeat/alternation source-tree workload manifests with ordinary Python `MANIFEST` modules while preserving the shared scorecard and manifest-by-id flow.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.py`
- `benchmarks/workloads/open_ended_quantified_group_boundary.py`
- `benchmarks/workloads/quantified_alternation_boundary.py`
- `benchmarks/workloads/optional_group_alternation_boundary.py`
- `tests/benchmarks/test_wider_ranged_repeat_quantified_group_boundary_benchmarks.py`
- Delete `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.json`
- Delete `benchmarks/workloads/open_ended_quantified_group_boundary.json`
- Delete `benchmarks/workloads/quantified_alternation_boundary.json`
- Delete `benchmarks/workloads/optional_group_alternation_boundary.json`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- `python/rebar_harness/benchmarks.py` continues to load benchmark manifests from both `.json` and `.py` paths through the existing shared validation path; do not add another family-specific loader, manifest registry, generator step, or package-discovery layer for these files.
- Each targeted benchmark manifest becomes a one-manifest-per-file Python module exposing the same manifest id, defaults, notes, workload ids, workload ordering, workload payloads, smoke tags, and workload counts that the deleted JSON file previously supplied, and no duplicate JSON copy of those four manifests remains in the tree.
- The four converted manifests preserve the current checkout's manifest ids and workload counts: `wider-ranged-repeat-quantified-group-boundary` with `62` workloads, `open-ended-quantified-group-boundary` with `36`, `quantified-alternation-boundary` with `42`, and `optional-group-alternation-boundary` with `13`.
- `DEFAULT_MANIFEST_PATHS` points at the new `.py` files for those four manifests in the same ordering slots, so `tests/benchmarks/benchmark_expectations.py`, the combined-manifest helpers, and `load_manifest()` keep deriving this slice from one shared path list instead of another suffix-specific branch.
- `tests/benchmarks/test_wider_ranged_repeat_quantified_group_boundary_benchmarks.py` no longer hard-codes the deleted `.json` path and still exercises the broader-range, open-ended, conditional, and backtracking-heavy benchmark rows already published through that manifest.
- The regenerated `reports/benchmarks/latest.json` preserves the current manifest ordering, manifest ids, workload ids, workload counts, representative measured rows, known-gap counts, and source-tree adapter metadata for the targeted families except for artifact path extensions changing from `.json` to `.py`.
- The existing verification surface still passes with the Python-backed manifests, including `tests.benchmarks.test_wider_ranged_repeat_quantified_group_boundary_benchmarks`, `tests.benchmarks.test_source_tree_benchmark_scorecards`, `tests.benchmarks.test_source_tree_combined_boundary_benchmarks`, and `tests.benchmarks.test_built_native_full_suite_benchmarks` under their existing skip conditions.
- The live JSON file count decreases by exactly `4` relative to the current dirty-checkout baseline; `rg --files -g '*.json' | wc -l` should move from `53` to `49`.

## Constraints
- Keep the scope to `wider_ranged_repeat_quantified_group_boundary`, `open_ended_quantified_group_boundary`, `quantified_alternation_boundary`, and `optional_group_alternation_boundary`; do not convert the five `conditional_group_exists*_boundary.json` manifests, correctness fixtures, agent specs, or report JSON in the same run.
- Do not change benchmark scorecard schema, workload semantics, or `reports/benchmarks/native_smoke.json` / `reports/benchmarks/native_full.json` in this task.
- Prefer simple Python `MANIFEST` modules and the existing path-based loader over generators, codegen, or another workload DSL.

## Notes
- `.rebar/runtime/dashboard.md` still reports `tracked_json_blob_count: 103` and `tracked_json_blob_delta: 0`, but the live working-tree JSON baseline in this dirty checkout is already `53`; verify reduction with `rg --files -g '*.json' | wc -l` rather than the lagging dashboard count until these deletions are committed.
- This four-file batch is the next contiguous JSON-only block inside `python/rebar_harness/benchmarks.py::DEFAULT_MANIFEST_PATHS` before the remaining conditional benchmark manifests.
- In the current checkout, `tests/benchmarks/test_wider_ranged_repeat_quantified_group_boundary_benchmarks.py` is the only focused benchmark test that still hard-codes one of these four manifest paths; the rest of the benchmark suite already derives these manifests through the shared path registry.
- The worktree already contains separate uncommitted correctness-fixture swaps and feature/parity changes; leave those out of scope instead of folding more in-flight cleanup into this task.

## Completion Notes
- 2026-03-14: Replaced `wider_ranged_repeat_quantified_group_boundary`, `open_ended_quantified_group_boundary`, `quantified_alternation_boundary`, and `optional_group_alternation_boundary` with plain Python `MANIFEST` modules generated from the current checkout payloads, repointed their `DEFAULT_MANIFEST_PATHS` entries to `.py`, and removed the deleted JSON originals without changing the shared mixed-path loader or adding any new manifest registry layer.
- 2026-03-14: Updated `tests/benchmarks/test_wider_ranged_repeat_quantified_group_boundary_benchmarks.py` to resolve the target manifest from `DEFAULT_MANIFEST_PATHS` by manifest id instead of hard-coding the deleted `.json` path, so the focused test now follows the same shared path list as the combined scorecard coverage.
- 2026-03-14: Verified with `python3 -m py_compile python/rebar_harness/benchmarks.py benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.py benchmarks/workloads/open_ended_quantified_group_boundary.py benchmarks/workloads/quantified_alternation_boundary.py benchmarks/workloads/optional_group_alternation_boundary.py tests/benchmarks/test_wider_ranged_repeat_quantified_group_boundary_benchmarks.py`, a direct `load_manifest()` check confirming workload counts `62`, `36`, `42`, and `13`, `PYTHONPATH=python python3 -m rebar_harness.benchmarks --report reports/benchmarks/latest.json`, `PYTHONPATH=python python3 -m unittest tests.benchmarks.test_wider_ranged_repeat_quantified_group_boundary_benchmarks tests.benchmarks.test_source_tree_benchmark_scorecards tests.benchmarks.test_source_tree_combined_boundary_benchmarks tests.benchmarks.test_built_native_full_suite_benchmarks` (`OK`, `skipped=1`), and `rg --files -g '*.json' | wc -l` (`49`, down from `53`).
