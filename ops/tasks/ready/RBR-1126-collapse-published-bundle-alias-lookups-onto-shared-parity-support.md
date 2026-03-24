# RBR-1126: Collapse published bundle alias lookups onto shared parity support

Status: ready
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining top-level published `manifest_id -> FixtureBundle` alias boilerplate from the Python parity suites by routing ordered bundle alias selection through one shared helper on `tests/python/fixture_parity_support.py` instead of repeating `FIXTURE_BUNDLES_BY_MANIFEST_ID[...]` and `OWNER_FIXTURE_BUNDLES_BY_MANIFEST_ID[...]` blocks inline.

## Deliverables
- `tests/python/fixture_parity_support.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/python/test_grouped_capture_parity_suite.py`
- `tests/python/test_open_ended_quantified_group_parity_suite.py`
- `tests/python/test_quantified_alternation_parity_suite.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
- `tests/python/test_conditional_group_exists_parity_suite.py`
- `tests/python/test_parser_matrix_parity_suite.py`

## Acceptance Criteria
- Add one shared helper surface on `tests/python/fixture_parity_support.py`, or a strictly smaller equivalent on that existing path, that:
  - accepts the existing published-bundle mapping keyed by `manifest_id`;
  - accepts an ordered list of requested manifest ids and returns the corresponding `FixtureBundle` objects in that same order;
  - rejects duplicate requested manifest ids loudly instead of silently repeating them;
  - rejects missing manifest ids loudly instead of leaving owner files to raise raw `KeyError`; and
  - preserves object identity so downstream suites still operate on the same already-loaded `FixtureBundle` instances.
- Extend `tests/python/test_fixture_parity_support_contract.py` with focused coverage for the new helper, including:
  - a success case that proves requested manifest ids resolve in the requested order to the same loaded bundle objects;
  - a duplicate-request rejection case; and
  - a missing-manifest rejection case.
- `tests/python/test_grouped_capture_parity_suite.py` stops assigning `GROUPED_MATCH_FIXTURE_BUNDLE`, `NAMED_GROUP_FIXTURE_BUNDLE`, `GROUPED_SEGMENT_FIXTURE_BUNDLE`, `NESTED_GROUP_FIXTURE_BUNDLE`, `NESTED_GROUP_ALTERNATION_FIXTURE_BUNDLE`, `GROUPED_ALTERNATION_FIXTURE_BUNDLE`, `OPTIONAL_GROUP_FIXTURE_BUNDLE`, and `OPTIONAL_GROUP_ALTERNATION_FIXTURE_BUNDLE` through repeated `FIXTURE_BUNDLES_BY_MANIFEST_ID[...]` indexing and uses the shared helper instead.
- `tests/python/test_open_ended_quantified_group_parity_suite.py` stops assigning `OPEN_ENDED_ALTERNATION_BUNDLE`, `OPEN_ENDED_CONDITIONAL_BUNDLE`, `BROADER_RANGE_OPEN_ENDED_ALTERNATION_BUNDLE`, `BROADER_RANGE_OPEN_ENDED_CONDITIONAL_BUNDLE`, `BROADER_RANGE_OPEN_ENDED_BACKTRACKING_HEAVY_BUNDLE`, `OPEN_ENDED_BACKTRACKING_HEAVY_BUNDLE`, and `NESTED_OPEN_ENDED_ALTERNATION_BUNDLE` through repeated `FIXTURE_BUNDLES_BY_MANIFEST_ID[...]` indexing and uses the shared helper instead.
- `tests/python/test_quantified_alternation_parity_suite.py` stops assigning `QUANTIFIED_ALTERNATION_BOUNDED_BUNDLE`, `QUANTIFIED_ALTERNATION_BROADER_RANGE_BUNDLE`, `QUANTIFIED_ALTERNATION_CONDITIONAL_BUNDLE`, `QUANTIFIED_ALTERNATION_OPEN_ENDED_BUNDLE`, `QUANTIFIED_ALTERNATION_NESTED_BRANCH_BUNDLE`, and `BACKTRACKING_HEAVY_BUNDLE` through repeated `FIXTURE_BUNDLES_BY_MANIFEST_ID[...]` indexing and uses the shared helper instead.
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` stops assigning `NESTED_BROADER_RANGE_ALTERNATION_BUNDLE`, `NESTED_BROADER_RANGE_CONDITIONAL_BUNDLE`, `BROADER_RANGE_CONDITIONAL_BUNDLE`, `BROADER_RANGE_BACKTRACKING_HEAVY_BUNDLE`, and `NESTED_BROADER_RANGE_BACKTRACKING_HEAVY_BUNDLE` through repeated `FIXTURE_BUNDLES_BY_MANIFEST_ID[...]` indexing and uses the shared helper instead.
- `tests/python/test_conditional_group_exists_parity_suite.py` stops assigning `QUANTIFIED_CONDITIONAL_BUNDLE`, `QUANTIFIED_CONDITIONAL_ALTERNATION_BUNDLE`, and `FULLY_EMPTY_ALTERNATION_BUNDLE` through repeated `FIXTURE_BUNDLES_BY_MANIFEST_ID[...]` indexing and uses the shared helper instead.
- `tests/python/test_parser_matrix_parity_suite.py` stops assigning `PARSER_MATRIX_OWNER_BUNDLE` and `CONDITIONAL_ASSERTION_DIAGNOSTIC_OWNER_BUNDLE` through repeated `OWNER_FIXTURE_BUNDLES_BY_MANIFEST_ID[...]` indexing and uses the shared helper instead.
- Preserve current behavior after the cleanup:
  - each suite keeps the same loaded bundle order, selected manifest ids, and per-bundle object identity as before;
  - downstream uses of `FIXTURE_BUNDLES_BY_MANIFEST_ID` and `OWNER_FIXTURE_BUNDLES_BY_MANIFEST_ID` that still need keyed access remain valid;
  - no fixture selection, case ordering, direct-test frontier coverage, or parity expectations change; and
  - no harness, report, README, or tracked project-state behavior changes.
- Keep the cleanup structural and limited to the eight files above. Do not widen it into implementation code, reports, benchmarks, README text, or tracked state prose.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py::test_published_fixture_bundles_by_manifest_id_returns_requested_bundles tests/python/test_fixture_parity_support_contract.py::test_published_fixture_bundles_by_manifest_id_rejects_duplicate_manifest_ids tests/python/test_fixture_parity_support_contract.py::test_load_published_fixture_bundles_preserves_selected_path_order tests/python/test_grouped_capture_parity_suite.py::test_fixture_bundles_load_expected_published_owner_order tests/python/test_grouped_capture_parity_suite.py::test_grouped_capture_direct_test_buckets_cover_selected_frontier tests/python/test_open_ended_quantified_group_parity_suite.py::test_parity_suite_stays_aligned_with_published_correctness_fixture tests/python/test_open_ended_quantified_group_parity_suite.py::test_open_ended_quantified_group_direct_test_case_id_buckets_cover_selected_frontier tests/python/test_quantified_alternation_parity_suite.py::test_parity_suite_stays_aligned_with_published_correctness_fixture tests/python/test_quantified_alternation_parity_suite.py::test_quantified_alternation_direct_test_case_id_buckets_cover_selected_frontier tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py::test_parity_suite_stays_aligned_with_published_correctness_fixture tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py::test_wider_ranged_repeat_quantified_group_direct_test_case_id_buckets_cover_selected_frontier tests/python/test_conditional_group_exists_parity_suite.py::test_parity_suite_stays_aligned_with_published_correctness_fixture tests/python/test_conditional_group_exists_parity_suite.py::test_generated_quantified_conditional_compile_cases_stay_anchored_to_published_manifests tests/python/test_parser_matrix_parity_suite.py::test_parser_matrix_parity_suite_stays_aligned_with_published_correctness_fixture tests/python/test_parser_matrix_parity_suite.py::test_parser_matrix_direct_test_buckets_cover_selected_frontier tests/python/test_parser_matrix_parity_suite.py::test_conditional_assertion_diagnostic_fixture_stays_aligned_with_published_correctness_fixture`
- `bash -lc "! rg -n '^([A-Z_]+_BUNDLE|[A-Z_]+_FIXTURE_BUNDLE|PARSER_MATRIX_OWNER_BUNDLE|CONDITIONAL_ASSERTION_DIAGNOSTIC_OWNER_BUNDLE) = (FIXTURE_BUNDLES_BY_MANIFEST_ID|OWNER_FIXTURE_BUNDLES_BY_MANIFEST_ID)\\[' tests/python/test_grouped_capture_parity_suite.py tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_quantified_alternation_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py tests/python/test_conditional_group_exists_parity_suite.py tests/python/test_parser_matrix_parity_suite.py"`

## Constraints
- Reuse `tests/python/fixture_parity_support.py` as the shared-support home; do not add a new helper module, registry, or abstraction tier.
- Keep the helper mapping-oriented and structural; do not couple it to suite-specific selector names, fixture paths, or owner-specific business logic.
- Preserve the existing top-level `FIXTURE_BUNDLES` and `*_BUNDLES_BY_MANIFEST_ID` values in every scoped file; this task is about deleting repeated alias plumbing, not changing how published bundles are loaded or cached.

## Notes
- `RBR-1126` is the next available unreserved task id in this checkout:
  - the highest live task id across `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, and `ops/tasks/blocked/` is `1125`; and
  - `rg -n 'RBR-112[6-9]|RBR-11[3-9][0-9]' ops/state/backlog.md ops/state/current_status.md` returned no reserved future ids in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` contains no task files in this checkout.
- JSON burn-down remains complete and current in both tracked and live views for this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, and `blocked: 0`; and
  - the latest runtime cycle shows both task workers finishing `done`, with no inherited-dirty checkpoint churn or stalled post-task refresh path.
- The remaining duplication is concrete in the live checkout:
  - `tests/python/test_grouped_capture_parity_suite.py:65` through `:80` still carry eight repeated `FIXTURE_BUNDLES_BY_MANIFEST_ID[...]` alias assignments;
  - `tests/python/test_open_ended_quantified_group_parity_suite.py:71` through `:89` still carry seven repeated `FIXTURE_BUNDLES_BY_MANIFEST_ID[...]` alias assignments;
  - `tests/python/test_quantified_alternation_parity_suite.py:84` through `:99` still carry six repeated `FIXTURE_BUNDLES_BY_MANIFEST_ID[...]` alias assignments;
  - `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py:60` through `:72` still carry five repeated `FIXTURE_BUNDLES_BY_MANIFEST_ID[...]` alias assignments;
  - `tests/python/test_conditional_group_exists_parity_suite.py:75` through `:81` still carry three repeated `FIXTURE_BUNDLES_BY_MANIFEST_ID[...]` alias assignments; and
  - `tests/python/test_parser_matrix_parity_suite.py:37` through `:38` still carry the same owner-local alias block through `OWNER_FIXTURE_BUNDLES_BY_MANIFEST_ID[...]`.
- The focused verification slice is green in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py::test_published_fixture_bundles_by_manifest_id_returns_requested_bundles tests/python/test_fixture_parity_support_contract.py::test_published_fixture_bundles_by_manifest_id_rejects_duplicate_manifest_ids tests/python/test_fixture_parity_support_contract.py::test_load_published_fixture_bundles_preserves_selected_path_order tests/python/test_grouped_capture_parity_suite.py::test_fixture_bundles_load_expected_published_owner_order tests/python/test_grouped_capture_parity_suite.py::test_grouped_capture_direct_test_buckets_cover_selected_frontier tests/python/test_open_ended_quantified_group_parity_suite.py::test_parity_suite_stays_aligned_with_published_correctness_fixture tests/python/test_open_ended_quantified_group_parity_suite.py::test_open_ended_quantified_group_direct_test_case_id_buckets_cover_selected_frontier tests/python/test_quantified_alternation_parity_suite.py::test_parity_suite_stays_aligned_with_published_correctness_fixture tests/python/test_quantified_alternation_parity_suite.py::test_quantified_alternation_direct_test_case_id_buckets_cover_selected_frontier tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py::test_parity_suite_stays_aligned_with_published_correctness_fixture tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py::test_wider_ranged_repeat_quantified_group_direct_test_case_id_buckets_cover_selected_frontier tests/python/test_conditional_group_exists_parity_suite.py::test_parity_suite_stays_aligned_with_published_correctness_fixture tests/python/test_conditional_group_exists_parity_suite.py::test_generated_quantified_conditional_compile_cases_stay_anchored_to_published_manifests tests/python/test_parser_matrix_parity_suite.py::test_parser_matrix_parity_suite_stays_aligned_with_published_correctness_fixture tests/python/test_parser_matrix_parity_suite.py::test_parser_matrix_direct_test_buckets_cover_selected_frontier tests/python/test_parser_matrix_parity_suite.py::test_conditional_assertion_diagnostic_fixture_stays_aligned_with_published_correctness_fixture` returned `63 passed in 0.30s` in this run.
- The negative `rg` verification above currently fails exactly on the targeted alias boilerplate, so it is an acceptance check for this cleanup rather than unrelated repo drift.
