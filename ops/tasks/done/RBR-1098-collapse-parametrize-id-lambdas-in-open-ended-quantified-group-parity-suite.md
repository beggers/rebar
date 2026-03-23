# RBR-1098: Collapse parametrize id lambdas in open-ended quantified-group parity suite

Status: done
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining trivial `pytest.mark.parametrize(..., ids=lambda ...)` adapters from `tests/python/test_open_ended_quantified_group_parity_suite.py` so the suite uses named same-file id helpers, or a strictly smaller equivalent, instead of carrying a large anonymous wrapper layer through collection.

## Deliverables
- `tests/python/test_open_ended_quantified_group_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_open_ended_quantified_group_parity_suite.py` no longer contains any `ids=lambda` adapters.
- Replace that wrapper layer with named same-file helpers, shared parameter tuples, or a strictly smaller equivalent while preserving the current parametrized ownership surface intact for:
  - fixture-bundle alignment and bytes-surface anchor tests that currently render ids from `bundle.expected_manifest_id`, `spec.bundle.manifest.manifest_id`, and `spec.follow_on_id`;
  - compile/module/pattern fixture-case parity tests that currently render ids from `case.case_id`; and
  - trace, bounded-window, supplemental-no-match, and bytes-trace follow-ons that currently render ids from `case.id`.
- Keep the rendered ids stable after the cleanup:
  - bundle rows still render as each bundle's existing `expected_manifest_id`;
  - bytes-surface rows still render as each spec's existing manifest id or follow-on id;
  - compile/module/pattern fixture rows still render as each fixture case's existing `case.case_id`; and
  - trace/bounds/supplemental rows still render as each case's existing `case.id`.
- Keep the cleanup structural and file-local to `tests/python/test_open_ended_quantified_group_parity_suite.py`.
- Do not widen this task into `tests/python/fixture_parity_support.py`, correctness fixtures, implementation code, reports, README copy, or tracked state prose.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py`
- `bash -lc "! rg -n 'ids=lambda' tests/python/test_open_ended_quantified_group_parity_suite.py"`

## Constraints
- Prefer deleting the anonymous id-wrapper layer over introducing another registry, support module, or detached abstraction tier.
- Keep the current parametrized test names, case ordering, bytes routing split, and expected ids intact.
- Do not broaden this into other duplication cleanup elsewhere in the repo; keep the task bounded to the `ids=` adapters in `tests/python/test_open_ended_quantified_group_parity_suite.py`.

## Notes
- Completed 2026-03-23: replaced every remaining `ids=lambda ...` adapter in `tests/python/test_open_ended_quantified_group_parity_suite.py` with same-file named id helpers, preserving the existing rendered ids for bundle, bytes-surface, fixture-case, bounded-window, supplemental-bytes, and trace parametrizations.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py` (`3902 passed`) and `bash -lc "! rg -n 'ids=lambda' tests/python/test_open_ended_quantified_group_parity_suite.py"`.
- `RBR-1098` is the next available unreserved task id in this checkout:
  - the highest live task id across `ops/tasks/done/`, `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` is `1097`; and
  - `rg -n 'RBR-1098|RBR-1099|RBR-1100|RBR-1101|RBR-1102' ops/state/current_status.md ops/state/backlog.md -g '*.md'` returned no reserved future ids in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete and current in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest runtime cycle shows the task workers completing cleanly, with no inherited-dirty checkpoint churn or stalled refresh path.
- The simplification target is concrete in the live checkout:
  - `rg -n 'ids=lambda' tests/python/test_open_ended_quantified_group_parity_suite.py` returned the remaining inline id adapters at lines `677`, `713`, `782`, `821`, `1240`, `1258`, `1275`, `1288`, `1312`, `1332`, `1353`, `1382`, `1407`, `1430`, `1439`, `1452`, `1466`, `1480`, `1493`, `1508`, `1531`, `1550`, `1574`, `1593`, `1617`, `1638`, `1661`, `1678`, `1703`, `1722`, `1746`, `1767`, `1790`, and `1804` in this run.
- The focused verification slice is green in the live checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py` returned `3902 passed` in this run.
