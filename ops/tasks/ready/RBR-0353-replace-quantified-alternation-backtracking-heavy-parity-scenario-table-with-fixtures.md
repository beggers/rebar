# RBR-0353: Replace the quantified-alternation backtracking-heavy parity scenario table with published fixtures

Status: ready
Owner: architecture-implementation
Created: 2026-03-15

## Goal
- Simplify `tests/python/test_quantified_alternation_backtracking_heavy_parity.py` by driving its published compile/module/pattern cases from the existing quantified-alternation backtracking-heavy correctness fixture instead of a second private scenario table, while keeping the extra exhaustive branch-order parity checks in the smallest local form that still adds value.

## Deliverables
- `tests/python/test_quantified_alternation_backtracking_heavy_parity.py`

## Acceptance Criteria
- `tests/python/test_quantified_alternation_backtracking_heavy_parity.py` loads the published slice through `rebar_harness.correctness.load_fixture_manifest(...)` and `FixtureCase` from exactly `tests/conformance/fixtures/quantified_alternation_backtracking_heavy_workflows.py` instead of keeping file-local `Scenario` / `SCENARIOS` tables that restate the same patterns, lower-bound successes, repeated-branch successes, and `abccd` no-match observations already stored in that fixture.
- The refactored suite keeps one manifest-alignment assertion covering:
  - manifest id `quantified-alternation-backtracking-heavy-workflows`
  - the exact published case-id set from that fixture
  - the exact numbered and named pattern set published by that fixture:
    - `a(b|bc){1,2}d`
    - `a(?P<word>b|bc){1,2}d`
  - the published operation/helper distribution of two `compile` rows, two module `search` rows, and eight pattern `fullmatch` rows
- Compile metadata parity runs from the loaded compile cases and preserves the current coverage for repeated `compile()` identity plus `.pattern`, `.flags`, `.groups`, and `.groupindex`.
- Published success and no-match parity for module `search()` and compiled-`Pattern.fullmatch()` runs from the loaded fixture cases, preserving the current CPython checks for the exact published lower-bound, mixed-order, repeated-branch, and explicit `abccd` no-match rows rather than restating those texts in a second private table.
- Exhaustive branch-trace parity still covers every successful one- and two-repetition branch order for both numbered and named patterns on both module `search()` and compiled `Pattern.fullmatch()`, but any remaining local trace generator is derived only from the fixture-backed compile patterns plus the single short/long branch-text map instead of another file-local scenario table with duplicated group metadata and miss lists.
- The remaining local no-match parity outside the published fixture stays limited to the current shared zero-repetition and overlap-tail failures (`ad` / `abccd`, plus the search-wrapped forms) for both numbered and named patterns; do not broaden into wider counted ranges, open-ended repeats, conditionals, branch-local backreferences, or other quantified frontiers.
- The suite continues to preserve the current match-result parity depth for success cases, including numbered and named `.group(...)` access, span/start/end checks, `.groups(...)`, `.groupdict(...)`, `.string`, `.pos`, `.endpos`, `.lastindex`, `.lastgroup`, and compiled-pattern metadata parity.
- After the refactor lands, `tests/python/test_quantified_alternation_backtracking_heavy_parity.py` no longer contains file-local `Scenario` or `SCENARIOS` definitions, and any remaining local parity metadata is limited to the extra exhaustive trace generation that the published fixture does not express today.

## Constraints
- Keep this task scoped to `tests/python/test_quantified_alternation_backtracking_heavy_parity.py`; do not change Rust code, `python/rebar/` runtime behavior, correctness fixture contents, benchmark workloads, or published reports to complete it.
- Reuse ordinary pytest parameterization plus the existing fixture-loading path already used by `tests/python/test_quantified_alternation_parity_suite.py` and `tests/python/test_conditional_group_exists_parity_suite.py`; do not add another manifest schema, generator, or family-specific loader layer.
- Keep backend selection and cache purging on the shared `tests/python/conftest.py` path instead of introducing another native-module gate or file-local backend wrapper.

## Notes
- `tests/python/test_quantified_alternation_backtracking_heavy_parity.py` is still a 214-line holdout from the earlier parity frontier work: it duplicates the same two quantified overlapping-branch patterns and most of the same visible success/no-match texts already published in `tests/conformance/fixtures/quantified_alternation_backtracking_heavy_workflows.py`.
- This is the adjacent quantified-alternation cleanup after `RBR-0351`: published case selection should live with the correctness fixture, while the extra exhaustive backtracking-order checks can remain as a very small local derivation rather than a second private source of truth.
