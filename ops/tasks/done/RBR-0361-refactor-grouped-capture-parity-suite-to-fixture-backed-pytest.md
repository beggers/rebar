# RBR-0361: Refactor the grouped-capture parity suite onto the shared fixture-backed pytest path

Status: done
Owner: architecture-implementation
Created: 2026-03-15

## Goal
- Remove the file-local `ParityCase` frontier table from `tests/python/test_grouped_capture_parity_suite.py` so the suite reuses the published correctness fixtures it already mirrors, while keeping any remaining miss-only observations as small explicit supplements.

## Deliverables
- `tests/python/test_grouped_capture_parity_suite.py`

## Acceptance Criteria
- The suite loads its published grouped, named-group, optional-group, and nested-group parity cases through `rebar_harness.correctness.load_fixture_manifest(...)` and `FixtureCase` instead of restating those workflows in the local `ParityCase` dataclass and `CASES` tuple.
- Case selection is driven from exactly these existing published fixture modules, which already define the frontier this suite exercises today:
- `tests/conformance/fixtures/grouped_match_workflows.py`
- `tests/conformance/fixtures/named_group_workflows.py`
- `tests/conformance/fixtures/optional_group_workflows.py`
- `tests/conformance/fixtures/nested_group_workflows.py`
- The refactor keeps the suite's current footprint narrow. Do not widen it into unrelated grouped manifests, and do not pull in the entire folded systematic optional-group corpus unless a small filtered subset is the cleanest way to preserve the current numbered and named optional-group coverage already asserted in this file.
- The refactor preserves the current parity depth for the existing suite footprint: compile metadata plus match-object parity (`group`, `groups`, `groupdict`, `span`, `start`, `end`, `lastindex`, `lastgroup`, `re.pattern`, `re.flags`, `re.groups`, `re.groupindex`) and the convenience APIs already asserted here (`Match.__getitem__` and `expand(...)`).
- Any current miss-only observations that are not represented directly by the published fixture rows above stay covered only as small explicit supplements derived from the loaded fixture-backed cases or compile patterns. Do not leave behind another hand-maintained frontier table.
- The suite remains a single backend-parameterized pytest module. Do not split the grouped-capture frontier into additional files, do not introduce a new helper module, and do not change the correctness fixtures themselves.

## Constraints
- Keep this task on the Python parity surface only. Do not change Rust code, `python/rebar/`, correctness fixtures, benchmark manifests, scorecards, README reporting, or queue/state files beyond this task file.
- Prefer the existing fixture-backed patterns already used by `tests/python/test_conditional_group_exists_parity_suite.py`, `tests/python/test_quantified_alternation_parity_suite.py`, and the recent cleanup tasks `RBR-0357` and `RBR-0359` over inventing another parity harness abstraction.
- Preserve the current case ids or explicit test ids where practical so failure output still points back to published manifest rows or the bounded supplemental misses.

## Notes
- `tests/python/test_grouped_capture_parity_suite.py` is now the clearest remaining grouped parity holdout that still duplicates published fixture data in a bespoke local case table instead of consuming the standard manifest path directly.
- `tests/conformance/fixtures/grouped_match_workflows.py` already carries the bounded `(ab)(c)` multi-capture fullmatch rows that the suite asserts today, while the named, optional, and nested grouped shapes are already published through their dedicated manifests.

## Completion Notes
- Replaced the file-local `ParityCase` table in `tests/python/test_grouped_capture_parity_suite.py` with four fixture bundles loaded through `load_fixture_manifest(...)` and `FixtureCase` from the grouped, named-group, optional-group, and nested-group manifests named in this task.
- Kept the suite footprint narrow by selecting only the existing grouped-capture rows it already exercised, including the non-systematic optional-group subset, while deriving compile metadata coverage from the loaded fixture-backed patterns.
- Preserved the current match-object and convenience-API parity depth and kept the remaining miss-only observations as a small explicit supplement keyed by loaded fixture case ids instead of another pattern/helper frontier table.
- Verified with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py` (`89 passed`).
