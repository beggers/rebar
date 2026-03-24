# RBR-1140: Collapse grouped quantified trace builders onto shared parity support

Status: ready
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining repeated compile-case-prefix stripping and `PatternTraceCase` branch-order builders from the grouped quantified parity suites by routing them through one shared helper surface on `tests/python/fixture_parity_support.py` instead of keeping nine near-duplicate local builders across the open-ended and wider-ranged-repeat owners.

## Deliverables
- `tests/python/fixture_parity_support.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/python/test_open_ended_quantified_group_parity_suite.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`

## Acceptance Criteria
- Add one bounded shared helper surface on `tests/python/fixture_parity_support.py` for compile-derived branch trace generation that covers the two duplicated shapes still live in the grouped quantified owners:
  - stripping the standard `-compile-metadata-str` / `-compile-metadata-bytes` suffixes from a compile case id to produce the stable trace prefix; and
  - expanding compile cases plus an ordered branch-text mapping and repetition-count range into ordered `PatternTraceCase` rows with stable ids, search texts, and fullmatch texts.
- Keep the helper(s) on the existing parity-support module instead of adding another helper file, registry, or data-description layer.
- `tests/python/test_open_ended_quantified_group_parity_suite.py` stops defining its suite-local `_compile_case_prefix(...)` helper and its seven suite-local trace builders:
  - remove `_build_open_ended_trace_cases`;
  - remove `_build_broader_range_open_ended_trace_cases`;
  - remove `_build_broader_range_open_ended_conditional_trace_cases`;
  - remove `_build_open_ended_bytes_trace_cases`;
  - remove `_build_broader_range_open_ended_conditional_bytes_trace_cases`;
  - remove `_build_open_ended_backtracking_trace_cases`;
  - remove `_build_open_ended_backtracking_bytes_trace_cases`;
  - preserve the current `OPEN_ENDED_*TRACE_CASES` values, `EXPECTED_*FULLMATCH_TEXTS` sets, branch-order coverage, `bytes`/`str` distinctions, and pytest ids exactly.
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` stops defining its suite-local `_build_backtracking_trace_cases(...)` helper and uses the same shared helper path instead:
  - preserve the current `BACKTRACKING_TRACE_CASES` contents, `EXPECTED_BACKTRACKING_FULLMATCH_TEXTS`, numbered/named variant coverage, and pytest ids exactly.
- Keep the explicit frontier declarations readable in the owner suites:
  - leave `OPEN_ENDED_BRANCH_TEXT`, `OPEN_ENDED_BACKTRACKING_BRANCH_TEXT`, `BACKTRACKING_BRANCH_TEXT`, the suite-local compile-pattern anchors, and the `EXPECTED_*FULLMATCH_TEXTS` declarations local;
  - do not move the bytes follow-on tables, bounded-pattern tables, or manifest/bundle declarations into the helper module.
- Extend `tests/python/test_fixture_parity_support_contract.py` with focused contract coverage for the new shared trace-builder surface:
  - one check proves compile-case prefix extraction preserves the current prefix for both `str` and `bytes` compile ids;
  - one check proves the shared trace builder preserves ordered ids and search/fullmatch text materialization for a representative open-ended branch map; and
  - one check proves the same builder preserves the numbered/named variant expansion shape used by the wider-ranged-repeat backtracking traces.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py::test_id_attribute_pytest_id_returns_case_id_attribute tests/python/test_open_ended_quantified_group_parity_suite.py::test_open_ended_trace_cases_cover_all_declared_branch_orders tests/python/test_open_ended_quantified_group_parity_suite.py::test_broader_range_open_ended_trace_cases_cover_all_declared_branch_orders tests/python/test_open_ended_quantified_group_parity_suite.py::test_broader_range_open_ended_conditional_trace_cases_cover_all_declared_branch_orders tests/python/test_open_ended_quantified_group_parity_suite.py::test_open_ended_bytes_trace_cases_cover_all_declared_branch_orders tests/python/test_open_ended_quantified_group_parity_suite.py::test_broader_range_open_ended_conditional_bytes_trace_cases_cover_all_declared_branch_orders tests/python/test_open_ended_quantified_group_parity_suite.py::test_open_ended_backtracking_trace_cases_cover_all_declared_branch_orders tests/python/test_open_ended_quantified_group_parity_suite.py::test_open_ended_backtracking_bytes_trace_cases_cover_all_declared_branch_orders tests/python/test_open_ended_quantified_group_parity_suite.py::test_open_ended_module_search_branch_traces_match_cpython tests/python/test_open_ended_quantified_group_parity_suite.py::test_open_ended_pattern_fullmatch_branch_traces_match_cpython tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py::test_backtracking_trace_cases_cover_all_declared_branch_orders tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py::test_backtracking_module_search_branch_traces_match_cpython tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py::test_backtracking_pattern_fullmatch_branch_traces_match_cpython`
- `bash -lc "! rg -n 'def (_compile_case_prefix|_build_open_ended_trace_cases|_build_broader_range_open_ended_trace_cases|_build_broader_range_open_ended_conditional_trace_cases|_build_open_ended_bytes_trace_cases|_build_broader_range_open_ended_conditional_bytes_trace_cases|_build_open_ended_backtracking_trace_cases|_build_open_ended_backtracking_bytes_trace_cases|_build_backtracking_trace_cases)\\(' tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py"`

## Constraints
- Keep the cleanup structural and limited to the four files above. Do not widen it into implementation code, correctness fixtures, benchmark files, README text, or tracked ops state prose.
- Prefer deleting duplicated suite-local trace-construction mechanics over introducing a broader abstraction that hides which branch maps or repetition ranges each owner is exercising.
- Preserve the current trace-case ordering, ids, search/fullmatch text payloads, parity failure messages, and `bytes` encoding behavior in both suites.

## Notes
- `RBR-1140` is the next available unreserved architecture task id in this checkout:
  - `ops/tasks/ready/` and `ops/tasks/in_progress/` are empty in this run;
  - `ops/tasks/blocked/` only contains feature tasks `RBR-1133` and `RBR-1135`; and
  - `rg -n "RBR-1140|RBR-1141|RBR-1142|RBR-1143" ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` only matched historical notes inside completed task files and did not reveal a live reserved task at `RBR-1140`.
- No blocked architecture task exists to reopen or retire first in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The live duplication is concrete and cross-file:
  - `tests/python/fixture_parity_support.py` already exports `PatternTraceCase`, but it still lacks a shared helper that owns compile-id prefix extraction and compile-derived branch-trace expansion;
  - `tests/python/test_open_ended_quantified_group_parity_suite.py` still defines `_compile_case_prefix(...)` plus seven local trace builders; and
  - `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` still defines `_build_backtracking_trace_cases(...)` for the same `PatternTraceCase` materialization shape.
- Verification status in this run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py::test_id_attribute_pytest_id_returns_case_id_attribute tests/python/test_open_ended_quantified_group_parity_suite.py::test_open_ended_trace_cases_cover_all_declared_branch_orders tests/python/test_open_ended_quantified_group_parity_suite.py::test_broader_range_open_ended_trace_cases_cover_all_declared_branch_orders tests/python/test_open_ended_quantified_group_parity_suite.py::test_broader_range_open_ended_conditional_trace_cases_cover_all_declared_branch_orders tests/python/test_open_ended_quantified_group_parity_suite.py::test_open_ended_bytes_trace_cases_cover_all_declared_branch_orders tests/python/test_open_ended_quantified_group_parity_suite.py::test_broader_range_open_ended_conditional_bytes_trace_cases_cover_all_declared_branch_orders tests/python/test_open_ended_quantified_group_parity_suite.py::test_open_ended_backtracking_trace_cases_cover_all_declared_branch_orders tests/python/test_open_ended_quantified_group_parity_suite.py::test_open_ended_backtracking_bytes_trace_cases_cover_all_declared_branch_orders tests/python/test_open_ended_quantified_group_parity_suite.py::test_open_ended_module_search_branch_traces_match_cpython tests/python/test_open_ended_quantified_group_parity_suite.py::test_open_ended_pattern_fullmatch_branch_traces_match_cpython tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py::test_backtracking_trace_cases_cover_all_declared_branch_orders tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py::test_backtracking_module_search_branch_traces_match_cpython tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py::test_backtracking_pattern_fullmatch_branch_traces_match_cpython` returned `971 passed` in this run.
  - `bash -lc "! rg -n 'def (_compile_case_prefix|_build_open_ended_trace_cases|_build_broader_range_open_ended_trace_cases|_build_broader_range_open_ended_conditional_trace_cases|_build_open_ended_bytes_trace_cases|_build_broader_range_open_ended_conditional_bytes_trace_cases|_build_open_ended_backtracking_trace_cases|_build_open_ended_backtracking_bytes_trace_cases|_build_backtracking_trace_cases)\\(' tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py"` currently fails only because those duplicated local builders are still present, which is the exact cleanup this task queues.
