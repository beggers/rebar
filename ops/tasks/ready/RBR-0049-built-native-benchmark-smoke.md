# RBR-0049: Publish a built-native benchmark smoke report

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Exercise a bounded published benchmark slice through a built native `rebar._rebar` import path so benchmark reporting no longer relies entirely on the source-tree shim.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `tests/benchmarks/test_built_native_benchmark_smoke.py`
- `reports/benchmarks/native_smoke.json`

## Acceptance Criteria
- The benchmark harness supports a dedicated built-native smoke mode that runs a small subset of already published workloads without silently falling back to the source-tree shim.
- `reports/benchmarks/native_smoke.json` records a real built-native run with `adapter_mode_resolved` set to `built-native`, `native_module_loaded` set to `true`, and concrete native-build provenance for the exercised smoke workloads.
- Direct test coverage pins the built-native smoke behavior and keeps the existing full-suite `reports/benchmarks/latest.json` flow intact.

## Constraints
- Keep this task scoped to a smoke-sized native benchmark slice; do not replace the full published benchmark suite, broaden regex behavior, or claim that all routine benchmark publication is native-backed.
- Reuse the existing adapter-provenance machinery from `RBR-0020` and the native import/build path validated by `RBR-0010`.
- Do not fabricate native timings or hide native build/load failures behind a shim fallback.

## Notes
- Build on `RBR-0020`, `RBR-0037A`, `RBR-0042`, `RBR-0042A`, and `RBR-0048`. This task exists because the benchmark harness can already distinguish shim versus built-native modes, but the tracked landing surfaces still only publish source-tree-shim timings.
