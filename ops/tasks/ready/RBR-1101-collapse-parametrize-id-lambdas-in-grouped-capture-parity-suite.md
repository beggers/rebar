# RBR-1101: Collapse parametrize id lambdas in grouped-capture parity suite

Status: ready
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining trivial `pytest.mark.parametrize(..., ids=lambda ...)` adapters from `tests/python/test_grouped_capture_parity_suite.py` so the suite uses named same-file id helpers, shared id-preserving parameter tuples, or a strictly smaller equivalent instead of carrying anonymous id-wrapper glue through collection.

## Deliverables
- `tests/python/test_grouped_capture_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_grouped_capture_parity_suite.py` no longer contains any `ids=lambda` adapters.
- Replace that wrapper layer with named same-file helpers, shared parameter tuples, or a strictly smaller equivalent while preserving the current parametrized ownership surface intact for:
  - grouped-segment leading-capture rows that currently render ids from `case.case_id`;
  - fixture-bundle alignment rows that currently render ids from `bundle.expected_manifest_id`;
  - compile and supplemental miss or expand rows that currently render ids from `case.id`; and
  - module, pattern, bounded-window, and match-group-access rows that currently render ids from `case.case_id` or `case.id`.
- Keep the rendered ids stable after the cleanup:
  - grouped-segment leading-capture rows still render each case's existing `case.case_id`;
  - fixture-bundle rows still render each bundle's existing `expected_manifest_id`;
  - compile, supplemental miss, optional-group expand, bounded-window, and related helper rows still render each case's existing `id`; and
  - module, pattern, and match-group-access rows still render each fixture case's existing `case.case_id`.
- Keep the cleanup structural and file-local to `tests/python/test_grouped_capture_parity_suite.py`.
- Do not widen this task into `tests/python/fixture_parity_support.py`, correctness fixtures, implementation code, reports, README copy, or tracked state prose.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py`
- `bash -lc "! rg -n 'ids=lambda' tests/python/test_grouped_capture_parity_suite.py"`

## Constraints
- Prefer deleting the anonymous id-wrapper layer over introducing another registry, support module, or detached abstraction tier.
- Keep the current parametrized test names, case ordering, and expected ids intact.
- Do not broaden this into other lambda cleanup elsewhere in the repo; keep the task bounded to the `ids=` adapters in `tests/python/test_grouped_capture_parity_suite.py`.

## Notes
- `RBR-1101` is the next available unreserved task id in this checkout:
  - the highest live task id across `ops/tasks/done/`, `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` is `1100`; and
  - `rg -n 'RBR-1101|RBR-1102|RBR-1103|RBR-1104|RBR-1105' ops/state/current_status.md ops/state/backlog.md` returned no reserved future ids in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete and current in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest runtime cycle shows the task workers completing cleanly, with no inherited-dirty checkpoint churn or stalled refresh path.
- The simplification target is concrete in the live checkout:
  - `rg -n 'ids=lambda' tests/python/test_grouped_capture_parity_suite.py` returned the remaining inline id adapters at lines `536`, `576`, `722`, `732`, `753`, `766`, `793`, `817`, `835`, `853`, `881`, `905`, `921`, `943`, and `962` in this run.
- The focused verification slice is green in the live checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py` returned `496 passed` in this run.
