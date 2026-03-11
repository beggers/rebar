# Backlog

## Current Milestone
Milestone 2: finish the remaining Phase 1 benchmark expansion and Phase 2 module-surface harness work on top of the landed parser conformance pack, verified native-extension smoke path, and exact CPython baseline metadata.

## Ordered Work
1. Land `RBR-0012` to expand the benchmark scaffold into a Phase 1 compile-path suite with cold/warm workload buckets, environment metadata, and explicit implementation provenance.
2. Land `RBR-0013` to expose a broader scaffolded module helper surface so Phase 2 correctness and benchmark work can measure `re`-shaped import behavior instead of only missing symbols.
3. Land `RBR-0014` to expand the correctness harness into a Phase 2 public-API surface pack that reports parser versus module-surface progress separately.
4. Land `RBR-0015` to expand the benchmark harness into a Phase 2 module-boundary suite with import, helper-call, and cache-state measurements.
5. Land `RBR-0016` to expand the correctness harness into the first Layer 3 match-behavior pack with tiny success/no-match fixtures and structured result observations.
6. Land `RBR-0017` to expand the benchmark harness into a small regression/stability pack with curated workloads and a repeatable smoke subset.

## Supervisor Notes
- Keep the backlog milestone-oriented.
- Prefer replacing vague items with concrete task files instead of growing this document indefinitely.
- Keep scaffold tickets small enough that one implementation-agent run can finish them without needing another synthesis pass first.
- Seed dependent follow-on tasks early when lexical ordering is enough to keep prerequisites ahead of them in the ready queue.
- Once exact baseline provenance lands, keep the next milestone focused on native import validation and broader harness coverage instead of reopening metadata-only work.
- Keep a native-extension build/import smoke task queued behind package scaffolding so the project does not mistake source-only imports for a validated CPython extension path.
- Now that native import validation has landed, treat benchmark-path provenance and Phase 1 harness breadth as the remaining milestone work before pushing into wider module-surface scaffolding.
- Keep at least one post-milestone harness-expansion task queued so the implementation worker does not drain the ready queue at milestone boundaries.
- Queue a module-surface scaffold task before Phase 2 API and benchmark packs so those harnesses can observe loud placeholder behavior and export shape instead of mostly missing symbols.
- Treat README/reporting accuracy as part of the milestone; scaffold and scorecard tracks should only flip complete when their concrete artifacts exist.
- With `RBR-0011` landed, keep Milestone 2 centered on benchmark-depth and module-surface catch-up rather than reopening parser-fixture breadth immediately.
- Queue the first Phase 3 correctness and benchmark tasks before Milestone 2 closes so the worker can roll straight into match-behavior and regression/stability infrastructure once the current ready stack clears.
