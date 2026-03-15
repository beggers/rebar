# RBR-0347: Consolidate the base conditional group-exists parity modules into one fixture-backed pytest suite

Status: ready
Owner: architecture-implementation
Created: 2026-03-15

## Goal
- Replace the five first-wave non-replacement conditional group-exists parity modules with one backend-parameterized pytest suite so the base two-arm and empty-arm conditional surface grows in one place instead of across repeated `unittest` classes, repeated `sys.path` setup, repeated cache-purge hooks, repeated native-module gates, and repeated match-assert boilerplate.

## Deliverables
- `tests/python/test_conditional_group_exists_parity_suite.py`
- Delete `tests/python/test_conditional_group_exists_parity.py`
- Delete `tests/python/test_conditional_group_exists_no_else_parity.py`
- Delete `tests/python/test_conditional_group_exists_empty_else_parity.py`
- Delete `tests/python/test_conditional_group_exists_empty_yes_else_parity.py`
- Delete `tests/python/test_conditional_group_exists_fully_empty_parity.py`

## Acceptance Criteria
- The new suite covers the currently landed numbered and named compile metadata, module `search()`, and compiled-`Pattern.fullmatch()` parity observations now spread across the five superseded modules for:
  - `a(b)?c(?(1)d|e)` and `a(?P<word>b)?c(?(word)d|e)`
  - `a(b)?c(?(1)d)` and `a(?P<word>b)?c(?(word)d)`
  - `a(b)?c(?(1)d|)` and `a(?P<word>b)?c(?(word)d|)`
  - `a(b)?c(?(1)|e)` and `a(?P<word>b)?c(?(word)|e)`
  - `a(b)?c(?(1)|)` and `a(?P<word>b)?c(?(word)|)`
- Case selection is driven from the published correctness fixtures already checked into the repo:
  - `tests/conformance/fixtures/conditional_group_exists_workflows.py`
  - `tests/conformance/fixtures/conditional_group_exists_no_else_workflows.py`
  - `tests/conformance/fixtures/conditional_group_exists_empty_else_workflows.py`
  - `tests/conformance/fixtures/conditional_group_exists_empty_yes_else_workflows.py`
  - `tests/conformance/fixtures/conditional_group_exists_fully_empty_workflows.py`
  The consolidated suite keeps one manifest-alignment assertion per fixture covering the manifest id, the published case-id set, the two compile patterns, and the operation split of two `compile`, two module `search`, and two pattern `fullmatch` rows, so the Python parity surface stays tied to the published correctness surface instead of drifting onto hand-maintained case tables.
- The implementation reuses the existing loader path in `rebar_harness.correctness`, especially `load_fixture_manifest(...)` and `FixtureCase`, rather than adding another manifest reader, another case format, or copied per-file pattern tables.
- Backend parameterization continues to flow through `tests/python/conftest.py` and the shared `regex_backend` fixture, so the consolidated suite uses one central cache-purge hook and one central native-availability gate instead of repeated `setUp()` / `tearDown()` methods and per-test `@unittest.skipUnless(...)` decorators.
- The consolidated suite preserves the current parity depth already asserted by the five singleton files:
  - repeated `compile()` identity for the active backend
  - compile metadata parity for `.pattern`, `.flags`, `.groups`, and `.groupindex`
  - match-result parity for `.group(0)`, `.group(1)`, `.groups()`, `.groupdict()`, `.span()`, `.span(1)`, `.start(1)`, `.end(1)`, `.lastindex`, and `.lastgroup`
  - named-group access parity where the fixture pattern exposes `word`
- After the consolidation lands, `rg --files tests/python | rg 'test_conditional_group_exists(_no_else|_empty_else|_empty_yes_else|_fully_empty)?_parity\\.py$'` returns no matches.

## Constraints
- Keep this task scoped to the five base conditional group-exists modules listed above; do not fold in nested, quantified, alternation-heavy, branch-local-backreference, or replacement-conditioned conditional parity files here.
- Keep the work on the Python test surface only. Do not change Rust code, `python/rebar/` runtime behavior, correctness fixtures, benchmark workloads, or published reports to complete it.
- Use ordinary pytest parameterization plus the existing shared helpers already in the repo. Do not introduce code generation, another compatibility layer, or another custom fixture schema.

## Notes
- The five targeted modules total 730 lines and are near-identical aside from pattern strings, present/absent haystacks, and named-group coverage.
- `tests/python/test_conditional_group_exists_replacement_parity_suite.py`, `tests/python/test_open_ended_quantified_group_parity_suite.py`, `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`, and `tests/python/test_callable_replacement_parity_suite.py` already demonstrate the intended repo shape for this kind of backend-parameterized parity coverage.
