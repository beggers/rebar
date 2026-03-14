# RBR-0333: Consolidate alternation-bearing conditional correctness scorecards into the data-driven suite

Status: ready
Owner: architecture-implementation
Created: 2026-03-14

## Goal
- Replace the remaining alternation-bearing conditional correctness wrapper modules with one legible, data-driven scorecard suite so these conditional frontiers are asserted in one place instead of across repeated cargo-build, subprocess, tracked-report, and representative-case boilerplate.

## Deliverables
- `tests/conformance/test_combined_correctness_scorecards.py`
- `tests/conformance/correctness_expectations.py`
- Delete `tests/conformance/test_correctness_conditional_group_exists_alternation_workflows.py`
- Delete `tests/conformance/test_correctness_conditional_group_exists_no_else_alternation_workflows.py`
- Delete `tests/conformance/test_correctness_conditional_group_exists_empty_else_alternation_workflows.py`
- Delete `tests/conformance/test_correctness_conditional_group_exists_empty_yes_else_alternation_workflows.py`
- Delete `tests/conformance/test_correctness_conditional_group_exists_fully_empty_alternation_workflows.py`
- Delete `tests/conformance/test_correctness_conditional_group_exists_quantified_alternation_workflows.py`

## Acceptance Criteria
- The six scorecard contracts currently spread across those superseded modules are covered from `tests/conformance/test_combined_correctness_scorecards.py` by extending the existing `assert_correctness_scorecard_suite(...)` path rather than adding another bespoke subprocess wrapper.
- `tests/conformance/correctness_expectations.py` grows one explicit manifest-keyed expectation table plus helper accessors for exactly these six manifests:
  - `conditional-group-exists-alternation-workflows`
  - `conditional-group-exists-no-else-alternation-workflows`
  - `conditional-group-exists-empty-else-alternation-workflows`
  - `conditional-group-exists-empty-yes-else-alternation-workflows`
  - `conditional-group-exists-fully-empty-alternation-workflows`
  - `conditional-group-exists-quantified-alternation-workflows`
- Fixture-prefix selection is derived from `python/rebar_harness/correctness.py` and the existing ordered `DEFAULT_FIXTURE_PATHS` inventory instead of restating long `--fixtures` command lines, cumulative manifest counts, or tracked-report metadata in six separate modules.
- The consolidated expectations keep representative alternation-bearing conditional behavior explicit for numbered and named compile metadata, present-versus-absent conditional arms, first-arm versus second-arm alternation branches, empty-arm variants, and the quantified-alternation slice's repeated-arm search/fullmatch observations where those cases are already published today.
- Representative case assertions are evaluated through the existing adapter path (`evaluate_case()`, `CpythonReAdapter`, and `RebarAdapter`) instead of hard-coding a permanent `pass` split, so the suite stays valid if any of these alternation-bearing conditional slices change status later.
- Shared report assertions remain in `tests/conformance/scorecard_suite_support.py` or existing shared assertion helpers; the new coverage must not reintroduce copied schema, baseline, tracked-report, fixture-accounting, layer-summary, or suite-summary assertions in per-manifest files.
- After the consolidation lands, none of the six superseded wrapper modules remain in `tests/conformance/`, and the adjacent non-alternation conditional workflow tests stay intact.

## Constraints
- Keep this task scoped to correctness test architecture for the six alternation-bearing conditional manifests listed above; do not change Rust code, `python/rebar/` runtime behavior, fixture contents, benchmark workloads, or published reports to complete it.
- Reuse the existing combined-scorecard helpers and expectation-building pattern already used by `RBR-0329` and `RBR-0331`; prefer deleting repeated wrapper modules over introducing another family-specific harness layer.
- Do not collapse the remaining nested, quantified-non-alternation, or branch-local-backreference conditional scorecard tests in the same run.

## Notes
- These six wrapper modules total 1,869 lines and still duplicate the same build-plus-regenerate flow with only manifest ids, suite ids, and representative alternation-bearing conditional cases varying.
- This is the next clean scorecard-family follow-on after `RBR-0329` and `RBR-0331`: the existing expectation builder already derives fixture prefixes from `DEFAULT_FIXTURE_PATHS`, so this family can land as another bounded table-plus-accessor extension rather than a new harness abstraction.
