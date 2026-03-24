# RBR-1148: Collapse generated parity matrix runners onto shared support

Status: done
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the repeated generated-parity matrix runner that still lives separately in the quantified alternation, branch-local backreference, and conditional-group-exists parity suites by routing those checks through one shared helper surface on `tests/python/fixture_parity_support.py` instead of keeping parallel `HELPERS`, `compile_with_cpython_parity(...)`, `record_generated_match_failure(...)`, and failure-preview plumbing in each owner.

## Deliverables
- `tests/python/fixture_parity_support.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/python/test_quantified_alternation_parity_suite.py`
- `tests/python/test_branch_local_backreference_parity_suite.py`
- `tests/python/test_conditional_group_exists_parity_suite.py`

## Acceptance Criteria
- Add one bounded shared helper surface on `tests/python/fixture_parity_support.py`, or reuse a strictly smaller equivalent on that file, for generated parity matrix execution:
  - start from the existing `compile_with_cpython_parity(...)` and `record_generated_match_failure(...)` support instead of re-implementing their behavior in another module;
  - accept caller-provided candidate texts plus a caller-provided pattern extractor so the helper can preserve the current mixed `str`/`bytes` quantified suites and the current `str`-only conditional suites without branching back out into owner-local loops;
  - keep the current generated matrix coverage shape: module and compiled-pattern calls for `search`, `match`, and `fullmatch` across every generated candidate text;
  - centralize the current failure-preview truncation and assertion message formatting on the shared helper surface instead of repeating `FAILURE_PREVIEW_LIMIT = 20` and the preview-assembly block in each owner; and
  - keep the helper on the existing parity-support module instead of adding another helper file, registry, or abstraction layer.
- `tests/python/test_quantified_alternation_parity_suite.py` stops owning the repeated generated matrix runner locally:
  - keep the suite-local generated spec table and `_generated_candidate_texts(...)` builder;
  - route `test_generated_quantified_alternation_text_matrix_matches_cpython(...)` through the shared helper instead of hand-writing the backend loop and failure-preview block; and
  - remove the now-redundant owner-local generated-matrix helper constant(s) when the shared helper fully subsumes them.
- `tests/python/test_branch_local_backreference_parity_suite.py` stops owning the same generated matrix runner locally:
  - keep `_generated_branch_local_candidate_texts(...)` and the suite-local spec table;
  - route `test_generated_quantified_branch_local_text_matrix_matches_cpython(...)` through the same shared helper; and
  - remove the now-redundant owner-local generated-matrix helper constant(s) when the shared helper fully subsumes them.
- `tests/python/test_conditional_group_exists_parity_suite.py` stops owning the same generated matrix runner twice:
  - keep the suite-local candidate-text sources for quantified and fully-empty conditional coverage;
  - route both `test_generated_quantified_conditional_text_matrix_matches_cpython(...)` and `test_generated_fully_empty_alternation_text_matrix_matches_cpython(...)` through the same shared helper instead of repeating the backend loop and failure-preview block twice in that file; and
  - remove the now-redundant owner-local generated-matrix helper constant(s) when the shared helper fully subsumes them.
- Extend `tests/python/test_fixture_parity_support_contract.py` with focused coverage for the shared helper instead of leaving the generated matrix contract implicit:
  - one check proves the helper executes the current module-and-pattern `search`/`match`/`fullmatch` matrix against representative generated candidate texts;
  - one check proves the helper preserves the current truncated failure-preview formatting when mismatches accumulate; and
  - one check proves the helper still accepts both `case_pattern` and `str_case_pattern` call sites without changing current owner behavior.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py::test_generated_quantified_alternation_compile_cases_stay_anchored_to_published_manifests tests/python/test_quantified_alternation_parity_suite.py::test_generated_quantified_alternation_text_matrix_matches_cpython tests/python/test_branch_local_backreference_parity_suite.py::test_generated_quantified_branch_local_compile_cases_stay_anchored_to_published_manifests tests/python/test_branch_local_backreference_parity_suite.py::test_generated_quantified_branch_local_text_matrix_matches_cpython tests/python/test_conditional_group_exists_parity_suite.py::test_generated_quantified_conditional_compile_cases_stay_anchored_to_published_manifests tests/python/test_conditional_group_exists_parity_suite.py::test_generated_fully_empty_alternation_compile_cases_stay_anchored_to_published_manifest tests/python/test_conditional_group_exists_parity_suite.py::test_generated_quantified_conditional_text_matrix_matches_cpython tests/python/test_conditional_group_exists_parity_suite.py::test_generated_fully_empty_alternation_text_matrix_matches_cpython tests/python/test_fixture_parity_support_contract.py::test_generated_specs_by_manifest_id_preserves_order_and_owner_labelled_lookup_failures tests/python/test_fixture_parity_support_contract.py::test_generated_compile_anchor_case_selection_preserves_flattened_order_across_bundles tests/python/test_fixture_parity_support_contract.py::test_generated_compile_anchor_helpers_preserve_representative_spec_contract_inputs`

## Constraints
- Keep the cleanup structural and limited to the five files above. Do not widen it into implementation code, correctness fixtures, benchmark files, README text, or tracked ops state prose.
- Prefer deleting repeated owner-local matrix-running code over adding a second wrapper layer that only renames the same loop.
- Preserve the current generated candidate-text sets, helper coverage (`search` / `match` / `fullmatch`), owner-specific pattern extractors, and failure-message prefixes exactly.

## Notes
- `RBR-1148` is the next available unreserved architecture task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run; and
  - `rg -n "RBR-1148|RBR-1149|RBR-1150|RBR-1151|RBR-1152" ops/state/backlog.md ops/state/current_status.md` returned no matches in this run.
- No blocked architecture task exists to reopen or retire first in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining duplication is concrete and cross-file in the current checkout:
  - `tests/python/test_quantified_alternation_parity_suite.py`, `tests/python/test_branch_local_backreference_parity_suite.py`, and `tests/python/test_conditional_group_exists_parity_suite.py` all still hand-write the same generated matrix execution loop over `search` / `match` / `fullmatch`;
  - those files still repeat the same `compile_with_cpython_parity(...)` setup, `record_generated_match_failure(...)` accumulation, and `FAILURE_PREVIEW_LIMIT` truncation logic; and
  - `tests/python/test_conditional_group_exists_parity_suite.py` repeats that same loop twice inside one owner, so the duplication is no longer just cross-file.
- Verification status in this run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py::test_generated_quantified_alternation_compile_cases_stay_anchored_to_published_manifests tests/python/test_quantified_alternation_parity_suite.py::test_generated_quantified_alternation_text_matrix_matches_cpython tests/python/test_branch_local_backreference_parity_suite.py::test_generated_quantified_branch_local_compile_cases_stay_anchored_to_published_manifests tests/python/test_branch_local_backreference_parity_suite.py::test_generated_quantified_branch_local_text_matrix_matches_cpython tests/python/test_conditional_group_exists_parity_suite.py::test_generated_quantified_conditional_compile_cases_stay_anchored_to_published_manifests tests/python/test_conditional_group_exists_parity_suite.py::test_generated_fully_empty_alternation_compile_cases_stay_anchored_to_published_manifest tests/python/test_conditional_group_exists_parity_suite.py::test_generated_quantified_conditional_text_matrix_matches_cpython tests/python/test_conditional_group_exists_parity_suite.py::test_generated_fully_empty_alternation_text_matrix_matches_cpython tests/python/test_fixture_parity_support_contract.py::test_generated_specs_by_manifest_id_preserves_order_and_owner_labelled_lookup_failures tests/python/test_fixture_parity_support_contract.py::test_generated_compile_anchor_case_selection_preserves_flattened_order_across_bundles tests/python/test_fixture_parity_support_contract.py::test_generated_compile_anchor_helpers_preserve_representative_spec_contract_inputs` returned `63 passed` in this run.
- Completed in this run:
  - Added `assert_generated_text_matrix_matches_cpython(...)` plus shared helper/preview support in `tests/python/fixture_parity_support.py`.
  - Routed the quantified alternation, branch-local backreference, and conditional generated parity matrix tests through that shared helper and removed their owner-local loop/preview constants.
  - Extended `tests/python/test_fixture_parity_support_contract.py` with shared-helper coverage for matrix execution order, truncated failure previews, and both `case_pattern` and `str_case_pattern` extractor call sites.
- Verification status after the refactor:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py::test_generated_quantified_alternation_compile_cases_stay_anchored_to_published_manifests tests/python/test_quantified_alternation_parity_suite.py::test_generated_quantified_alternation_text_matrix_matches_cpython tests/python/test_branch_local_backreference_parity_suite.py::test_generated_quantified_branch_local_compile_cases_stay_anchored_to_published_manifests tests/python/test_branch_local_backreference_parity_suite.py::test_generated_quantified_branch_local_text_matrix_matches_cpython tests/python/test_conditional_group_exists_parity_suite.py::test_generated_quantified_conditional_compile_cases_stay_anchored_to_published_manifests tests/python/test_conditional_group_exists_parity_suite.py::test_generated_fully_empty_alternation_compile_cases_stay_anchored_to_published_manifest tests/python/test_conditional_group_exists_parity_suite.py::test_generated_quantified_conditional_text_matrix_matches_cpython tests/python/test_conditional_group_exists_parity_suite.py::test_generated_fully_empty_alternation_text_matrix_matches_cpython tests/python/test_fixture_parity_support_contract.py::test_generated_specs_by_manifest_id_preserves_order_and_owner_labelled_lookup_failures tests/python/test_fixture_parity_support_contract.py::test_generated_compile_anchor_case_selection_preserves_flattened_order_across_bundles tests/python/test_fixture_parity_support_contract.py::test_generated_compile_anchor_helpers_preserve_representative_spec_contract_inputs tests/python/test_fixture_parity_support_contract.py::test_assert_generated_text_matrix_matches_cpython_executes_module_and_pattern_matrix tests/python/test_fixture_parity_support_contract.py::test_assert_generated_text_matrix_matches_cpython_truncates_failure_preview tests/python/test_fixture_parity_support_contract.py::test_assert_generated_text_matrix_matches_cpython_accepts_current_pattern_extractors` returned `67 passed` in this run.
