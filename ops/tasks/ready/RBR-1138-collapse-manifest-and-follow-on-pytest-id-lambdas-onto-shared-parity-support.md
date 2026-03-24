# RBR-1138: Collapse manifest and follow-on pytest id lambdas onto shared parity support

Status: ready
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining repeated `pytest` id lambdas that only expose `bundle.expected_manifest_id`, `spec.bundle.expected_manifest_id`, or `spec.follow_on_id` across the parity-owner suites by routing them through one shared accessor surface on `tests/python/fixture_parity_support.py`.

## Deliverables
- `tests/python/fixture_parity_support.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/python/test_quantified_alternation_parity_suite.py`
- `tests/python/test_branch_local_backreference_parity_suite.py`
- `tests/python/test_conditional_group_exists_parity_suite.py`
- `tests/python/test_open_ended_quantified_group_parity_suite.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`

## Acceptance Criteria
- Add one shared parity-support accessor path on `tests/python/fixture_parity_support.py`, or reuse a strictly smaller equivalent on that file, for the three id shapes still repeated inline across these suites:
  - a helper for `FixtureBundle.expected_manifest_id`;
  - a helper for spec objects that expose `spec.bundle.expected_manifest_id`; and
  - a helper for direct-follow-on specs that expose `spec.follow_on_id`.
- Keep the cleanup on the existing parity-support module instead of adding a new helper file, registry, protocol layer, or owner-local wrapper family.
- `tests/python/test_quantified_alternation_parity_suite.py`, `tests/python/test_branch_local_backreference_parity_suite.py`, `tests/python/test_conditional_group_exists_parity_suite.py`, `tests/python/test_open_ended_quantified_group_parity_suite.py`, and `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` stop spelling these id callbacks inline as `lambda bundle: bundle.expected_manifest_id`, `lambda spec: spec.bundle.expected_manifest_id`, or `lambda spec: spec.follow_on_id`.
- Preserve the current parametrization ids exactly:
  - bundle rows still render each bundle's existing `expected_manifest_id`;
  - generated-spec rows still render each spec bundle's existing `expected_manifest_id`; and
  - direct-follow-on rows still render each spec's existing `follow_on_id`.
- Extend `tests/python/test_fixture_parity_support_contract.py` with focused coverage for the new shared accessor surface without growing another owner-specific contract block.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py::test_generated_quantified_alternation_compile_cases_stay_anchored_to_published_manifests tests/python/test_quantified_alternation_parity_suite.py::test_direct_bytes_follow_on_cases_stay_explicit_with_one_direct_follow_on_anchor tests/python/test_branch_local_backreference_parity_suite.py::test_generated_quantified_branch_local_compile_cases_stay_anchored_to_published_manifests tests/python/test_open_ended_quantified_group_parity_suite.py::test_bytes_cases_stay_explicit_with_expected_bundle_coverage tests/python/test_open_ended_quantified_group_parity_suite.py::test_direct_bytes_follow_on_manifests_exclude_only_bytes_rows_from_generic_case_buckets tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py::test_wider_ranged_repeat_direct_bytes_follow_on_case_surfaces_resolve_to_expected_published_mixed_fixtures tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py::test_direct_bytes_follow_on_cases_stay_explicit_with_one_direct_follow_on_anchor tests/python/test_conditional_group_exists_parity_suite.py::test_generated_quantified_conditional_compile_cases_stay_anchored_to_published_manifests`
- `bash -lc "! rg -n 'ids=lambda bundle: bundle\\.expected_manifest_id|ids=lambda spec: spec\\.bundle\\.expected_manifest_id|ids=lambda spec: spec\\.follow_on_id' tests/python/test_quantified_alternation_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py tests/python/test_conditional_group_exists_parity_suite.py tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py"`

## Constraints
- Keep the cleanup structural and limited to the seven files above. Do not widen it into implementation code, correctness fixtures, benchmark files, README text, or tracked ops state prose.
- Preserve the current selected fixture frontiers, generated candidate-text checks, bytes follow-on routing, and `pytest` id strings in all five parity suites.
- Prefer deleting repeated inline callbacks over adding another abstraction layer that hides what attribute each id comes from.

## Notes
- `RBR-1138` is the next available unreserved architecture task id in this checkout:
  - `ops/tasks/ready/` and `ops/tasks/in_progress/` are empty in this run;
  - `ops/tasks/blocked/` only contains feature tasks `RBR-1133` and `RBR-1135`; and
  - `rg -n "RBR-1138|RBR-1139|RBR-1140" ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` returned no reserved future task id in this run.
- No blocked architecture task exists to reopen or retire first in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The live duplication is still concrete and bounded:
  - `tests/python/fixture_parity_support.py` currently has shared helpers for `FixtureCase.case_id` and `.id` carriers, but not for `FixtureBundle.expected_manifest_id`, `spec.bundle.expected_manifest_id`, or `spec.follow_on_id`;
  - the five target suites still contain sixteen inline lambdas for those same three id shapes; and
  - the second verification command above currently fails only because those inline lambdas are still present.
