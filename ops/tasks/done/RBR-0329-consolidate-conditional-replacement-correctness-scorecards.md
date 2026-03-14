# RBR-0329: Consolidate conditional replacement correctness scorecards into the data-driven suite

Status: done
Owner: architecture-implementation
Created: 2026-03-14
Completed: 2026-03-14

## Goal
- Replace the remaining conditional-replacement correctness wrapper modules with one legible, data-driven scorecard suite so this replacement-conditioned frontier is asserted in one place instead of across repeated cargo-build, subprocess, tracked-report, and representative-case boilerplate.

## Deliverables
- `tests/conformance/test_combined_correctness_scorecards.py`
- `tests/conformance/correctness_expectations.py`
- `tests/conformance/scorecard_suite_support.py`
- `tests/report_assertions.py`
- Delete `tests/conformance/test_correctness_conditional_group_exists_replacement_workflows.py`
- Delete `tests/conformance/test_correctness_conditional_group_exists_no_else_replacement_workflows.py`
- Delete `tests/conformance/test_correctness_conditional_group_exists_empty_else_replacement_workflows.py`
- Delete `tests/conformance/test_correctness_conditional_group_exists_empty_yes_else_replacement_workflows.py`
- Delete `tests/conformance/test_correctness_conditional_group_exists_fully_empty_replacement_workflows.py`
- Delete `tests/conformance/test_correctness_conditional_group_exists_alternation_replacement_workflows.py`
- Delete `tests/conformance/test_correctness_conditional_group_exists_nested_replacement_workflows.py`
- Delete `tests/conformance/test_correctness_conditional_group_exists_quantified_replacement_workflows.py`

## Acceptance Criteria
- The conditional-replacement scorecard contracts currently spread across those eight superseded modules are covered from `tests/conformance/test_combined_correctness_scorecards.py` by extending the existing data-driven `assert_correctness_scorecard_suite(...)` pattern rather than adding another bespoke subprocess wrapper.
- `tests/conformance/correctness_expectations.py` grows one explicit manifest-keyed expectation table and helper accessors for exactly these eight manifests:
  - `conditional-group-exists-replacement-workflows`
  - `conditional-group-exists-no-else-replacement-workflows`
  - `conditional-group-exists-empty-else-replacement-workflows`
  - `conditional-group-exists-empty-yes-else-replacement-workflows`
  - `conditional-group-exists-fully-empty-replacement-workflows`
  - `conditional-group-exists-alternation-replacement-workflows`
  - `conditional-group-exists-nested-replacement-workflows`
  - `conditional-group-exists-quantified-replacement-workflows`
- Fixture-prefix selection is derived from `python/rebar_harness/correctness.py` and its existing ordered fixture registry plus manifest-loading helpers instead of restating long `--fixtures` command lines, cumulative manifest counts, or tracked-report metadata in eight separate modules.
- The consolidated expectations keep representative replacement behavior explicit for numbered and named `sub()` and `subn()` workflows, including present versus absent conditional arms, empty-arm variants, alternation-heavy replacement branches, nested replacement-conditioned conditionals, quantified replacement-conditioned conditionals, and compiled-`Pattern` entrypoints where the source manifests currently publish them.
- Representative case assertions are evaluated through the existing adapter path (`evaluate_case()`, `CpythonReAdapter`, and `RebarAdapter`) instead of hard-coding a permanent `pass` versus `unimplemented` split, so the suite stays valid as replacement parity widens.
- Shared report assertions remain in `tests/report_assertions.py` or `tests/conformance/scorecard_suite_support.py`; the new coverage must not reintroduce copied schema, baseline, tracked-report, fixture-accounting, layer-summary, or suite-summary assertions in per-manifest files.
- After the consolidation lands, none of the eight superseded wrapper modules remain in `tests/conformance/`, and the adjacent non-replacement conditional workflow tests stay intact.

## Constraints
- Keep this task scoped to correctness test architecture for the eight replacement-conditioned manifests listed above; do not change Rust code, `python/rebar/` runtime behavior, fixture contents, benchmark workloads, or published reports to complete it.
- Reuse the existing combined-scorecard helpers and expectation-building pattern from `RBR-0274`; prefer deleting repeated wrapper modules over introducing another family-specific harness layer.
- Do not collapse unrelated non-replacement conditional scorecard tests in the same run.

## Notes
- These eight wrapper modules total about 1.8k lines and currently duplicate the same cargo-build plus scorecard-regeneration flow with only manifest ids and representative replacement cases varying.
- Build on the existing data-driven shape already used in `tests/conformance/test_combined_correctness_scorecards.py`; this should be a follow-on consolidation, not a new testing architecture.

## Completion Notes
- Added a dedicated eight-manifest conditional-replacement expectation table plus helper accessors in `tests/conformance/correctness_expectations.py`, and wired `tests/conformance/test_combined_correctness_scorecards.py` to run that family through `assert_correctness_scorecard_suite(...)`.
- Kept the coverage on shared assertion paths by adding `assert_correctness_suites_present(...)` in `tests/report_assertions.py` and reusing it from `tests/conformance/scorecard_suite_support.py`.
- Deleted the eight superseded conditional-replacement wrapper modules and verified the new shared path with `PYTHONPATH=python python3 -m unittest tests.conformance.test_combined_correctness_scorecards.CorrectnessScorecardSuitesTest.test_runner_regenerates_conditional_replacement_correctness_scorecards tests.conformance.test_combined_correctness_scorecards.CorrectnessScorecardSuitesTest.test_runner_regenerates_open_ended_quantified_group_scorecards -q`.
