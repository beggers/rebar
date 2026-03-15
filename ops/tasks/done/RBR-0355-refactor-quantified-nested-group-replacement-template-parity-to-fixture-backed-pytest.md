# RBR-0355: Refactor quantified nested-group replacement-template parity onto the shared fixture-backed pytest path

Status: done
Owner: architecture-implementation
Created: 2026-03-15

## Goal
- Simplify `tests/python/test_quantified_nested_group_replacement_template_parity.py` by deriving its numbered and named replacement-template parity cases from the published quantified nested-group replacement fixture and the shared pytest backend path instead of a second private `ReplacementCase` table inside a standalone native-gated `unittest` module.

## Deliverables
- `tests/python/test_quantified_nested_group_replacement_template_parity.py`

## Acceptance Criteria
- `tests/python/test_quantified_nested_group_replacement_template_parity.py` loads its published cases through `rebar_harness.correctness.load_fixture_manifest(...)` and `FixtureCase` from exactly `tests/conformance/fixtures/quantified_nested_group_replacement_workflows.py` instead of keeping a file-local `ReplacementCase` dataclass and `CASES` tuple that restate the same patterns, replacements, haystacks, and count-limited `subn()` cases already stored in that fixture.
- The refactored suite keeps one manifest-alignment assertion covering:
  - manifest id `quantified-nested-group-replacement-workflows`
  - the exact published case-id set from that fixture
  - the exact numbered and named pattern set published by that fixture:
    - `a((bc)+)d`
    - `a(?P<outer>(?P<inner>bc)+)d`
  - the published operation/helper distribution of two module `sub()` rows, two module `subn()` rows, two pattern `sub()` rows, and two pattern `subn()` rows
- Compile metadata parity is still asserted for the two fixture-backed patterns above, preserving the current coverage for repeated `compile()` identity plus `.pattern`, `.flags`, `.groups`, and `.groupindex`, but the pattern list is derived from the loaded fixture instead of another file-local case table.
- Module replacement parity runs from the loaded `FixtureCase` rows and preserves the current numbered and named coverage for:
  - lower-bound outer-capture `sub()` replacement on `zzabcdzz`
  - first-match-only inner-capture `subn()` replacement on `zzabcbcdabcbcdzz`
  The suite compares public `rebar.sub()` / `rebar.subn()` results against CPython without broadening into callable replacement, alternation inside the repeated site, broader counted repeats, or deeper nested grouped execution.
- Compiled-pattern replacement parity runs from the loaded `FixtureCase` rows and preserves the current numbered and named coverage for:
  - repeated-outer-capture `Pattern.sub()` replacement on `zzabcbcdzz`
  - first-match-only inner-capture `Pattern.subn()` replacement on `zzabcbcdabcbcdzz`
- Backend selection and cache purging flow through `tests/python/conftest.py` and the shared `regex_backend` fixture/autouse purge hook instead of file-local `unittest.skipUnless(...)`, `setUp()` / `tearDown()`, or other private native-module gating.
- After the refactor lands, `tests/python/test_quantified_nested_group_replacement_template_parity.py` no longer imports `unittest` or defines file-local `ReplacementCase` / `CASES` tables that duplicate data already stored in the published correctness fixture.

## Constraints
- Keep this task scoped to `tests/python/test_quantified_nested_group_replacement_template_parity.py`; do not change Rust code, `python/rebar/` runtime behavior, correctness fixture contents, benchmark workloads, or published reports to complete it.
- Reuse ordinary pytest parameterization plus the existing fixture-loading path already used by `tests/python/test_quantified_alternation_parity_suite.py`, `tests/python/test_conditional_group_exists_replacement_parity_suite.py`, and `tests/python/test_quantified_branch_local_backreference_parity.py`; do not add another manifest schema, generator, or family-specific loader layer.
- Keep the adjacent nested-group replacement-template, grouped-alternation replacement-template, and callable-replacement parity modules out of scope for this run.

## Notes
- `tests/python/test_quantified_nested_group_replacement_template_parity.py` is a remaining standalone native-backed parity holdout from `RBR-0305`: it duplicates all eight published numbered and named `sub()` / `subn()` workflows already tracked in `tests/conformance/fixtures/quantified_nested_group_replacement_workflows.py`.
- This is the same simplification pattern already used by `RBR-0347`, `RBR-0351`, and `RBR-0353`: keep the Python parity surface anchored to the published fixture frontier instead of maintaining a second hand-written source of truth.

## Completion Notes
- Replaced the file-local `ReplacementCase` / `CASES` `unittest` table in `tests/python/test_quantified_nested_group_replacement_template_parity.py` with one fixture-backed pytest module that loads `FixtureCase` rows directly from `tests/conformance/fixtures/quantified_nested_group_replacement_workflows.py`.
- Kept one manifest-alignment assertion covering the exact manifest id, case-id set, numbered and named pattern set, and the published module/pattern `sub()` / `subn()` distribution, with compile metadata parity now driven from the fixture-derived pattern set.
- Rebuilt the module and compiled-pattern replacement-template parity checks from the loaded fixture rows, preserving the bounded lower-bound, repeated-outer-capture, and first-match-only `subn()` coverage without broadening scope.
- Verified with `.venv/bin/python -m pytest -q tests/python/test_quantified_nested_group_replacement_template_parity.py` (`21 passed`).
