# RBR-1132: Collapse grouped quantified bundle-id and case-id mirrors

Status: done
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the last stale `fixture_bundle_manifest_id` consumers and the repeated whole-bundle selected-case-id comprehensions from the grouped-quantified parity suites by routing them through the existing `FixtureBundle` surface plus one canonical shared helper on `tests/python/fixture_parity_support.py`.

## Deliverables
- `tests/python/fixture_parity_support.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/python/test_open_ended_quantified_group_parity_suite.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
- `tests/python/test_quantified_alternation_parity_suite.py`
- `tests/python/test_branch_local_backreference_parity_suite.py`

## Acceptance Criteria
- Add one shared helper on `tests/python/fixture_parity_support.py`, or reuse a strictly smaller equivalent on that same path, that is canonical for returning the ordered published `case_id` frontier from an iterable of `FixtureBundle` objects:
  - it preserves bundle order and in-bundle case order;
  - it returns the same `case_id` sequence currently produced by `tuple(case.case_id for bundle in FIXTURE_BUNDLES for case in bundle.cases)`;
  - it does not add a new helper module, registry, or abstraction tier; and
  - it is reusable by multiple parity suites rather than remaining owner-local glue.
- `tests/python/test_open_ended_quantified_group_parity_suite.py` and `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` stop importing or parametrizing through the already-deleted `fixture_bundle_manifest_id` wrapper:
  - bundle parametrization ids route through `bundle.expected_manifest_id` or a strictly smaller equivalent already attached to `FixtureBundle`;
  - both suites collect again without import errors; and
  - their direct-test bucket coverage continues to target the same ordered selected frontier.
- The four grouped-quantified parity suites listed above stop spelling the same whole-bundle selected-case-id flattening inline and instead use the shared parity-support path while preserving current behavior:
  - `tests/python/test_open_ended_quantified_group_parity_suite.py`
  - `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
  - `tests/python/test_quantified_alternation_parity_suite.py`
  - `tests/python/test_branch_local_backreference_parity_suite.py`
- Extend `tests/python/test_fixture_parity_support_contract.py` with focused coverage for the shared ordered-case-id helper:
  - a success case that proves it preserves bundle order and in-bundle case order across multiple bundles; and
  - a contract check that keeps the helper aligned with `flatten_fixture_bundles(...)` or an equivalent existing shared bundle-order surface.
- Keep the cleanup structural and limited to the six files above. Do not widen it into implementation code, reports, benchmark manifests, README text, or tracked project-state prose.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py::test_ordered_fixture_bundle_case_ids_preserve_bundle_and_case_order tests/python/test_fixture_parity_support_contract.py::test_ordered_fixture_bundle_case_ids_match_flattened_case_ids tests/python/test_open_ended_quantified_group_parity_suite.py -k 'parity_suite_stays_aligned_with_published_correctness_fixture or direct_test_case_id_buckets_cover_selected_frontier' tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py -k 'parity_suite_stays_aligned_with_published_correctness_fixture or direct_test_case_id_buckets_cover_selected_frontier' tests/python/test_quantified_alternation_parity_suite.py -k 'parity_suite_tracks_published_case_frontier or direct_test_case_id_buckets_cover_selected_frontier' tests/python/test_branch_local_backreference_parity_suite.py -k 'parity_suite_tracks_published_case_frontier or direct_test_case_id_buckets_cover_selected_frontier'`
- `bash -lc "! rg -n 'fixture_bundle_manifest_id|selected_case_ids=tuple\\(case\\.case_id for bundle in FIXTURE_BUNDLES for case in bundle\\.cases\\)' tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py tests/python/test_quantified_alternation_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py"`

## Constraints
- Reuse `FixtureBundle.expected_manifest_id` and `tests/python/fixture_parity_support.py`; do not reintroduce `fixture_bundle_manifest_id()` or add another wrapper layer just to rename the same data.
- Prefer deleting duplicated suite-local selection glue over adding owner-specific helpers.
- Preserve the current direct-test bucket labels, published bundle ordering, and selected case-id ordering in all four suites.

## Notes
- Completed 2026-03-24: added `ordered_fixture_bundle_case_ids()` plus the missing grouped-quantified surface id helpers on `tests/python/fixture_parity_support.py`, switched the grouped-quantified suites to `bundle.expected_manifest_id` and the shared ordered-case-id helper, and extended `tests/python/test_fixture_parity_support_contract.py` with focused ordering/alignment coverage.
- Verified with the task's targeted pytest selection (`7 passed`) and the negative `rg` check for both stale `fixture_bundle_manifest_id` imports/usages and the duplicated whole-bundle `selected_case_ids` comprehension.
- `RBR-1132` is the next available unreserved task id in this checkout:
  - the highest live task id across `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, and `ops/tasks/blocked/` is `1131`; and
  - `rg -n 'RBR-1132|RBR-1133|RBR-1134|RBR-1135' ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` returned no reserved future ids in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete and current in both tracked and live views for this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, and `blocked: 0`;
  - the latest cycle completed `architecture-implementation` and `feature-implementation` as `done`; and
  - no inherited-dirty checkpoint churn or stalled post-task refresh path is recorded in the current runtime artifacts.
- The remaining duplication and drift are concrete in the live checkout:
  - `tests/python/test_open_ended_quantified_group_parity_suite.py` still imports `fixture_bundle_manifest_id`, still uses `ids=fixture_bundle_manifest_id`, and still spells `selected_case_ids=tuple(case.case_id for bundle in FIXTURE_BUNDLES for case in bundle.cases)`;
  - `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` carries the same dead import, stale id callback, and whole-bundle selected-case-id comprehension;
  - `tests/python/test_quantified_alternation_parity_suite.py` and `tests/python/test_branch_local_backreference_parity_suite.py` still carry the same whole-bundle selected-case-id comprehension even though shared bundle flattening already lives on `tests/python/fixture_parity_support.py`; and
  - `rg -n 'fixture_bundle_manifest_id|case\\.case_id for bundle in FIXTURE_BUNDLES for case in bundle\\.cases' tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py tests/python/test_quantified_alternation_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py` currently matches exactly those stale lines.
- Verification status in this run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py -k 'direct_test_case_id_buckets_cover_selected_frontier or parity_suite_tracks_published_case_frontier'` returned `2 passed`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py -k 'direct_test_case_id_buckets_cover_selected_frontier or parity_suite_tracks_published_case_frontier'` returned `2 passed`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py -k 'direct_test_case_id_buckets_cover_selected_frontier or parity_suite_stays_aligned_with_published_correctness_fixture'` currently fails during collection because the suite still imports the deleted `fixture_bundle_manifest_id` symbol, which is part of the exact cleanup scoped here; and
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py -k 'direct_test_case_id_buckets_cover_selected_frontier or parity_suite_stays_aligned_with_published_correctness_fixture'` fails for the same targeted reason.
