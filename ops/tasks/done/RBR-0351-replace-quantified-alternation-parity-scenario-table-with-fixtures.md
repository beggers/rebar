# RBR-0351: Replace the quantified alternation parity scenario table with published fixtures

Status: done
Owner: architecture-implementation
Created: 2026-03-15

## Goal
- Simplify `tests/python/test_quantified_alternation_parity_suite.py` by driving its parity cases from the published quantified-alternation correctness fixtures instead of a second private `ParityCase` table, so the Python parity surface cannot drift away from the scorecard frontier it is meant to defend.

## Deliverables
- `tests/python/test_quantified_alternation_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_quantified_alternation_parity_suite.py` loads its parity cases through `rebar_harness.correctness.load_fixture_manifest(...)` and `FixtureCase` instead of keeping a file-local `ParityCase` dataclass plus a hand-maintained `CASES` table that restates patterns, example haystacks, and no-match rows already stored in published fixtures.
- The suite is anchored to exactly these five published fixture modules and no others:
  - `tests/conformance/fixtures/quantified_alternation_workflows.py`
  - `tests/conformance/fixtures/quantified_alternation_broader_range_workflows.py`
  - `tests/conformance/fixtures/quantified_alternation_conditional_workflows.py`
  - `tests/conformance/fixtures/quantified_alternation_open_ended_workflows.py`
  - `tests/conformance/fixtures/quantified_alternation_nested_branch_workflows.py`
- The refactored suite keeps one manifest-alignment assertion per fixture covering:
  - the exact manifest id
  - the exact published case-id set
  - the exact numbered and named pattern set published by that fixture
  - the operation/helper distribution already published by that fixture:
    - `quantified-alternation-workflows`: two `compile`, two module `search`, and two pattern `fullmatch` rows
    - `quantified-alternation-broader-range-workflows`: two `compile`, four module `search`, and ten pattern `fullmatch` rows
    - `quantified-alternation-conditional-workflows`: two `compile`, four module `search`, and six pattern `fullmatch` rows
    - `quantified-alternation-open-ended-workflows`: two `compile`, four module `search`, and ten pattern `fullmatch` rows
    - `quantified-alternation-nested-branch-workflows`: two `compile`, two module `search`, and six pattern `fullmatch` rows
- Compile metadata parity still runs against CPython for every loaded compile case, preserving the current coverage surface for:
  - `a(b|c){1,2}d` and `a(?P<word>b|c){1,2}d`
  - `a(b|c){1,3}d` and `a(?P<word>b|c){1,3}d`
  - `a((b|c){1,2})?(?(1)d|e)` and `a(?P<outer>(b|c){1,2})?(?(outer)d|e)`
  - `a(b|c){1,}d` and `a(?P<word>b|c){1,}d`
  - `a((b|c)|de){1,2}d` and `a(?P<word>(b|c)|de){1,2}d`
- Match-result parity still runs against CPython for every loaded module `search()` and compiled-`Pattern.fullmatch()` case, preserving the current assertions for:
  - numbered and named capture access
  - `.group(0)` plus all numbered groups used by the published slice
  - `.groups()`, `.groupdict()`, `.span()`, `.lastindex`, and `.lastgroup`
  - no-match paths already published in the broader-range, conditional, open-ended, and nested-branch fixtures
- Backend selection and cache purging flow through the shared `tests/python/conftest.py` infrastructure instead of a file-local native-module gate or duplicated backend setup.
- After the refactor lands, `tests/python/test_quantified_alternation_parity_suite.py` no longer contains hand-maintained pattern/string case tables that duplicate data already stored in the published quantified-alternation fixtures.

## Constraints
- Keep this task scoped to `tests/python/test_quantified_alternation_parity_suite.py`; do not change Rust code, `python/rebar/` runtime behavior, correctness fixture contents, benchmark workloads, or published reports to complete it.
- Reuse ordinary pytest parameterization and the existing fixture-loading path already used by `tests/python/test_conditional_group_exists_parity_suite.py` and `tests/python/test_callable_replacement_parity_suite.py`; do not add another manifest schema, generator, or family-specific loader layer.
- Keep quantified-alternation backtracking-heavy coverage, branch-local-backreference coverage, grouped counted-repeat suites, and the separate `tests/python/test_conditional_group_exists_quantified_alternation_parity.py` file out of scope for this run.

## Notes
- This suite is now the clearest remaining example of a Python parity test restating published correctness data in a second private table: the same bounded, broader-range, conditional, open-ended, and nested-branch patterns and example texts already live in the five quantified-alternation fixture modules above.
- `tests/python/test_conditional_group_exists_parity_suite.py` and `tests/python/test_conditional_group_exists_replacement_parity_suite.py` are the nearest existing shapes to copy: both stay fixture-backed while keeping per-manifest alignment assertions explicit.

## Completion Notes
- Replaced the file-local `ParityCase` table in `tests/python/test_quantified_alternation_parity_suite.py` with five explicit fixture bundles loaded through `load_fixture_manifest(...)`, keeping only manifest-shape expectations in the suite.
- Kept one manifest-alignment assertion per quantified-alternation fixture, covering the exact manifest id, case-id set, numbered and named pattern set, and the published `compile` / module `search` / pattern `fullmatch` distribution for each bundle.
- Rebuilt compile, module `search()`, and compiled-pattern `fullmatch()` parity from `FixtureCase` objects, deriving numbered and named group checks from the compiled CPython pattern so the suite no longer duplicates fixture haystacks or no-match rows in a second private table.
- Verified with `.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py` (`126 passed`).
