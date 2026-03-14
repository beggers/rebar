# RBR-0341: Consolidate the cumulative correctness scorecard wrappers into the data-driven suite

Status: done
Owner: architecture-implementation
Created: 2026-03-14

## Goal
- Replace the remaining cumulative prefix correctness wrapper modules with one legible, data-driven scorecard path so the phase-ladder from parser through grouped-match is asserted through shared expectation tables instead of repeated cargo-build, subprocess, temp-report, and tracked-report boilerplate.

## Deliverables
- `tests/conformance/test_combined_correctness_scorecards.py`
- `tests/conformance/correctness_expectations.py`
- Delete `tests/conformance/test_correctness_parser_matrix.py`
- Delete `tests/conformance/test_correctness_public_api_surface.py`
- Delete `tests/conformance/test_correctness_match_behavior.py`
- Delete `tests/conformance/test_correctness_exported_symbol_surface.py`
- Delete `tests/conformance/test_correctness_pattern_object_surface.py`
- Delete `tests/conformance/test_correctness_module_workflow.py`
- Delete `tests/conformance/test_correctness_collection_replacement_workflows.py`
- Delete `tests/conformance/test_correctness_literal_flag_workflows.py`
- Delete `tests/conformance/test_correctness_grouped_match_workflows.py`

## Acceptance Criteria
- The nine cumulative scorecard contracts currently spread across those superseded modules are covered from `tests/conformance/test_combined_correctness_scorecards.py` by extending the existing `assert_correctness_scorecard_suite(...)` path rather than adding another bespoke subprocess wrapper.
- `tests/conformance/correctness_expectations.py` grows one explicit manifest-keyed expectation table plus helper accessors for exactly these cumulative manifests:
  - `parser-matrix`
  - `public-api-surface`
  - `match-behavior-smoke`
  - `exported-symbol-surface`
  - `pattern-object-surface`
  - `module-workflow-surface`
  - `collection-replacement-workflows`
  - `literal-flag-workflows`
  - `grouped-match-workflows`
- Fixture-prefix selection is derived from `python/rebar_harness/correctness.py` and the ordered `DEFAULT_FIXTURE_PATHS` inventory instead of restating long `--fixtures` command lines, cumulative manifest counts, temporary report loading, or tracked-report checks in nine separate modules.
- The consolidated expectations keep representative cumulative behavior explicit for parser diagnostics, public API helper behavior, match result-shape cases, exported symbol metadata, pattern-object metadata, cache and purge workflows, collection and replacement helpers, literal-flag cache and `IGNORECASE` flows, unsupported-flag observations, and grouped capture/result-shape workflows where those assertions are already published today.
- Representative case assertions are evaluated through the existing adapter path (`evaluate_case()`, `CpythonReAdapter`, and `RebarAdapter`) instead of hard-coding permanent `pass` fragments or direct JSON observation literals, so the suite stays valid as nearby parity slices evolve.
- Shared report assertions remain in `tests/conformance/scorecard_suite_support.py` or the existing report-assertion helpers; the new coverage must not reintroduce copied schema, baseline, phase, fixture-accounting, layer-summary, suite-summary, temp-report, or tracked-report boilerplate in per-manifest files.
- After the consolidation lands, none of the nine superseded wrapper modules remain in `tests/conformance/`, and `pytest tests/conformance/test_combined_correctness_scorecards.py -q` covers the cumulative ladder from `parser-matrix` through `grouped-match-workflows`.

## Constraints
- Keep this task scoped to correctness test architecture for the cumulative manifests listed above; do not change Rust code, `python/rebar/` runtime behavior, fixture contents, benchmark workloads, or published reports to complete it.
- Reuse the existing combined-scorecard helpers and `_build_scorecard_expectation(...)` prefix-selection pattern already used by the recent correctness-scorecard consolidation tasks; prefer deleting repeated wrapper modules over introducing another family-specific harness layer.
- Keep the tracked-scorecard comparison wrappers such as `tests/conformance/test_correctness_quantified_nested_group_replacement_workflows.py` and `tests/conformance/test_correctness_exact_repeat_quantified_group_alternation_workflows.py` out of scope for this task.

## Notes
- These nine wrapper modules currently total 1,881 lines of largely repeated build-plus-regenerate scaffolding.
- `_build_scorecard_expectation(...)` already derives cumulative fixture prefixes from `DEFAULT_FIXTURE_PATHS`, so this ladder is structurally aligned with the shared expectation path already; the remaining work is to encode the representative-case tables and delete the wrappers.

## Completion
- Landed the cumulative prefix manifests in `COMBINED_CORRECTNESS_MANIFEST_EXPECTATIONS`, strengthened the shared scorecard/report assertions to validate cumulative suite/layer structure plus diagnostics consistency, and deleted the nine superseded wrapper modules.
- Verified with `.venv/bin/python -m pytest tests/conformance/test_combined_correctness_scorecards.py -q` (`9 passed, 826 subtests passed`), and confirmed the deleted wrapper paths show `D` in `git diff --name-status`.
