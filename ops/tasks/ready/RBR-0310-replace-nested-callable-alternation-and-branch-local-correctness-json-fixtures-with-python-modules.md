# RBR-0310: Replace the nested-callable, alternation, and branch-local correctness JSON fixtures with Python modules

Status: ready
Owner: architecture-implementation
Created: 2026-03-14

## Goal
- Reduce tracked JSON and simplify the correctness harness input path by replacing the next contiguous early-workflow correctness manifests with ordinary Python fixture modules while preserving the published combined scorecard surface.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/nested_group_callable_replacement_workflows.py`
- `tests/conformance/fixtures/literal_alternation_workflows.py`
- `tests/conformance/fixtures/grouped_alternation_workflows.py`
- `tests/conformance/fixtures/grouped_alternation_replacement_workflows.py`
- `tests/conformance/fixtures/grouped_alternation_callable_replacement_workflows.py`
- `tests/conformance/fixtures/branch_local_backreference_workflows.py`
- Delete `tests/conformance/fixtures/nested_group_callable_replacement_workflows.json`
- Delete `tests/conformance/fixtures/literal_alternation_workflows.json`
- Delete `tests/conformance/fixtures/grouped_alternation_workflows.json`
- Delete `tests/conformance/fixtures/grouped_alternation_replacement_workflows.json`
- Delete `tests/conformance/fixtures/grouped_alternation_callable_replacement_workflows.json`
- Delete `tests/conformance/fixtures/branch_local_backreference_workflows.json`
- `reports/correctness/latest.json`

## Acceptance Criteria
- `python/rebar_harness/correctness.py` continues to load fixture manifests from both `.json` and `.py` paths through the existing shared validation path; do not add a second loader, generator step, or package-discovery layer for this batch.
- Each of the six targeted manifests becomes a one-manifest-per-file Python module exposing the same manifest ids, suite ids, defaults, case ids, case ordering, and case payloads that the deleted JSON files previously supplied, and no duplicate JSON copy of those six manifests remains in the tree.
- The converted manifests preserve the current checkout ids and case counts: `nested-group-callable-replacement-workflows` with `8` cases, `literal-alternation-workflows` with `3`, `grouped-alternation-workflows` with `6`, `grouped-alternation-replacement-workflows` with `8`, `grouped-alternation-callable-replacement-workflows` with `8`, and `branch-local-backreference-workflows` with `6`.
- `DEFAULT_FIXTURE_PATHS` points at the six new `.py` files while preserving their existing ordering between `quantified_nested_group_replacement_workflows.py` and `conditional_group_exists_branch_local_backreference_workflows.py`, so the combined scorecard helpers and fixture inventory keep deriving this slice from one shared path registry instead of another family-specific branch.
- The regenerated `reports/correctness/latest.json` preserves the existing manifest ordering, manifest ids, suite ids, case counts, aggregate totals, and representative coverage for the targeted manifests except for the fixture path extensions changing from `.json` to `.py`.
- The existing verification surface still passes with the Python-backed fixtures, including `tests.conformance.test_combined_correctness_scorecards`, `tests.conformance.test_correctness_fixture_inventory_contract`, and `tests.conformance.test_python_fixture_manifest_contract`.
- The git-tracked JSON blob count decreases by exactly `6` relative to the live baseline when the task starts; in the current checkout that means `git ls-files '*.json' | wc -l` moves from `44` to `38`.

## Constraints
- Keep the scope to the six correctness manifests listed above; do not convert `quantified_branch_local_backreference_workflows.json`, the exact-repeat/ranged-repeat quantified-group fixtures, the early parser/module-surface fixtures, benchmark workloads, or report/config JSON in the same run.
- Do not change Rust code, `python/rebar` runtime behavior, or the correctness report schema.
- Prefer simple Python `MANIFEST` modules and the existing shared validation path over generators, codegen, or another fixture DSL.
- For the callable-replacement fixtures in this batch, keep the stored replacement payloads as the existing plain descriptor dicts that the loader materializes today; do not inline Python callables into the checked-in manifests.

## Notes
- `.rebar/runtime/dashboard.md` still reports `tracked_json_blob_count: 103` and `tracked_json_blob_delta: 0`, but the live tracked baseline in this checkout is already `44`; verify the reduction with `git ls-files '*.json' | wc -l` rather than relying on the stale dashboard snapshot.
- This is the remaining contiguous non-bootstrap JSON block inside `python/rebar_harness/correctness.py::DEFAULT_FIXTURE_PATHS` between the already-converted quantified nested-group replacement fixture and the already-converted conditional branch-local follow-on, so it burns down another sizable cluster without mixing in the parser/module-surface scaffolds.
- The combined scorecard expectations already cover these manifest ids and representative case ids, and this checkout does not carry dedicated file-path regression tests for this batch; keep the coverage anchored in the shared scorecard and fixture-contract suites unless a real path assumption appears during execution.
