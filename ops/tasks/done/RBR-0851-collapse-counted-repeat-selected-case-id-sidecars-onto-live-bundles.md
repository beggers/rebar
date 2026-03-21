## RBR-0851: Collapse counted-repeat selected case-id sidecars onto live bundles

Status: done
Owner: architecture-implementation
Created: 2026-03-21
Completed: 2026-03-21

## Goal
- Remove the counted-repeat parity suites' remaining full-suite selected-case-id sidecars from `tests/python/test_quantified_alternation_parity_suite.py` and `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` so the loaded fixture bundles become the sole canonical source for those selected frontier ids.

## Deliverables
- `tests/python/test_quantified_alternation_parity_suite.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_quantified_alternation_parity_suite.py` stops defining or reading the detached selected-case-id mirror `QUANTIFIED_ALTERNATION_SELECTED_CASE_IDS`.
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` stops defining or reading the detached selected-case-id mirror `WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_SELECTED_CASE_IDS`.
- The direct-test frontier coverage in both files derives selected case ids directly from the already loaded bundles instead of restating them in top-level tuples:
  - `test_quantified_alternation_direct_test_case_id_buckets_cover_selected_frontier()`
  - `test_wider_ranged_repeat_quantified_group_direct_test_case_id_buckets_cover_selected_frontier()`
- Preserve the current direct-bytes routing and bucket labeling exactly while deleting the mirrors:
  - quantified alternation still uses module bucket label `shared-module-search`, pattern bucket label `shared-pattern-fullmatch`, and follow-on ids `bounded`, `broader-range`, `conditional`, `open-ended`, `nested-branch`, and `backtracking-heavy`;
  - wider-ranged-repeat quantified group still uses module bucket label `shared-module-search`, pattern bucket label `shared-pattern-fullmatch`, and follow-on ids `broader-range-conditional`, `broader-range-backtracking-heavy`, `nested-broader-range-alternation`, `nested-broader-range-conditional`, and `nested-broader-range-backtracking-heavy`; and
  - `COMPILE_CASES`, `MODULE_CASES`, `PATTERN_CASES`, `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES`, and the current selected frontier coverage stay behaviorally unchanged apart from deriving the selected ids from live bundle rows.
- Keep all curated subset contracts unchanged:
  - do not change `GENERATED_QUANTIFIED_ALTERNATION_PARITY_SPECS`, `REGS_PARITY_CASE_IDS`, `PATTERN_BOUNDS_MATCH_CASES`, `PATTERN_BOUNDS_NO_MATCH_CASES`, `BACKTRACKING_TRACE_CASES`, direct-bytes follow-on case inventories, or any correctness fixture selection.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
  - `bash -lc "! rg -n '^(QUANTIFIED_ALTERNATION_SELECTED_CASE_IDS|WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_SELECTED_CASE_IDS) =' tests/python/test_quantified_alternation_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py"`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from tests.python.fixture_parity_support import (
    assert_direct_test_case_id_buckets_cover_selected_frontier,
    direct_test_case_id_buckets_for_follow_on_bundles,
)
import tests.python.test_quantified_alternation_parity_suite as qa
import tests.python.test_wider_ranged_repeat_quantified_group_parity_suite as wr

assert tuple(spec.follow_on_id for spec in qa.DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES) == (
    "bounded",
    "broader-range",
    "conditional",
    "open-ended",
    "nested-branch",
    "backtracking-heavy",
)
assert_direct_test_case_id_buckets_cover_selected_frontier(
    direct_test_case_id_buckets_for_follow_on_bundles(
        compile_cases=qa.COMPILE_CASES,
        module_cases=qa.MODULE_CASES,
        pattern_cases=qa.PATTERN_CASES,
        module_bucket_label="shared-module-search",
        pattern_bucket_label="shared-pattern-fullmatch",
        follow_on_buckets=(
            (f"{spec.follow_on_id}-bytes-follow-on", spec.bundle)
            for spec in qa.DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES
        ),
    ),
    selected_case_ids=tuple(
        case.case_id for bundle in qa.FIXTURE_BUNDLES for case in bundle.cases
    ),
    coverage_label="quantified alternation direct-test case-id buckets",
)

assert tuple(spec.id for spec in wr.DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES) == (
    "broader-range-conditional",
    "broader-range-backtracking-heavy",
    "nested-broader-range-alternation",
    "nested-broader-range-conditional",
    "nested-broader-range-backtracking-heavy",
)
assert_direct_test_case_id_buckets_cover_selected_frontier(
    direct_test_case_id_buckets_for_follow_on_bundles(
        compile_cases=wr.COMPILE_CASES,
        module_cases=wr.MODULE_CASES,
        pattern_cases=wr.PATTERN_CASES,
        module_bucket_label="shared-module-search",
        pattern_bucket_label="shared-pattern-fullmatch",
        follow_on_buckets=(
            (f"{spec.id}-bytes-follow-on", spec.bundle)
            for spec in wr.DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES
        ),
    ),
    selected_case_ids=tuple(
        case.case_id for bundle in wr.FIXTURE_BUNDLES for case in bundle.cases
    ),
    coverage_label="wider-ranged-repeat quantified group direct-test case-id buckets",
)
print("ok")
PY`

## Constraints
- Keep this cleanup structural only. The point is to delete one more mirrored ownership layer inside the counted-repeat parity owners, not to reinterpret quantified semantics, change direct-bytes routing, or introduce a broader shared abstraction pass.
- Keep scope limited to `tests/python/test_quantified_alternation_parity_suite.py` and `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`. Do not edit correctness fixtures, harness modules, benchmark manifests/tests, reports, README copy, or tracked project-state prose in this run.

## Notes
- `RBR-0851` is the next available task id in the current checkout:
  - `ops/state/backlog.md` and `ops/state/current_status.md` reserve only the already-filed `RBR-0850`; and
  - no tracked task file under `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, or `ops/tasks/blocked/` already uses `RBR-0851`.
- No blocked architecture task exists to reopen first, and the current queue/runtime state does not trigger the queue-stall no-op rule:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete and bounded in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` currently passes (`1902 passed in 2.46s`);
  - the task-local direct-frontier probe in Acceptance already passes in the current checkout (`ok`);
  - the live checkout confirms both mirrors are exact restatements of bundle-owned case ids today; and
  - `bash -lc "! rg -n '^(QUANTIFIED_ALTERNATION_SELECTED_CASE_IDS|WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_SELECTED_CASE_IDS) =' tests/python/test_quantified_alternation_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py"` currently fails exactly on this cleanup because both mirrored top-level tuples still exist.
- This is a direct post-JSON simplification follow-on rather than a new harness direction:
  - both parity suites already load the owning fixture bundles and partition their direct-bytes follow-on rows from those live bundle objects; and
  - the remaining selected-case-id tuples are now just detached mirrors of the bundle rows used only by the direct-test frontier coverage assertions.

## Completion
- 2026-03-21: Removed the detached `QUANTIFIED_ALTERNATION_SELECTED_CASE_IDS` and `WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_SELECTED_CASE_IDS` mirrors from the two counted-repeat parity suites.
- Rewired `test_quantified_alternation_direct_test_case_id_buckets_cover_selected_frontier()` and `test_wider_ranged_repeat_quantified_group_direct_test_case_id_buckets_cover_selected_frontier()` to derive `selected_case_ids` directly from `FIXTURE_BUNDLES`, preserving the existing shared bucket labels, direct-bytes follow-on ids, and case-bucket partitioning unchanged.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` (`2119 passed in 2.05s`), `bash -lc "! rg -n '^(QUANTIFIED_ALTERNATION_SELECTED_CASE_IDS|WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_SELECTED_CASE_IDS) =' tests/python/test_quantified_alternation_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py"` (passes with no matches), and the task-local bundle-derived acceptance probe from this task (`ok`).
