# RBR-0285: Replace the conditional-group-exists fully-empty correctness JSON fixtures with Python modules

Status: ready
Owner: architecture-implementation
Created: 2026-03-14

## Goal
- Reduce tracked JSON and simplify the correctness harness input path by replacing the `conditional_group_exists_fully_empty*` correctness manifests with ordinary Python fixture modules while preserving the published scorecard surface.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/conditional_group_exists_fully_empty_workflows.py`
- `tests/conformance/fixtures/conditional_group_exists_fully_empty_alternation_workflows.py`
- `tests/conformance/fixtures/conditional_group_exists_fully_empty_nested_workflows.py`
- `tests/conformance/fixtures/conditional_group_exists_fully_empty_quantified_workflows.py`
- `tests/conformance/fixtures/conditional_group_exists_fully_empty_replacement_workflows.py`
- Delete `tests/conformance/fixtures/conditional_group_exists_fully_empty_workflows.json`
- Delete `tests/conformance/fixtures/conditional_group_exists_fully_empty_alternation_workflows.json`
- Delete `tests/conformance/fixtures/conditional_group_exists_fully_empty_nested_workflows.json`
- Delete `tests/conformance/fixtures/conditional_group_exists_fully_empty_quantified_workflows.json`
- Delete `tests/conformance/fixtures/conditional_group_exists_fully_empty_replacement_workflows.json`
- `reports/correctness/latest.json`

## Acceptance Criteria
- `python/rebar_harness/correctness.py` continues to load fixture manifests from both `.json` and `.py` paths through the existing shared validation path; do not add another loader, generator step, or package-discovery layer for this family.
- Each of the five targeted `conditional_group_exists_fully_empty*` manifests becomes a one-manifest-per-file Python module exposing the same manifest ids, suite ids, defaults, case ids, and case payloads that the deleted JSON files previously supplied, and no duplicate JSON copy of those five manifests remains in the tree.
- `DEFAULT_FIXTURE_PATHS` points at the five new `.py` files in the same positions relative to the surrounding conditional manifests, so combined fixture ordering, manifest inventory, and `python -m rebar_harness.correctness --fixtures ...` behavior stay path-based and unchanged apart from the extension swap.
- The regenerated `reports/correctness/latest.json` preserves the existing manifest ordering, manifest ids, suite ids, case counts, and aggregate totals for the targeted fully-empty family except for the fixture path extensions changing from `.json` to `.py`.
- The existing correctness verification surface still passes with the Python-backed fixtures: `tests.conformance.test_combined_correctness_scorecards`, `tests.conformance.test_correctness_conditional_group_exists_fully_empty_alternation_workflows`, `tests.conformance.test_correctness_conditional_group_exists_fully_empty_nested_workflows`, `tests.conformance.test_correctness_conditional_group_exists_fully_empty_quantified_workflows`, and `tests.conformance.test_correctness_conditional_group_exists_fully_empty_replacement_workflows`.
- The git-tracked JSON blob count decreases by exactly 5 relative to the live baseline in this checkout, from `103` to `98`.

## Constraints
- Keep the scope to the five `conditional_group_exists_fully_empty*` correctness manifests listed above; do not convert `empty_else`, `empty_yes_else`, `no_else`, assertion-diagnostic, benchmark, or report JSON in the same run.
- Do not change Rust code, `python/rebar` runtime behavior, or the correctness report schema.
- Prefer simple Python `MANIFEST` modules and the existing shared validation path over generators, codegen, or another fixture DSL.

## Notes
- `.rebar/runtime/dashboard.md` still reports `tracked_json_blob_count: 129` and `tracked_json_blob_delta: 0`, but the live tracked baseline in this checkout is already `103`; verify the count with `git ls-files '*.json' | wc -l` instead of relying on the stale dashboard total.
- `RBR-0284` already converted the adjacent `conditional_group_exists_empty_yes_else*` family, so this task should follow that same path-based fixture swap rather than introducing another harness abstraction.
- The fully-empty family already has combined-scorecard coverage plus four dedicated conformance tests, so this is a bounded representation cleanup rather than a correctness-harness redesign.
