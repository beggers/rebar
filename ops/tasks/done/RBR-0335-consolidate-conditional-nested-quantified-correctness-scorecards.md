# RBR-0335: Consolidate nested and quantified conditional correctness scorecards into the data-driven suite

Status: done
Owner: architecture-implementation
Created: 2026-03-14
Completed: 2026-03-14

## Goal
- Replace the remaining non-alternation conditional correctness wrapper modules for nested and quantified group-exists workflows with one legible, data-driven scorecard suite so this conditional frontier is asserted in one place instead of across repeated cargo-build, subprocess, tracked-report, and representative-case boilerplate.

## Deliverables
- `tests/conformance/test_combined_correctness_scorecards.py`
- `tests/conformance/correctness_expectations.py`
- Delete `tests/conformance/test_correctness_conditional_group_exists_nested_workflows.py`
- Delete `tests/conformance/test_correctness_conditional_group_exists_no_else_nested_workflows.py`
- Delete `tests/conformance/test_correctness_conditional_group_exists_empty_else_nested_workflows.py`
- Delete `tests/conformance/test_correctness_conditional_group_exists_empty_yes_else_nested_workflows.py`
- Delete `tests/conformance/test_correctness_conditional_group_exists_fully_empty_nested_workflows.py`
- Delete `tests/conformance/test_correctness_conditional_group_exists_quantified_workflows.py`
- Delete `tests/conformance/test_correctness_conditional_group_exists_no_else_quantified_workflows.py`
- Delete `tests/conformance/test_correctness_conditional_group_exists_empty_else_quantified_workflows.py`
- Delete `tests/conformance/test_correctness_conditional_group_exists_empty_yes_else_quantified_workflows.py`
- Delete `tests/conformance/test_correctness_conditional_group_exists_fully_empty_quantified_workflows.py`

## Acceptance Criteria
- The ten scorecard contracts currently spread across those superseded modules are covered from `tests/conformance/test_combined_correctness_scorecards.py` by extending the existing `assert_correctness_scorecard_suite(...)` path rather than adding another bespoke subprocess wrapper.
- `tests/conformance/correctness_expectations.py` grows one explicit manifest-keyed expectation table plus helper accessors for exactly these ten manifests:
  - `conditional-group-exists-nested-workflows`
  - `conditional-group-exists-no-else-nested-workflows`
  - `conditional-group-exists-empty-else-nested-workflows`
  - `conditional-group-exists-empty-yes-else-nested-workflows`
  - `conditional-group-exists-fully-empty-nested-workflows`
  - `conditional-group-exists-quantified-workflows`
  - `conditional-group-exists-no-else-quantified-workflows`
  - `conditional-group-exists-empty-else-quantified-workflows`
  - `conditional-group-exists-empty-yes-else-quantified-workflows`
  - `conditional-group-exists-fully-empty-quantified-workflows`
- Fixture-prefix selection is derived from `python/rebar_harness/correctness.py` and the existing ordered `DEFAULT_FIXTURE_PATHS` inventory instead of restating long `--fixtures` command lines, cumulative manifest counts, or tracked-report metadata in ten separate modules.
- The consolidated expectations keep representative non-alternation conditional behavior explicit for numbered and named compile metadata, present-versus-absent outer arms, nested inner-else reachability, omitted-arm versus empty-arm variants, fully empty branches, and quantified repeat success-versus-missing-repeat observations where those cases are already published today.
- Representative case assertions are evaluated through the existing adapter path (`evaluate_case()`, `CpythonReAdapter`, and `RebarAdapter`) instead of hard-coding permanent `pass` snapshots or manually copying CPython/rebar observation fragments, so the suite stays valid if any of these nested or quantified conditional slices change status later.
- Shared report assertions remain in `tests/conformance/scorecard_suite_support.py` or existing shared assertion helpers; the new coverage must not reintroduce copied schema, baseline, tracked-report, fixture-accounting, layer-summary, or suite-summary assertions in per-manifest files.
- After the consolidation lands, none of the ten superseded wrapper modules remain in `tests/conformance/`, and the adjacent `conditional_group_exists_branch_local_backreference`, alternation-bearing conditional, quantified-nested-group, and exact-repeat grouped-alternation correctness workflow tests stay intact.

## Constraints
- Keep this task scoped to correctness test architecture for the ten nested/quantified conditional manifests listed above; do not change Rust code, `python/rebar/` runtime behavior, fixture contents, benchmark workloads, or published reports to complete it.
- Reuse the existing combined-scorecard helpers and expectation-building pattern already used by `RBR-0331` and `RBR-0333`; prefer deleting repeated wrapper modules over introducing another family-specific harness layer.
- Do not collapse the separate branch-local-backreference conditional wrapper or any benchmark tests in the same run.

## Notes
- These ten wrapper modules total 2,717 lines and still duplicate the same build-plus-regenerate flow with only manifest ids and representative nested/quantified conditional cases varying.
- The existing `_build_scorecard_expectation(...)` path in `tests/conformance/correctness_expectations.py` already derives cumulative fixture prefixes from `DEFAULT_FIXTURE_PATHS`, so this family can land as another bounded table-plus-accessor extension instead of a new abstraction.

## Completion
- Added `CONDITIONAL_NESTED_QUANTIFIED_CORRECTNESS_SCORECARD_EXPECTATIONS` plus shared accessors in `tests/conformance/correctness_expectations.py`, and routed the ten nested/quantified conditional manifests through `tests/conformance/test_combined_correctness_scorecards.py`.
- Moved the last non-alternation nested/quantified conditional scorecard coverage onto `assert_correctness_scorecard_suite(...)`, including the previously duplicated `conditional-group-exists-empty-else-nested-workflows` entry that had partially lived in the combined expectation table.
- Deleted the ten superseded nested/quantified conditional wrapper modules from `tests/conformance/`.

## Verification
- `.venv/bin/python -m pytest tests/conformance/test_combined_correctness_scorecards.py -q`
- `.venv/bin/python - <<'PY'` importing `conditional_nested_quantified_scorecard_target_manifest_ids()` confirmed it resolves exactly the ten intended manifests from `DEFAULT_FIXTURE_PATHS`, and `combined_target_manifest_ids()` no longer includes `conditional-group-exists-empty-else-nested-workflows`.
- `git diff --name-status -- tests/conformance/test_correctness_conditional_group_exists_nested_workflows.py tests/conformance/test_correctness_conditional_group_exists_no_else_nested_workflows.py tests/conformance/test_correctness_conditional_group_exists_empty_else_nested_workflows.py tests/conformance/test_correctness_conditional_group_exists_empty_yes_else_nested_workflows.py tests/conformance/test_correctness_conditional_group_exists_fully_empty_nested_workflows.py tests/conformance/test_correctness_conditional_group_exists_quantified_workflows.py tests/conformance/test_correctness_conditional_group_exists_no_else_quantified_workflows.py tests/conformance/test_correctness_conditional_group_exists_empty_else_quantified_workflows.py tests/conformance/test_correctness_conditional_group_exists_empty_yes_else_quantified_workflows.py tests/conformance/test_correctness_conditional_group_exists_fully_empty_quantified_workflows.py` showed each deleted wrapper as `D`, and `rg --files tests/conformance | rg 'test_correctness_conditional_group_exists_(nested|no_else_nested|empty_else_nested|empty_yes_else_nested|fully_empty_nested|quantified|no_else_quantified|empty_else_quantified|empty_yes_else_quantified|fully_empty_quantified)_workflows\\.py$'` returned no matches.
