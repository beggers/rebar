# RBR-0359: Refactor the open-ended quantified-group parity suite onto the shared fixture-backed pytest path

Status: done
Owner: architecture-implementation
Created: 2026-03-15

## Goal
- Remove the file-local `ParityCase` frontier table from `tests/python/test_open_ended_quantified_group_parity_suite.py` so the suite reuses the published correctness fixtures it already mirrors, while keeping any remaining non-published miss coverage as small explicit supplements.

## Deliverables
- `tests/python/test_open_ended_quantified_group_parity_suite.py`

## Acceptance Criteria
- The suite loads its published `str` compile, `module.search()`, and compiled-`Pattern.fullmatch()` parity cases through `rebar_harness.correctness.load_fixture_manifest(...)` and `FixtureCase` instead of restating those workflows in the local `ParityCase` dataclass and `CASES` tuple.
- Case selection is driven from exactly these existing published fixture modules, which already define the frontier this suite exercises today:
- `tests/conformance/fixtures/open_ended_quantified_group_alternation_workflows.py`
- `tests/conformance/fixtures/open_ended_quantified_group_alternation_conditional_workflows.py`
- `tests/conformance/fixtures/open_ended_quantified_group_alternation_backtracking_heavy_workflows.py`
- `tests/conformance/fixtures/broader_range_open_ended_quantified_group_alternation_workflows.py`
- `tests/conformance/fixtures/broader_range_open_ended_quantified_group_alternation_conditional_workflows.py`
- `tests/conformance/fixtures/broader_range_open_ended_quantified_group_alternation_backtracking_heavy_workflows.py`
- `tests/conformance/fixtures/nested_open_ended_quantified_group_alternation_workflows.py`
- The refactor preserves the current parity depth for the existing suite footprint: compile metadata plus match-object parity (`group`, `groups`, `groupdict`, `span`, `start`, `end`, `lastindex`, `lastgroup`, `re.pattern`, `re.flags`, `re.groups`, `re.groupindex`) and the convenience APIs already asserted in this file (`Match.__getitem__` and `expand(...)`).
- If any current miss-only observations are not represented by the published fixture rows above, keep them only as small explicit add-ons derived from the loaded compile patterns or manifest bundles rather than another hand-maintained frontier table. Do not leave a second `ParityCase`-style structure behind.
- The suite remains a single backend-parameterized pytest module. Do not split the open-ended frontier into additional files, do not introduce a new helper module, and do not change the correctness fixtures themselves.

## Constraints
- Keep this task on the Python parity surface only. Do not change Rust code, `python/rebar/`, correctness fixtures, benchmark manifests, scorecards, README reporting, or queue/state files beyond this task file.
- Prefer the existing fixture-backed shapes already used by `tests/python/test_quantified_alternation_parity_suite.py` and `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` over inventing another parity harness abstraction.
- Preserve the current case ids or explicit test ids where practical so failure output still points back to the published manifest rows or the bounded supplemental misses.

## Notes
- Build on `RBR-0263`, which already consolidated this frontier into one pytest suite, and on recent fixture-backed cleanup tasks such as `RBR-0351`, `RBR-0355`, and `RBR-0357`.
- This cleanup exists because `tests/python/test_open_ended_quantified_group_parity_suite.py` still carries a large local frontier table even though the same bounded open-ended grouped slice is already published through standard correctness fixtures.

## Completion Notes
- Replaced the file-local `ParityCase` frontier table in `tests/python/test_open_ended_quantified_group_parity_suite.py` with fixture bundles loaded through `load_fixture_manifest(...)` and `FixtureCase` from the seven published open-ended grouped manifests named in this task.
- Kept the suite as one backend-parameterized pytest module and preserved compile metadata parity plus the existing match-object and convenience-API assertions for fixture-backed `module.search()` and compiled-`Pattern.fullmatch()` rows.
- Confirmed the current suite footprint is fully represented by the published fixture rows, so no supplemental miss-only table remains.
- Verified with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py` (`376 passed`).
