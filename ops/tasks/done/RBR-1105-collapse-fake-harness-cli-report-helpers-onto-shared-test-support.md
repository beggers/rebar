# RBR-1105: Collapse fake harness CLI report helpers onto shared test support

Status: done
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the duplicated fake harness CLI/report-writing glue now split between `tests/python/test_shared_test_support_contract.py` and `tests/python/test_ops_harness.py` by moving that support onto the existing shared test-support surface instead of keeping two owner-local copies of the same subprocess/report-path plumbing.

## Deliverables
- `tests/conftest.py`
- `tests/python/test_shared_test_support_contract.py`
- `tests/python/test_ops_harness.py`

## Acceptance Criteria
- Add one shared helper surface in `tests/conftest.py`, or a strictly smaller equivalent on the existing shared test-support path, that covers the fake harness CLI plumbing both owner files currently restate:
  - building `subprocess.CompletedProcess[str]` values for mocked harness CLI calls; and
  - resolving the `--report` path from mocked CLI args so tests can write synthetic scorecards through one shared path.
- `tests/python/test_shared_test_support_contract.py` stops carrying owner-local copies of:
  - `completed_process(...)`; and
  - `_report_path_from_cli_args(...)`.
- `tests/python/test_ops_harness.py` stops carrying its owner-local `completed_process(...)` helper and stops hand-parsing `--report` inside the three `fake_run_harness_cli(...)` scorecard tests around the `run_harness_scorecard(...)` contract.
- Keep the existing harness-helper coverage intact after the cleanup:
  - the shared-test-support `run_harness_cli(...)` and `run_harness_scorecard(...)` contract tests still pass;
  - the ops-harness tests that validate scorecard loading from mocked JSON and Python reports still pass; and
  - current CLI arg ordering, synthetic report filenames, and summary payload assertions stay unchanged.
- Keep the cleanup structural and limited to shared test support plus the two owner files above. Do not edit `python/rebar_harness/`, implementation code, reports, README copy, or tracked state prose.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_shared_test_support_contract.py tests/python/test_ops_harness.py -k 'run_harness_scorecard'`
- `bash -lc "! rg -n '^def completed_process\\(|^def _report_path_from_cli_args\\(|index\\(\\\"--report\\\"\\)' tests/python/test_shared_test_support_contract.py tests/python/test_ops_harness.py"`

## Constraints
- Prefer extending the existing shared support surface in `tests/conftest.py` over adding a new support module, registry, or detached abstraction tier.
- Preserve the current mocked CLI behavior, report contents, and test ids; this task is about deleting duplicate support glue, not changing harness semantics.
- Do not widen the task into broader `subprocess` mocking cleanup elsewhere in the suite.

## Notes
- `RBR-1105` is the next available unreserved task id in this checkout:
  - the highest live task id across `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, and `ops/tasks/blocked/` is `1104`; and
  - `rg -n 'RBR-1105|RBR-1106|RBR-1107|RBR-1108|RBR-1109|RBR-1110' ops/state/current_status.md ops/state/backlog.md` returned no reserved future ids in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete and current in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest runtime cycle shows both task workers completing `done`, with no inherited-dirty checkpoint churn or stalled refresh path.
- The simplification target is concrete in the live checkout:
  - `tests/python/test_shared_test_support_contract.py:26` and `tests/python/test_ops_harness.py:19` each define an owner-local `completed_process(...)` helper today; and
  - `tests/python/test_shared_test_support_contract.py:47` plus `tests/python/test_ops_harness.py:1736-1738`, `tests/python/test_ops_harness.py:1777-1778`, and `tests/python/test_ops_harness.py:1816-1817` each hand-parse `--report` from mocked CLI args in this run.
- The focused verification slice is green in the live checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_shared_test_support_contract.py tests/python/test_ops_harness.py -k 'run_harness_scorecard'` returned `10 passed, 81 deselected, 2 subtests passed` in this run.

## Completion Notes
- Added shared `completed_process(...)` and `report_path_from_cli_args(...)` helpers in `tests/conftest.py` so fake harness CLI result construction and `--report` path resolution now live on the shared test-support surface.
- Removed the owner-local `completed_process(...)` and `_report_path_from_cli_args(...)` copies from `tests/python/test_shared_test_support_contract.py`, and switched the scorecard contract mocks to the shared helpers.
- Removed the owner-local `completed_process(...)` copy from `tests/python/test_ops_harness.py` and replaced the three hand-parsed `--report` lookups in the mocked scorecard tests with the shared helper.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_shared_test_support_contract.py tests/python/test_ops_harness.py -k 'run_harness_scorecard'`
  - `bash -lc "! rg -n '^def completed_process\\(|^def _report_path_from_cli_args\\(|index\\(\\\"--report\\\"\\)' tests/python/test_shared_test_support_contract.py tests/python/test_ops_harness.py"`
