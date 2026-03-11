# RBR-0012: Expand the benchmark harness into a compile-path suite

Status: done
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
- `reports/benchmarks/latest.json` captures summary timing fields, environment metadata, cache mode labels, baseline provenance, and explicit implementation provenance, including whether the measured `rebar` path used the source-tree shim or a loaded native module.
- A smoke or unit test regenerates the compile-matrix benchmark report and validates the expanded scorecard structure.

## Constraints
- Keep this task on Phase 1 compile-path benchmarking only; do not add module-boundary import/search/match benchmarks yet.
- Do not fabricate `rebar` benchmark wins or ratios when the implementation side is still scaffold-only.
- Preserve compatibility with the exact-baseline metadata work from `RBR-0009`; the benchmark and correctness reports should stay schema-aligned where they record interpreter provenance.

## Notes
- Use `docs/benchmarks/plan.md` as the primary task spec, especially the Phase 1 compile-path suite guidance.
- Build on `RBR-0008`, `RBR-0009`, and the native-load truth from `RBR-0010`; this task should extend the runner and workload corpus, not replace the Phase 0 smoke path.
- The suite does not need to benchmark a built wheel yet, but it must keep the report honest about whether the timing path is a source-tree shim or a native-loaded module.
- Keep the workload corpus small enough for one implementation-agent run and a fast local verification loop.

## Completion Notes
- Expanded `python/rebar_harness/benchmarks.py` into a Phase 1 compile-matrix runner with cache-mode summaries, explicit implementation provenance, and richer per-workload reporting while keeping the exact CPython baseline metadata shape aligned with the correctness harness.
- Added `benchmarks/workloads/compile_matrix.json` with six representative parser workloads covering cold, warm, and purged cache modes plus mirrored `bytes` cases tied to the syntax-scope construct families.
- Added `tests/benchmarks/test_compile_benchmark_matrix.py`, kept the existing smoke benchmark path working, and regenerated `reports/benchmarks/latest.json` from the new default compile matrix.
- Follow-up note for supervisor: once `RBR-0013` lands broader module helpers, the next benchmark expansion can reuse the new scorecard/cache-mode structure for `RBR-0015` module-boundary timings instead of inventing a separate schema.
