# RBR-0357: Refactor the wider-ranged-repeat quantified-group parity suite onto the shared fixture-backed pytest path

Status: done
Owner: architecture-implementation
Created: 2026-03-15

## Goal
- Remove the large file-local scenario table from `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` so the suite reuses the published correctness fixtures it already mirrors, while keeping the bounded bytes-only and branch-trace coverage that is not represented by ordinary fixture rows.

## Deliverables
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`

## Acceptance Criteria
- The suite loads its published `str` compile, `module.search()`, and compiled-`Pattern.fullmatch()` parity cases through `rebar_harness.correctness.load_fixture_manifest(...)` and `FixtureCase` instead of restating those workflows in file-local `Scenario`, `ParityCase`, `SCENARIOS`, `_parity_case(...)`, and `CASES` tables.
- Case selection is driven from exactly these existing published fixture modules, which already define the frontier this suite exercises today:
- `tests/conformance/fixtures/wider_ranged_repeat_quantified_group_workflows.py`
- `tests/conformance/fixtures/wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py`
- `tests/conformance/fixtures/wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py`
- `tests/conformance/fixtures/broader_range_wider_ranged_repeat_quantified_group_alternation_workflows.py`
- `tests/conformance/fixtures/broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py`
- `tests/conformance/fixtures/broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py`
- `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_workflows.py`
- `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py`
- `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py`
- The suite keeps its current bounded non-fixture supplements, but only as small explicit add-ons:
- the broader `{1,4}` grouped-conditional `bytes` rows for `a((bc|de){1,4})?(?(1)d|e)` and `a(?P<outer>(bc|de){1,4})?(?(outer)d|e)` remain covered with the current `rebar` skip reason for unsupported bytes parity;
- the broader-range and nested broader-range backtracking branch-trace checks remain covered through one focused generator/helper path instead of being mixed into the main published workflow table.
- The refactor preserves the current parity depth for the existing suite footprint: compile metadata plus match-object parity (`group`, `groups`, `groupdict`, `span`, `start`, `end`, `lastindex`, `lastgroup`, `re.pattern`, `re.flags`, `re.groups`, `re.groupindex`) and the convenience APIs already asserted in this file.
- The suite remains a single backend-parameterized pytest module. Do not add a second wider-ranged-repeat parity file, do not fork a family-specific helper module, and do not widen scope into the separate `{1,3}` grouped-alternation-only manifest `tests/conformance/fixtures/wider_ranged_repeat_quantified_group_alternation_workflows.py`, which this suite does not currently exercise.

## Constraints
- Keep this task on the Python parity surface only. Do not change Rust code, `python/rebar/`, correctness fixtures, benchmark manifests, scorecards, README reporting, or queue/state files beyond this task file.
- Prefer the existing fixture-backed patterns already used by `tests/python/test_quantified_alternation_parity_suite.py` and `tests/python/test_conditional_group_exists_parity_suite.py` over inventing a new parity harness abstraction.
- Preserve the current case ids or explicit test ids where practical so failure output stays legible and still points back to the published manifest rows or bounded supplemental cases.

## Notes
- Build on `RBR-0272`, which already consolidated this frontier into one suite, and on recent fixture-backed cleanup tasks such as `RBR-0355`, `RBR-0353`, and `RBR-0351`.
- This cleanup exists because `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` is still one of the larger remaining parity-suite holdouts that duplicates published correctness cases in a bespoke local scenario table instead of consuming the standard fixture path directly.

## Completion Notes
- Replaced the file-local `Scenario` / `ParityCase` tables in `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` with fixture bundles loaded through `load_fixture_manifest(...)` and `FixtureCase` from the nine published wider-ranged-repeat grouped manifests named in this task.
- Kept the two broader `{1,4}` grouped-conditional `bytes` supplements as small explicit add-ons with the existing `rebar` skip reason, and collapsed the broader-range plus nested broader-range backtracking branch-trace coverage onto one shared generator/helper path.
- Preserved compile metadata parity plus match-object and convenience-API parity for the fixture-backed `search()` / compiled-`Pattern.fullmatch()` rows while keeping the suite as one backend-parameterized pytest module.
- Verified with `.venv/bin/python -m pytest -q tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` (`904 passed, 10 skipped`).
