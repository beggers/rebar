# RBR-0292: Replace the native-smoke benchmark JSON manifests with Python modules

Status: done
Owner: architecture-implementation
Created: 2026-03-14

## Goal
- Reduce tracked JSON on the benchmark side and simplify benchmark-manifest flow by replacing the three published native-smoke workload manifests with ordinary Python modules while keeping the existing source-tree and built-native benchmark surfaces unchanged.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/pattern_boundary.py`
- `benchmarks/workloads/collection_replacement_boundary.py`
- `benchmarks/workloads/literal_flag_boundary.py`
- Delete `benchmarks/workloads/pattern_boundary.json`
- Delete `benchmarks/workloads/collection_replacement_boundary.json`
- Delete `benchmarks/workloads/literal_flag_boundary.json`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- `python/rebar_harness/benchmarks.py` loads benchmark manifests from both `.json` and `.py` paths through one shared validation path; do not add a family-specific loader, generator step, or package-discovery abstraction for these manifests.
- Each targeted native-smoke manifest becomes a one-manifest-per-file Python module exposing the same manifest id, defaults, notes, workload ids, workload ordering, and workload payloads that the deleted JSON file previously supplied, and no duplicate JSON copy of those three manifests remains in the tree.
- `DEFAULT_MANIFEST_PATHS` and `DEFAULT_NATIVE_SMOKE_MANIFEST_PATHS` point at the new `.py` files in the same ordering slots, so `run_benchmarks()`, `run_built_native_smoke_benchmarks()`, `tests/benchmarks/benchmark_expectations.py`, and the existing source-tree combined scorecard coverage all continue to derive their inventory from the existing path lists plus `load_manifest()` rather than a second registry.
- The regenerated `reports/benchmarks/latest.json` preserves the current manifest ordering, manifest ids, workload ids, workload counts, measured-vs-known-gap totals, and combined benchmark contract for the in-scope manifests except for the artifact path extensions changing from `.json` to `.py`.
- The mixed `.json`/`.py` benchmark surface still passes the existing verification path, including `tests.benchmarks.test_source_tree_benchmark_scorecards`, `tests.benchmarks.test_source_tree_combined_boundary_benchmarks`, `tests.benchmarks.test_built_native_benchmark_smoke`, and `tests.benchmarks.test_built_native_full_suite_benchmarks` under their existing skip conditions.
- The live JSON file count decreases by exactly 3 relative to the current checkout baseline; in this worktree, `rg --files -g '*.json' | wc -l` should move from `80` to `77`.

## Constraints
- Keep the scope to `pattern_boundary`, `collection_replacement_boundary`, and `literal_flag_boundary`; do not convert `module_boundary`, compile/regression manifests, grouped boundary manifests, or correctness fixtures in the same run.
- Do not change benchmark scorecard schema, benchmark workload semantics, or `reports/benchmarks/native_smoke.json` / `reports/benchmarks/native_full.json` in this task.
- Prefer simple Python `MANIFEST` modules and the shared path-based loader over generators, codegen, or another workload DSL.

## Notes
- `.rebar/runtime/dashboard.md` currently reports `tracked_json_blob_count: 103` and `tracked_json_blob_delta: 0`, but the live working-tree JSON baseline in this dirty checkout is already `80`; verify reduction with `rg --files -g '*.json' | wc -l` rather than `git ls-files` until the staged deletions land.
- The correctness harness already proved the mixed `.json`/`.py` manifest path in `python/rebar_harness/correctness.py`; mirror that architecture on the benchmark side instead of introducing a second benchmark-only representation layer.
- Keep the manifest model path-based so explicit `python -m rebar_harness.benchmarks --manifest ...` calls continue to accept direct file paths without another discovery abstraction.

## Completion Notes
- 2026-03-14: Replaced the `pattern_boundary`, `collection_replacement_boundary`, and `literal_flag_boundary` benchmark manifests with plain Python `MANIFEST` modules, updated the shared benchmark loader plus default/native-smoke manifest path lists to accept mixed `.json`/`.py` paths through one validation path, and regenerated `reports/benchmarks/latest.json` with the same manifest/workload inventory and totals but `.py` artifact paths for the converted manifests.
- Verified with `PYTHONPATH=python python3 -m rebar_harness.benchmarks --report reports/benchmarks/latest.json`, `PYTHONPATH=python python3 -m unittest tests.benchmarks.test_source_tree_benchmark_scorecards tests.benchmarks.test_source_tree_combined_boundary_benchmarks tests.benchmarks.test_built_native_benchmark_smoke tests.benchmarks.test_built_native_full_suite_benchmarks` (`OK`, `skipped=2`), and `rg --files -g '*.json' | wc -l` (`77`).
