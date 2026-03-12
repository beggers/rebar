# Backlog

## Current Milestone
Milestone 2: finish benchmark-provenance hardening plus the exported-symbol/pattern scorecards, then roll directly into the first honest-behavior slice for literal-only matching, compile-cache/purge observability, `escape()` parity, and the first literal-only collection/replacement helpers on top of the landed Phase 1 parser conformance and compile-path benchmark packs, verified native-extension smoke path, helper-surface scaffold, exported-symbol scaffold, compiled-pattern scaffold, exact CPython baseline metadata, the Phase 2 public-API correctness scorecard, the first Phase 3 match-behavior smoke pack, and the new regression/stability benchmark pack.

## Ordered Work
1. Land `RBR-0020` to teach the benchmark harness to report source-tree-shim versus built-native timing provenance so measurement paths stay aligned with the validated `rebar._rebar` smoke route.
2. Land `RBR-0021` to expand correctness coverage across exported flags/constants and public helper types now that the symbol surface has landed.
3. Land `RBR-0022` to expand correctness coverage across compiled `Pattern` scaffold attributes and method placeholders now that `compile()` returns a concrete scaffold object.
4. Land `RBR-0023` to implement a tiny literal-only `compile`/`search`/`match`/`fullmatch` path plus a concrete `Match` scaffold so the first match-behavior pack can start accumulating real passes instead of only honest unimplemented results.
5. Land `RBR-0024` to make successful literal-only `compile()` results observable through cache hits and `purge()` resets so public cache behavior and benchmark cache modes stop being placeholder-only.
6. Land `RBR-0025` to turn `escape()` into a real CPython-compatible helper for both `str` and `bytes` so the module surface gains at least one fully implemented public helper without waiting for the general engine.
7. Land `RBR-0026` to extend the benchmark harness with precompiled-pattern helper workloads once `Pattern` objects and a bounded literal-only path exist.
8. Land `RBR-0027` to extend the correctness harness into a module-workflow pack that covers literal-only compile/search flows, cache/purge observations, and `escape()` parity.
9. Land `RBR-0028` to implement literal-only `split`/`findall`/`finditer` behavior on both module and `Pattern` surfaces once the first `Match` scaffold exists.
10. Land `RBR-0029` to implement literal-only `sub`/`subn` behavior with plain replacement payloads before broad replacement-template compatibility work begins.

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
- With `RBR-0019` landed, keep the front of Milestone 2 on `RBR-0020` through `RBR-0022` so the new symbol and `Pattern` surfaces reach benchmark/correctness reporting before the honest-behavior slice.
- Treat exported-symbol placeholder work as complete until `RBR-0021` says otherwise; do not reopen more import-shape scaffolding ahead of the compiled-pattern and provenance tasks.
- Once `RBR-0014` lands the Phase 2 public-API scorecard, keep Milestone 2 focused on module-boundary benchmarking and concrete post-scaffold correctness instead of continuing to treat public-API harness setup as the primary open item.
- Queue a benchmark-provenance follow-on behind the first module-boundary suite so routine reports converge toward the validated built-native import path instead of remaining permanently source-tree-shim only.
- Queue correctness follow-ons immediately behind exported-symbol and compiled-pattern scaffolds so newly landed surface area reaches the published scorecard quickly instead of living only in narrow unit tests.
- Once the regression/stability benchmark pack lands, stop treating it as an open milestone gate and retarget the front of the queue to exported-symbol scaffolding, pattern scaffolding, and benchmark-provenance hardening.
- Once placeholder-only import and pattern scaffolds are queued, bias the next task slice toward narrow honest behavior (`literal` matching, cache/purge visibility, and `escape()` parity) instead of adding more placeholder-only surface area.
- Queue benchmark and correctness follow-ons directly behind those honest-behavior tasks so new observable behavior reaches the published scorecards quickly rather than living only in unit tests.
- Keep at least one bounded literal-only helper slice queued behind `RBR-0027` so the worker can roll from the first match/cache/escape wins into collection and replacement helpers without another supervisor-only queue rewrite.
