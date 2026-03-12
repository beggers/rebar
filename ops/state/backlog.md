# Backlog

## Current Milestone
Milestone 2: build on the landed exported-symbol and compiled-pattern scaffolds plus the first literal-only `compile`/`search`/`match`/`fullmatch` behavior slice and observable compile-cache/purge behavior by adding `escape()` parity, precompiled-pattern and module-workflow scorecard coverage, the first literal-only collection/replacement helpers, their follow-on correctness/benchmark packs, and then the next bounded literal-flag slice on top of the landed Phase 1 parser conformance and compile-path benchmark packs, verified native-extension smoke path, helper-surface scaffold, exact CPython baseline metadata, the Phase 2 public-API correctness scorecard, the first Phase 3 match-behavior smoke pack, the regression/stability benchmark pack, benchmark adapter/provenance reporting, and the pattern-object correctness pack.

## Ordered Work
1. Land `RBR-0025` to turn `escape()` into a real CPython-compatible helper for both `str` and `bytes` so the module surface gains at least one fully implemented public helper without waiting for the general engine.
2. Land `RBR-0026` to extend the benchmark harness with precompiled-pattern helper workloads now that `Pattern` objects and a bounded literal-only path exist.
3. Land `RBR-0027` to extend the correctness harness into a module-workflow pack that covers literal-only compile/search flows, cache/purge observations, and `escape()` parity.
4. Land `RBR-0028` to implement literal-only `split`/`findall`/`finditer` behavior on both module and `Pattern` surfaces now that the first `Match` scaffold exists.
5. Land `RBR-0029` to implement literal-only `sub`/`subn` behavior with plain replacement payloads before broad replacement-template compatibility work begins.
6. Land `RBR-0030` to publish correctness coverage for the first literal-only collection and replacement helpers as soon as `RBR-0028` and `RBR-0029` land.
7. Land `RBR-0031` to extend the benchmark harness with tiny collection/replacement boundary workloads once those helpers stop being placeholders.
8. Land `RBR-0032` to implement bounded literal-only `IGNORECASE` behavior for module and `Pattern` match helpers without broadening into non-literal regex parsing.
9. Land `RBR-0033` to publish correctness coverage for that literal-only `IGNORECASE` slice so flag-sensitive behavior reaches the scorecard immediately.
10. Land `RBR-0034` to benchmark the bounded literal-only flag-sensitive helper paths so the benchmark suite tracks their call-boundary cost separately from later engine work.

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
- With `RBR-0023` and `RBR-0024` landed, keep the front of Milestone 2 on `RBR-0025` through `RBR-0027` so the first literal-only match/cache slice is followed immediately by `escape()` parity and its benchmark/correctness follow-ons.
- Treat exported-symbol and compiled-pattern scaffold coverage as complete unless later behavior work exposes a real compatibility gap; do not reopen more import-shape or placeholder-only `Pattern` scaffolding ahead of the honest-behavior tasks.
- Once `RBR-0014` lands the Phase 2 public-API scorecard, keep Milestone 2 focused on module-boundary benchmarking and concrete post-scaffold correctness instead of continuing to treat public-API harness setup as the primary open item.
- Use the landed benchmark-provenance adapter modes in future workload expansions; do not let new benchmark packs regress to unlabeled source-versus-native execution paths.
- Queue correctness follow-ons immediately behind exported-symbol and compiled-pattern scaffolds so newly landed surface area reaches the published scorecard quickly instead of living only in narrow unit tests.
- Once the regression/stability benchmark pack lands, stop treating it as an open milestone gate and retarget the front of the queue to exported-symbol scaffolding, pattern scaffolding, and benchmark-provenance hardening.
- Keep README/reporting focused on explicit coverage and gap counts until correctness and benchmark reports cover enough real behavior that headline ratios or speedups would be representative.
- Once placeholder-only import and pattern scaffolds are queued, bias the next task slice toward narrow honest behavior (`literal` matching, cache/purge visibility, and `escape()` parity) instead of adding more placeholder-only surface area.
- Queue benchmark and correctness follow-ons directly behind those honest-behavior tasks so new observable behavior reaches the published scorecards quickly rather than living only in unit tests.
- Keep at least one bounded literal-only helper slice queued behind `RBR-0027` so the worker can roll from the first match/cache/escape wins into collection and replacement helpers without another supervisor-only queue rewrite.
- Keep collection/replacement scorecard follow-ons queued behind `RBR-0029` so newly implemented helper behavior reaches the published correctness and benchmark reports instead of living only in unit tests.
- After `RBR-0031`, queue bounded literal-flag work before broader parser or native-path performance pushes so the next behavior slice continues tightening real `re` compatibility instead of jumping to infrastructure-only work.
