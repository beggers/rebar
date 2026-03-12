# Backlog

## Current Milestone
Milestone 2: build on the landed exported-symbol and compiled-pattern scaffolds, the first literal-only `compile`/`search`/`match`/`fullmatch` behavior slice, observable compile-cache/purge behavior, local `escape()` parity, the module-workflow correctness pack, the precompiled pattern-boundary benchmark pack, the first literal-only collection and replacement helpers, their published correctness and benchmark packs, the landed literal-only API-level `IGNORECASE` slice plus its published correctness and benchmark follow-ons, the landed bounded inline-flag and lookbehind compile parity slices, the remaining Rust-boundary migration task needed to stop deepening Python semantics, the remaining bounded parser acceptance tasks needed to finish the currently published parser-matrix debt plus compile-benchmark catch-up, the queued module-workflow cleanup tasks for the remaining published replacement and flag-sensitive gaps, and then a built-native benchmark smoke follow-on so publication paths stay aligned with the verified native import path.

## Ordered Work
1. Land `RBR-0040` to implement the published character-class plus API-level `IGNORECASE` compile case without broadening into general regex execution.
2. Land `RBR-0041` to implement compile-only acceptance for the remaining published possessive-quantifier and atomic-group parser cases.
3. Land `RBR-0042` to convert the compile-path benchmark pack from scaffold-only toward partial measurement as those published parser cases become real `rebar` compile successes.
4. Land `RBR-0042A` to move the currently supported literal-only collection and replacement helpers behind the Rust extension boundary before more workflow breadth lands.
5. Land `RBR-0043` to add literal-only replacement-template and callable-replacement parity for the remaining module `sub()` workflow gaps that do not require grouped-pattern support.
6. Land `RBR-0044` to add a bounded single-dot non-literal workflow slice so the published `findall()` and `IGNORECASE search()` gaps for `a.c` stop reporting as `unimplemented`.
7. Land `RBR-0045` to carry the published inline `(?i)` literal compile win through the module workflow surface so `search()` stops lagging the parser slice.
8. Land `RBR-0046` to add the bounded bytes `LOCALE` literal search case so the remaining published bytes-only flag workflow is not left behind the parser and API-level flag work.
9. Land `RBR-0047` to add the narrow grouped-literal replacement-template slice needed for the last published `module.sub()` grouping-dependent gap.
10. Land `RBR-0048` to catch benchmark coverage up with those post-parser workflow wins instead of leaving the benchmark report one milestone behind the published correctness surface.
11. Land `RBR-0049` to publish a built-native benchmark smoke report so benchmark reporting stays anchored to the verified native import path instead of the source-tree shim alone.

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
- With `RBR-0039` landed, keep the front of Milestone 2 on `RBR-0040` through `RBR-0042A` so the remaining parser compile-parity cleanup stays contiguous with the newly Rust-backed compile/match slice and the remaining collection/replacement boundary migration lands before more workflow breadth.
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
- After `RBR-0042A`, keep the queue moving into the remaining published module-workflow `unimplemented` cases instead of broadening the corpus again immediately; the next concrete work is bounded replacement-variant, wildcard, inline-flag, `LOCALE`, and grouped-template cleanup.
- After `RBR-0035`, retarget the queue to bounded parser compile-parity tasks because the remaining currently published correctness gaps then sit in parser-matrix compile cases rather than module-surface failures.
- Keep compile-benchmark catch-up queued immediately behind the parser compile-parity tasks so the compile-path report starts measuring new parser support instead of lagging one milestone behind the correctness surface.
- Treat `USER-ASK-2` as durable architectural direction: new compatibility behavior belongs in Rust, while `python/rebar/__init__.py` should stay limited to symbol export, object wrappers, argument normalization, cache plumbing, and FFI calls.
- If a ready task is already satisfied as a side effect of earlier landed work, retire it directly in the queue and advance the milestone front instead of burning a no-op worker cycle.
- Keep a built-native benchmark smoke task queued behind the current milestone so benchmark publication paths stay anchored to the verified native import path while the main full-suite report still uses the source-tree shim.
