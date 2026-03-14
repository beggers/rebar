# RBR-0281: Replace the open-ended quantified-group correctness JSON fixtures with Python modules

Status: ready
Owner: architecture-implementation
Created: 2026-03-14

## Goal
- Reduce tracked JSON and simplify the correctness harness input path by replacing the isolated open-ended quantified-group correctness manifests with ordinary Python fixture modules while preserving the existing scorecard surface.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/open_ended_quantified_group_alternation_workflows.py`
- `tests/conformance/fixtures/nested_open_ended_quantified_group_alternation_workflows.py`
- `tests/conformance/fixtures/broader_range_open_ended_quantified_group_alternation_workflows.py`
- `tests/conformance/fixtures/open_ended_quantified_group_alternation_conditional_workflows.py`
- `tests/conformance/fixtures/broader_range_open_ended_quantified_group_alternation_conditional_workflows.py`
- `tests/conformance/fixtures/open_ended_quantified_group_alternation_backtracking_heavy_workflows.py`
- `tests/conformance/fixtures/broader_range_open_ended_quantified_group_alternation_backtracking_heavy_workflows.py`
- Delete `tests/conformance/fixtures/open_ended_quantified_group_alternation_workflows.json`
- Delete `tests/conformance/fixtures/nested_open_ended_quantified_group_alternation_workflows.json`
- Delete `tests/conformance/fixtures/broader_range_open_ended_quantified_group_alternation_workflows.json`
- Delete `tests/conformance/fixtures/open_ended_quantified_group_alternation_conditional_workflows.json`
- Delete `tests/conformance/fixtures/broader_range_open_ended_quantified_group_alternation_conditional_workflows.json`
- Delete `tests/conformance/fixtures/open_ended_quantified_group_alternation_backtracking_heavy_workflows.json`
- Delete `tests/conformance/fixtures/broader_range_open_ended_quantified_group_alternation_backtracking_heavy_workflows.json`
- `tests/conformance/correctness_expectations.py`
- `tests/conformance/test_open_ended_quantified_group_scorecards.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- `python/rebar_harness/correctness.py` loads fixture manifests from both `.json` and `.py` paths through one validation path, so the existing JSON-backed manifests outside this task keep working unchanged while the targeted open-ended family moves to Python.
- Each of the seven targeted open-ended quantified-group manifests becomes a one-manifest-per-file Python module exposing the same manifest id, suite id, case ids, defaults, and case payloads that the deleted JSON file previously supplied; no duplicate JSON copy of those seven manifests remains in the tree.
- `DEFAULT_FIXTURE_PATHS` points at the seven new `.py` fixture files, and `tests/conformance/correctness_expectations.py` continues to derive its manifest inventory from `DEFAULT_FIXTURE_PATHS` plus `load_fixture_manifest()` without needing a second inventory code path for this family.
- The consolidated open-ended scorecard suite and the combined correctness scorecard suite still pass with the Python-backed fixtures, and the regenerated `reports/correctness/latest.json` preserves the existing open-ended manifest ordering, manifest ids, suite ids, case counts, and aggregate totals except for the fixture path extensions changing from `.json` to `.py`.
- The tracked JSON blob count decreases by exactly 7 relative to the pre-task baseline because the seven deleted JSON fixtures are replaced by Python modules instead of new tracked JSON.

## Constraints
- Keep the scope to the seven open-ended quantified-group correctness manifests listed above; do not convert wider-ranged-repeat, quantified-alternation, conditional, or benchmark manifests in the same run.
- Do not change Rust code, `python/rebar` runtime behavior, or the correctness report schema.
- Prefer simple Python `MANIFEST` modules and shared validation over generators, codegen, or another fixture DSL.

## Notes
- `.rebar/runtime/dashboard.md` currently reports `tracked_json_blob_count: 129` and `tracked_json_blob_delta: 0`, so this task needs to make JSON-count reduction its primary result rather than a secondary cleanup.
- `RBR-0279` already consolidated this family’s scorecard assertions into `tests/conformance/test_open_ended_quantified_group_scorecards.py`, which keeps the verification surface stable while the fixture representation changes underneath it.
- Keep the Python fixtures path-based rather than package-discovery based. A path loader keeps `--fixtures` behavior intact and avoids turning this into a broader harness rewrite.
