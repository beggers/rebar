# RBR-0339: Consolidate nested broader-range wider-ranged-repeat quantified-group alternation correctness scorecards

Status: ready
Owner: architecture-implementation
Created: 2026-03-14

## Goal
- Replace the remaining nested broader-range wider-ranged-repeat quantified-group alternation correctness wrapper modules with one legible, data-driven scorecard suite so this nested counted-repeat frontier is asserted in one place instead of across repeated cargo-build, subprocess, tracked-report, and representative-case boilerplate.

## Deliverables
- `tests/conformance/test_combined_correctness_scorecards.py`
- `tests/conformance/correctness_expectations.py`
- Delete `tests/conformance/test_correctness_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_workflows.py`
- Delete `tests/conformance/test_correctness_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py`
- Delete `tests/conformance/test_correctness_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py`

## Acceptance Criteria
- The three nested broader-range wider-ranged-repeat quantified-group alternation scorecard contracts currently spread across those superseded modules are covered from `tests/conformance/test_combined_correctness_scorecards.py` by extending the existing `assert_correctness_scorecard_suite(...)` path rather than adding another bespoke subprocess wrapper.
- `tests/conformance/correctness_expectations.py` grows one explicit manifest-keyed expectation table plus helper accessors for exactly these three manifests:
  - `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-workflows`
  - `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-workflows`
  - `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-workflows`
- Fixture-prefix selection is derived from `python/rebar_harness/correctness.py` and the existing ordered `DEFAULT_FIXTURE_PATHS` inventory instead of restating long `--report` reruns, cumulative manifest counts, or tracked-report metadata in three separate modules.
- The consolidated expectations keep representative nested broader-range behavior explicit for numbered and named compile metadata, lower-bound `module.search()` hits, repeated `Pattern.fullmatch()` successes across mixed or upper-bound paths, present-versus-absent conditional flows, and no-match short, invalid-tail, or overflow observations where those cases are already published today.
- Representative case assertions are evaluated through the existing adapter path (`evaluate_case()`, `CpythonReAdapter`, and `RebarAdapter`) instead of hard-coding permanent `pass` or `unimplemented` fragments, so the suite stays valid as nearby parity slices change status later.
- Shared report assertions remain in `tests/conformance/scorecard_suite_support.py` or the existing shared assertion helpers; the new coverage must not reintroduce copied schema, baseline, tracked-report, fixture-accounting, layer-summary, or suite-summary assertions in per-manifest files.
- After the consolidation lands, none of the three superseded wrapper modules remain in `tests/conformance/`, and the queued `nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_workflows` follow-on stays outside this task.

## Constraints
- Keep this task scoped to correctness test architecture for the three nested broader-range manifests listed above; do not change Rust code, `python/rebar/` runtime behavior, fixture contents, benchmark workloads, or published reports to complete it.
- Reuse the existing combined-scorecard helpers and expectation-building pattern already used by `RBR-0331`, `RBR-0335`, and `RBR-0337`; prefer deleting repeated wrapper modules over introducing another family-specific harness layer.
- Do not fold `nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_workflows` into this task or make the consolidation depend on `RBR-0338` landing first.

## Notes
- These three wrapper modules still total 549 lines and duplicate the same build-plus-regenerate flow with only manifest ids and representative nested broader-range cases varying.
- `tests/conformance/correctness_expectations.py` does not currently carry a nested broader-range expectation family, so this task can land as one bounded table-plus-accessor extension on the existing shared path.
