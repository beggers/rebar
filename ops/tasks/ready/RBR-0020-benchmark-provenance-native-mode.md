# RBR-0020: Harden benchmark provenance around source and native execution modes

Status: ready
Owner: implementation
Created: 2026-03-11

## Goal
- Teach the benchmark harness to report whether timings came from the source-tree shim or a built native-module install path so benchmark results stay aligned with the validated `rebar._rebar` smoke route.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `tests/benchmarks/test_benchmark_adapter_provenance.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark runner can execute its existing workload packs against an explicit adapter/provenance mode, with the default source-tree shim path preserved and a built native-module path supported when the environment provides the necessary tooling.
- `reports/benchmarks/latest.json` records truthful provenance fields for the executed path, including whether the native module was loaded, whether the timing path was `source-tree-shim` or built/native, and why a native path was unavailable when the run stayed on the shim.
- The report schema remains compatible with the compile-path and module-boundary/regression suites; this task extends provenance detail instead of replacing existing workload-family summaries.
- A smoke or unit test regenerates the report and validates both the default shim-path behavior and the environment-gated native-path handling without requiring `maturin` to be installed in every run.

## Constraints
- Do not fabricate native timings or claim performance wins because a built path exists; missing native tooling must stay explicit in the report or test expectations.
- Keep the task focused on benchmark adapter provenance and execution-mode honesty, not on broad engine implementation or new workload families.
- Preserve compatibility with the exact-baseline metadata from `RBR-0009`, the native import smoke contract from `RBR-0010`, and the benchmark families added in `RBR-0012` and `RBR-0015`.

## Notes
- Use `docs/benchmarks/plan.md` as the benchmark contract, especially the environment/provenance guidance and the requirement to keep benchmark claims honest.
- Build on `RBR-0010` and `RBR-0015`; this task exists because the repo already has a verified built import smoke path, but the published benchmark report still reflects only the source-tree shim.
