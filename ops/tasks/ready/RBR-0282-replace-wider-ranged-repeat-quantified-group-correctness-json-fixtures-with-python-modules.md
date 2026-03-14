# RBR-0282: Replace the wider-ranged-repeat quantified-group correctness JSON fixtures with Python modules

Status: ready
Owner: architecture-implementation
Created: 2026-03-14

## Goal
- Reduce tracked JSON and simplify the correctness harness input path by replacing the wider-ranged-repeat quantified-group correctness manifests with ordinary Python fixture modules while preserving the existing scorecard surface.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/wider_ranged_repeat_quantified_group_workflows.py`
- `tests/conformance/fixtures/wider_ranged_repeat_quantified_group_alternation_workflows.py`
- `tests/conformance/fixtures/broader_range_wider_ranged_repeat_quantified_group_alternation_workflows.py`
- `tests/conformance/fixtures/wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py`
- `tests/conformance/fixtures/broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py`
- `tests/conformance/fixtures/wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py`
- `tests/conformance/fixtures/broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.py`
- Delete `tests/conformance/fixtures/wider_ranged_repeat_quantified_group_workflows.json`
- Delete `tests/conformance/fixtures/wider_ranged_repeat_quantified_group_alternation_workflows.json`
- Delete `tests/conformance/fixtures/broader_range_wider_ranged_repeat_quantified_group_alternation_workflows.json`
- Delete `tests/conformance/fixtures/wider_ranged_repeat_quantified_group_alternation_conditional_workflows.json`
- Delete `tests/conformance/fixtures/broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.json`
- Delete `tests/conformance/fixtures/wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.json`
- Delete `tests/conformance/fixtures/broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows.json`
- `tests/conformance/correctness_expectations.py`
- `tests/conformance/test_wider_ranged_repeat_quantified_group_scorecards.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- `python/rebar_harness/correctness.py` continues to load fixture manifests from both `.json` and `.py` paths through one shared validation path; do not add a second loader, generator step, or package-discovery layer for this family.
- Each of the seven targeted wider-ranged-repeat quantified-group manifests becomes a one-manifest-per-file Python module exposing the same manifest id, suite id, defaults, case ids, and case payloads that the deleted JSON file previously supplied, and no duplicate JSON copy of those seven manifests remains in the tree.
- `DEFAULT_FIXTURE_PATHS` points at the seven new `.py` files, and `tests/conformance/correctness_expectations.py` plus `tests/conformance/test_wider_ranged_repeat_quantified_group_scorecards.py` continue deriving manifest inventory from `DEFAULT_FIXTURE_PATHS` with `load_fixture_manifest()` rather than growing a family-specific code path.
- The consolidated wider-ranged-repeat scorecard suite and the combined correctness scorecard suite still pass with the Python-backed fixtures, and the regenerated `reports/correctness/latest.json` preserves the existing manifest ordering, manifest ids, suite ids, case counts, and aggregate totals except for the fixture path extensions changing from `.json` to `.py`.
- The git-tracked JSON blob count decreases by exactly 7 relative to the current live baseline in this checkout, from `122` to `115`, because the seven deleted correctness fixtures are replaced by Python modules instead of new tracked JSON.

## Constraints
- Keep the scope to the seven wider-ranged-repeat quantified-group correctness manifests listed above; do not convert benchmark workloads, open-ended quantified-group fixtures, or the pending nested broader `{1,4}` follow-on in the same run.
- Do not change Rust code, `python/rebar` runtime behavior, or the correctness report schema.
- Prefer simple Python `MANIFEST` modules and shared validation over generators, codegen, or another fixture DSL.

## Notes
- `RBR-0277` already consolidated this family's scorecard assertions into `tests/conformance/test_wider_ranged_repeat_quantified_group_scorecards.py`, and `RBR-0281` already proved the mixed `.json`/`.py` fixture path in `python/rebar_harness/correctness.py`, so this task is a bounded representation cleanup rather than a harness redesign.
- The latest tracked dashboard snapshot still shows a flat JSON delta, but the live tracked JSON baseline in this checkout is already `122` after `RBR-0281`; verify the count with `git ls-files '*.json' | wc -l` instead of relying on the stale pre-`RBR-0281` dashboard number.
- Keep the fixture path model path-based so `python -m rebar_harness.correctness --fixtures ...` continues to work without another discovery abstraction.
