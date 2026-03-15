# RBR-0369: Fold the quantified alternation conditional-group-exists parity module into the quantified fixture-backed suite

Status: ready
Owner: architecture-implementation
Created: 2026-03-15

## Goal
- Replace `tests/python/test_conditional_group_exists_quantified_alternation_parity.py` with one expanded backend-parameterized suite in `tests/python/test_conditional_group_exists_quantified_parity_suite.py` so the quantified conditional family stops living across two near-duplicate fixture loaders and parity harnesses.

## Deliverables
- `tests/python/test_conditional_group_exists_quantified_parity_suite.py`
- Delete `tests/python/test_conditional_group_exists_quantified_alternation_parity.py`

## Acceptance Criteria
- The shared suite loads `tests/conformance/fixtures/conditional_group_exists_quantified_alternation_workflows.py` through `rebar_harness.correctness.load_fixture_manifest(...)` and `FixtureCase`, reusing the existing `FixtureBundle` path instead of leaving a second standalone parity module or inventing another loader.
- The consolidated suite keeps one manifest-alignment assertion for the quantified alternation fixture covering its manifest id, published case-id set, the numbered and named compile-pattern set for `a(b)?c(?(1)(de|df)|(eg|eh)){2}` and `a(?P<word>b)?c(?(word)(de|df)|(eg|eh)){2}`, and the exact `compile` / module `search` / pattern `fullmatch` operation split published today.
- The expanded suite preserves the current parity depth from the deleted module for this alternation-bearing quantified slice: repeated `compile()` identity, compile metadata parity for `.pattern`, `.flags`, `.groups`, and `.groupindex`, dynamic numeric capture parity through the highest capture index exposed by the pattern, `.groups(default)`, `.groupdict(default)`, `.string`, `.pos`, `.endpos`, `.span()`, `.span(n)`, `.start(n)`, `.end(n)`, `.lastindex`, `.lastgroup`, `.regs`, and named-group access for `word` when present.
- The current local supplemental coverage in `tests/python/test_conditional_group_exists_quantified_alternation_parity.py` is not dropped just because it is not published in the correctness fixture. Keep the mixed-arm `Pattern.fullmatch()` traces for the numbered and named patterns plus the explicit module/pattern no-match rows for partial-second-arm, too-short, and wrong-arm miss paths on the consolidated suite.
- Backend parameterization continues to flow only through `tests/python/conftest.py` and `regex_backend`. Do not reintroduce per-file cache hooks, bespoke skip gates, or another suite-local backend wrapper.
- After the consolidation lands, `rg --files tests/python | rg 'test_conditional_group_exists_quantified_alternation_parity\\.py$'` returns no matches.

## Constraints
- Keep this task scoped to the quantified conditional group-exists Python parity surface. Do not change Rust code, `python/rebar/`, correctness fixtures, benchmark manifests, scorecards, README/status files, or queue/state files beyond this task file.
- Do not fold `tests/python/test_conditional_group_exists_assertion_diagnostic_parity.py`, the replacement suite, or other non-quantified conditional families into the same run.
- Use ordinary pytest parameterization plus the existing shared helpers already in the repo. Do not add code generation, another fixture schema, or a new parity support module.

## Notes
- `tests/python/test_conditional_group_exists_quantified_parity_suite.py` already carries the non-alternation quantified two-arm, no-else, empty-else, empty-yes-else, and fully-empty families. The standalone alternation file is the remaining quantified conditional holdout.
- `rg --files tests/python | rg 'test_conditional_group_exists.*parity\\.py$'` currently leaves only this quantified alternation module plus the separate assertion-diagnostic file outside the consolidated suite naming pattern.
- The standalone file is 321 lines and duplicates the same fixture loading, manifest-shape assertions, compile parity, and match parity machinery already present in the quantified suite; this task should delete that split rather than adding more shared abstraction.
