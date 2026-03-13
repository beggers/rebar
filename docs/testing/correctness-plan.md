# Correctness Harness Plan

## Purpose

This document defines how `rebar` will prove correctness against CPython before optimization work begins. It turns the public-module contract in [`docs/spec/drop-in-re-compatibility.md`](../spec/drop-in-re-compatibility.md) and the parser boundary in [`docs/spec/syntax-scope.md`](../spec/syntax-scope.md) into an incremental test-harness plan that an implementation agent can build without large manual curation up front.

The goal is not just "tests exist." The goal is a repeatable differential harness that can answer:

- Does `rebar` accept and reject the same pattern and flag combinations as CPython?
- Does it expose the same observable `re` module behavior for successful and failing calls?
- Can the project publish a stable correctness scorecard that shows current compatibility coverage and failures over time?

## Reference Boundary

- Initial baseline: CPython `3.12.x`, matching the parser target in [`docs/spec/syntax-scope.md`](../spec/syntax-scope.md).
- Initial assumption: the first harness can compare against one pinned `3.12.x` interpreter while the prose spec still refers to the `3.12.x` family.
- Required follow-up: if differential runs expose patch-level parser or diagnostic drift inside `3.12.x`, pin the exact tested patch release in harness configuration and scorecard metadata instead of averaging behavior.
- Out of scope for the first correctness harness: proving behavior across multiple Python versions at once.

## Guiding Rules

- Correctness must be proven at the Python-visible `re` boundary, not only inside Rust parser internals.
- Parser correctness and matcher/runtime correctness should be tracked separately so parser progress is visible before the full engine is complete.
- Differential tests against CPython should be preferred over hand-maintained expected outputs whenever practical.
- Fixtures should start small and additive. The repo should not require a massive manually curated corpus before the first useful harness run.
- `str` and `bytes` behavior must be exercised independently because the contracts differ in user-visible ways.
- Diagnostics are part of correctness. The harness should capture exception type, warning category, and stable message shape where user code can observe them.

## Harness Layers

The correctness harness should grow in four layers. Later implementation tasks can ship these layers incrementally.

### Layer 1: Parser Acceptance And Diagnostics

This layer answers whether `compile()` accepts or rejects the same pattern and flag combinations as CPython.

Checks:

- compile success versus failure
- exception type on failure
- warning category, count, and trigger point where applicable
- stable diagnostic fields that user code can inspect, such as the error message shape and position metadata if exposed
- parser-derived metadata on success, such as pattern text, flags, groups, and groupindex

Primary use:

- Validate the parser milestone before matching semantics are complete.

### Layer 2: Pattern Object Parity

This layer checks user-visible behavior of compiled patterns without requiring broad match-engine completeness.

Checks:

- object type and repr shape once those surfaces exist
- `.pattern`, `.flags`, `.groups`, and `.groupindex`
- method argument handling and early validation for `search`, `match`, `fullmatch`, `split`, `findall`, `finditer`, `sub`, and `subn`
- cache and purge effects that are visible through ordinary `re` usage

Primary use:

- Catch module-surface regressions that a parser-only harness would miss.

### Layer 3: Match Result Parity

This layer checks observable behavior for successful and unsuccessful matches.

Checks:

- match truthiness
- `group()`, `groups()`, `groupdict()`, and indexing behavior
- `span()`, `start()`, `end()`, `pos`, `endpos`, `lastindex`, and `lastgroup`
- string-versus-bytes result types
- iterator result ordering and exhaustion behavior

Primary use:

- Prove that parser decisions and execution semantics combine into the expected Python-visible results.

### Layer 4: Module Workflow Parity

This layer checks end-to-end `re` module behavior across common workflows.

Checks:

- module-level helpers such as `compile`, `search`, `match`, `fullmatch`, `split`, `findall`, `finditer`, `sub`, `subn`, `escape`, and `purge`
- repeated-call behavior where caching changes observable outcomes or performance-sensitive code paths
- interactions between pattern compilation, flags, replacement handling, warnings, and module-level convenience entry points

Primary use:

- Confirm that `rebar` is converging on a real drop-in `re` replacement rather than an isolated parser.

## Fixture Sources

The harness should combine generated cases, curated regression fixtures, and imported upstream references.

### Differential Fixture Generators

These should be the default source of early coverage because they scale without large manual maintenance.

Sources:

- construct-family generators derived from [`docs/spec/syntax-scope.md`](../spec/syntax-scope.md)
- compact systematic feature manifests that expand one landed slice into deterministic numbered-versus-named, module-versus-compiled, and present-versus-absent matrices
- flag-combination matrices
- `str`/`bytes` mirrored cases
- invalid-pattern mutators that intentionally create malformed escapes, repeats, groups, backreferences, and inline-flag placements

Benefits:

- fast expansion of parser coverage
- broader landed-slice regression evidence without hand-writing one fixture record per obvious matrix variant
- explicit tie-back to the syntax scope document
- easy regeneration when the harness shape changes

### Curated Regression Fixtures

These should capture behaviors that generators handle poorly.

Sources:

- bugs found during implementation
- CPython quirks discovered through differential runs
- edge cases involving diagnostics, warning timing, lookbehind width checks, duplicate names, or bytes-only restrictions

Format guidance:

- prefer small data files with one case per record
- store the input shape and a short reason label
- avoid storing full expected outputs when CPython can remain the oracle

### Upstream Reference Material

These sources should seed fixtures where licensing and practicality allow.

Candidate inputs:

- CPython `Lib/test/test_re.py` scenarios translated into harness-friendly case records
- CPython documentation examples that exercise public `re` behavior
- a small set of compatibility smoke cases copied from project docs/spec prose

Constraint:

- imported upstream tests should be normalized into `rebar`'s fixture format instead of embedding the entire upstream test harness.

## Differential Testing Strategy

The primary oracle should be a baseline CPython interpreter and standard-library `re`.

For each case, the harness should execute the same operation against:

1. baseline CPython `re`
2. `rebar` exposed through the intended CPython-facing module surface

The harness should compare structured observations rather than raw stdout.

Recommended observation shape:

- operation kind, such as `compile`, `pattern.search`, or `module.findall`
- input payload: pattern, flags, search text, replacement text, and text model
- outcome class: success, exception, warning plus success, or warning plus exception
- normalized result payload for successful calls
- normalized diagnostic payload for failures and warnings

Normalization rules should be explicit and conservative:

- compare exact values where stability is expected, such as spans, flags, group mappings, and return types
- compare exception and warning classes exactly
- compare diagnostic text with a stable normalization pass only when exact wording may vary by incidental formatting; any normalization rule must be documented and kept narrow
- never normalize away semantic differences just to make the score look better

## Parser-Specific Assertions

Parser correctness needs dedicated assertions because it is the first milestone and because not all module behavior depends on a fully implemented matcher.

Parser assertions should include:

- compile accept/reject parity
- parsed flag parity, including inline and scoped flags
- group count and group-name mapping parity
- validation parity for backreferences, conditionals, and malformed constructs
- lookbehind width-check parity
- warning parity for ambiguous or deprecated syntax where CPython emits warnings at compile time

Parser results should be reportable even if later match execution is still partially stubbed.

## Module-Level Compatibility Assertions

Public `re` compatibility still has to be defined before the engine is complete, so the harness should stage module checks by readiness.

Early module assertions:

- function presence and import shape
- argument parsing and exception timing
- return-type shape for operations already implemented
- cache visibility for `compile`/`purge` flows once cache behavior exists

Later module assertions:

- full result parity for `search`, `match`, `fullmatch`, `findall`, `finditer`, `split`, `sub`, and `subn`
- replacement-template behavior for `sub` and `subn`, which is deferred from the parser syntax scope but still part of public `re` correctness
- iterator and match-object parity under repeated access

This split keeps parser progress measurable without pretending that module parity is optional.

## Incremental Delivery Path

The harness should be built in small implementation tasks that leave behind runnable artifacts at each step.

### Phase 0: Harness Skeleton

Deliver:

- a test runner entry point
- a fixture format
- a CPython oracle adapter
- a placeholder `rebar` adapter
- a minimal scorecard writer that can publish "not implemented" counters without faking passing coverage

Exit criteria:

- one or more compile smoke cases run through the differential pipeline end to end

### Phase 1: Parser Conformance Pack

Deliver:

- generated parser fixture families tied to syntax-scope construct groups
- compile success/failure comparison
- warning and exception capture
- parser metadata comparison on successful compile

Exit criteria:

- the harness can publish parser acceptance totals and failure categories in `reports/correctness/latest.json`

### Phase 2: Public API Surface Pack

Deliver:

- module import and exported-surface checks
- pattern attribute checks
- early method argument-validation checks
- cache/purge smoke tests

Exit criteria:

- scorecard includes module-surface coverage and can distinguish parser progress from API-surface progress

### Phase 3: Match Behavior Pack

Deliver:

- match-result fixtures for core methods
- `str` and `bytes` result parity checks
- iterator and group-access comparisons

Exit criteria:

- scorecard includes match-result pass/fail counts for implemented APIs

### Phase 4: Regression And Coverage Expansion

Deliver:

- curated regression corpus from discovered bugs
- imported upstream scenarios where useful
- scorecard trend stability and richer failure bucketing

Exit criteria:

- new correctness bugs land as permanent regression fixtures instead of one-off notes

## Suggested Fixture Record Shape

The exact file format can be chosen later, but each case should be able to represent:

- case id
- layer, such as `parser`, `pattern_api`, `match_api`, or `module_api`
- operation
- pattern
- flags
- text model: `str` or `bytes`
- input text if the operation needs it
- replacement text if the operation needs it
- expected capability gate if the case is known to be deferred
- notes or source tag, such as `generated`, `cpython_import`, or `regression`

This keeps fixtures reusable across both CPython and `rebar` adapters.

## Correctness Scorecard Shape

`reports/correctness/latest.json` should publish a stable top-level shape even while coverage is still growing.

Recommended top-level fields:

- `schema_version`: integer version for future scorecard evolution
- `generated_at`: UTC timestamp for the report
- `baseline`: object describing the oracle interpreter and target family
- `implementation`: object describing the tested `rebar` revision or build
- `summary`: object with aggregate totals and pass rates
- `layers`: object keyed by harness layer name with per-layer totals
- `capabilities`: object keyed by major compatibility area
- `failures`: array of representative failing cases or failure buckets
- `waived`: array of explicitly deferred or temporarily accepted gaps, if any
- `artifacts`: object pointing to optional detailed outputs, such as junit-style test logs or fixture manifests

Recommended contents for selected fields:

- `baseline`: `python_implementation`, `python_version`, `python_version_family`, and `exact_re_module` metadata if needed
- `implementation`: `git_commit`, `module_name`, `build_mode`, and optional Rust crate/package version
- `summary`: `total_cases`, `passed`, `failed`, `errored`, `skipped`, `pass_rate`, and `known_gap_count`
- `layers`: one object each for `parser`, `pattern_api`, `match_api`, and `module_api`, each with totals plus readiness notes
- `capabilities`: counters for areas such as `compile_acceptance`, `diagnostics`, `flags`, `group_metadata`, `bytes_behavior`, `module_surface`, `match_results`, and `replacement_templates`
- `failures`: each entry should include at least `case_id`, `layer`, `operation`, `failure_kind`, and a short normalized diff summary
- `waived`: each entry should include a reason, linked task or issue reference if available, and an expiry/revisit note

The scorecard should favor stable machine-readable counts over prose summaries so the README and future dashboards can consume it directly.

## Practical Constraints For The First Harness

- Do not block the first useful harness on building a perfect generator for every regex construct family.
- Do not require the first implementation tasks to vendor all of CPython's `re` tests.
- Do not hide unsupported areas by silently skipping them; publish them as deferred or not yet implemented in the scorecard.
- Prefer pure-Python harness code around the CPython extension boundary unless Rust-side hooks are required for observability.
- Keep per-case outputs structured so failures can become regression fixtures with minimal manual rewriting.

## Follow-Up Implementation Tasks This Plan Enables

- scaffold the correctness harness runner and scorecard writer
- define the fixture schema and adapter interface for CPython versus `rebar`
- generate the first parser acceptance corpus from the syntax-scope construct map
- import a small curated subset of CPython `re` tests into the fixture format
- add module-surface smoke tests for `compile`, `search`, `match`, and `purge`
- wire README/reporting consumption to the published correctness scorecard once reports exist

## Open Questions To Settle During Implementation

- Which exact CPython `3.12.x` patch release will be the first pinned oracle in CI and local runs?
- How much diagnostic text can be compared exactly before patch-level drift requires narrowly documented normalization?
- Which public cache behaviors should be treated as strict compatibility requirements versus informational implementation detail?
- At what point should replacement-template parsing move from deferred module coverage into required scorecard coverage?

Those questions should be answered by executable harness behavior and follow-up tasking, not by leaving the plan ambiguous.
