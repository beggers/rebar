# RBR-1100: Collapse parametrize id lambdas in wider-ranged-repeat quantified-group parity suite

Status: done
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining trivial `pytest.mark.parametrize(..., ids=lambda ...)` adapters from `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` so the suite uses named same-file id helpers, or a strictly smaller equivalent, instead of carrying anonymous id-wrapper glue through collection.

## Deliverables
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` no longer contains any `ids=lambda` adapters.
- Replace that wrapper layer with named same-file helpers, shared parameter tuples, or a strictly smaller equivalent while preserving the current parametrized ownership surface intact for:
  - fixture-bundle alignment rows that currently render ids from `bundle.expected_manifest_id`;
  - direct-bytes follow-on surface rows that currently render ids from `surface.id` or `spec.id`;
  - compile/module/pattern fixture-case parity rows that currently render ids from `case.case_id`; and
  - bounded-window, direct-bytes follow-on case, and backtracking-trace rows that currently render ids from `case.id`.
- Keep the rendered ids stable after the cleanup:
  - fixture-bundle rows still render as each bundle's existing `expected_manifest_id`;
  - direct-bytes surface rows still render as each surface or spec's existing `id`;
  - compile/module/pattern fixture rows still render as each fixture case's existing `case.case_id`; and
  - bounded-window, direct-bytes follow-on case, and trace rows still render as each case's existing `id`.
- Keep the cleanup structural and file-local to `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`.
- Do not widen this task into `tests/python/fixture_parity_support.py`, correctness fixtures, implementation code, reports, README copy, or tracked state prose.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
- `bash -lc "! rg -n 'ids=lambda' tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py"`

## Constraints
- Prefer deleting the anonymous id-wrapper layer over introducing another registry, support module, or detached abstraction tier.
- Keep the current parametrized test names, case ordering, direct-bytes routing split, and expected ids intact.
- Do not broaden this into other lambda cleanup elsewhere in the repo; keep the task bounded to the `ids=` adapters in `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`.

## Notes
- `RBR-1100` is the next available unreserved task id in this checkout:
  - the highest live task id across `ops/tasks/done/`, `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` is `1099`; and
  - `rg -n 'RBR-1100|RBR-1101|RBR-1102|RBR-1103|RBR-1104|RBR-1105' ops/state/current_status.md ops/state/backlog.md ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked` returned only historical mentions inside done-task notes in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete and current in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest runtime cycle shows the task workers completing cleanly, with no inherited-dirty checkpoint churn or stalled refresh path.
- The simplification target is concrete in the live checkout:
  - `rg -n 'ids=lambda' tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` returned the remaining inline id adapters at lines `470`, `484`, `688`, `711`, `802`, `820`, `834`, `843`, `857`, `871`, `885`, `899`, `914`, `932`, `945`, `969`, `989`, `1010`, `1039`, `1064`, `1087`, and `1102` in this run.
- The focused verification slice is green in the live checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` returned `1353 passed` in this run.

## Completion
- Replaced every remaining file-local `ids=lambda ...` adapter in `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` with named helpers and a shared `DIRECT_BYTES_FOLLOW_ON_CASES` tuple, preserving the existing collected ids for fixture bundles, direct-bytes surfaces, fixture cases, bounded-window cases, direct-bytes follow-on cases, and backtracking trace rows.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
  - `bash -lc "! rg -n 'ids=lambda' tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py"`
