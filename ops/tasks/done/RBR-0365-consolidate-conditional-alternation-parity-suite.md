# RBR-0365: Consolidate the alternation-heavy conditional group-exists parity modules into one fixture-backed pytest suite

Status: done
Owner: architecture-implementation
Created: 2026-03-15

## Goal
- Replace the five landed alternation-heavy conditional group-exists parity modules with one backend-parameterized pytest suite so this conditional surface stops living across repeated `unittest` classes, repeated `sys.path` setup, repeated cache-purge hooks, repeated native-module gates, and repeated match-assert boilerplate.

## Deliverables
- `tests/python/test_conditional_group_exists_alternation_parity_suite.py`
- Delete `tests/python/test_conditional_group_exists_alternation_parity.py`
- Delete `tests/python/test_conditional_group_exists_no_else_alternation_parity.py`
- Delete `tests/python/test_conditional_group_exists_empty_else_alternation_parity.py`
- Delete `tests/python/test_conditional_group_exists_empty_yes_else_alternation_parity.py`
- Delete `tests/python/test_conditional_group_exists_fully_empty_alternation_parity.py`

## Acceptance Criteria
- The new suite covers the currently landed numbered and named compile metadata, module helper, and compiled-`Pattern.fullmatch()` parity observations now spread across the five superseded modules for:
  - `a(b)?c(?(1)(de|df)|(eg|eh))` and `a(?P<word>b)?c(?(word)(de|df)|(eg|eh))`
  - `a(b)?c(?(1)(de|df))` and `a(?P<word>b)?c(?(word)(de|df))`
  - `a(b)?c(?(1)(de|df)|)` and `a(?P<word>b)?c(?(word)(de|df)|)`
  - `a(b)?c(?(1)|(e|f))` and `a(?P<word>b)?c(?(word)|(e|f))`
  - `a(b)?c(?(1)|(?:|))` and `a(?P<word>b)?c(?(word)|(?:|))`
- Case selection is driven from the published correctness fixtures already checked into the repo:
  - `tests/conformance/fixtures/conditional_group_exists_alternation_workflows.py`
  - `tests/conformance/fixtures/conditional_group_exists_no_else_alternation_workflows.py`
  - `tests/conformance/fixtures/conditional_group_exists_empty_else_alternation_workflows.py`
  - `tests/conformance/fixtures/conditional_group_exists_empty_yes_else_alternation_workflows.py`
  - `tests/conformance/fixtures/conditional_group_exists_fully_empty_alternation_workflows.py`
  The consolidated suite keeps one manifest-alignment assertion per fixture covering the manifest id, the published case-id set, the numbered and named compile patterns, and the exact operation/helper split each fixture publishes today, including the fully-empty family's module `fullmatch()` rows.
- The implementation reuses the existing loader path in `rebar_harness.correctness`, especially `load_fixture_manifest(...)` and `FixtureCase`, rather than adding another manifest reader, another case format, or copied per-file pattern tables.
- Backend parameterization continues to flow through `tests/python/conftest.py` and the shared `regex_backend` fixture, so the consolidated suite uses one central cache-purge hook and one central native-availability gate instead of repeated `setUp()` / `tearDown()` methods and per-test `@unittest.skipUnless(...)` decorators.
- The consolidated suite preserves the current parity depth already asserted by the five singleton files:
  - repeated `compile()` identity for the active backend
  - compile metadata parity for `.pattern`, `.flags`, `.groups`, and `.groupindex`
  - match-result parity for `.group(0)`, `.groups()`, `.groupdict()`, `.span()`, `.lastindex`, and `.lastgroup`
  - numbered capture parity through the highest capture index each fixture exposes today, including `.group(n)`, `.span(n)`, `.start(n)`, and `.end(n)` for the extra alternation-arm groups in the two-arm conditional fixture
  - named-group access parity where the fixture pattern exposes `word`
  - `None` parity for the fully-empty family's extra-suffix rejection rows and the other absent or failure outcomes already published by these fixtures
- After the consolidation lands, `rg --files tests/python | rg 'test_conditional_group_exists(_no_else|_empty_else|_empty_yes_else|_fully_empty)?_alternation_parity\\.py$'` returns no matches.

## Constraints
- Keep this task scoped to the five alternation-heavy conditional group-exists modules listed above. Do not fold in `tests/python/test_conditional_group_exists_quantified_alternation_parity.py`, the base or nested conditional suites, quantified-non-alternation conditional suites, branch-local-backreference conditional suites, or replacement-conditioned conditional parity.
- Keep the work on the Python test surface only. Do not change Rust code, `python/rebar/` runtime behavior, correctness fixtures, benchmark workloads, or published reports to complete it.
- Use ordinary pytest parameterization plus the existing shared helpers already in the repo. Do not introduce code generation, another compatibility layer, or another custom fixture schema.

## Notes
- The five targeted singleton modules total 928 lines and are near-identical aside from pattern strings, capture depth, helper selection, present-versus-absent haystacks, and named-group coverage.
- `ops/tasks/done/RBR-0347-consolidate-base-conditional-group-exists-parity-suite.md` and `ops/tasks/done/RBR-0363-consolidate-nested-conditional-group-exists-parity-suite.md` are the exact shape to follow here: one backend-parameterized suite, one manifest-alignment assertion per published fixture, and no new helper module.
- The published correctness-scorecard side for this family already lives in the combined expectation path after `ops/tasks/done/RBR-0333-consolidate-conditional-alternation-correctness-scorecards.md`; this task brings the Python parity surface up to the same repo shape instead of leaving the alternation-bearing conditional checks scattered across singleton modules.

## Completion Notes
- Added `tests/python/test_conditional_group_exists_alternation_parity_suite.py`, loading the five published alternation-heavy conditional fixture manifests through `load_fixture_manifest(...)` and asserting each manifest id, published case-id set, numbered and named compile patterns, and the exact `compile` / module-helper / pattern-helper split each fixture publishes today, including the fully-empty family's module `fullmatch()` rows.
- Replaced the repeated `unittest` classes with one backend-parameterized pytest suite that keeps compile identity, compile metadata, dynamic numeric capture parity through each pattern's highest group index, named-group access parity, and `None` parity for the fully-empty extra-suffix rejection rows on the shared `regex_backend` path.
- Deleted the five superseded singleton parity modules and verified with `.venv/bin/python -m pytest tests/python/test_conditional_group_exists_alternation_parity_suite.py -q` (`89 passed`), `git diff --name-status -- ...` reporting `D` for all five removed files, and `rg --files tests/python | rg 'test_conditional_group_exists(_no_else|_empty_else|_empty_yes_else|_fully_empty)?_alternation_parity\\.py$'` returning no matches.
