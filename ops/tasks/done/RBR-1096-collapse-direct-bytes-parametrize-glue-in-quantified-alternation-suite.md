# RBR-1096: Collapse direct-bytes parametrize glue in quantified alternation suite

Status: done
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining direct-bytes parametrize wrapper layer from `tests/python/test_quantified_alternation_parity_suite.py` so that this bounded follow-on block stops rebuilding the same case tuple and anonymous `ids=` adapter seven times during collection.

## Deliverables
- `tests/python/test_quantified_alternation_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_quantified_alternation_parity_suite.py` no longer uses `_direct_bytes_follow_on_cases()` inside any `pytest.mark.parametrize(...)` decorator.
- Replace the current repeated direct-bytes collection glue with one named same-file constant/helper, or a strictly smaller equivalent, while preserving the current parametrized ownership surface for:
  - `test_direct_bytes_follow_on_compile_metadata_matches_cpython`
  - `test_direct_bytes_follow_on_module_search_matches_cpython`
  - `test_direct_bytes_follow_on_module_search_match_convenience_api_matches_cpython`
  - `test_direct_bytes_follow_on_module_search_match_group_access_matches_cpython`
  - `test_direct_bytes_follow_on_pattern_fullmatch_matches_cpython`
  - `test_direct_bytes_follow_on_pattern_fullmatch_match_convenience_api_matches_cpython`
  - `test_direct_bytes_follow_on_pattern_fullmatch_match_group_access_matches_cpython`
- Those seven direct-bytes parametrized tests no longer use `ids=lambda case: case.id`.
- Keep the rendered case ids stable for that direct-bytes block; the rows should still render as each case's existing `case.id`.
- Keep the cleanup structural and file-local to `tests/python/test_quantified_alternation_parity_suite.py`.
- Do not widen this task into `tests/python/fixture_parity_support.py`, correctness fixtures, implementation code, reports, README copy, or tracked state prose.

## Verification
- `./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py -k 'direct_bytes_follow_on_compile_metadata_matches_cpython or direct_bytes_follow_on_module_search_matches_cpython or direct_bytes_follow_on_module_search_match_convenience_api_matches_cpython or direct_bytes_follow_on_module_search_match_group_access_matches_cpython or direct_bytes_follow_on_pattern_fullmatch_matches_cpython or direct_bytes_follow_on_pattern_fullmatch_match_convenience_api_matches_cpython or direct_bytes_follow_on_pattern_fullmatch_match_group_access_matches_cpython'`
- `bash -lc "! rg -n '_direct_bytes_follow_on_cases\\(\\)|ids=lambda case: case\\.id' tests/python/test_quantified_alternation_parity_suite.py | rg '1178|1179|1191|1192|1211|1212|1231|1232|1252|1253|1285|1286|1310|1311'"`

## Constraints
- Prefer deleting the repeated direct-bytes wrapper layer over introducing another registry, support module, or detached abstraction tier.
- Keep the current test names, case ordering, direct-bytes routing, and expected ids intact.
- Do not broaden this into the other remaining `ids=lambda` adapters elsewhere in `tests/python/test_quantified_alternation_parity_suite.py`; keep the task bounded to the direct-bytes follow-on block.

## Notes
- `RBR-1096` is the next available unreserved task id in this checkout:
  - the highest live task id across `ops/tasks/done/`, `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` is `1095`; and
  - `rg -n 'RBR-1096|RBR-1097|RBR-1098|RBR-1099|RBR-1100' ops/state/current_status.md ops/state/backlog.md ops/tasks -g '*.md'` returned only historical mentions inside done-task notes, not a live reservation.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete and current in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest runtime cycle shows the task workers completing cleanly, with no inherited-dirty checkpoint churn or stalled refresh path.
- The live simplification target is the repeated direct-bytes block at lines `1178-1311`:
  - `rg -n '_direct_bytes_follow_on_cases\\(\\)|ids=lambda case: case\\.id' tests/python/test_quantified_alternation_parity_suite.py` returned the seven repeated `_direct_bytes_follow_on_cases()` decorators and their paired anonymous `ids=` adapters in this run.
- The focused verification slice is already green in the live checkout:
  - `./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py -k 'direct_bytes_follow_on_compile_metadata_matches_cpython or direct_bytes_follow_on_module_search_matches_cpython or direct_bytes_follow_on_module_search_match_convenience_api_matches_cpython or direct_bytes_follow_on_module_search_match_group_access_matches_cpython or direct_bytes_follow_on_pattern_fullmatch_matches_cpython or direct_bytes_follow_on_pattern_fullmatch_match_convenience_api_matches_cpython or direct_bytes_follow_on_pattern_fullmatch_match_group_access_matches_cpython'` returned `168 passed, 610 deselected` in this run.

## Completion
- Replaced the repeated direct-bytes decorator glue in `tests/python/test_quantified_alternation_parity_suite.py` with shared `DIRECT_BYTES_FOLLOW_ON_CASES` and `DIRECT_BYTES_FOLLOW_ON_PARAMS` constants so the seven direct-bytes follow-on tests keep the same case ordering and rendered ids without calling `_direct_bytes_follow_on_cases()` or using `ids=lambda case: case.id`.
- Verified with `./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py -k 'direct_bytes_follow_on_compile_metadata_matches_cpython or direct_bytes_follow_on_module_search_matches_cpython or direct_bytes_follow_on_module_search_match_convenience_api_matches_cpython or direct_bytes_follow_on_module_search_match_group_access_matches_cpython or direct_bytes_follow_on_pattern_fullmatch_matches_cpython or direct_bytes_follow_on_pattern_fullmatch_match_convenience_api_matches_cpython or direct_bytes_follow_on_pattern_fullmatch_match_group_access_matches_cpython'` (`168 passed, 610 deselected`) and the task's `rg` acceptance check.
