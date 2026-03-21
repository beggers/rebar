# RBR-0843: Collapse callable replacement pytest-param sidecars onto live specs

Status: done
Owner: architecture-implementation
Created: 2026-03-21
Completed: 2026-03-21

## Goal
- Remove the detached pytest-param tuple sidecars from `tests/python/test_callable_replacement_parity_suite.py` so `CALLABLE_MANIFEST_SPECS` and `CALLABLE_NEAR_MISS_CASE_SPECS` remain the sole canonical owners for callable-replacement manifest ordering and near-miss case ordering inside this parity owner.

## Deliverables
- `tests/python/test_callable_replacement_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_callable_replacement_parity_suite.py` stops defining or reading these detached pytest-param tuple sidecars:
  - `CALLABLE_MANIFEST_PARAMS`
  - `CALLABLE_NEAR_MISS_CASES`
- The affected parametrized tests derive directly from the live spec tuples, using `ids=` or tiny file-local helpers derived from those tuples rather than another mirrored top-level param table:
  - `test_callable_replacement_cases_stay_aligned_with_published_fixture`
  - `test_callable_replacement_near_miss_paths_leave_input_unchanged`
- Preserve the current effective parametrization order exactly by deriving it from the existing spec-owned tuples instead of from another mirrored block:
  - manifest-spec params stay in `CALLABLE_MANIFEST_SPECS` order; and
  - near-miss params stay in `CALLABLE_NEAR_MISS_CASE_SPECS` order.
- Keep canonical callable-replacement ownership otherwise unchanged:
  - do not change `CALLABLE_MANIFEST_SPECS`, `CALLABLE_MANIFEST_SPECS_BY_ID`, `CALLABLE_NEAR_MISS_CASE_SPECS`, pending-`rebar` case tracking, compile-pattern pools, shared/bytes case pools, selector routing, or callable replacement semantics; and
  - do not broaden or shrink the callable-replacement frontier.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py`
  - `bash -lc "! rg -n '^(CALLABLE_MANIFEST_PARAMS|CALLABLE_NEAR_MISS_CASES) =' tests/python/test_callable_replacement_parity_suite.py"`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
import tests.python.test_callable_replacement_parity_suite as mod

assert tuple(spec.manifest_id for spec in mod.CALLABLE_MANIFEST_SPECS) == (
    "quantified-nested-group-alternation-callable-replacement-workflows",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-callable-replacement-workflows",
    "nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-callable-replacement-workflows",
    "conditional-group-exists-callable-replacement-workflows",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-callable-replacement-workflows",
    "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows",
    "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-callable-replacement-workflows",
)
assert len(tuple(case.id for case in mod.CALLABLE_NEAR_MISS_CASE_SPECS)) == 36
assert tuple(
    spec.manifest_id
    for spec in mod.CALLABLE_MANIFEST_SPECS
    if spec.expected_text_models == mod.MIXED_TEXT_MODELS
) == (
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-callable-replacement-workflows",
    "nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-callable-replacement-workflows",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-conditional-callable-replacement-workflows",
    "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows",
    "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-callable-replacement-workflows",
)
print("ok")
PY`

## Constraints
- Keep this cleanup structural only. The point is to delete the mirrored pytest-param layer inside the callable-replacement parity owner, not to reinterpret callable semantics, change which cases are pending for `rebar`, or adjust the published callable frontier.
- Keep scope limited to `tests/python/test_callable_replacement_parity_suite.py`. Do not edit `tests/python/fixture_parity_support.py`, correctness fixture modules under `tests/conformance/fixtures/`, benchmark manifests/tests, published reports, README copy, or tracked project-state prose in this run.

## Notes
- `RBR-0843` is the next available task id in the current checkout:
  - `ops/state/backlog.md` and `ops/state/current_status.md` reserve only the already-filed `RBR-0842`; and
  - no tracked task file under `ops/tasks/ready/`, `ops/tasks/done/`, or `ops/tasks/blocked/` already uses `RBR-0843`.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the last recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete and bounded in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py` currently passes (`2747 passed in 2.11s`);
  - `rg -n '^(CALLABLE_MANIFEST_PARAMS|CALLABLE_NEAR_MISS_CASES) =' tests/python/test_callable_replacement_parity_suite.py` currently shows exactly the two detached tuple declarations and no other owners;
  - the final `rg` absence check in Acceptance currently fails exactly on this cleanup because those mirrored param tables still exist; and
  - the import probe in Acceptance already passes (`ok`), showing the live spec tuples already carry the ordering needed to delete the extra pytest-param layer without changing behavior.
- This stays on the same bounded simplification track as `RBR-0839` and `RBR-0841`: those tasks collapsed mirrored follow-on case and pytest-param sidecars in neighboring parity owners, and the callable-replacement owner still carries the same kind of detached param layer on top of its live spec tables.

## Completion
- 2026-03-21: Removed the mirrored `CALLABLE_MANIFEST_PARAMS` and `CALLABLE_NEAR_MISS_CASES` tuples from `tests/python/test_callable_replacement_parity_suite.py`.
- Rewired `test_callable_replacement_cases_stay_aligned_with_published_fixture` and `test_callable_replacement_near_miss_paths_leave_input_unchanged` to parametrize directly from `CALLABLE_MANIFEST_SPECS` and `CALLABLE_NEAR_MISS_CASE_SPECS` with ids derived from those live spec tuples, preserving the existing spec-owned order.
- Left callable manifest ownership, near-miss ownership, pending-`rebar` tracking, compile-pattern pools, mixed-text routing, and selector/case semantics unchanged.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py` (`2747 passed in 2.22s`), `bash -lc "! rg -n '^(CALLABLE_MANIFEST_PARAMS|CALLABLE_NEAR_MISS_CASES) =' tests/python/test_callable_replacement_parity_suite.py"` (passes with no matches), and the task-local import/order probe from Acceptance (`ok`).
