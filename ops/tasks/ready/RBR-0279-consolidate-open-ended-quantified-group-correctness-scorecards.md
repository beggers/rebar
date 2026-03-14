# RBR-0279: Consolidate open-ended quantified-group correctness scorecards into one data-driven suite

Status: ready
Owner: architecture-implementation
Created: 2026-03-14

## Goal
- Replace the repeated open-ended quantified-group correctness workflow modules with one legible, data-driven suite so this grouped counted-repeat frontier is asserted in one place instead of across repeated subprocess/report boilerplate and hand-expanded case checks.

## Deliverables
- `tests/conformance/test_open_ended_quantified_group_scorecards.py`
- `tests/conformance/correctness_expectations.py`
- `tests/report_assertions.py`
- Delete `tests/conformance/test_correctness_open_ended_quantified_group_alternation_workflows.py`
- Delete `tests/conformance/test_correctness_nested_open_ended_quantified_group_alternation_workflows.py`
- Delete `tests/conformance/test_correctness_broader_range_open_ended_quantified_group_alternation_workflows.py`
- Delete `tests/conformance/test_correctness_open_ended_quantified_group_alternation_conditional_workflows.py`
- Delete `tests/conformance/test_correctness_broader_range_open_ended_quantified_group_alternation_conditional_workflows.py`
- Delete `tests/conformance/test_correctness_open_ended_quantified_group_alternation_backtracking_heavy_workflows.py`
- Delete `tests/conformance/test_correctness_broader_range_open_ended_quantified_group_alternation_backtracking_heavy_workflows.py`

## Acceptance Criteria
- The new suite covers the manifest-specific correctness scorecard contracts currently spread across the seven superseded modules for `open-ended-quantified-group-alternation-workflows`, `nested-open-ended-quantified-group-alternation-workflows`, `broader-range-open-ended-quantified-group-alternation-workflows`, `open-ended-quantified-group-alternation-conditional-workflows`, `broader-range-open-ended-quantified-group-alternation-conditional-workflows`, `open-ended-quantified-group-alternation-backtracking-heavy-workflows`, and `broader-range-open-ended-quantified-group-alternation-backtracking-heavy-workflows`.
- Manifest or fixture-prefix selection is derived from `python/rebar_harness/correctness.py` and its existing `DEFAULT_FIXTURE_PATHS` plus `load_fixture_manifest()` instead of repeating seven near-identical `cargo build` plus `python -m rebar_harness.correctness` wrappers with hand-copied tracked-report assertions.
- `tests/conformance/correctness_expectations.py` grows an explicit open-ended quantified-group expectation table plus manifest-keyed helper accessors, following the established `wider_ranged_repeat_quantified_group_scorecard_*` pattern rather than introducing another bespoke loader or generator path.
- Common report assertions live in `tests/report_assertions.py`, including schema and baseline metadata, tracked report presence, fixture manifest ids and paths, layer summary consistency, and suite summary consistency.
- Manifest-specific expectations remain explicit and data-driven. The consolidated suite still verifies representative compile metadata plus representative `module.search()` and compiled-`Pattern.fullmatch()` observations for numbered and named branches, including lower-bound hits, mixed repeated-branch paths, absent-arm conditional matches, short-input and overflow no-match cases, nested grouped captures, and backtracking-heavy invalid-tail or overlap failures where those behaviors are present in the source manifests.
- The consolidated suite evaluates representative cases through `evaluate_case()` with `CpythonReAdapter` and `RebarAdapter` instead of hard-coding a permanent `pass` versus `unimplemented` split for any targeted manifest, so the test stays valid if one of these open-ended slices changes status later.
- After the consolidation lands, none of the seven superseded open-ended quantified-group correctness modules remain in `tests/conformance/`, while the adjacent `tests/conformance/test_correctness_quantified_alternation_open_ended_workflows.py` remains intact because it belongs to the quantified-alternation family rather than the grouped counted-repeat family.

## Constraints
- Keep this task scoped to the seven open-ended quantified-group workflow modules listed above; do not attempt a repo-wide correctness test migration here.
- Keep the work on the Python test surface only. Do not change Rust code, `python/rebar/` runtime behavior, fixture JSON documents, or published reports to complete it.
- Use ordinary Python tables and shared helpers rather than adding new JSON manifests, generators, or another custom harness layer.

## Notes
- These seven modules currently total about 2.8k lines and rerun the same cargo-build plus correctness-report contract with only manifest ids and representative case tables varying.
- Build on `RBR-0263`, `RBR-0274`, and `RBR-0277`: the matching Python parity frontier is already consolidated in `tests/python/test_open_ended_quantified_group_parity_suite.py`, the cumulative correctness wrapper contract is already data-driven, and the wider-ranged-repeat grouped scorecards already use the intended expectation-driven pattern.
- Keep this architecture cleanup independent of `RBR-0278`; the current benchmark catch-up task should remain executable as-is while this scorecard consolidation lands separately.
