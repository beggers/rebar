# RBR-0283: Replace the quantified-alternation correctness JSON fixtures with Python modules

Status: ready
Owner: architecture-implementation
Created: 2026-03-14

## Goal
- Reduce tracked JSON and simplify the correctness harness input path by replacing the standalone quantified-alternation correctness manifests with ordinary Python fixture modules while preserving the existing scorecard surface.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/quantified_alternation_workflows.py`
- `tests/conformance/fixtures/quantified_alternation_broader_range_workflows.py`
- `tests/conformance/fixtures/quantified_alternation_open_ended_workflows.py`
- `tests/conformance/fixtures/quantified_alternation_nested_branch_workflows.py`
- `tests/conformance/fixtures/quantified_alternation_conditional_workflows.py`
- `tests/conformance/fixtures/quantified_alternation_backtracking_heavy_workflows.py`
- `tests/conformance/fixtures/quantified_alternation_branch_local_backreference_workflows.py`
- Delete `tests/conformance/fixtures/quantified_alternation_workflows.json`
- Delete `tests/conformance/fixtures/quantified_alternation_broader_range_workflows.json`
- Delete `tests/conformance/fixtures/quantified_alternation_open_ended_workflows.json`
- Delete `tests/conformance/fixtures/quantified_alternation_nested_branch_workflows.json`
- Delete `tests/conformance/fixtures/quantified_alternation_conditional_workflows.json`
- Delete `tests/conformance/fixtures/quantified_alternation_backtracking_heavy_workflows.json`
- Delete `tests/conformance/fixtures/quantified_alternation_branch_local_backreference_workflows.json`
- `reports/correctness/latest.json`

## Acceptance Criteria
- `python/rebar_harness/correctness.py` continues to load fixture manifests from both `.json` and `.py` paths through the existing shared validation path; do not add a second loader, generator step, or package-discovery layer for this family.
- Each of the seven targeted quantified-alternation manifests becomes a one-manifest-per-file Python module exposing the same manifest id, suite id, defaults, case ids, and case payloads that the deleted JSON file previously supplied, and no duplicate JSON copy of those seven manifests remains in the tree.
- `DEFAULT_FIXTURE_PATHS` points at the seven new `.py` files while preserving the existing quantified-alternation ordering between `conditional_group_exists_quantified_alternation_workflows.json` and the later non-quantified families, so `tests/conformance/test_combined_correctness_scorecards.py` and the existing manifest-loading helpers keep deriving fixture inventory from one path registry instead of a family-specific branch.
- The regenerated `reports/correctness/latest.json` preserves the existing manifest ordering, manifest ids, suite ids, case counts, and aggregate totals for the targeted quantified-alternation family except for the fixture path extensions changing from `.json` to `.py`.
- The existing quantified-alternation correctness surface still passes with the Python-backed fixtures: `tests.conformance.test_combined_correctness_scorecards`, `tests.conformance.test_correctness_quantified_alternation_broader_range_workflows`, `tests.conformance.test_correctness_quantified_alternation_open_ended_workflows`, `tests.conformance.test_correctness_quantified_alternation_nested_branch_workflows`, `tests.conformance.test_correctness_quantified_alternation_conditional_workflows`, `tests.conformance.test_correctness_quantified_alternation_backtracking_heavy_workflows`, and `tests.conformance.test_correctness_quantified_alternation_branch_local_backreference_workflows`.
- The git-tracked JSON blob count decreases by exactly 7 relative to the live baseline when the task starts; in the current checkout that means `115` tracked `*.json` files become `108`.

## Constraints
- Keep the scope to the seven quantified-alternation correctness manifests listed above; do not convert `conditional_group_exists_quantified_alternation_workflows.json`, benchmark workloads, grouped counted-repeat fixtures, or other correctness families in the same run.
- Do not change Rust code, `python/rebar` runtime behavior, or the correctness report schema.
- Prefer simple Python `MANIFEST` modules and the existing shared validation path over generators, codegen, or another fixture DSL.

## Notes
- `.rebar/runtime/dashboard.md` still reports `tracked_json_blob_count: 129` and `tracked_json_blob_delta: 0`, but the live tracked baseline in this checkout is already `115` after `RBR-0281` and `RBR-0282`; verify the count with `git ls-files '*.json' | wc -l` instead of relying on the stale dashboard total.
- `RBR-0274` already folded the base `quantified-alternation-workflows` manifest into `tests/conformance/test_combined_correctness_scorecards.py`, and the six follow-on quantified-alternation manifests already have dedicated correctness scorecard tests that assert manifest ids and representative cases rather than hard-coding `.json` path strings.
- Keep the fixture model path-based so `python -m rebar_harness.correctness --fixtures ...` continues to accept explicit file paths without another discovery abstraction.
