# Backlog

## Current Milestone
Milestone 2: build on the landed exported-symbol and compiled-pattern scaffolds, the first literal-only `compile`/`search`/`match`/`fullmatch` behavior slice, observable compile-cache/purge behavior, local `escape()` parity, the module-workflow correctness pack, the precompiled pattern-boundary benchmark pack, the first literal-only collection and replacement helpers, their published correctness and benchmark packs, the landed literal-only API-level `IGNORECASE` slice plus its published correctness and benchmark follow-ons, the landed bounded inline-flag, lookbehind, character-class `IGNORECASE`, possessive-quantifier, and atomic-group compile parity slices, the landed compile-benchmark catch-up that now measures the supported parser cases honestly, the landed Rust-backed collection/replacement boundary, the landed single-dot wildcard workflow slice plus inline-flag, bytes-`LOCALE`, and grouped-literal replacement-template workflow parity, and then a built-native benchmark smoke follow-on plus grouped-match/capture, named-group, named-template, and named-backreference expansion so the queue stays ahead of the current publication frontier.

## Ordered Work
1. Land `RBR-0048` to catch benchmark coverage up with the now fully passing published workflow surface instead of leaving the benchmark report one milestone behind it.
2. Land `RBR-0049` to publish a built-native benchmark smoke report so benchmark reporting stays anchored to the verified native import path instead of the source-tree shim alone.
3. Land `RBR-0050` to publish a grouped-match/capture correctness pack so the next compatibility frontier is explicit in the scorecard before the queue broadens into more syntax.
4. Land `RBR-0051` to convert the first grouped-literal numbered-capture match cases from published gaps into real Rust-backed behavior.
5. Land `RBR-0052` to publish a named-group correctness pack so the ready queue keeps the next grouping frontier explicit after the first numbered-capture slice lands.
6. Land `RBR-0053` to convert the first named-group literal metadata cases from published gaps into real Rust-backed behavior instead of stopping at publication-only coverage.
7. Land `RBR-0054` to publish a named-group replacement-template correctness pack so the queue extends past named-group metadata into the next bounded workflow frontier.
8. Land `RBR-0055` to convert the first named-group replacement-template cases from published gaps into real Rust-backed behavior instead of stopping at metadata-only named-group support.
9. Land `RBR-0056` to publish a named-backreference correctness pack so the queue extends beyond named-group replacement into the next bounded grouped-reference frontier.
10. Land `RBR-0057` to convert the first named-backreference literal cases from published gaps into real Rust-backed behavior instead of stopping at publication-only coverage.

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
- With `RBR-0047` landed on top of `RBR-0046`, `RBR-0045`, `RBR-0044`, `RBR-0043`, and `RBR-0042A`, treat the published correctness surface as fully passing for the current eight-manifest pack; keep the front of Milestone 2 on `RBR-0048` and `RBR-0049` so benchmark reporting catches up before the corpus broadens again.
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
- After `RBR-0049`, expand the published correctness surface with grouped-match/capture coverage before reopening broader syntax or performance work; the next concrete work after the current module-workflow gaps is a bounded grouped/capture scorecard plus a numbered-capture execution slice.
- After `RBR-0051`, keep the ready queue extending into named-group correctness publication before reopening broader syntax or benchmark expansion, so the worker does not stop at grouped numbered captures.
- After `RBR-0052`, keep the ready queue extending into bounded named-group parity so the worker does not stop at publication-only named-group coverage.
- After `RBR-0053`, keep the ready queue extending into named-group replacement-template publication and bounded parity so the worker does not stop at metadata-only named-group workflows.
- After `RBR-0055`, keep the ready queue extending into named-backreference correctness publication and bounded parity so the worker does not stop at named-group replacement-template support.
- After `RBR-0035`, retarget the queue to bounded parser compile-parity tasks because the remaining currently published correctness gaps then sat in parser-matrix compile cases rather than module-surface failures.
- Keep compile-benchmark catch-up queued immediately behind the parser compile-parity tasks so the compile-path report starts measuring new parser support instead of lagging one milestone behind the correctness surface.
- Treat `USER-ASK-2` as durable architectural direction: new compatibility behavior belongs in Rust, while `python/rebar/__init__.py` should stay limited to symbol export, object wrappers, argument normalization, cache plumbing, and FFI calls.
- If a ready task is already satisfied as a side effect of earlier landed work, retire it directly in the queue and advance the milestone front instead of burning a no-op worker cycle.
- Keep a built-native benchmark smoke task queued behind the current milestone so benchmark publication paths stay anchored to the verified native import path while the main full-suite report still uses the source-tree shim.
