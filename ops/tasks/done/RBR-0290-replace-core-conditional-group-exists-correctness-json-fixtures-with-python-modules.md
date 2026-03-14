# RBR-0290: Replace the core conditional-group-exists correctness JSON fixtures with Python modules

Status: done
Owner: architecture-implementation
Created: 2026-03-14

## Goal
- Reduce tracked JSON and simplify the correctness harness input path by replacing the remaining core `conditional_group_exists*` correctness manifests with ordinary Python fixture modules while preserving the published scorecard surface.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/conditional_group_exists_workflows.py`
- `tests/conformance/fixtures/conditional_group_exists_replacement_workflows.py`
- `tests/conformance/fixtures/conditional_group_exists_alternation_workflows.py`
- `tests/conformance/fixtures/conditional_group_exists_nested_workflows.py`
- `tests/conformance/fixtures/conditional_group_exists_quantified_workflows.py`
- `tests/conformance/fixtures/conditional_group_exists_assertion_diagnostics.py`
- Delete `tests/conformance/fixtures/conditional_group_exists_workflows.json`
- Delete `tests/conformance/fixtures/conditional_group_exists_replacement_workflows.json`
- Delete `tests/conformance/fixtures/conditional_group_exists_alternation_workflows.json`
- Delete `tests/conformance/fixtures/conditional_group_exists_nested_workflows.json`
- Delete `tests/conformance/fixtures/conditional_group_exists_quantified_workflows.json`
- Delete `tests/conformance/fixtures/conditional_group_exists_assertion_diagnostics.json`
- `reports/correctness/latest.json`

## Acceptance Criteria
- `python/rebar_harness/correctness.py` continues to load fixture manifests from both `.json` and `.py` paths through the existing shared validation path; do not add another loader, generator step, or package-discovery layer for this family.
- Each of the six targeted manifests becomes a one-manifest-per-file Python module exposing the same manifest ids, suite ids, defaults, case ids, and case payloads that the deleted JSON files previously supplied, and no duplicate JSON copy of those six manifests remains in the tree.
- `DEFAULT_FIXTURE_PATHS` points at the six new `.py` files in the same positions relative to the surrounding conditional manifests, so combined fixture ordering, manifest inventory, and `python -m rebar_harness.correctness --fixtures ...` behavior stay path-based and unchanged apart from the extension swaps.
- The regenerated `reports/correctness/latest.json` preserves the existing manifest ordering, manifest ids, suite ids, case counts, and aggregate totals for the targeted core conditional-group-exists family except for the fixture path extensions changing from `.json` to `.py`.
- The existing correctness verification surface still passes with the Python-backed fixtures: `tests.conformance.test_combined_correctness_scorecards`, `tests.conformance.test_correctness_conditional_group_exists_alternation_workflows`, `tests.conformance.test_correctness_conditional_group_exists_nested_workflows`, `tests.conformance.test_correctness_conditional_group_exists_quantified_workflows`, and `tests.conformance.test_correctness_conditional_group_exists_replacement_workflows`.
- The live tracked JSON file count decreases by exactly 6 relative to the task-start baseline; in the current checkout, `git ls-files '*.json' | wc -l` should move from `103` to `97`.

## Constraints
- Keep the scope to the six `conditional_group_exists*` manifests listed above; do not convert `conditional_group_exists_no_else*`, `conditional_group_exists_empty_*`, `conditional_group_exists_branch_local_backreference_workflows.json`, `conditional_group_exists_quantified_alternation_workflows.json`, benchmark workloads, or report JSON in the same run.
- Do not change Rust code, `python/rebar` runtime behavior, or the correctness report schema.
- Prefer simple Python `MANIFEST` modules and the existing shared validation path over generators, codegen, or another fixture DSL.

## Notes
- `.rebar/runtime/dashboard.md` currently reports `tracked_json_blob_count: 103` and `tracked_json_blob_delta: 0`.
- The base `conditional-group-exists-workflows` and parser-only `conditional-group-exists-assertion-diagnostics` manifests do not have dedicated standalone test modules in this checkout; `tests.conformance.test_combined_correctness_scorecards` is the acceptance surface that must keep covering those two manifests after the extension swap.
- The current worktree already contains separate uncommitted fixture swaps for `conditional_group_exists_no_else*` and `parser_smoke`; leave those files out of scope for this task rather than folding another in-flight cleanup into it.

## Completion Notes
- Repointed the six in-scope `DEFAULT_FIXTURE_PATHS` entries in `python/rebar_harness/correctness.py` from `.json` to `.py` while keeping the existing shared `.json`/`.py` manifest loader path intact.
- Replaced the six targeted core `conditional_group_exists*` JSON fixtures with one-manifest-per-file Python `MANIFEST` modules that preserve the same manifest ids, suite ids, defaults, case ids, and case payloads, then deleted the JSON originals.
- Regenerated `reports/correctness/latest.json` in the current worktree; the targeted fixture paths now resolve to the new `.py` modules, and the required conformance suite passed against that regenerated report.
- Verified with `PYTHONPATH=python python3 -m unittest tests.conformance.test_combined_correctness_scorecards tests.conformance.test_correctness_conditional_group_exists_alternation_workflows tests.conformance.test_correctness_conditional_group_exists_nested_workflows tests.conformance.test_correctness_conditional_group_exists_quantified_workflows tests.conformance.test_correctness_conditional_group_exists_replacement_workflows`.
- Verified the live working-tree JSON count moved from `87` to `81` via `rg --files -g '*.json' | wc -l`; `git ls-files '*.json' | wc -l` still reports `103` until the harness-owned commit updates the index, and the six in-scope fixture paths now exist only as `.py` files.
