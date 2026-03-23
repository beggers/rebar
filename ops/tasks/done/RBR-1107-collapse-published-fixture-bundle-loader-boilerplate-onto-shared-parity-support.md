## RBR-1107: Collapse published fixture-bundle loader boilerplate onto shared parity support

Status: done
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the repeated top-level published fixture-bundle loading/indexing boilerplate that several large Python parity suites still restate on top of `tests/python/fixture_parity_support.py`, so selected fixture loading and manifest-id indexing travel through one shared support path instead of four owner-local comprehensions.

## Deliverables
- `tests/python/fixture_parity_support.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/python/test_grouped_capture_parity_suite.py`
- `tests/python/test_quantified_alternation_parity_suite.py`
- `tests/python/test_branch_local_backreference_parity_suite.py`
- `tests/python/test_conditional_group_exists_parity_suite.py`

## Acceptance Criteria
- Add one shared helper surface in `tests/python/fixture_parity_support.py`, or a strictly smaller equivalent on that existing support path, that combines the owner-local top-level setup those suites currently restate:
  - resolving one or more correctness fixture selectors to published fixture paths;
  - building the ordered `FixtureBundle` tuple for those paths with the requested `pattern_extractor`; and
  - building the manifest-id index with the same duplicate-manifest validation currently enforced by `published_fixture_bundles_by_manifest_id(...)`.
- Extend `tests/python/test_fixture_parity_support_contract.py` so the shared helper is covered for:
  - preserving the published fixture path order in the returned bundle tuple; and
  - rejecting duplicate manifest ids through the new combined helper path.
- `tests/python/test_grouped_capture_parity_suite.py`, `tests/python/test_quantified_alternation_parity_suite.py`, `tests/python/test_branch_local_backreference_parity_suite.py`, and `tests/python/test_conditional_group_exists_parity_suite.py` stop open-coding the same two-step top-level loader/index pattern:
  - `FIXTURE_BUNDLES = tuple(build_selected_fixture_bundle(...) for path in select_correctness_fixture_paths(...))`; and
  - `FIXTURE_BUNDLES_BY_MANIFEST_ID = published_fixture_bundles_by_manifest_id(FIXTURE_BUNDLES)`.
- Preserve the current bundle order, manifest-id aliases, and suite behavior in all four owner files after the cleanup. This task is structural only; it must not change fixture selection, manifest routing, or test expectations.
- Keep the cleanup limited to the shared parity-support path plus the four owner suites above. Do not widen it into other parity suites, harness implementation code, reports, README text, or tracked state prose.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_grouped_capture_parity_suite.py tests/python/test_quantified_alternation_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py tests/python/test_conditional_group_exists_parity_suite.py`
- `bash -lc "! rg -n '^FIXTURE_BUNDLES = tuple\\(|^FIXTURE_BUNDLES_BY_MANIFEST_ID = published_fixture_bundles_by_manifest_id\\(' tests/python/test_grouped_capture_parity_suite.py tests/python/test_quantified_alternation_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py tests/python/test_conditional_group_exists_parity_suite.py"`

## Constraints
- Prefer extending `tests/python/fixture_parity_support.py` over adding a new support module, registry, or helper class.
- Preserve the existing manifest ordering semantics from `select_correctness_fixture_paths(...)`; the shared helper must not reorder published bundles.
- Preserve duplicate-manifest validation instead of silently overwriting bundle entries.
- Do not widen this into deeper case-generation refactors or unrelated `ids=lambda` cleanup in the touched suites.

## Notes
- `RBR-1107` is the next available unreserved task id in this checkout:
  - the highest live task id across `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, and `ops/tasks/blocked/` is `1106`; and
  - `rg -n 'RBR-1107|RBR-1108|RBR-1109|RBR-1110|RBR-1111' ops/state/current_status.md ops/state/backlog.md` returned no reserved future ids in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down is complete in both tracked and live views for this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest runtime cycle shows both task workers finishing `done`, with no inherited-dirty checkpoint churn or stalled refresh path.
- The duplication is live and concrete in the current checkout:
  - `tests/python/test_grouped_capture_parity_suite.py:60-64`, `tests/python/test_quantified_alternation_parity_suite.py:80-84`, `tests/python/test_branch_local_backreference_parity_suite.py:87-94`, and `tests/python/test_conditional_group_exists_parity_suite.py:72-78` each restate the same top-level `select_correctness_fixture_paths(...)` -> `build_selected_fixture_bundle(...)` -> `published_fixture_bundles_by_manifest_id(...)` setup today.
- The focused verification slice is already green in this checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_grouped_capture_parity_suite.py tests/python/test_quantified_alternation_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py tests/python/test_conditional_group_exists_parity_suite.py` returned `2764 passed` in this run.

## Completion
- Added `load_published_fixture_bundles(...)` to `tests/python/fixture_parity_support.py` so selector resolution, ordered bundle construction, and duplicate-manifest index validation travel through one shared helper.
- Extended `tests/python/test_fixture_parity_support_contract.py` with coverage for preserved selector path order and duplicate manifest-id rejection through the new combined helper.
- Switched the grouped-capture, quantified-alternation, branch-local-backreference, and conditional-group-exists parity suites to the shared helper without changing their manifest aliases, bundle order, or expectations.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_grouped_capture_parity_suite.py tests/python/test_quantified_alternation_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py tests/python/test_conditional_group_exists_parity_suite.py` (`2766 passed`) and `bash -lc "! rg -n '^FIXTURE_BUNDLES = tuple\\(|^FIXTURE_BUNDLES_BY_MANIFEST_ID = published_fixture_bundles_by_manifest_id\\(' tests/python/test_grouped_capture_parity_suite.py tests/python/test_quantified_alternation_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py tests/python/test_conditional_group_exists_parity_suite.py"` (passed).
