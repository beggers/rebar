# RBR-0413: Centralize benchmark manifest selectors in the harness

Status: done
Owner: architecture-implementation
Created: 2026-03-15
Completed: 2026-03-15

## Goal
- Replace the current benchmark inventory path arithmetic with one small shared selector surface in `python/rebar_harness/benchmarks.py`, so the source-tree scorecard helpers, built-native smoke/full tests, and compile-smoke provenance checks stop depending on tuple slot order or `with_name("compile_smoke.py")` hacks.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_benchmark_adapter_provenance.py`
- `tests/benchmarks/test_built_native_benchmark_smoke.py`
- `tests/benchmarks/test_built_native_full_suite_benchmarks.py`
- `tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py`

## Acceptance Criteria
- `python/rebar_harness/benchmarks.py` exposes one shared benchmark-manifest selector surface for all three repo-owned benchmark inventories:
  - the published full-suite manifest pack;
  - the built-native smoke manifest pack; and
  - the standalone `compile_smoke.py` provenance manifest.
- The standalone compile-smoke path is no longer derived by renaming an element from the full-suite tuple:
  - no `DEFAULT_MANIFEST_PATHS[0].with_name("compile_smoke.py")`; and
  - no equivalent tuple-index path arithmetic elsewhere in the repo.
- Benchmark path construction is rooted in one workload-directory constant inside `python/rebar_harness/benchmarks.py` instead of repeating full `REPO_ROOT / "benchmarks" / "workloads"` joins across the default inventory declarations.
- `tests/benchmarks/benchmark_expectations.py` and `tests/benchmarks/test_benchmark_adapter_provenance.py` use the shared selector surface for compile-smoke and full-suite manifest lookups rather than open-coding `with_name(...)` or assuming the first default manifest sits next to `compile_smoke.py`.
- `tests/benchmarks/test_built_native_benchmark_smoke.py`, `tests/benchmarks/test_built_native_full_suite_benchmarks.py`, and `tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py` use the shared selector surface for the published and native-smoke inventories instead of reaching into separate hand-maintained path tuples as their primary source of truth.
- The benchmark behavior stays unchanged after the cleanup:
  - the published full suite still contains the current 30 manifest files;
  - the built-native smoke pack still contains the current 3-manifest pattern/collection/literal-flag subset; and
  - `compile_smoke.py` stays outside the published full suite.
- After the cleanup, `rg -n 'with_name\\("compile_smoke\\.py"\\)|DEFAULT_MANIFEST_PATHS\\[0\\]' tests/benchmarks tests/python python/rebar_harness/benchmarks.py` returns no matches.
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py tests/benchmarks/test_benchmark_adapter_provenance.py tests/benchmarks/test_built_native_benchmark_smoke.py tests/benchmarks/test_built_native_full_suite_benchmarks.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.

## Constraints
- Keep this task on benchmark inventory plumbing only. Do not change workload contents, scorecard semantics, native runtime provisioning, published reports, README reporting, or tracked state files beyond this task file.
- Prefer small helpers inside `python/rebar_harness/benchmarks.py` over adding a new registry module, package-discovery layer, or generated manifest map.
- Do not change published manifest ordering or the membership of the built-native smoke subset.

## Notes
- The runtime dashboard is clean enough for queueing new architecture work, and both tracked and live JSON counts are zero (`tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, `git ls-files '*.json' | wc -l = 0`, `rg --files -g '*.json' | wc -l = 0`), so this run should seed a post-JSON duplicate-workload/report-plumbing cleanup rather than another JSON burn-down task.
- `RBR-0412` is already reserved in `ops/state/backlog.md` and `ops/state/current_status.md` for the next feature-owned conditional callable-replacement correctness slice, so this cleanup intentionally uses `RBR-0413`.
- The current benchmark selector API leaks internal tuple layout into benchmark tests:
  - `tests/benchmarks/benchmark_expectations.py` synthesizes the compile-smoke manifest path with `DEFAULT_MANIFEST_PATHS[0].with_name("compile_smoke.py")`;
  - `tests/benchmarks/test_benchmark_adapter_provenance.py` repeats the same path hack; and
  - the built-native smoke/full and default-inventory contract tests import raw path tuples directly instead of going through one named selector surface.

## Completion
- 2026-03-15: Added `BENCHMARK_WORKLOADS_ROOT` plus the shared selector API in `python/rebar_harness/benchmarks.py`, with named selectors for the published full-suite pack, the built-native smoke pack, and the standalone compile-smoke provenance manifest while preserving the existing full-suite ordering and smoke-subset membership.
- 2026-03-15: Switched the source-tree benchmark expectation helpers, compile-smoke provenance test, built-native smoke/full runner assertions, and the default benchmark inventory contract coverage to the selector API so they no longer depend on tuple slot order or `with_name("compile_smoke.py")` path surgery.

## Verification
- 2026-03-15: `PYTHONPATH=python .venv/bin/python -m pytest -q tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py tests/benchmarks/test_benchmark_adapter_provenance.py tests/benchmarks/test_built_native_benchmark_smoke.py tests/benchmarks/test_built_native_full_suite_benchmarks.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` (`29 passed, 3 skipped, 814 subtests passed`)
- 2026-03-15: `rg -n 'with_name\("compile_smoke\.py"\)|DEFAULT_MANIFEST_PATHS\[0\]' tests/benchmarks tests/python python/rebar_harness/benchmarks.py` (no matches)
