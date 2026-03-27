## RBR-1451: Localize open-ended direct-bytes case tables onto the owner suite

Owner: architecture-implementation
Created: 2026-03-27

## Goal
- Remove the remaining open-ended owner-specific direct-bytes case tables from `tests/python/fixture_parity_support.py`.
- Keep the open-ended quantified-group direct-bytes data with `tests/python/test_open_ended_quantified_group_parity_suite.py`, and stop letting the detached support-contract suite depend on those owner-specific constants.

## Deliverables
- `tests/python/fixture_parity_support.py`
- `tests/python/test_open_ended_quantified_group_parity_suite.py`
- `tests/python/test_fixture_parity_support_contract.py`

## Acceptance Criteria
- Rewrite `tests/python/test_open_ended_quantified_group_parity_suite.py` so it defines the open-ended direct-bytes case tables it currently imports from `tests.python.fixture_parity_support`:
  - `OPEN_ENDED_ALTERNATION_BYTES_CASES`
  - `NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES`
  - `OPEN_ENDED_CONDITIONAL_BYTES_CASES`
  - `OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES`
  - `BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES`
  - `BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES`
  - `BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES`
- `tests/python/test_open_ended_quantified_group_parity_suite.py` no longer imports those seven constants from `tests.python.fixture_parity_support`, but it keeps the existing bytes-surface routing, expected text maps, follow-on ordering, and parity assertions unchanged.
- Delete those seven constants from `tests/python/fixture_parity_support.py`; do not widen into the other shared grouped-quantified direct-bytes helpers or the branch-local / quantified-alternation / wider-ranged-repeat owner data in this run.
- `tests/python/test_fixture_parity_support_contract.py` stops referencing those seven open-ended owner constants; retire or relocate the leftover owner-specific contract checks instead of recreating another shared data table inside the contract file.
- Keep the run structural only:
  - do not change `python/rebar_harness/`, `python/rebar/`, Rust sources, published reports, or tracked project-state prose
  - do not widen into `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`; that suite currently has unrelated direct-bytes assertion drift in this checkout, so this task must stay isolated to the open-ended owner lane
  - do not add a replacement shared support module under `tests/`

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py`
- `./.venv/bin/python -m py_compile tests/python/fixture_parity_support.py tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_fixture_parity_support_contract.py`
- `rg -n '^(OPEN_ENDED_ALTERNATION_BYTES_CASES|NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES|OPEN_ENDED_CONDITIONAL_BYTES_CASES|OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES|BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES|BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES|BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES) = ' tests/python/test_open_ended_quantified_group_parity_suite.py`
- `bash -lc "! rg -n '^    (BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES|BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES|BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES|NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES|OPEN_ENDED_ALTERNATION_BYTES_CASES|OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES|OPEN_ENDED_CONDITIONAL_BYTES_CASES),?$' tests/python/test_open_ended_quantified_group_parity_suite.py"`
- `bash -lc "! rg -n '^(OPEN_ENDED_ALTERNATION_BYTES_CASES|NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES|OPEN_ENDED_CONDITIONAL_BYTES_CASES|OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES|BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES|BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES|BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES) = ' tests/python/fixture_parity_support.py"`
- `bash -lc "! rg -n 'OPEN_ENDED_ALTERNATION_BYTES_CASES|NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES|OPEN_ENDED_CONDITIONAL_BYTES_CASES|OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES|BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES|BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES|BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES' tests/python/test_fixture_parity_support_contract.py"`

## Notes
- Completed 2026-03-27: moved the seven open-ended direct-bytes supplemental tables into `tests/python/test_open_ended_quantified_group_parity_suite.py`, deleted their shared-support definitions from `tests/python/fixture_parity_support.py`, and retired the leftover contract checks in `tests/python/test_fixture_parity_support_contract.py` that referenced those owner-specific constants.
- Verification: `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py`; `./.venv/bin/python -m py_compile tests/python/fixture_parity_support.py tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_fixture_parity_support_contract.py`; the task’s positive and negative `rg` checks all passed after the move.
- Queue and JSON check in this planning run:
  - `.rebar/runtime/dashboard.md` reported `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the runtime JSON count was not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and identifier check in this planning run:
  - `ops/tasks/blocked/` contained no architecture task to reopen or normalize first.
  - `rg -n 'RBR-1451|RBR-1452|RBR-1453|RBR-1454' ops/state/current_status.md ops/state/backlog.md` returned no matches, so `RBR-1451` was available.
- Candidate selection in this planning run:
  - `tests/python/fixture_parity_support.py` still defines the seven open-ended direct-bytes case tables at lines `537-633`, but after `RBR-1449` no benchmark or correctness-publication owner still depends on them.
  - `tests/python/test_open_ended_quantified_group_parity_suite.py` is now the only live owner that imports those seven constants, and `tests/python/test_fixture_parity_support_contract.py` still carries four residual references to the open-ended tables even though `RBR-0667` already moved the broader open-ended direct-bytes ownership contract onto the owner suite.
  - Keeping those owner-specific bytes tables in `tests/python/fixture_parity_support.py` preserves an unnecessary cross-suite data layer after the non-parity consumers were already removed.
  - A broader grouped-quantified cleanup candidate was rejected for this run because `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py tests/python/test_fixture_parity_support_contract.py` is already red on unrelated wider-ranged-repeat direct-bytes drift in the current checkout.
- Verification status in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py` passed (`3902 passed in 2.51s`).
  - `./.venv/bin/python -m py_compile tests/python/fixture_parity_support.py tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_fixture_parity_support_contract.py` passed.
  - `rg -n '^(OPEN_ENDED_ALTERNATION_BYTES_CASES|NESTED_OPEN_ENDED_ALTERNATION_BYTES_CASES|OPEN_ENDED_CONDITIONAL_BYTES_CASES|OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES|BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES|BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BYTES_CASES|BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BYTES_CASES) = ' tests/python/test_open_ended_quantified_group_parity_suite.py` is intentionally red in the current checkout because the owner suite still imports those tables instead of defining them locally.
  - The three negative `rg` verifications are intentionally red in the current checkout because the owner import lines, shared-support definitions, and detached-contract references are the exact boundary this task removes.
