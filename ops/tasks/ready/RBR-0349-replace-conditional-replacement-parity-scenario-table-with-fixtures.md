# RBR-0349: Replace the conditional replacement parity scenario table with published fixtures

Status: ready
Owner: architecture-implementation
Created: 2026-03-15

## Goal
- Simplify `tests/python/test_conditional_group_exists_replacement_parity_suite.py` by driving its case selection from the published conditional replacement correctness fixtures instead of a second private scenario table, so the Python parity surface cannot drift away from the scorecard frontier it is meant to defend.

## Deliverables
- `tests/python/test_conditional_group_exists_replacement_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_conditional_group_exists_replacement_parity_suite.py` loads its parity cases through `rebar_harness.correctness.load_fixture_manifest(...)` and `FixtureCase` instead of keeping file-local `ProbeSpec`, `Scenario`, or `ReplacementCase` tables that restate replacement patterns, haystacks, counts, and helper coverage.
- The suite is anchored to exactly these eight published fixture modules and no others:
  - `tests/conformance/fixtures/conditional_group_exists_replacement_workflows.py`
  - `tests/conformance/fixtures/conditional_group_exists_no_else_replacement_workflows.py`
  - `tests/conformance/fixtures/conditional_group_exists_empty_else_replacement_workflows.py`
  - `tests/conformance/fixtures/conditional_group_exists_empty_yes_else_replacement_workflows.py`
  - `tests/conformance/fixtures/conditional_group_exists_fully_empty_replacement_workflows.py`
  - `tests/conformance/fixtures/conditional_group_exists_alternation_replacement_workflows.py`
  - `tests/conformance/fixtures/conditional_group_exists_nested_replacement_workflows.py`
  - `tests/conformance/fixtures/conditional_group_exists_quantified_replacement_workflows.py`
- The refactored suite keeps one manifest-alignment assertion per fixture covering:
  - the exact manifest id
  - the exact published case-id set
  - the exact numbered and named pattern set published by that fixture
  - the shared operation/helper distribution of two module `sub` rows, two module `subn` rows, two pattern `sub` rows, and two pattern `subn` rows
- Replacement parity still runs against CPython for every loaded fixture case, preserving the current coverage surface for:
  - numbered and named constant replacement paths
  - module-level and compiled-`Pattern` entrypoints
  - `sub()` and `subn()` result parity
  - count-limited `subn()` behavior
  - present-versus-absent arms, empty-arm spellings, alternation-heavy arms, nested conditionals, and quantified replacements already published by those fixtures
- Backend selection and cache purging flow through the shared `tests/python/conftest.py` infrastructure instead of a file-local native-module gate or duplicated backend setup.
- After the refactor lands, `tests/python/test_conditional_group_exists_replacement_parity_suite.py` no longer contains hand-maintained scenario dataclasses or pattern/string/count tables that duplicate data already stored in the published fixtures.

## Constraints
- Keep this task scoped to `tests/python/test_conditional_group_exists_replacement_parity_suite.py`; do not change Rust code, `python/rebar/` runtime behavior, correctness fixture contents, benchmark workloads, or published reports to complete it.
- Reuse ordinary pytest parameterization and the existing fixture-loading path already used by `tests/python/test_conditional_group_exists_parity_suite.py`; do not add another manifest schema, generator, or family-specific loader layer.
- Keep bytes replacement coverage, callable replacement behavior, replacement-template behavior, and broader non-conditional replacement suites out of scope for this run.

## Notes
- The current suite is only one file, but it still restates all 16 numbered and named replacement patterns already published across the eight conditional replacement fixtures, which is now the wrong side of the repo’s “one parity harness, one source of fixture truth” direction.
- `tests/python/test_conditional_group_exists_parity_suite.py` is the nearest existing shape to copy: it already shows how this exact regex family can stay fixture-backed while keeping manifest-alignment assertions explicit.
