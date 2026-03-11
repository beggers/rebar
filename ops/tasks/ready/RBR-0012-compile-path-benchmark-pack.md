# RBR-0012: Expand the benchmark harness into a compile-path suite

Status: ready
Owner: implementation
Created: 2026-03-11

## Goal
- Grow the Phase 0 benchmark scaffold into the first Phase 1 compile-path benchmark suite with representative workload buckets, cache-state labeling, and environment metadata.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/compile_matrix.json`
- `tests/benchmarks/test_compile_benchmark_matrix.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark runner can execute a compile-oriented workload matrix with at least cold and warm cache modes and publish per-workload timing records for CPython plus honest placeholder status for `rebar` where timing is not yet meaningful.
- The workload matrix includes representative parser buckets tied to `docs/spec/syntax-scope.md`, such as a tiny literal, a grouped/class pattern, and a heavier parser-stress case; include mirrored `bytes` coverage where it materially changes the compile path.
- `reports/benchmarks/latest.json` captures summary timing fields, environment metadata, cache mode labels, and baseline provenance in the scorecard shape defined by `docs/benchmarks/plan.md`.
- A smoke or unit test regenerates the compile-matrix benchmark report and validates the expanded scorecard structure.

## Constraints
- Keep this task on Phase 1 compile-path benchmarking only; do not add module-boundary import/search/match benchmarks yet.
- Do not fabricate `rebar` benchmark wins or ratios when the implementation side is still scaffold-only.
- Preserve compatibility with the exact-baseline metadata work from `RBR-0009`; the benchmark and correctness reports should stay schema-aligned where they record interpreter provenance.

## Notes
- Use `docs/benchmarks/plan.md` as the primary task spec, especially the Phase 1 compile-path suite guidance.
- Build on `RBR-0008` and `RBR-0009`; this task should extend the runner and workload corpus, not replace the Phase 0 smoke path.
- Keep the workload corpus small enough for one implementation-agent run and a fast local verification loop.
