# RBR-0312: Replace the nested-group and counted-repeat correctness JSON fixtures with Python modules

Status: done
Owner: architecture-implementation
Created: 2026-03-14

## Goal
- Reduce tracked JSON and simplify the correctness harness input path by replacing the remaining nested-group and counted-repeat correctness manifests with ordinary Python fixture modules while preserving the published combined scorecard surface.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/nested_group_workflows.py`
- `tests/conformance/fixtures/nested_group_alternation_workflows.py`
- `tests/conformance/fixtures/nested_group_replacement_workflows.py`
- `tests/conformance/fixtures/quantified_branch_local_backreference_workflows.py`
- `tests/conformance/fixtures/exact_repeat_quantified_group_workflows.py`
- `tests/conformance/fixtures/exact_repeat_quantified_group_alternation_workflows.py`
- `tests/conformance/fixtures/ranged_repeat_quantified_group_workflows.py`
- Delete `tests/conformance/fixtures/nested_group_workflows.json`
- Delete `tests/conformance/fixtures/nested_group_alternation_workflows.json`
- Delete `tests/conformance/fixtures/nested_group_replacement_workflows.json`
- Delete `tests/conformance/fixtures/quantified_branch_local_backreference_workflows.json`
- Delete `tests/conformance/fixtures/exact_repeat_quantified_group_workflows.json`
- Delete `tests/conformance/fixtures/exact_repeat_quantified_group_alternation_workflows.json`
- Delete `tests/conformance/fixtures/ranged_repeat_quantified_group_workflows.json`
- `reports/correctness/latest.json`

## Acceptance Criteria
- `python/rebar_harness/correctness.py` continues to load fixture manifests from both `.json` and `.py` paths through the existing shared validation path; do not add a second loader, generator step, or package-discovery layer for this batch.
- Each of the seven targeted manifests becomes a one-manifest-per-file Python module exposing the same manifest ids, suite ids, defaults, case ids, case ordering, and case payloads that the deleted JSON files previously supplied, and no duplicate JSON copy of those seven manifests remains in the tree.
- The converted manifests preserve the current checkout ids and case counts: `nested-group-workflows` with `6` cases, `nested-group-alternation-workflows` with `6`, `nested-group-replacement-workflows` with `8`, `quantified-branch-local-backreference-workflows` with `8`, `exact-repeat-quantified-group-workflows` with `6`, `exact-repeat-quantified-group-alternation-workflows` with `10`, and `ranged-repeat-quantified-group-workflows` with `6`.
- `DEFAULT_FIXTURE_PATHS` points at the seven new `.py` files while preserving the current manifest ordering between `grouped_segment_workflows.py` and `wider_ranged_repeat_quantified_group_workflows.py`; keep `quantified_nested_group_replacement_workflows.py`, `nested_group_callable_replacement_workflows.py`, `optional_group_workflows.py`, and the wider-ranged-repeat fixtures in their current relative slots instead of introducing another family-specific fixture list.
- The regenerated `reports/correctness/latest.json` preserves the existing manifest ordering, manifest ids, suite ids, case counts, aggregate totals, and representative coverage for the targeted manifests except for the fixture path extensions changing from `.json` to `.py`.
- The existing verification surface still passes with the Python-backed fixtures, including `tests.conformance.test_combined_correctness_scorecards`, `tests.conformance.test_correctness_fixture_inventory_contract`, `tests.conformance.test_python_fixture_manifest_contract`, `tests.conformance.test_correctness_quantified_branch_local_backreference_workflows`, `tests.conformance.test_correctness_exact_repeat_quantified_group_alternation_workflows`, and `tests.conformance.test_correctness_quantified_nested_group_replacement_workflows`.
- The live JSON count decreases by exactly `7` relative to the current checkout baseline; in this checkout both `git ls-files '*.json' | wc -l` and `rg --files -g '*.json' | wc -l` start at `32` and should finish at `25`, with `rg --files -g '*.json' | wc -l` as the source of truth if the worker runs in a dirty tree where deleted tracked paths linger in `git ls-files`.

## Constraints
- Keep the scope to the seven correctness manifests listed above; do not convert the early parser/module-surface fixtures, `conditional_group_exists_nested_replacement_workflows.json`, `conditional_group_exists_quantified_alternation_workflows.json`, benchmark workloads, or report/config JSON in the same run.
- Do not change Rust code, `python/rebar` runtime behavior, or the correctness report schema.
- Prefer simple Python `MANIFEST` modules and the existing shared validation path over generators, codegen, or another fixture DSL.

## Notes
- `.rebar/runtime/dashboard.md` still reports `tracked_json_blob_count: 103` and `tracked_json_blob_delta: 0`, but the live tracked/filesystem JSON baseline in this checkout is already `32`; size and verify the task against the live counts rather than the stale dashboard snapshot.
- This batch removes the remaining nested-group and counted-repeat JSON fixtures from the default correctness registry without touching the early bootstrap path constants that still appear in several dedicated tests, so it burns down seven tracked JSON files in one run without coupling the work to a broader path-assertion rewrite.
- The current checkout does not carry dedicated fixture-path assertions for these seven manifests; keep verification anchored in the shared combined scorecard and fixture-contract suites plus the existing quantified branch-local, exact-repeat alternation, and quantified nested-group replacement scorecard tests unless a real path-specific assumption appears during execution.

## Completion Notes
- Repointed the seven targeted `DEFAULT_FIXTURE_PATHS` entries in `python/rebar_harness/correctness.py` from `.json` to `.py` while preserving their existing slots between `grouped_segment_workflows.py` and `wider_ranged_repeat_quantified_group_workflows.py`, so the shared mixed-extension loader remains the only manifest path.
- Replaced `nested_group_workflows.json`, `nested_group_alternation_workflows.json`, `nested_group_replacement_workflows.json`, `quantified_branch_local_backreference_workflows.json`, `exact_repeat_quantified_group_workflows.json`, `exact_repeat_quantified_group_alternation_workflows.json`, and `ranged_repeat_quantified_group_workflows.json` with one-manifest-per-file Python `MANIFEST` modules carrying the same manifest ids, suite ids, defaults, case ids, case ordering, and case payloads, then deleted the JSON originals.
- Regenerated `reports/correctness/latest.json`; the converted manifests remain in fixture-order slots `14`, `15`, `16`, `25`, `27`, `28`, and `29`, keep their `6`, `6`, `8`, `8`, `6`, `10`, and `6` case counts, preserve the combined `86`-manifest / `779`-case / `779`-pass / `0`-failure / `0`-unimplemented scorecard totals, and now publish `.py` fixture paths for the targeted slice.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.json` and `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py tests/conformance/test_correctness_fixture_inventory_contract.py tests/conformance/test_python_fixture_manifest_contract.py tests/conformance/test_correctness_quantified_branch_local_backreference_workflows.py tests/conformance/test_correctness_exact_repeat_quantified_group_alternation_workflows.py tests/conformance/test_correctness_quantified_nested_group_replacement_workflows.py` (`8` tests passed, `1024` subtests passed).
- Verified the live JSON reduction with `rg --files -g '*.json' | wc -l` as `32 -> 25`; in this dirty pre-commit worktree `git ls-files '*.json' | wc -l` still reports deleted tracked paths, so the matching deleted-path count was confirmed separately as `git ls-files --deleted '*.json' | wc -l = 7`.
