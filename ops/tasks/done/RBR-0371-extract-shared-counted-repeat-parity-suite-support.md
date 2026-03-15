# RBR-0371: Extract shared counted-repeat parity-suite support for the fixture-backed pytest path

Status: done
Owner: architecture-implementation
Created: 2026-03-15
Completed: 2026-03-15

## Goal
- Remove the duplicated fixture-backed parity scaffolding that `tests/python/test_open_ended_quantified_group_parity_suite.py` and `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` now carry in parallel after `RBR-0357` and `RBR-0359`, while keeping each suite's published frontier and bounded supplements explicit.

## Deliverables
- `tests/python/fixture_parity_support.py`
- `tests/python/test_open_ended_quantified_group_parity_suite.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`

## Acceptance Criteria
- Add a thin support module at `tests/python/fixture_parity_support.py` that owns only the generic helper code repeated across the two counted-repeat suites:
- published-fixture path selection against `rebar_harness.correctness.DEFAULT_FIXTURE_PATHS`;
- `FixtureCase` pattern extraction for both `str` and `bytes`;
- CPython compile-parity helpers;
- shared `Pattern` and `Match` metadata parity assertions; and
- `Match.__getitem__` or `expand(...)` convenience-template helpers that work for both `str` and `bytes`.
- Update `tests/python/test_open_ended_quantified_group_parity_suite.py` and `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` to import that shared support instead of keeping duplicated local implementations of the compile or match-parity helpers, template builders, and published-fixture path selection logic.
- Keep the suite-local frontier declarations readable and explicit in each file. `FIXTURE_BUNDLES`, expected manifest ids, expected compile-pattern sets, expected `Counter((operation, helper))` distributions, bytes-only broader `{1,4}` conditional supplements, and broader-range or nested branch-trace cases stay local rather than being hidden inside the helper module.
- Preserve the current backend-parameterized pytest coverage for both suites, including compile metadata parity, `module.search()` parity, compiled-`Pattern.fullmatch()` parity, `Match.__getitem__`, `expand(...)`, the current `rebar` skip behavior for unsupported broader `{1,4}` conditional `bytes` rows, and the focused backtracking trace checks.
- The refactor stays scoped to these two counted-repeat suites. Do not migrate unrelated parity modules in the same run, do not widen correctness coverage, and do not move these helpers into `python/rebar_harness` or `python/rebar`.
- Verification passes with `.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`.

## Constraints
- Keep this task on the Python parity surface only. Do not change Rust code, `python/rebar/`, correctness fixtures, benchmark manifests, scorecards, README reporting, or tracked state files beyond this task file.
- Prefer one thin local support module plus deleted duplication over a broader new harness abstraction. Do not merge the two suites into one giant file and do not introduce another custom loader layer.
- Preserve suite-specific failure output so manifest ids and case ids still surface clearly in pytest parameterization and assertion failures.

## Notes
- Build directly on `RBR-0357` and `RBR-0359`, which already moved both counted-repeat suites onto the published fixture path.
- This cleanup exists because those two files now repeat the same repo-root, fixture-path, compile-parity, pattern-parity, match-parity, and convenience-API scaffolding almost verbatim even though their remaining differences are mostly the manifest inventories and bounded supplemental cases.

## Completion
- Added `tests/python/fixture_parity_support.py` as a thin local helper module for the shared counted-repeat suite support: published fixture-path selection against `DEFAULT_FIXTURE_PATHS`, generic `FixtureCase` pattern extraction for `str` and `bytes`, CPython compile parity, shared pattern/match metadata assertions, and common `Match.__getitem__` / `expand(...)` convenience-template checks.
- Updated `tests/python/test_open_ended_quantified_group_parity_suite.py` and `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` to import that support instead of carrying duplicated local compile, pattern-parity, match-parity, and fixture-path-selection helpers.
- Kept the suite-local fixture bundles, expected manifest ids and pattern sets, operation/helper counters, bytes-only broader `{1,4}` conditional supplements, and broader-range or nested backtracking trace cases explicit in their original files while preserving the existing backend-parameterized parity coverage and `rebar` skip behavior.

## Verification
- `.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
