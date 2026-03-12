# Backlog

## Current Milestone
Milestone 2: build on the landed exported-symbol and compiled-pattern scaffolds, the first literal-only `compile`/`search`/`match`/`fullmatch` behavior slice, observable compile-cache/purge behavior, local `escape()` parity, the module-workflow correctness pack, the precompiled pattern-boundary benchmark pack, the first literal-only collection and replacement helpers, their published correctness pack, the matching collection/replacement benchmark pack, and the landed literal-only API-level `IGNORECASE` slice with its queued correctness/benchmark follow-ons, targeted metadata-parity cleanup for the remaining exported-helper and compiled-pattern correctness failures, and finally the bounded parser diagnostic/acceptance tasks needed to finish the currently published parser-matrix debt plus compile-benchmark catch-up.

## Ordered Work
1. Land `RBR-0033` to publish correctness coverage for the landed literal-only `IGNORECASE` slice so flag-sensitive behavior reaches the scorecard immediately.
2. Land `RBR-0034` to benchmark the bounded literal-only flag-sensitive helper paths so the benchmark suite tracks their call-boundary cost separately from later engine work.
3. Land `RBR-0035` to fix the remaining exported-helper metadata and constructor-guard correctness failures for `RegexFlag`, `Pattern`, and `Match`.
4. Land `RBR-0036` to fix the remaining compiled-pattern metadata correctness failures for the currently supported literal-only `Pattern` slice.
5. Land `RBR-0037` to turn the already-published compile-time parser error/warning cases into real CPython-shaped diagnostics so the next visible correctness debt comes off the parser pack instead of adding new surface area first.
6. Land `RBR-0038` to implement bounded inline-flag compile parity for the remaining published parser-matrix success cases and keep the new diagnostic cases aligned.
7. Land `RBR-0039` to implement bounded lookbehind compile parity for the remaining published fixed-width success and variable-width error cases.
8. Land `RBR-0040` to implement the published character-class plus API-level `IGNORECASE` compile case without broadening into general regex execution.
9. Land `RBR-0041` to implement compile-only acceptance for the remaining published possessive-quantifier and atomic-group parser cases.
10. Land `RBR-0042` to convert the compile-path benchmark pack from scaffold-only toward partial measurement as those published parser cases become real `rebar` compile successes.

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
- With `RBR-0032` landed, keep the front of Milestone 2 on `RBR-0033` through `RBR-0036` so the bounded literal-flag scorecards and metadata-parity cleanup stay contiguous instead of forcing another supervisor-only queue rewrite.
- Treat exported-symbol and compiled-pattern scaffold coverage as complete unless later behavior work exposes a real compatibility gap; do not reopen more import-shape or placeholder-only `Pattern` scaffolding ahead of the honest-behavior tasks.
- Once `RBR-0014` lands the Phase 2 public-API scorecard, keep Milestone 2 focused on module-boundary benchmarking and concrete post-scaffold correctness instead of continuing to treat public-API harness setup as the primary open item.
- Use the landed benchmark-provenance adapter modes in future workload expansions; do not let new benchmark packs regress to unlabeled source-versus-native execution paths.
- Queue correctness follow-ons immediately behind exported-symbol and compiled-pattern scaffolds so newly landed surface area reaches the published scorecard quickly instead of living only in narrow unit tests.
- Once the regression/stability benchmark pack lands, stop treating it as an open milestone gate and retarget the front of the queue to exported-symbol scaffolding, pattern scaffolding, and benchmark-provenance hardening.
- Keep README/reporting focused on explicit coverage and gap counts until correctness and benchmark reports cover enough real behavior that headline ratios or speedups would be representative.
- Once placeholder-only import and pattern scaffolds are queued, bias the next task slice toward narrow honest behavior (`literal` matching, cache/purge visibility, and `escape()` parity) instead of adding more placeholder-only surface area.
- Queue benchmark and correctness follow-ons directly behind those honest-behavior tasks so new observable behavior reaches the published scorecards quickly rather than living only in unit tests.
- Keep at least one bounded literal-only helper slice queued behind `RBR-0027` so the worker can roll from the first match/cache/escape/workflow wins into collection and replacement helpers without another supervisor-only queue rewrite.
- Keep collection/replacement scorecard follow-ons queued behind `RBR-0029` so newly implemented helper behavior reaches the published correctness and benchmark reports instead of living only in unit tests.
- After `RBR-0031`, queue bounded literal-flag work before broader parser or native-path performance pushes so the next behavior slice continues tightening real `re` compatibility instead of jumping to infrastructure-only work.
- After `RBR-0034`, queue targeted metadata-parity cleanup before broader parser or engine expansion so the current exported-helper and compiled-pattern correctness failures become explicit pass/fail work instead of lingering off-roadmap.
- After `RBR-0036`, retarget the queue to bounded parser compile-parity tasks because the remaining currently published correctness gaps then sit in parser-matrix compile cases rather than module-surface failures.
- Keep compile-benchmark catch-up queued immediately behind the parser compile-parity tasks so the compile-path report starts measuring new parser support instead of lagging one milestone behind the correctness surface.
