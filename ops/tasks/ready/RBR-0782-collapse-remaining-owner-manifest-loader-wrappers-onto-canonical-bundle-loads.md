# RBR-0782: Collapse remaining owner-manifest loader wrappers onto canonical bundle loads

Status: ready
Owner: architecture-implementation
Created: 2026-03-20

## Goal
- Delete the last four file-local owner-manifest loader wrappers that simply restate `load_published_fixture_bundles(...)` input order and manifest ids already covered by `tests/python/test_fixture_parity_support_contract.py`.
- Make each suite's existing `*_FIXTURE_NAMES` tuple the only local ownership list, and build `FIXTURE_BUNDLES` directly from the canonical published-manifest loader without changing any downstream bundle aliases, generated parity anchors, bytes follow-on routing, trace buckets, or direct-test coverage buckets.

## Deliverables
- `tests/python/test_quantified_alternation_parity_suite.py`
- `tests/python/test_open_ended_quantified_group_parity_suite.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
- `tests/python/test_branch_local_backreference_parity_suite.py`

## Acceptance Criteria
- Each target file stops defining the redundant owner-loader wrapper and parallel manifest-id sidecar:
  - `tests/python/test_quantified_alternation_parity_suite.py` removes `QUANTIFIED_ALTERNATION_MANIFEST_IDS` and `_load_quantified_alternation_fixture_bundles()`.
  - `tests/python/test_open_ended_quantified_group_parity_suite.py` removes `OPEN_ENDED_QUANTIFIED_GROUP_MANIFEST_IDS` and `_load_open_ended_quantified_group_fixture_bundles()`.
  - `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` removes `WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_MANIFEST_IDS` and `_load_wider_ranged_repeat_quantified_group_fixture_bundles()`.
  - `tests/python/test_branch_local_backreference_parity_suite.py` removes `BRANCH_LOCAL_BACKREFERENCE_MANIFEST_IDS` and `_load_branch_local_backreference_fixture_bundles()`.
- In all four suites, `FIXTURE_BUNDLES` is built directly from `load_published_fixture_bundles(...)` using the existing `*_FIXTURE_NAMES` tuple and `CORRECTNESS_FIXTURES_ROOT / fixture_name`, with `pattern_extractor=case_pattern`.
- Preserve structure and ordering after the cleanup:
  - keep each file's `*_FIXTURE_NAMES` tuple in its current order;
  - keep every existing `published_fixture_bundle_by_manifest_id(...)` alias resolving the same manifest ids it resolves today;
  - keep the current members and ordering of the downstream generated parity specs, supplemental case surfaces, direct-bytes follow-on routing, selected-case/frontier buckets, bounded-pattern buckets, and trace bundles in all four files.
- Keep scope structural only:
  - prefer deleting the wrappers over adding another shared registry or another helper layer; and
  - do not edit `tests/conformance/fixtures/*.py`, `tests/python/fixture_parity_support.py`, benchmark files, reports, README copy, or tracked project-state prose.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest tests/python/test_fixture_parity_support_contract.py tests/python/test_quantified_alternation_parity_suite.py tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py -q`
  - `bash -lc "! rg -n 'def _load_(quantified_alternation|open_ended_quantified_group|wider_ranged_repeat_quantified_group|branch_local_backreference)_fixture_bundles\\(|(QUANTIFIED_ALTERNATION|OPEN_ENDED_QUANTIFIED_GROUP|WIDER_RANGED_REPEAT_QUANTIFIED_GROUP|BRANCH_LOCAL_BACKREFERENCE)_MANIFEST_IDS =' tests/python/test_quantified_alternation_parity_suite.py tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py"`

## Constraints
- Keep this as one bounded cleanup across the four remaining suites above; do not expand into the fixture-backed replacement suite, fixture manifest contents, or another fixture-support refactor.
- Do not change runtime behavior, fixture coverage, manifest ordering, or published manifest ids.

## Notes
- `RBR-0782` is free in the current checkout: `rg -n "RBR-0782|RBR-0783|RBR-0784" ops/state/current_status.md ops/state/backlog.md ops/tasks -S` returned no matches.
- No blocked architecture task exists to reopen first, and rule 10 does not apply here:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in the current checkout.
- JSON burn-down is complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The cleanup target is concrete in the live checkout:
  - `rg -n "def _load_(quantified_alternation|open_ended_quantified_group|wider_ranged_repeat_quantified_group|branch_local_backreference)_fixture_bundles\\(|(QUANTIFIED_ALTERNATION|OPEN_ENDED_QUANTIFIED_GROUP|WIDER_RANGED_REPEAT_QUANTIFIED_GROUP|BRANCH_LOCAL_BACKREFERENCE)_MANIFEST_IDS =" tests/python/test_quantified_alternation_parity_suite.py tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py` currently reports exactly the four duplicated wrappers and four manifest-id sidecars this task should remove.
  - The acceptance pytest command is already green in the current checkout (`6830 passed in 5.65s`), so any post-change failure there belongs to this cleanup.
- This follows the same post-JSON simplification track as the recent owner-bundle cleanups that removed mirrored full-manifest metadata from adjacent suites without changing behavior:
  - `ops/tasks/done/RBR-0778-collapse-open-ended-quantified-group-bundle-spec-sidecars-onto-owner-manifests.md`
  - `ops/tasks/done/RBR-0780-collapse-quantified-alternation-bundle-spec-sidecars-onto-owner-manifests.md`
