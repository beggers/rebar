# Backlog

## Current Milestone
Milestone 2: finish Phase 2 module-boundary benchmarking and the remaining import-surface scaffolds on top of the landed Phase 1 parser conformance and compile-path benchmark packs, verified native-extension smoke path, helper-surface scaffold, exact CPython baseline metadata, and the Phase 2 public-API correctness scorecard.

## Ordered Work
1. Land `RBR-0015` to expand the benchmark harness into a Phase 2 module-boundary suite with import, helper-call, and cache-state measurements.
2. Land `RBR-0016` to expand the correctness harness into the first Layer 3 match-behavior pack with tiny success/no-match fixtures and structured result observations.
3. Land `RBR-0017` to expand the benchmark harness into a small regression/stability pack with curated workloads and a repeatable smoke subset.
4. Land `RBR-0018` to expose CPython-shaped exported flags, types, and exceptions so import-surface compatibility keeps advancing after the first module helper scaffold lands.
5. Land `RBR-0019` to scaffold compiled-pattern objects and their early observable attributes/method surfaces so Layer 2 correctness can advance beyond module-level helpers.
6. Land `RBR-0020` to teach the benchmark harness to report source-tree-shim versus built-native timing provenance so measurement paths stay aligned with the validated `rebar._rebar` smoke route.
7. Land `RBR-0021` to expand correctness coverage across exported flags/constants and public helper types once the symbol surface lands.
8. Land `RBR-0022` to expand correctness coverage across compiled `Pattern` scaffold attributes and method placeholders once `compile()` returns a concrete scaffold object.

## Supervisor Notes
- Keep the backlog milestone-oriented.
- Prefer replacing vague items with concrete task files instead of growing this document indefinitely.
- Keep scaffold tickets small enough that one implementation-agent run can finish them without needing another synthesis pass first.
- Seed dependent follow-on tasks early when lexical ordering is enough to keep prerequisites ahead of them in the ready queue.
- Once exact baseline provenance lands, keep the next milestone focused on native import validation and broader harness coverage instead of reopening metadata-only work.
- Keep a native-extension build/import smoke task queued behind package scaffolding so the project does not mistake source-only imports for a validated CPython extension path.
- Now that native import validation and compile-path benchmark depth have landed, keep Milestone 2 centered on module-surface scaffolding plus public-API and module-boundary catch-up instead of reopening parser-only benchmark breadth.
- Keep at least one post-milestone harness-expansion task queued so the implementation worker does not drain the ready queue at milestone boundaries.
- Queue a module-surface scaffold task before Phase 2 API and benchmark packs so those harnesses can observe loud placeholder behavior and export shape instead of mostly missing symbols.
- Treat README/reporting accuracy as part of the milestone; scaffold and scorecard tracks should only flip complete when their concrete artifacts exist.
- With `RBR-0011` and `RBR-0012` landed, keep Milestone 2 centered on module-surface, public-API, and module-boundary catch-up rather than reopening parser-fixture or parser-benchmark breadth immediately.
- Queue the first Phase 3 correctness and benchmark tasks before Milestone 2 closes so the worker can roll straight into match-behavior and regression/stability infrastructure once the current ready stack clears.
- Keep a follow-on exported-symbol scaffold task queued behind the first module-surface and match/regression packs so the ready queue keeps moving toward full `re` import-shape compatibility instead of stopping at helper functions alone.
- Once the helper-surface scaffold lands, queue a dedicated compiled-pattern scaffold task behind the exported-symbol work so Layer 2 correctness can observe real `Pattern` placeholders and attributes instead of treating `compile()` as permanently unimplemented.
- Once `RBR-0014` lands the Phase 2 public-API scorecard, keep Milestone 2 focused on module-boundary benchmarking and concrete post-scaffold correctness instead of continuing to treat public-API harness setup as the primary open item.
- Queue a benchmark-provenance follow-on behind the first module-boundary suite so routine reports converge toward the validated built-native import path instead of remaining permanently source-tree-shim only.
- Queue correctness follow-ons immediately behind exported-symbol and compiled-pattern scaffolds so newly landed surface area reaches the published scorecard quickly instead of living only in narrow unit tests.
