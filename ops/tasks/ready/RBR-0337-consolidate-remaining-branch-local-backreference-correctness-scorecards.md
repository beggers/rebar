# RBR-0337: Consolidate the remaining branch-local-backreference correctness scorecards into the data-driven suite

Status: ready
Owner: architecture-implementation
Created: 2026-03-14

## Goal
- Replace the remaining branch-local-backreference correctness wrapper modules with one legible, data-driven scorecard path so this frontier is asserted through shared expectation tables instead of repeated cargo-build, subprocess, tracked-report, and observation boilerplate.

## Deliverables
- `tests/conformance/test_combined_correctness_scorecards.py`
- `tests/conformance/correctness_expectations.py`
- Delete `tests/conformance/test_correctness_conditional_group_exists_branch_local_backreference_workflows.py`
- Delete `tests/conformance/test_correctness_optional_group_alternation_branch_local_backreference_workflows.py`
- Delete `tests/conformance/test_correctness_quantified_branch_local_backreference_workflows.py`
- Delete `tests/conformance/test_correctness_nested_group_alternation_branch_local_backreference_workflows.py`
- Delete `tests/conformance/test_correctness_quantified_nested_group_alternation_branch_local_backreference_workflows.py`

## Acceptance Criteria
- The scorecard contracts currently spread across those five superseded modules are covered from `tests/conformance/test_combined_correctness_scorecards.py` by extending the existing `assert_correctness_scorecard_suite(...)` path rather than adding another bespoke subprocess wrapper.
- `tests/conformance/correctness_expectations.py` grows one explicit manifest-keyed expectation table plus helper accessors for exactly these three currently non-data-driven manifests:
  - `conditional-group-exists-branch-local-backreference-workflows`
  - `optional-group-alternation-branch-local-backreference-workflows`
  - `quantified-branch-local-backreference-workflows`
- The existing `COMBINED_CORRECTNESS_MANIFEST_EXPECTATIONS` path remains the source of truth for:
  - `nested-group-alternation-branch-local-backreference-workflows`
  - `quantified-nested-group-alternation-branch-local-backreference-workflows`
  and the consolidation proves those two manifests are already fully covered there instead of copying them into a second expectation family.
- Fixture-prefix selection is derived from `python/rebar_harness/correctness.py` and the existing ordered `DEFAULT_FIXTURE_PATHS` inventory instead of restating long `--fixtures` command lines, cumulative manifest counts, or tracked-report metadata in five separate modules.
- The consolidated expectations keep branch-local-backreference behavior explicit for numbered and named compile metadata, same-branch replay successes, conditional present-versus-absent arms, optional-group omitted-capture behavior, lower-bound quantified hits, repeated-branch `Pattern.fullmatch()` successes, and no-match or absent-branch observations where those cases are already published today.
- Representative case assertions are evaluated through the existing adapter path (`evaluate_case()`, `CpythonReAdapter`, and `RebarAdapter`) instead of hard-coding permanent `pass` or `unimplemented` observation fragments, so the suite stays valid as these slices change status later.
- Shared report assertions remain in `tests/conformance/scorecard_suite_support.py` or the existing shared assertion helpers; the new coverage must not reintroduce copied schema, baseline, tracked-report, fixture-accounting, layer-summary, or suite-summary assertions in per-manifest files.
- After the consolidation lands, none of the five superseded wrapper modules remain in `tests/conformance/`, and the preserved shared path stays verifiable with the branch-local-focused subset of `tests/conformance/test_combined_correctness_scorecards.py`.

## Constraints
- Keep this task scoped to correctness test architecture for the current branch-local-backreference manifests listed above; do not change Rust code, `python/rebar/` runtime behavior, fixture contents, benchmark workloads, or published reports to complete it.
- Reuse the existing combined-scorecard helpers and expectation-building pattern already used by `RBR-0329`, `RBR-0331`, `RBR-0333`, and `RBR-0335`; prefer deleting repeated wrapper modules over introducing another family-specific harness layer.
- Do not fold the queued broader `{1,4}` follow-on manifest `nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_workflows` into this task.

## Notes
- These five wrapper modules still total 1,573 lines of largely repeated build-plus-regenerate scaffolding.
- `combined_correctness_case("nested-group-alternation-branch-local-backreference-workflows")` already covers all 8 published cases for that manifest, and `combined_correctness_case("quantified-nested-group-alternation-branch-local-backreference-workflows")` already covers all 10 published cases for that manifest, so those two files are pure wrapper redundancy now.
- This task is independent of `RBR-0336`: it only consolidates scorecard plumbing around manifests that are already landed in the current checkout.
