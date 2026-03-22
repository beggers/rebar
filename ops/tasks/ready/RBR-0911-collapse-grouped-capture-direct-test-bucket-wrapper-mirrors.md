# RBR-0911: Collapse grouped-capture direct-test bucket wrapper mirrors

Status: ready
Owner: architecture-implementation
Created: 2026-03-22

## Goal
- Remove the detached `_bundle_case_ids()`, `_grouped_capture_direct_test_bundles()`, and `_grouped_capture_direct_test_case_id_buckets()` wrappers from `tests/python/test_grouped_capture_parity_suite.py`, so the grouped-capture direct-frontier coverage test derives its bucket labels and selected case ids straight from the live owner bundles that file already loads instead of maintaining an extra helper stack around `bundle.cases`.

## Deliverables
- `tests/python/test_grouped_capture_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_grouped_capture_parity_suite.py` no longer defines or reads `_bundle_case_ids()`, `_grouped_capture_direct_test_bundles()`, or `_grouped_capture_direct_test_case_id_buckets()`:
  - delete all three helpers instead of replacing them with another detached case-id helper layer; and
  - if any local structure remains, keep it as one tiny live ordered tuple of `(bucket_label, bundle)` entries or an equivalent inline construction over the existing bundle constants, not a second case-id mirror.
- `test_grouped_capture_direct_test_buckets_cover_selected_frontier()` is rewired through live owner-bundle data:
  - derive the bucket labels from the existing grouped-capture bundle constants already loaded in this file, preserving the current ordered label sequence exactly as:
    - `grouped-match`
    - `named-group`
    - `grouped-segment`
    - `grouped-alternation`
    - `optional-group`
    - `optional-group-alternation`
    - `nested-group`
    - `nested-group-alternation`
  - derive each bucket value as the `frozenset` of `case.case_id` values from the corresponding bundle's live `cases`;
  - derive the `selected_case_ids` argument for `assert_direct_test_case_id_buckets_cover_selected_frontier()` directly from the same ordered bundle entries and their live `cases`;
  - keep `coverage_label="grouped capture direct-test case-id buckets"` unchanged; and
  - preserve the current frontier exactly, with no added or dropped grouped-capture case ids.
- Keep this cleanup structural only:
  - do not change grouped-capture fixture contents, match-parity behavior, generated miss cases, replacement-expansion coverage, harness support modules, or tracked project-state prose; and
  - do not widen into a broader grouped-capture refactor or another parity-suite cleanup in this run.
- Verification passes with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py`
  - `bash -lc "! rg -n '^def (_bundle_case_ids|_grouped_capture_direct_test_bundles|_grouped_capture_direct_test_case_id_buckets)\\b' tests/python/test_grouped_capture_parity_suite.py"`

## Constraints
- Keep the change limited to `tests/python/test_grouped_capture_parity_suite.py`. Do not edit fixtures, `tests/python/fixture_parity_support.py`, other parity suites, harness modules, reports, or state files in this run.
- Preserve the current grouped-capture direct-test bucket order and coverage; the point is to delete the wrapper mirrors, not to reinterpret the selected frontier.

## Notes
- `RBR-0911` is the next available architecture task id in the current checkout:
  - `rg -n 'RBR-0911|RBR-091[2-9]|RBR-09[2-9][0-9]' ops/state/backlog.md ops/state/current_status.md` returned no reserved follow-on id in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | rg '^RBR-0911'` returned no existing task file.
- There is no blocked architecture task to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The mirror target is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py` currently passes (`432 passed in 0.31s`);
  - `bash -lc "! rg -n '^def (_bundle_case_ids|_grouped_capture_direct_test_bundles|_grouped_capture_direct_test_case_id_buckets)\\b' tests/python/test_grouped_capture_parity_suite.py"` currently fails exactly on the remaining helper wrappers at lines `93`, `97`, and `110`; and
  - `test_grouped_capture_direct_test_buckets_cover_selected_frontier()` already recovers both the bucket-order assertion and `selected_case_ids` from those wrappers alone, so deleting the wrappers is a bounded owner-file cleanup rather than a behavior change.
