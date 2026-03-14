# RBR-0331: Consolidate quantified-alternation correctness scorecards into the data-driven suite

Status: done
Owner: architecture-implementation
Created: 2026-03-14

## Goal
- Replace the remaining quantified-alternation correctness wrapper modules with one legible, data-driven scorecard suite so this quantified frontier is asserted in one place instead of across repeated cargo-build, subprocess, tracked-report, and representative-case boilerplate.

## Deliverables
- `tests/conformance/test_combined_correctness_scorecards.py`
- `tests/conformance/correctness_expectations.py`
- `tests/conformance/scorecard_suite_support.py`
- Delete `tests/conformance/test_correctness_quantified_alternation_broader_range_workflows.py`
- Delete `tests/conformance/test_correctness_quantified_alternation_open_ended_workflows.py`
- Delete `tests/conformance/test_correctness_quantified_alternation_nested_branch_workflows.py`
- Delete `tests/conformance/test_correctness_quantified_alternation_backtracking_heavy_workflows.py`
- Delete `tests/conformance/test_correctness_quantified_alternation_conditional_workflows.py`
- Delete `tests/conformance/test_correctness_quantified_alternation_branch_local_backreference_workflows.py`

## Acceptance Criteria
- The quantified-alternation scorecard contracts currently spread across those six superseded modules are covered from `tests/conformance/test_combined_correctness_scorecards.py` by extending the existing `assert_correctness_scorecard_suite(...)` path rather than adding another bespoke subprocess wrapper.
- `tests/conformance/correctness_expectations.py` grows one explicit manifest-keyed expectation table plus helper accessors for exactly these six manifests:
  - `quantified-alternation-broader-range-workflows`
  - `quantified-alternation-open-ended-workflows`
  - `quantified-alternation-nested-branch-workflows`
  - `quantified-alternation-backtracking-heavy-workflows`
  - `quantified-alternation-conditional-workflows`
  - `quantified-alternation-branch-local-backreference-workflows`
- Fixture-prefix selection is derived from `python/rebar_harness/correctness.py` and its existing ordered fixture registry plus manifest-loading helpers instead of restating long `--fixtures` command lines, cumulative manifest counts, or tracked-report metadata in six separate modules.
- The consolidated expectations keep representative quantified-alternation behavior explicit for numbered and named compile metadata, module-search lower-bound hits, pattern-level repeated-match successes, below-lower-bound or invalid-branch no-match observations, overlapping/backtracking branch order, conditional present-versus-absent flows, and same-branch backreference replay where those cases are already published today.
- Representative case assertions are evaluated through the existing adapter path (`evaluate_case()`, `CpythonReAdapter`, and `RebarAdapter`) instead of hard-coding a permanent `pass` versus `unimplemented` split, so the suite stays valid as quantified-alternation parity widens.
- Shared report assertions remain in `tests/conformance/scorecard_suite_support.py` or existing shared assertion helpers; the new coverage must not reintroduce copied schema, baseline, tracked-report, fixture-accounting, layer-summary, or suite-summary assertions in per-manifest files.
- After the consolidation lands, none of the six superseded wrapper modules remain in `tests/conformance/`, and the adjacent quantified-nested-group and optional-group correctness workflow tests stay intact.

## Constraints
- Keep this task scoped to correctness test architecture for the six quantified-alternation manifests listed above; do not change Rust code, `python/rebar/` runtime behavior, fixture contents, benchmark workloads, or published reports to complete it.
- Reuse the existing combined-scorecard helpers and expectation-building pattern already used by `RBR-0329`; prefer deleting repeated wrapper modules over introducing another family-specific harness layer.
- Do not collapse unrelated quantified-nested-group, optional-group, or conditional-replacement scorecard tests in the same run.

## Notes
- These six wrapper modules total about 2.6k lines and still duplicate the same build-plus-regenerate flow with only manifest ids and representative quantified-alternation cases varying.
- This task intentionally stays independent of the active `RBR-0330` feature slice so the architecture queue can keep shrinking duplicated correctness plumbing without waiting on new quantified nested-group fixtures to land first.

## Completion
- Added `QUANTIFIED_ALTERNATION_CORRECTNESS_SCORECARD_EXPECTATIONS` plus shared accessors in `tests/conformance/correctness_expectations.py` for the six quantified-alternation manifests, and routed them through `tests/conformance/test_combined_correctness_scorecards.py`.
- Kept the shared assertions on the existing `assert_correctness_scorecard_suite(...)` path, with representative-case checks evaluated through `evaluate_case()` rather than hard-coded `pass`/`unimplemented` expectations.
- Deleted the six superseded quantified-alternation wrapper modules after verifying the consolidated suite covered them.

## Verification
- `.venv/bin/python -m pytest tests/conformance/test_combined_correctness_scorecards.py`
- `git diff --name-status -- tests/conformance/test_correctness_quantified_alternation_broader_range_workflows.py tests/conformance/test_correctness_quantified_alternation_open_ended_workflows.py tests/conformance/test_correctness_quantified_alternation_nested_branch_workflows.py tests/conformance/test_correctness_quantified_alternation_backtracking_heavy_workflows.py tests/conformance/test_correctness_quantified_alternation_conditional_workflows.py tests/conformance/test_correctness_quantified_alternation_branch_local_backreference_workflows.py`
- `rg --files tests/conformance | rg 'test_correctness_quantified_alternation_(broader_range|open_ended|nested_branch|backtracking_heavy|conditional|branch_local_backreference)_workflows\\.py$'` returned no matches.
