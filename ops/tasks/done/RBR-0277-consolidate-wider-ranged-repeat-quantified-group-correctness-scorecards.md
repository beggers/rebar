# RBR-0277: Consolidate wider-ranged-repeat quantified-group correctness scorecards into one data-driven suite

Status: done
Owner: architecture-implementation
Created: 2026-03-14

## Goal
- Replace the six wider-ranged-repeat quantified-group correctness workflow modules with one legible, data-driven suite so this counted-repeat grouped frontier is asserted in one place instead of across repeated subprocess/report boilerplate and hand-expanded case checks.

## Deliverables
- `tests/conformance/test_wider_ranged_repeat_quantified_group_scorecards.py`
- `tests/conformance/correctness_expectations.py`
- `tests/report_assertions.py`
- Delete `tests/conformance/test_correctness_wider_ranged_repeat_quantified_group_alternation_workflows.py`
- Delete `tests/conformance/test_correctness_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py`
- Delete `tests/conformance/test_correctness_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py`
- Delete `tests/conformance/test_correctness_broader_range_wider_ranged_repeat_quantified_group_alternation_workflows.py`
- Delete `tests/conformance/test_correctness_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py`
- Delete `tests/conformance/test_correctness_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py`

## Acceptance Criteria
- The new suite covers the manifest-specific correctness scorecard contracts currently spread across the six superseded modules for `wider-ranged-repeat-quantified-group-alternation-workflows`, `wider-ranged-repeat-quantified-group-alternation-conditional-workflows`, `wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-workflows`, `broader-range-wider-ranged-repeat-quantified-group-alternation-workflows`, `broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-workflows`, and `broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-workflows`.
- Manifest or fixture-prefix selection is derived from `python/rebar_harness/correctness.py` and its existing `DEFAULT_FIXTURE_PATHS` plus manifest-loading helpers instead of repeating six near-identical `cargo build` and `python -m rebar_harness.correctness` wrappers with hand-copied tracked-report assertions.
- Common report assertions live in shared helpers in `tests/report_assertions.py`, including schema and baseline metadata, tracked report presence, fixture manifest ids and paths, layer summary consistency, and suite summary consistency.
- Manifest-specific expectations remain explicit and data-driven. The consolidated suite still verifies compile metadata plus representative `module.search()` and compiled-`Pattern.fullmatch()` observations for numbered and named branches, including spans, `group_spans`, `groupdict`, named-group fields, no-match `None` cases, lower-bound and upper-bound counted-repeat paths, mixed-branch workflows, and overflow or missing-suffix failures where present.
- The new suite stays valid before and after feature follow-ons: do not hard-code the broader `{1,4}` backtracking-heavy manifest as permanently `unimplemented`; assertions must tolerate the live `pass` versus `unimplemented` split for those cases so `RBR-0276` can land without another test-architecture rewrite.
- After the consolidation lands, none of the six superseded modules remain in `tests/conformance/`.

## Constraints
- Keep this task scoped to the six wider-ranged-repeat quantified-group workflow modules listed above; do not attempt a repo-wide correctness test migration here.
- Keep the work on the Python test surface only. Do not change Rust code, `python/rebar/` runtime behavior, fixture JSON documents, or published reports to complete it.
- Use ordinary Python tables and shared helpers rather than new JSON manifests, generators, or another custom harness layer.

## Notes
- The six current modules total roughly 2.3k lines and rerun the same cargo-build plus correctness-report contract with only manifest ids and case tables varying.
- Build on `RBR-0272` and `RBR-0274`: the wider-ranged-repeat parity frontier is already consolidated on the Python side, and the combined correctness wrapper contract is already data-driven. This task applies the same simplification to the remaining wider-ranged-repeat manifest-specific correctness surface.

## Completion Notes
- Added `tests/conformance/test_wider_ranged_repeat_quantified_group_scorecards.py`, backed by shared manifest-prefix expectations in `tests/conformance/correctness_expectations.py` and shared case/report assertions in `tests/report_assertions.py`.
- Removed the six superseded wider-ranged-repeat quantified-group correctness modules and verified the consolidated suite alongside `tests/conformance/test_combined_correctness_scorecards.py` with `PYTHONPATH=python python3 -m unittest ... -q`.
