# RBR-1134: Collapse grouped-quantified pytest id wrappers onto shared parity support

Status: ready
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the last suite-local pytest id wrapper mirrors from the grouped-quantified parity family by routing the open-ended and wider-ranged suites through one canonical shared accessor surface on `tests/python/fixture_parity_support.py` instead of repeating tiny `return case.case_id` and `return case.id` helpers in each suite.

## Deliverables
- `tests/python/fixture_parity_support.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/python/test_open_ended_quantified_group_parity_suite.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`

## Acceptance Criteria
- Add one canonical shared pytest-id accessor path on `tests/python/fixture_parity_support.py`, or reuse a strictly smaller equivalent on that same file, for the two id shapes still mirrored in the grouped-quantified suites:
  - one helper returns `FixtureCase.case_id` for published fixture rows;
  - one helper returns `.id` for the supplemental, bounded-pattern, and trace-case carriers already used by these suites; and
  - keep the cleanup on the existing parity-support module instead of adding another helper file, registry, protocol layer, or detached abstraction.
- `tests/python/test_open_ended_quantified_group_parity_suite.py` stops defining the four suite-local pytest id wrappers and imports the shared parity-support helper surface instead:
  - remove `fixture_case_param_id`, `supplemental_case_param_id`, `bounded_pattern_case_param_id`, and `trace_case_param_id`;
  - preserve the current parametrization ids for fixture, supplemental, bounded-pattern, and trace cases; and
  - keep the suite's current selected frontier, trace coverage, and bytes follow-on coverage unchanged.
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` stops defining the two suite-local pytest id wrappers and imports the same shared parity-support helper surface instead:
  - remove `fixture_case_id` and `named_case_id`;
  - preserve the current parametrization ids for fixture, direct bytes follow-on, bounded-pattern, and backtracking-trace rows; and
  - keep the suite's current direct bytes routing and backtracking trace coverage unchanged.
- Extend `tests/python/test_fixture_parity_support_contract.py` with focused contract coverage for the shared pytest-id accessors:
  - a fixture-case check that proves the shared helper returns `case.case_id`;
  - an `.id`-carrier check that proves the shared helper works for at least two existing grouped-quantified case carriers with different concrete types; and
  - keep the contract localized to the shared helper surface rather than growing another owner-specific contract section.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py::test_compile_metadata_matches_cpython tests/python/test_open_ended_quantified_group_parity_suite.py::test_pattern_bounds_matches_cpython tests/python/test_open_ended_quantified_group_parity_suite.py::test_supplemental_bytes_compile_metadata_matches_cpython tests/python/test_open_ended_quantified_group_parity_suite.py::test_open_ended_module_search_branch_traces_match_cpython tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py::test_compile_metadata_matches_cpython tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py::test_pattern_bounds_matches_cpython tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py::test_direct_bytes_follow_on_compile_metadata_matches_cpython tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py::test_backtracking_module_search_branch_traces_match_cpython`
- `bash -lc "! rg -n 'def (fixture_case_param_id|supplemental_case_param_id|bounded_pattern_case_param_id|trace_case_param_id|fixture_case_id|named_case_id)\\(' tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py"`

## Constraints
- Keep the cleanup structural and limited to the four files above. Do not widen it into implementation code, correctness fixtures, benchmark files, README text, or tracked ops state prose.
- Preserve current pytest param ids, selected case frontiers, trace-case ordering, and bytes follow-on routing behavior in both grouped-quantified suites.
- Prefer deleting suite-local wrapper glue over introducing generic introspection helpers that obscure what id attribute is being used.

## Notes
- `RBR-1134` is the next available unreserved architecture task id in this checkout:
  - the highest live task id across `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, and `ops/tasks/blocked/` is `1133`; and
  - `rg -n 'RBR-1134|RBR-1135|RBR-1136|RBR-1137' ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` returned no reserved future ids in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, and `blocked: 0`;
  - the latest cycle completed both `architecture-implementation` and `feature-implementation` tasks as `done`; and
  - no inherited-dirty checkpoint churn or stalled post-task refresh path is recorded in the current runtime artifacts.
- The live duplication is still concrete and bounded:
  - `tests/python/fixture_parity_support.py` does not yet expose a shared pytest id accessor for `FixtureCase.case_id` or the shared `.id` carriers used by the grouped-quantified suites;
  - `tests/python/test_open_ended_quantified_group_parity_suite.py` still defines four suite-local wrappers that only return `case.case_id` or `case.id`;
  - `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` still defines two suite-local wrappers with the same mirrored behavior; and
  - `rg -n 'def (fixture_case_param_id|supplemental_case_param_id|bounded_pattern_case_param_id|trace_case_param_id|fixture_case_id|named_case_id)\\(' tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` currently matches exactly those six wrapper definitions.
- Verification status in this run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py::test_compile_metadata_matches_cpython tests/python/test_open_ended_quantified_group_parity_suite.py::test_pattern_bounds_matches_cpython tests/python/test_open_ended_quantified_group_parity_suite.py::test_supplemental_bytes_compile_metadata_matches_cpython tests/python/test_open_ended_quantified_group_parity_suite.py::test_open_ended_module_search_branch_traces_match_cpython tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py::test_compile_metadata_matches_cpython tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py::test_pattern_bounds_matches_cpython tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py::test_direct_bytes_follow_on_compile_metadata_matches_cpython tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py::test_backtracking_module_search_branch_traces_match_cpython` returned `636 passed` in this run; and
  - the negative `rg` verification command above currently fails for the exact six suite-local wrapper definitions that this cleanup is meant to delete.
