# RBR-0429: Fold quantified-alternation and branch-local parity suites into shared fixture bundles

Status: ready
Owner: architecture-implementation
Created: 2026-03-16

## Goal
- Replace the remaining whole-manifest `FixtureBundle` / `_fixture_bundle(...)` scaffolding in two large Python parity suites with the existing shared helpers in `tests/python/fixture_parity_support.py`, while deleting the dead branch-local unsupported-backend metadata that is no longer carrying any live behavior.

## Deliverables
- `tests/python/test_quantified_alternation_parity_suite.py`
- `tests/python/test_branch_local_backreference_parity_suite.py`

## Acceptance Criteria
- Both targeted suites stop defining their own whole-manifest bundle wrapper layer:
  - remove the local `FixtureBundle` dataclass and `_fixture_bundle(...)` loader from [tests/python/test_quantified_alternation_parity_suite.py](/home/ubuntu/rebar/tests/python/test_quantified_alternation_parity_suite.py);
  - remove the local `FixtureBundle` dataclass and `_fixture_bundle(...)` loader from [tests/python/test_branch_local_backreference_parity_suite.py](/home/ubuntu/rebar/tests/python/test_branch_local_backreference_parity_suite.py); and
  - reuse the existing `load_fixture_bundle(...)`, `assert_fixture_bundle_contract(...)`, and `published_fixture_paths_from_bundles(...)` helper surface from [tests/python/fixture_parity_support.py](/home/ubuntu/rebar/tests/python/fixture_parity_support.py) instead of introducing another support module or registry.
- [tests/python/test_quantified_alternation_parity_suite.py](/home/ubuntu/rebar/tests/python/test_quantified_alternation_parity_suite.py) still covers the current nine whole-manifest bundles, with the same exact case-id sets, pattern sets, and `(operation, helper)` counts for:
  - `literal-alternation-workflows`
  - `exact-repeat-quantified-group-alternation-workflows`
  - `quantified-alternation-workflows`
  - `quantified-nested-group-alternation-workflows`
  - `quantified-alternation-backtracking-heavy-workflows`
  - `quantified-alternation-broader-range-workflows`
  - `quantified-alternation-conditional-workflows`
  - `quantified-alternation-open-ended-workflows`
  - `quantified-alternation-nested-branch-workflows`
- [tests/python/test_quantified_alternation_parity_suite.py](/home/ubuntu/rebar/tests/python/test_quantified_alternation_parity_suite.py) routes its published-fixture path assertion through `published_fixture_paths_from_bundles(FIXTURE_BUNDLES)` and routes the repeated manifest-alignment assertion through `assert_fixture_bundle_contract(...)` with the same `case_pattern(...)` extractor and the same implicit `{"str"}` text-model expectation.
- [tests/python/test_branch_local_backreference_parity_suite.py](/home/ubuntu/rebar/tests/python/test_branch_local_backreference_parity_suite.py) still covers the current ten whole-manifest bundles, with the same exact case-id sets, compile-pattern sets, and `(operation, helper)` counts for:
  - `branch-local-backreference-workflows`
  - `quantified-branch-local-backreference-workflows`
  - `optional-group-alternation-branch-local-backreference-workflows`
  - `conditional-group-exists-branch-local-backreference-workflows`
  - `nested-group-alternation-branch-local-backreference-workflows`
  - `quantified-alternation-branch-local-backreference-workflows`
  - `quantified-nested-group-alternation-branch-local-backreference-workflows`
  - `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-workflows`
  - `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-workflows`
  - `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-workflows`
- [tests/python/test_branch_local_backreference_parity_suite.py](/home/ubuntu/rebar/tests/python/test_branch_local_backreference_parity_suite.py) routes its published-fixture path assertion through `published_fixture_paths_from_bundles(FIXTURE_BUNDLES)` and routes the repeated manifest-alignment assertion through `assert_fixture_bundle_contract(...)` with `str_case_pattern(...)`.
- Because no current branch-local bundle sets `unsupported_backends` or `unsupported_backend_reason`, [tests/python/test_branch_local_backreference_parity_suite.py](/home/ubuntu/rebar/tests/python/test_branch_local_backreference_parity_suite.py) deletes the dead unsupported-backend bundle fields, the derived `UNSUPPORTED_BACKENDS_BY_CASE_ID` / `UNSUPPORTED_BACKEND_REASONS_BY_CASE_ID` maps, and `_skip_unsupported_backend(...)`, with compile and workflow tests running directly and behavior staying unchanged.
- The cleanup preserves all current suite-local behavioral coverage outside the shared bundle plumbing:
  - keep `BACKTRACKING_TRACE_CASES`, `SUPPLEMENTAL_NO_MATCH_CASES`, and their assertions in [tests/python/test_quantified_alternation_parity_suite.py](/home/ubuntu/rebar/tests/python/test_quantified_alternation_parity_suite.py);
  - keep `MATCH_CONVENIENCE_CASE_IDS`, `MATCH_GROUP_ACCESS_CASE_IDS`, `PATTERN_BOUNDS_MATCH_CASES`, `PATTERN_BOUNDS_NO_MATCH_CASES`, `SupplementalMissCase`, and `BoundedPatternCase` coverage in [tests/python/test_branch_local_backreference_parity_suite.py](/home/ubuntu/rebar/tests/python/test_branch_local_backreference_parity_suite.py); and
  - do not change correctness fixtures, Rust code, `python/rebar/`, selector behavior, benchmark workloads, published reports, README text, or tracked state files beyond this task file.
- After the cleanup:
  - `rg -n 'class FixtureBundle|def _fixture_bundle\\(|sorted\\(\\(bundle\\.manifest\\.path for bundle in FIXTURE_BUNDLES\\)' tests/python/test_quantified_alternation_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py` returns no matches.
  - `rg -n 'unsupported_backends|unsupported_backend_reason|_skip_unsupported_backend' tests/python/test_branch_local_backreference_parity_suite.py` returns no matches.
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_quantified_alternation_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py`.

## Constraints
- Prefer the existing helper surface in [tests/python/fixture_parity_support.py](/home/ubuntu/rebar/tests/python/fixture_parity_support.py) over extending it; if a tiny helper adjustment becomes necessary, keep it narrowly scoped to whole-manifest bundle reuse and add/update focused contract coverage in [tests/python/test_fixture_parity_support_contract.py](/home/ubuntu/rebar/tests/python/test_fixture_parity_support_contract.py).
- Do not broaden this cleanup into the more custom local-bundle owners in:
  - [tests/python/test_callable_replacement_parity_suite.py](/home/ubuntu/rebar/tests/python/test_callable_replacement_parity_suite.py)
  - [tests/python/test_open_ended_quantified_group_replacement_template_parity_suite.py](/home/ubuntu/rebar/tests/python/test_open_ended_quantified_group_replacement_template_parity_suite.py)
- Do not add new parity coverage or delete existing supplemental assertions; this task is structural cleanup only.

## Notes
- The queue was empty at the start of this run, recent runtime artifacts show no inherited-dirty or post-task refresh stall, and both tracked and live JSON counts are zero (`tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, `git ls-files '*.json' | wc -l = 0`, `rg --files -g '*.json' | wc -l = 0`), so this run should seed one post-JSON duplicate-plumbing cleanup instead of no-oping.
- [tests/python/test_quantified_alternation_parity_suite.py](/home/ubuntu/rebar/tests/python/test_quantified_alternation_parity_suite.py) and [tests/python/test_branch_local_backreference_parity_suite.py](/home/ubuntu/rebar/tests/python/test_branch_local_backreference_parity_suite.py) are the remaining whole-manifest parity suites still carrying local bundle dataclasses, manifest loaders, selector-path sorting, and repeated bundle-contract assertions after `RBR-0422` and `RBR-0427`.
- `RBR-0428` is already reserved in tracked backlog/current-status text for the next feature-owned conditional replacement-template parity slice, so this architecture follow-on starts at `RBR-0429`.
