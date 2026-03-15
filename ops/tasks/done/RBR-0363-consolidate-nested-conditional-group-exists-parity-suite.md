# RBR-0363: Consolidate the nested conditional group-exists parity modules into one fixture-backed pytest suite

Status: done
Owner: architecture-implementation
Created: 2026-03-15

## Goal
- Replace the four landed nested conditional group-exists parity modules with one backend-parameterized pytest suite so the nested conditional surface stops living across repeated `unittest` classes, repeated `sys.path` setup, repeated cache-purge hooks, repeated native-module gates, and repeated match-assert boilerplate.

## Deliverables
- `tests/python/test_conditional_group_exists_nested_parity_suite.py`
- Delete `tests/python/test_conditional_group_exists_nested_parity.py`
- Delete `tests/python/test_conditional_group_exists_no_else_nested_parity.py`
- Delete `tests/python/test_conditional_group_exists_empty_yes_else_nested_parity.py`
- Delete `tests/python/test_conditional_group_exists_fully_empty_nested_parity.py`

## Acceptance Criteria
- The new suite covers the currently landed numbered and named compile metadata, module helper, and compiled-`Pattern.fullmatch()` parity observations now spread across the four superseded modules for:
  - `a(b)?c(?(1)(?(1)d|e)|f)` and `a(?P<word>b)?c(?(word)(?(word)d|e)|f)`
  - `a(b)?c(?(1)(?(1)d))` and `a(?P<word>b)?c(?(word)(?(word)d))`
  - `a(b)?c(?(1)|(?(1)e|f))` and `a(?P<word>b)?c(?(word)|(?(word)e|f))`
  - `a(b)?c(?(1)|(?(1)|))` and `a(?P<word>b)?c(?(word)|(?(word)|))`
- Case selection is driven from the published correctness fixtures already checked into the repo:
  - `tests/conformance/fixtures/conditional_group_exists_nested_workflows.py`
  - `tests/conformance/fixtures/conditional_group_exists_no_else_nested_workflows.py`
  - `tests/conformance/fixtures/conditional_group_exists_empty_yes_else_nested_workflows.py`
  - `tests/conformance/fixtures/conditional_group_exists_fully_empty_nested_workflows.py`
  The consolidated suite keeps one manifest-alignment assertion per fixture covering the manifest id, the published case-id set, the numbered and named compile patterns, and the operation split each manifest publishes today.
- The suite also pulls the non-systematic numbered and named published rows from `tests/conformance/fixtures/conditional_group_exists_empty_else_nested_workflows.py` so the nested explicit-empty-else slice finally lives on the same standard parity path as the rest of the nested conditional family. Do not pull the fixture's `systematic` rows into this suite.
- The implementation reuses the existing loader path in `rebar_harness.correctness`, especially `load_fixture_manifest(...)` and `FixtureCase`, rather than adding another manifest reader, another case format, or copied per-file pattern tables.
- Backend parameterization continues to flow through `tests/python/conftest.py` and the shared `regex_backend` fixture, so the consolidated suite uses one central cache-purge hook and one central native-availability gate instead of repeated `setUp()` / `tearDown()` methods and per-test `@unittest.skipUnless(...)` decorators.
- The consolidated suite preserves the current parity depth already asserted by the four singleton files:
  - repeated `compile()` identity for the active backend
  - compile metadata parity for `.pattern`, `.flags`, `.groups`, and `.groupindex`
  - match-result parity for `.group(0)`, `.group(1)`, `.groups()`, `.groupdict()`, `.span()`, `.span(1)`, `.start(1)`, `.end(1)`, `.lastindex`, and `.lastgroup`
  - named-group access parity where the fixture pattern exposes `word`
  - present, absent, and bounded failure outcomes for the module `fullmatch()` and compiled-`Pattern.fullmatch()` rows already published by these nested manifests
- After the consolidation lands, `rg --files tests/python | rg 'test_conditional_group_exists(_no_else|_empty_yes_else|_fully_empty)?_nested_parity\\.py$'` returns no matches.

## Constraints
- Keep this task scoped to the nested conditional group-exists parity surface listed above. Do not fold `tests/python/test_folded_systematic_capture_parity.py`, quantified conditional suites, alternation-heavy conditional suites, branch-local-backreference conditional suites, or replacement-conditioned conditional parity into the same run.
- Keep the work on the Python test surface only. Do not change Rust code, `python/rebar/` runtime behavior, correctness fixtures, benchmark workloads, or published reports to complete it.
- Use ordinary pytest parameterization plus the existing shared helpers already in the repo. Do not introduce code generation, another compatibility layer, or another custom fixture schema.

## Notes
- The four targeted singleton modules total 676 lines and are near-identical aside from pattern strings, present/absent/failure texts, and named-group coverage.
- `ops/tasks/done/RBR-0347-consolidate-base-conditional-group-exists-parity-suite.md` is the exact shape to follow for this nested family: one backend-parameterized suite, one manifest-alignment assertion per published fixture, and no new helper module.
- `tests/conformance/fixtures/conditional_group_exists_empty_else_nested_workflows.py` is already part of the published correctness corpus; using only its non-systematic rows here keeps the nested family on one standard parity path without dragging the separate folded-systematic capture cleanup into this task.

## Completion Notes
- Added `tests/python/test_conditional_group_exists_nested_parity_suite.py`, loading the five nested conditional fixture manifests through `load_fixture_manifest(...)` and asserting manifest id, selected case ids, compile patterns, and the `compile` / module `search` / module `fullmatch` / pattern `fullmatch` split for each bundle.
- Folded the nested explicit-empty-else non-systematic rows from `tests/conformance/fixtures/conditional_group_exists_empty_else_nested_workflows.py` into the same backend-parameterized parity path while leaving that fixture's systematic rows on `tests/python/test_folded_systematic_capture_parity.py`.
- Deleted the four superseded singleton parity modules and verified with `.venv/bin/python -m pytest tests/python/test_conditional_group_exists_nested_parity_suite.py tests/python/test_folded_systematic_capture_parity.py -q` (`122 passed`) plus `rg --files tests/python | rg 'test_conditional_group_exists(_no_else|_empty_yes_else|_fully_empty)?_nested_parity\\.py$'` returning no matches.
