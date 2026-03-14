# RBR-0298: Replace the early source-tree boundary benchmark JSON manifests with Python modules

Status: done
Owner: architecture-implementation
Created: 2026-03-14

## Goal
- Reduce tracked JSON and simplify the benchmark harness input path by replacing the next four early source-tree boundary workload manifests with ordinary Python `MANIFEST` modules while preserving the existing combined scorecard and manifest-by-id helper flow.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/grouped_named_boundary.py`
- `benchmarks/workloads/numbered_backreference_boundary.py`
- `benchmarks/workloads/grouped_segment_boundary.py`
- `benchmarks/workloads/literal_alternation_boundary.py`
- Delete `benchmarks/workloads/grouped_named_boundary.json`
- Delete `benchmarks/workloads/numbered_backreference_boundary.json`
- Delete `benchmarks/workloads/grouped_segment_boundary.json`
- Delete `benchmarks/workloads/literal_alternation_boundary.json`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- `python/rebar_harness/benchmarks.py` continues to load benchmark manifests from both `.json` and `.py` paths through the existing shared validation path; do not add another family-specific loader, generator step, manifest registry, or package-discovery layer for these files.
- Each targeted workload manifest becomes a one-manifest-per-file Python module exposing the same manifest id, defaults, notes, workload ids, workload ordering, workload payloads, smoke tags, and workload counts that the deleted JSON file previously supplied, and no duplicate JSON copy of those four manifests remains in the tree.
- `DEFAULT_MANIFEST_PATHS` points at the new `.py` files for `grouped_named_boundary`, `numbered_backreference_boundary`, `grouped_segment_boundary`, and `literal_alternation_boundary` in the same ordering slots, so the existing combined benchmark surface and manifest-by-id helpers continue to derive those manifests from one path list instead of another suffix-specific branch.
- The regenerated `reports/benchmarks/latest.json` preserves the current manifest ordering, manifest ids, workload ids, workload counts, known-gap counts, representative measured rows, and source-tree adapter metadata for the targeted families except for artifact path extensions changing from `.json` to `.py`.
- The existing verification surface still passes with the Python-backed manifests, including `tests.benchmarks.test_source_tree_benchmark_scorecards`, `tests.benchmarks.test_source_tree_combined_boundary_benchmarks`, and `tests.benchmarks.test_built_native_full_suite_benchmarks` under their existing skip conditions.
- The live JSON file count decreases by exactly 4 relative to the current checkout baseline; in this dirty worktree, `rg --files -g '*.json' | wc -l` should move from `68` to `64`.

## Constraints
- Keep the scope to `grouped_named_boundary`, `numbered_backreference_boundary`, `grouped_segment_boundary`, and `literal_alternation_boundary`; do not convert later grouped/nested benchmark families, correctness fixtures, or report/config JSON in the same run.
- Do not change benchmark scorecard schema, workload semantics, or `reports/benchmarks/native_smoke.json` / `reports/benchmarks/native_full.json` in this task.
- Prefer simple Python `MANIFEST` modules and the existing path-based loader over generators, codegen, or another workload DSL.

## Notes
- `.rebar/runtime/dashboard.md` currently reports `tracked_json_blob_count: 103` and `tracked_json_blob_delta: 0`, so this run should keep burning down ordinary tracked manifests instead of seeding another non-JSON cleanup.
- `python/rebar_harness/benchmarks.py` already supports mixed `.json`/`.py` manifests, and the benchmark expectation helpers derive source-tree manifests by id from `DEFAULT_MANIFEST_PATHS`; these four files are still JSON mainly by suffix inertia, so another helper layer would add duplication without buying clarity.
- The current checkout is dirty and the dashboard count lags the live working-tree manifest count; verify the reduction with `rg --files -g '*.json' | wc -l` until the deletions are committed.

## Completion Notes
- 2026-03-14: Replaced `grouped_named_boundary`, `numbered_backreference_boundary`, `grouped_segment_boundary`, and `literal_alternation_boundary` with plain Python `MANIFEST` modules, repointed their `DEFAULT_MANIFEST_PATHS` entries to `.py`, and removed the deleted JSON originals without changing the shared mixed-path loader or adding another benchmark registry layer.
- 2026-03-14: Verified the new modules load to the exact same manifest payloads as the deleted JSON by comparing each `MANIFEST` dict against `git show HEAD:...json`, then regenerated `reports/benchmarks/latest.json` with the same default-suite shape and `.py` artifact paths for the converted manifests.
- 2026-03-14: Verified with `python3 -m py_compile python/rebar_harness/benchmarks.py benchmarks/workloads/grouped_named_boundary.py benchmarks/workloads/numbered_backreference_boundary.py benchmarks/workloads/grouped_segment_boundary.py benchmarks/workloads/literal_alternation_boundary.py`, `PYTHONPATH=python python3 -m rebar_harness.benchmarks --report reports/benchmarks/latest.json`, `PYTHONPATH=python python3 -m unittest tests.benchmarks.test_source_tree_benchmark_scorecards tests.benchmarks.test_source_tree_combined_boundary_benchmarks tests.benchmarks.test_built_native_full_suite_benchmarks` (`OK`, `skipped=1`), and `rg --files -g '*.json' | wc -l` (`64`, down from `68`). `python3 -m pytest ...` was not available because `pytest` is not installed in this checkout.
