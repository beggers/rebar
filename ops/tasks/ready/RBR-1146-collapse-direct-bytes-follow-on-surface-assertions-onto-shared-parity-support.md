# RBR-1146: Collapse direct-bytes follow-on surface assertions onto shared parity support

Status: ready
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the repeated direct-bytes follow-on surface-assertion block that still lives separately in the quantified alternation, branch-local backreference, open-ended quantified-group, and wider-ranged-repeat quantified-group parity owners by routing those checks through one shared helper surface on `tests/python/fixture_parity_support.py` instead of keeping parallel `expected_compile_patterns`, bytes-payload, published-text, and operation-count assertions beside the already-shared direct-bytes routing support.

## Deliverables
- `tests/python/fixture_parity_support.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/python/test_quantified_alternation_parity_suite.py`
- `tests/python/test_branch_local_backreference_parity_suite.py`
- `tests/python/test_open_ended_quantified_group_parity_suite.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`

## Acceptance Criteria
- Add one bounded shared helper surface on `tests/python/fixture_parity_support.py`, or reuse a strictly smaller equivalent on that file, for the direct-bytes follow-on surface contract that is still repeated across the parity owners:
  - start from `assert_direct_bytes_follow_on_bundle_routing(...)` instead of re-implementing routing;
  - cover the expected bytes compile-pattern set taken from the bundle's published compile rows;
  - cover the current str/bytes row-count pairing, `-str` to `-bytes` case-id pairing, and operation/helper-count assertions;
  - cover the current bytes-payload sanity checks for `search_matches`, `search_misses`, `fullmatch_matches`, and `fullmatch_misses`;
  - cover published module-search and pattern-fullmatch text maps via `published_bytes_texts_by_pattern(...)`;
  - preserve the branch-local unsupported-backend expectation path on the shared helper surface instead of leaving that distinction as owner-local duplicated logic; and
  - keep the helper on the existing parity-support module instead of adding another helper file, registry, or abstraction layer.
- `tests/python/test_quantified_alternation_parity_suite.py` stops owning the duplicated direct-bytes surface assertions locally:
  - keep `test_direct_bytes_follow_on_manifests_exclude_only_bytes_rows_from_generic_case_buckets(...)` and `test_direct_bytes_follow_on_cases_stay_explicit_with_one_direct_follow_on_anchor(...)` as owner-facing coverage points, but route their repeated assertion body through the shared helper;
  - remove the owner-local `expected_compile_patterns` calculation and the repeated published-text / bytes-payload assertion block from the direct-follow-on test body; and
  - preserve the current direct-follow-on manifest set, unsupported-backend expectations, and expected module/fullmatch text maps exactly.
- `tests/python/test_branch_local_backreference_parity_suite.py` stops owning the same surface assertions locally:
  - keep the suite-local direct bucket-label assertion that ties the follow-on bundle to its canonical direct-test bucket label;
  - route the remaining bytes surface assertions through the same shared helper;
  - remove the owner-local `expected_compile_patterns` calculation and repeated published-text / bytes-payload assertion block; and
  - preserve the current unsupported-backend expectations, bucket-label spellings, and expected text maps exactly.
- `tests/python/test_open_ended_quantified_group_parity_suite.py` and `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` stop owning the same direct-follow-on assertion block locally:
  - keep the existing owner-local fixture-frontier and manifest-pairing checks intact;
  - route the direct-follow-on bytes-surface assertions through the shared helper instead of repeating the compile-pattern, case-pairing, operation-count, payload-type, and published-text assertions in each file; and
  - preserve the current direct-follow-on manifest ids, expected module/fullmatch text maps, and supported-backend behavior exactly.
- Extend `tests/python/test_fixture_parity_support_contract.py` with focused shared-helper coverage instead of adding more owner-local contract checks:
  - one check proves the shared helper preserves the supported-backend direct-bytes surface contract on a representative quantified/open-ended style bundle;
  - one check proves the same helper preserves the branch-local unsupported-backend expectations and published text maps; and
  - one check proves the shared helper rejects a drifted bytes surface contract with a targeted assertion message rather than silently accepting the mismatch.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py::test_direct_bytes_follow_on_manifests_exclude_only_bytes_rows_from_generic_case_buckets tests/python/test_quantified_alternation_parity_suite.py::test_direct_bytes_follow_on_cases_stay_explicit_with_one_direct_follow_on_anchor tests/python/test_branch_local_backreference_parity_suite.py::test_direct_bytes_follow_on_cases_stay_explicit_with_one_direct_follow_on_anchor tests/python/test_open_ended_quantified_group_parity_suite.py::test_direct_bytes_follow_on_manifests_exclude_only_bytes_rows_from_generic_case_buckets tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py::test_direct_bytes_follow_on_manifests_exclude_only_bytes_rows_from_generic_case_buckets tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py::test_direct_bytes_follow_on_cases_stay_explicit_with_one_direct_follow_on_anchor tests/python/test_fixture_parity_support_contract.py -k 'direct_bytes_follow_on_bundle_routing or grouped_quantified_bytes_surface_spec or published_bytes_texts_by_pattern'`

## Constraints
- Keep the cleanup structural and limited to the six files above. Do not widen it into implementation code, correctness fixtures, benchmark files, README text, or tracked ops state prose.
- Prefer deleting duplicated owner-local assertion bodies over adding another wrapper layer that merely renames the same checks.
- Preserve current direct-follow-on manifest ids, bucket labels, unsupported-backend behavior, published text maps, and bytes payload expectations exactly.

## Notes
- `RBR-1146` is the next available unreserved architecture task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run; and
  - `rg -n 'RBR-1146|RBR-1147|RBR-1148|RBR-1149|RBR-1150' ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` matched only historical notes inside completed task files and did not reveal a live reserved future task id at `RBR-1146`.
- No blocked architecture task exists to reopen or retire first in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining duplication is concrete and cross-file in the current checkout:
  - `tests/python/test_quantified_alternation_parity_suite.py`, `tests/python/test_branch_local_backreference_parity_suite.py`, `tests/python/test_open_ended_quantified_group_parity_suite.py`, and `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` each still hand-write the same direct-bytes surface checks on top of `assert_direct_bytes_follow_on_bundle_routing(...)`;
  - those files still repeat the same bytes compile-pattern extraction from `fixture_cases_for_operation((spec.bundle,), "compile")`, the same str/bytes case-count and `-bytes` pairing assertions, and the same `published_bytes_texts_by_pattern(...)` comparison shape; and
  - `tests/python/fixture_parity_support.py` already owns the adjacent direct-bytes routing, mixed-text pairing, published-text extraction, and grouped-quantified bytes-spec surfaces, so this repeated assertion body belongs there rather than in each owner.
- Verification status in this run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py::test_direct_bytes_follow_on_manifests_exclude_only_bytes_rows_from_generic_case_buckets tests/python/test_quantified_alternation_parity_suite.py::test_direct_bytes_follow_on_cases_stay_explicit_with_one_direct_follow_on_anchor tests/python/test_branch_local_backreference_parity_suite.py::test_direct_bytes_follow_on_cases_stay_explicit_with_one_direct_follow_on_anchor tests/python/test_open_ended_quantified_group_parity_suite.py::test_direct_bytes_follow_on_manifests_exclude_only_bytes_rows_from_generic_case_buckets tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py::test_direct_bytes_follow_on_manifests_exclude_only_bytes_rows_from_generic_case_buckets tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py::test_direct_bytes_follow_on_cases_stay_explicit_with_one_direct_follow_on_anchor tests/python/test_fixture_parity_support_contract.py -k 'direct_bytes_follow_on_bundle_routing or grouped_quantified_bytes_surface_spec or published_bytes_texts_by_pattern'` returned `15 passed` in this run.
