# RBR-0184: Publish a strict built-native full-suite benchmark sidecar

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Publish the already-tracked combined benchmark suite through a real built `rebar._rebar` path as a sidecar artifact so native-path measurement no longer stops at the six-workload smoke report.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `tests/benchmarks/test_built_native_full_suite_benchmarks.py`
- `reports/benchmarks/native_full.json`

## Acceptance Criteria
- The benchmark harness supports a strict built-native full-suite mode that runs the existing combined published workload set through a built native wheel without silently falling back to the source-tree shim.
- `reports/benchmarks/native_full.json` is checked in from a real built-native run, preserves the combined-suite schema used by the tracked benchmark artifacts, and records built-native provenance such as `adapter_mode_requested`, `adapter_mode_resolved`, `build_mode`, `timing_path`, and native-module load state as `built-native`.
- The sidecar report keeps the same honest known-gap behavior as the published suite: workloads still unsupported by `rebar` remain explicit `unimplemented` rows instead of disappearing from the report.
- Direct test coverage pins both the strict no-fallback contract and the shape/provenance of the sidecar report while leaving `reports/benchmarks/latest.json` as the source-tree-shim-backed primary publication artifact.

## Constraints
- Keep this task scoped to benchmark-path publication and provenance; do not broaden regex support, change the primary `reports/benchmarks/latest.json` contract, or remove `reports/benchmarks/native_smoke.json`.
- If the native wheel cannot be built or loaded, the strict full-suite path must fail loudly rather than degrade to shim timings.
- Reuse the existing combined published workload set instead of inventing a second benchmark family for the same behaviors.

## Notes
- Build on `RBR-0049`, `RBR-0174`, and the existing built-native provisioning path in `python/rebar_harness/benchmarks.py`.
- This task exists so the persistent shim-only full-suite publication risk gets a bounded follow-on without changing the landing-page contract prematurely.
