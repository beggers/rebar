# RBR-0026: Add precompiled pattern-boundary benchmarks

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the benchmark harness so it can measure precompiled `Pattern` helper overhead separately from module-level helper overhead once the bounded literal-only path exists.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/pattern_boundary.json`
- `tests/benchmarks/test_pattern_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark runner can execute a pattern-boundary workload manifest alongside the existing compile-path, module-boundary, and regression manifests without breaking the current report schema.
- The new workload pack includes a small set of precompiled `Pattern.search`, `Pattern.match`, and `Pattern.fullmatch` cases over tiny literal-only `str` and `bytes` inputs, with cache/provenance labeling that keeps the measurement about call-boundary cost rather than throughput claims.
- `reports/benchmarks/latest.json` records the new workloads distinctly enough that precompiled-pattern overhead is visible separately from module-level helper timing, while still keeping unsupported operations honest when the bounded behavior slice does not cover them yet.
- A smoke or unit test regenerates the expanded benchmark report end to end and validates the updated workload/report structure.

## Constraints
- Keep this task on tiny pattern-boundary call overhead only; do not introduce large-haystack throughput claims or broad regex-engine benchmarks.
- Preserve compatibility with the provenance work from `RBR-0020` and the literal-only honesty contract from `RBR-0023`/`RBR-0024`.
- Do not fabricate benchmark wins for unsupported pattern methods or execution modes.

## Notes
- Use `docs/benchmarks/plan.md` as the primary task spec, especially the Phase 2 guidance that distinguishes module-level helpers from precompiled pattern calls.
