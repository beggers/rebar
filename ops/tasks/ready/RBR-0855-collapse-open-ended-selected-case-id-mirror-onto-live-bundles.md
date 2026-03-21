# RBR-0855: Collapse the open-ended selected case-id mirror onto live bundles

Status: ready
Owner: architecture-implementation
Created: 2026-03-21

## Goal
- Remove the remaining open-ended quantified-group selected-case-id mirror from `tests/python/test_open_ended_quantified_group_parity_suite.py` so the loaded `FIXTURE_BUNDLES` stay the sole canonical owner for the direct-frontier case set.

## Deliverables
- `tests/python/test_open_ended_quantified_group_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_open_ended_quantified_group_parity_suite.py` stops defining or reading the detached mirror `OPEN_ENDED_QUANTIFIED_GROUP_SELECTED_CASE_IDS`.
- `test_open_ended_quantified_group_direct_test_case_id_buckets_cover_selected_frontier()` derives `selected_case_ids` directly from the already loaded `FIXTURE_BUNDLES` instead of routing through a handwritten top-level tuple.
- Preserve the current direct-frontier routing exactly while deleting the mirror:
  - keep the direct bucket labels `shared-module-search` and `shared-pattern-fullmatch`;
  - keep `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` ordered by the same four follow-on ids: `broader-range-alternation`, `open-ended-backtracking-heavy`, `broader-range-conditional`, and `broader-range-backtracking-heavy`; and
  - keep `FIXTURE_BUNDLES`, `OPEN_ENDED_BYTES_CASE_SURFACES`, `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES`, `COMPILE_CASES`, `MODULE_CASES`, `PATTERN_CASES`, `OPEN_ENDED_TRACE_BUNDLES`, `OPEN_ENDED_TRACE_CASES`, and the bounded-pattern case inventories behaviorally unchanged apart from deriving the selected ids from live bundle rows.
- Do not broaden scope beyond this mirror deletion:
  - do not change correctness fixtures, shared fixture-support helpers, benchmark manifests/tests, harness modules, reports, README copy, or tracked project-state prose; and
  - do not retune the direct-bytes follow-on routing, trace generation, or bounded match/no-match inventories in this run.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py`
  - `bash -lc "! rg -n '^(OPEN_ENDED_QUANTIFIED_GROUP_SELECTED_CASE_IDS) =' tests/python/test_open_ended_quantified_group_parity_suite.py"`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from tests.python.fixture_parity_support import (
    assert_direct_test_case_id_buckets_cover_selected_frontier,
    direct_test_case_id_buckets_for_follow_on_bundles,
)
import tests.python.test_open_ended_quantified_group_parity_suite as mod

assert tuple(spec.follow_on_id for spec in mod.DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES) == (
    "broader-range-alternation",
    "open-ended-backtracking-heavy",
    "broader-range-conditional",
    "broader-range-backtracking-heavy",
)
assert_direct_test_case_id_buckets_cover_selected_frontier(
    direct_test_case_id_buckets_for_follow_on_bundles(
        compile_cases=mod.COMPILE_CASES,
        module_cases=mod.MODULE_CASES,
        pattern_cases=mod.PATTERN_CASES,
        module_bucket_label="shared-module-search",
        pattern_bucket_label="shared-pattern-fullmatch",
        follow_on_buckets=(
            (f"{spec.follow_on_id}-bytes-follow-on", spec.bundle)
            for spec in mod.DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES
        ),
    ),
    selected_case_ids=tuple(
        case.case_id for bundle in mod.FIXTURE_BUNDLES for case in bundle.cases
    ),
    coverage_label="open-ended quantified group direct-test case-id buckets",
)
print("ok")
PY`

## Constraints
- Keep this cleanup structural only. The point is to delete one more mirrored ownership layer inside the open-ended quantified-group parity owner, not to reinterpret open-ended semantics or introduce another shared helper pass.
- Keep scope limited to `tests/python/test_open_ended_quantified_group_parity_suite.py`.

## Notes
- `RBR-0855` is the next available architecture task id in the current checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, and `ops/tasks/blocked/` contain no existing `RBR-0855`; and
  - `ops/state/backlog.md` and `ops/state/current_status.md` do not reserve `RBR-0855`.
- No blocked architecture task exists to reopen first, and the queue/runtime state does not trigger the queue-stall no-op rule:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete and bounded in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py` currently passes;
  - the task-local direct-frontier probe in Acceptance already passes in the current checkout (`ok`);
  - `bash -lc "! rg -n '^(OPEN_ENDED_QUANTIFIED_GROUP_SELECTED_CASE_IDS) =' tests/python/test_open_ended_quantified_group_parity_suite.py"` currently fails exactly on this cleanup because the mirrored tuple still exists; and
  - `OPEN_ENDED_QUANTIFIED_GROUP_SELECTED_CASE_IDS` is used only as a restatement of `tuple(case.case_id for bundle in FIXTURE_BUNDLES for case in bundle.cases)` for the direct-frontier coverage assertion.
- This stays on the existing open-ended simplification track rather than opening a new harness direction:
  - `RBR-0725` already collapsed the open-ended generic bucket-routing sidecars onto canonical follow-on ownership;
  - `RBR-0727` already collapsed the open-ended direct-test bucket sidecar onto canonical case owners; and
  - `RBR-0778` already collapsed open-ended bundle-spec sidecars onto owner manifests, leaving this selected-case mirror as the next small deletion on the same parity owner.
