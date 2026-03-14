# RBR-0274: Consolidate the cumulative correctness wrapper tests into one data-driven suite

Status: done
Owner: architecture-implementation
Created: 2026-03-13

## Goal
- Replace the repeated cumulative correctness wrapper modules with one legible, data-driven conformance suite so the combined correctness report contract is asserted in one place instead of across dozens of near-identical files that restate the growing fixture prefix and baseline metadata.

## Deliverables
- `tests/conformance/test_combined_correctness_scorecards.py`
- `tests/conformance/correctness_expectations.py`
- `tests/report_assertions.py`
- Delete the superseded cumulative wrapper modules listed in the Notes section.

## Acceptance Criteria
- The new suite covers the existing combined-scorecard contracts currently spread across the 26 superseded cumulative wrapper modules listed below.
- Fixture-prefix selection is derived from the existing ordered fixture registry in `python/rebar_harness/correctness.py`, using `DEFAULT_FIXTURE_PATHS` and the current manifest-loading helpers, instead of restating long `*_FIXTURES_PATH` constant blocks or full `--fixtures` command lines per module.
- Common correctness-report assertions live in shared helpers rather than being recopied per wrapper file: schema version, phase, baseline metadata, tracked-report presence, summary consistency, and layer or suite summary consistency.
- Manifest-specific expectations remain explicit but data-driven by target manifest id. Each case still checks the selected fixture prefix, the newly added manifest, representative layer or suite ids, and representative case-local observations without hard-coding drifting repo-wide cumulative totals in 26 separate files.
- The specialized correctness tests that are not part of this repeated cumulative-wrapper pattern remain intact and readable, including `tests/conformance/test_correctness_smoke.py`, `tests/conformance/test_correctness_parser_matrix.py`, `tests/conformance/test_correctness_public_api_surface.py`, `tests/conformance/test_correctness_exported_symbol_surface.py`, `tests/conformance/test_correctness_pattern_object_surface.py`, `tests/conformance/test_correctness_module_workflow.py`, `tests/conformance/test_correctness_collection_replacement_workflows.py`, `tests/conformance/test_correctness_literal_flag_workflows.py`, `tests/conformance/test_systematic_feature_corpus.py`, and `tests/conformance/test_systematic_feature_corpus_generator.py`.
- After the consolidation lands, none of the 26 superseded cumulative wrapper modules remain in `tests/conformance/`.

## Constraints
- Keep this task scoped to correctness test architecture. Do not change Rust code, `python/rebar/` runtime behavior, fixture JSON documents, benchmark workloads, or published reports to complete it.
- Prefer test-only changes. If a tiny helper is needed outside `tests/`, keep it limited to exposing the existing default fixture ordering or manifest-loading behavior from `python/rebar_harness/correctness.py`.
- Preserve the current combined correctness coverage and assertion depth. This task is a simplification pass, not a reduction in scorecard checks.
- Use ordinary Python expectation tables and helpers rather than adding JSON manifests, generated blobs, or another custom test harness layer.

## Notes
- These 26 cumulative wrapper modules total roughly 8.8k lines and currently duplicate the same cargo-build, subprocess, baseline, summary, and manifest-prefix assertions that `RBR-0262` already consolidated on the benchmark side.
- Keep the new expectation data keyed by manifest id or fixture-prefix target so future feature-manifest additions stop forcing edits across many historical wrapper files.
- Superseded cumulative wrapper modules:
```text
tests/conformance/test_correctness_branch_local_backreference_workflows.py
tests/conformance/test_correctness_conditional_group_exists_assertion_diagnostics.py
tests/conformance/test_correctness_conditional_group_exists_empty_else_workflows.py
tests/conformance/test_correctness_conditional_group_exists_empty_yes_else_workflows.py
tests/conformance/test_correctness_conditional_group_exists_fully_empty_workflows.py
tests/conformance/test_correctness_conditional_group_exists_no_else_workflows.py
tests/conformance/test_correctness_conditional_group_exists_workflows.py
tests/conformance/test_correctness_exact_repeat_quantified_group_workflows.py
tests/conformance/test_correctness_grouped_alternation_callable_replacement_workflows.py
tests/conformance/test_correctness_grouped_alternation_replacement_workflows.py
tests/conformance/test_correctness_grouped_alternation_workflows.py
tests/conformance/test_correctness_grouped_segment_workflows.py
tests/conformance/test_correctness_literal_alternation_workflows.py
tests/conformance/test_correctness_named_backreference_workflows.py
tests/conformance/test_correctness_named_group_replacement_workflows.py
tests/conformance/test_correctness_named_group_workflows.py
tests/conformance/test_correctness_nested_group_alternation_workflows.py
tests/conformance/test_correctness_nested_group_callable_replacement_workflows.py
tests/conformance/test_correctness_nested_group_replacement_workflows.py
tests/conformance/test_correctness_nested_group_workflows.py
tests/conformance/test_correctness_numbered_backreference_workflows.py
tests/conformance/test_correctness_optional_group_alternation_workflows.py
tests/conformance/test_correctness_optional_group_workflows.py
tests/conformance/test_correctness_quantified_alternation_workflows.py
tests/conformance/test_correctness_ranged_repeat_quantified_group_workflows.py
tests/conformance/test_correctness_wider_ranged_repeat_quantified_group_workflows.py
```

## Completion Note
- Consolidated the repeated cumulative correctness wrappers into `tests/conformance/test_combined_correctness_scorecards.py`, with manifest-keyed prefix selection and representative case expectations centralized in `tests/conformance/correctness_expectations.py`.
- Extended `tests/report_assertions.py` so shared correctness contract checks now cover report metadata, fixture-prefix assertions, and real layer and suite summary consistency instead of repeating those checks across 26 modules.
- Deleted the 26 superseded cumulative wrapper modules listed above; the combined correctness scorecard contract now lives in the single data-driven suite.
- Verified the preserved correctness surface with `python3 -m unittest tests.conformance.test_combined_correctness_scorecards tests.conformance.test_correctness_smoke tests.conformance.test_correctness_parser_matrix tests.conformance.test_correctness_public_api_surface tests.conformance.test_correctness_exported_symbol_surface tests.conformance.test_correctness_pattern_object_surface tests.conformance.test_correctness_module_workflow tests.conformance.test_correctness_collection_replacement_workflows tests.conformance.test_correctness_literal_flag_workflows tests.conformance.test_systematic_feature_corpus` and `python3 -m unittest tests.conformance.test_correctness_match_behavior`.
- `python3 -m unittest tests.conformance.test_systematic_feature_corpus_generator` could not run in this VM because the module imports `pytest` and `pytest` is not installed here.
