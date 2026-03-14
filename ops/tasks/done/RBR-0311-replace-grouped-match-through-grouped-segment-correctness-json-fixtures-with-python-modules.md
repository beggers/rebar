# RBR-0311: Replace the grouped-match through grouped-segment correctness JSON fixtures with Python modules

Status: done
Owner: architecture-implementation
Created: 2026-03-14

## Goal
- Reduce tracked JSON and simplify the correctness harness input path by replacing the next contiguous early-workflow correctness manifests with ordinary Python fixture modules while preserving the published combined scorecard surface.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/grouped_match_workflows.py`
- `tests/conformance/fixtures/named_group_workflows.py`
- `tests/conformance/fixtures/named_group_replacement_workflows.py`
- `tests/conformance/fixtures/named_backreference_workflows.py`
- `tests/conformance/fixtures/numbered_backreference_workflows.py`
- `tests/conformance/fixtures/grouped_segment_workflows.py`
- `tests/conformance/test_correctness_grouped_match_workflows.py`
- Delete `tests/conformance/fixtures/grouped_match_workflows.json`
- Delete `tests/conformance/fixtures/named_group_workflows.json`
- Delete `tests/conformance/fixtures/named_group_replacement_workflows.json`
- Delete `tests/conformance/fixtures/named_backreference_workflows.json`
- Delete `tests/conformance/fixtures/numbered_backreference_workflows.json`
- Delete `tests/conformance/fixtures/grouped_segment_workflows.json`
- `reports/correctness/latest.json`

## Acceptance Criteria
- `python/rebar_harness/correctness.py` continues to load fixture manifests from both `.json` and `.py` paths through the existing shared validation path; do not add a second loader, generator step, or package-discovery layer for this batch.
- Each of the six targeted manifests becomes a one-manifest-per-file Python module exposing the same manifest ids, suite ids, defaults, case ids, case ordering, and case payloads that the deleted JSON files previously supplied, and no duplicate JSON copy of those six manifests remains in the tree.
- The converted manifests preserve the current checkout ids and case counts: `grouped-match-workflows` with `6` cases, `named-group-workflows` with `3`, `named-group-replacement-workflows` with `4`, `named-backreference-workflows` with `3`, `numbered-backreference-workflows` with `3`, and `grouped-segment-workflows` with `6`.
- `DEFAULT_FIXTURE_PATHS` points at the six new `.py` files while preserving their existing ordering between `literal_flag_workflows.json` and `nested_group_workflows.json`, so the combined scorecard helpers and fixture inventory keep deriving this slice from one shared path registry instead of another family-specific branch.
- `tests/conformance/test_correctness_grouped_match_workflows.py` points `GROUPED_MATCH_FIXTURES_PATH` at the new Python manifest while leaving the earlier prerequisite fixture-path constants intact, and the test still exercises the same nine-manifest slice and `86`-case grouped-match scorecard contract.
- The regenerated `reports/correctness/latest.json` preserves the existing manifest ordering, manifest ids, suite ids, case counts, aggregate totals, and representative coverage for the targeted manifests except for the fixture path extensions changing from `.json` to `.py`.
- The existing verification surface still passes with the Python-backed fixtures, including `tests.conformance.test_combined_correctness_scorecards`, `tests.conformance.test_correctness_grouped_match_workflows`, `tests.conformance.test_correctness_fixture_inventory_contract`, and `tests.conformance.test_python_fixture_manifest_contract`.
- The git-tracked JSON blob count decreases by exactly `6` relative to the live baseline when the task starts; in the current checkout that means `git ls-files '*.json' | wc -l` moves from `38` to `32`.

## Constraints
- Keep the scope to the six correctness manifests listed above; do not convert the early parser/module-surface fixtures, the nested-group trio, the quantified-group or conditional fixtures, benchmark workloads, or report/config JSON in the same run.
- Do not change Rust code, `python/rebar` runtime behavior, or the correctness report schema.
- Prefer simple Python `MANIFEST` modules and the existing shared validation path over generators, codegen, or another fixture DSL.

## Notes
- `.rebar/runtime/dashboard.md` still reports `tracked_json_blob_count: 103` and `tracked_json_blob_delta: 0`, but the live tracked baseline in this clean checkout is `38`; verify the reduction with `git ls-files '*.json' | wc -l` rather than relying on the stale runtime snapshot.
- This is the remaining contiguous early-workflow JSON block inside `python/rebar_harness/correctness.py::DEFAULT_FIXTURE_PATHS` between `literal_flag_workflows.json` and `nested_group_workflows.json`, so it burns down another six tracked JSON fixtures without mixing in the earlier parser/module-surface scaffolds or the later nested-group trio.
- `tests/conformance/test_correctness_grouped_match_workflows.py` is the only direct fixture-path test in this batch; the other targeted manifests are already covered through the shared combined scorecard and fixture-contract suites, so avoid inventing new one-off path tests unless a real assumption appears during execution.

## Completion Notes
- Repointed the six targeted `DEFAULT_FIXTURE_PATHS` entries in `python/rebar_harness/correctness.py` from `.json` to `.py` and updated `tests/conformance/test_correctness_grouped_match_workflows.py` so `GROUPED_MATCH_FIXTURES_PATH` now targets the Python-backed grouped-match manifest while the preceding eight fixture constants stay unchanged.
- Replaced `grouped_match_workflows.json`, `named_group_workflows.json`, `named_group_replacement_workflows.json`, `named_backreference_workflows.json`, `numbered_backreference_workflows.json`, and `grouped_segment_workflows.json` with one-manifest-per-file Python `MANIFEST` modules carrying the same manifest ids, suite ids, defaults, case ids, case ordering, and case payloads, then deleted the JSON originals.
- Regenerated `reports/correctness/latest.json`; the targeted fixture paths now resolve to `.py`, the converted manifest case counts remain `6`, `3`, `4`, `3`, `3`, and `6`, the grouped-match nine-manifest slice remains `86` cases, and the combined report remains `779` executed / `779` passed / `0` failed / `0` unimplemented.
- Verified with `python3 -m unittest tests.conformance.test_combined_correctness_scorecards tests.conformance.test_correctness_grouped_match_workflows tests.conformance.test_correctness_fixture_inventory_contract tests.conformance.test_python_fixture_manifest_contract` and `PYTHONPATH=python python3 -m rebar_harness.correctness --report reports/correctness/latest.json`.
- `python3 -m pytest ...` was not available because `pytest` is not installed in this checkout. In the working tree, `git ls-files '*.json' | wc -l` still reports deleted tracked files until the harness commit lands, so the live six-file reduction was verified with `rg --files -g '*.json' | wc -l` as `38 -> 32` and `git ls-files --deleted '*.json' | wc -l` as `6`.
