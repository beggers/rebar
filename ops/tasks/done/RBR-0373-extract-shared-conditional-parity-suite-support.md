# RBR-0373: Extract shared conditional parity-suite support for the fixture-backed pytest path

Status: done
Owner: architecture-implementation
Created: 2026-03-15
Completed: 2026-03-15

## Goal
- Remove the repeated fixture-backed compile and match parity scaffolding that the conditional-group-exists parity suites still carry in parallel after `tests/python/fixture_parity_support.py` landed, while keeping each suite's published frontier and bounded supplements explicit.

## Deliverables
- `tests/python/fixture_parity_support.py`
- `tests/python/test_conditional_group_exists_parity_suite.py`
- `tests/python/test_conditional_group_exists_nested_parity_suite.py`
- `tests/python/test_conditional_group_exists_alternation_parity_suite.py`
- `tests/python/test_conditional_group_exists_quantified_parity_suite.py`

## Acceptance Criteria
- Extend `tests/python/fixture_parity_support.py` only with generic helper code already repeated across the four conditional suites:
  - `FixtureCase` pattern extraction for `str` cases;
  - CPython compile-parity helpers;
  - shared `Pattern` metadata parity assertions;
  - shared `Match` metadata parity assertions; and
  - one shared helper for `Match | None` result parity when a fixture row or supplemental case is expected to miss.
- Update the four conditional suites to import that shared support instead of keeping suite-local implementations of `_case_pattern`, `_compile_with_cpython_parity`, `_assert_pattern_parity`, `_assert_match_parity`, or `_assert_match_result_parity`.
- Keep the suite-local frontier declarations readable and explicit in each file. `FIXTURE_BUNDLES`, expected manifest ids, expected case-id sets, expected compile-pattern sets, operation/helper `Counter(...)` distributions, the nested suite's selected-case filtering for the non-systematic empty-else rows, and the quantified suite's explicit supplemental miss and mixed-arm cases stay local rather than being hidden in the helper module.
- Preserve the current backend-parameterized pytest coverage for all four suites, including compile identity, compile metadata parity, present-match parity, `None` parity for absent or failure rows, and the quantified suite's stronger metadata checks on `.groups(default)`, `.groupdict(default)`, `.string`, `.pos`, `.endpos`, and `.regs`.
- Preserve the current dynamic group-index parity depth where the suites already assert it today, especially on the alternation and quantified conditional rows.
- The refactor stays scoped to these four conditional suites. Do not move helper code into `python/rebar_harness`, do not add another support module under `tests/python/`, and do not fold replacement-conditioned or branch-local-backreference suites into the same run.
- Verification passes with `.venv/bin/python -m pytest -q tests/python/test_conditional_group_exists_parity_suite.py tests/python/test_conditional_group_exists_nested_parity_suite.py tests/python/test_conditional_group_exists_alternation_parity_suite.py tests/python/test_conditional_group_exists_quantified_parity_suite.py`.

## Constraints
- Keep this task on the Python parity surface only. Do not change Rust code, `python/rebar/`, correctness fixtures, benchmark manifests, published scorecards, README reporting, or tracked project-state files beyond this task file.
- Prefer extending the existing `tests/python/fixture_parity_support.py` module over inventing `tests/python/conditional_parity_support.py` or another suite-family helper layer.
- Preserve suite-specific parameterization and assertion failure readability so manifest ids and case ids still surface clearly in pytest output.

## Notes
- `tests/python/test_conditional_group_exists_parity_suite.py`, `tests/python/test_conditional_group_exists_nested_parity_suite.py`, `tests/python/test_conditional_group_exists_alternation_parity_suite.py`, and `tests/python/test_conditional_group_exists_quantified_parity_suite.py` still each embed the same `FixtureCase` pattern extraction plus compile and match parity helpers even though they already share the same fixture-backed suite shape.
- Build directly on `RBR-0371`; the repo already has one thin local helper module for fixture-backed parity suites, so this task should reuse that path instead of introducing a second support abstraction.
- Keep `tests/python/test_conditional_group_exists_replacement_parity_suite.py` out of scope for now because its replacement-specific assertions are a distinct surface.

## Completion
- Extended `tests/python/fixture_parity_support.py` with a shared `str_case_pattern(...)` helper, optional `regs` checking in the common match-parity assertions, and a shared `assert_match_result_parity(...)` entrypoint for `Match | None` rows.
- Updated the four conditional parity suites to import the shared fixture-backed compile and match helpers instead of keeping suite-local `_case_pattern`, `_compile_with_cpython_parity`, `_assert_pattern_parity`, `_assert_match_parity`, or `_assert_match_result_parity` copies.
- Kept all suite-local fixture bundles, manifest and case-id expectations, operation/helper counters, the nested empty-else case filtering, and the quantified suite's supplemental mixed-arm and miss cases explicit in their original files while preserving the quantified suite's stronger match metadata coverage.

## Verification
- `.venv/bin/python -m pytest -q tests/python/test_conditional_group_exists_parity_suite.py tests/python/test_conditional_group_exists_nested_parity_suite.py tests/python/test_conditional_group_exists_alternation_parity_suite.py tests/python/test_conditional_group_exists_quantified_parity_suite.py`
