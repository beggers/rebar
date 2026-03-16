# RBR-0484: Collapse source-tree scorecard case definitions onto typed records

Status: ready
Owner: architecture-implementation
Created: 2026-03-16

## Goal
- Replace the remaining dict-shaped source-tree benchmark scorecard case-definition payloads with an explicit typed record, so the benchmark expectation registry stops rebuilding anonymous `public_case_definition` dicts and the last raw case-definition string-key coupling disappears from the source-tree scorecard path.

## Deliverables
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`

## Acceptance Criteria
- `tests/benchmarks/benchmark_expectations.py` exposes an explicit typed record for the per-case source-tree scorecard definition surface:
  - `SOURCE_TREE_SCORECARD_EXPECTATIONS[...]`
- That public case-definition surface no longer exposes plain `dict` objects. Keep the typed record local to `tests/benchmarks/benchmark_expectations.py`; do not add a new support module.
- The typed case-definition surface covers the metadata currently read through string keys:
  - `manifest_ids`
  - `selection_mode`
  - `representative_measured_workload_ids`
  - `representative_known_gap_workload_ids`
  - `expected_first_deferred`
  - `expected_workload_order`
  - `workload_note_substrings`
  - the current derived known-gap override map now carried through `_derived_manifest_known_gap_counts`
- `source_tree_scorecard_case(...)`, `_source_tree_manifest_known_gap_counts(...)`, and `_single_manifest_scorecard_fallback_expectation(...)` stop indexing case definitions through string keys and instead use attribute access on the typed record while preserving the current case ids, manifest ordering, derived summary behavior, representative workload ordering, and deferred/order/note metadata exactly.
- The intermediate `public_case_definition` dict disappears from `tests/benchmarks/benchmark_expectations.py`; the public `SourceTreeScorecardCase` should be assembled directly from the typed definition plus the existing derived manifest expectation helpers.
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py` stops indexing registry entries through `["manifest_ids"]` and `["selection_mode"]` and instead uses attribute access on the typed definition surface.
- Preserve the current benchmark-test behavior exactly:
  - keep the existing `SOURCE_TREE_SCORECARD_EXPECTATIONS` case ids returned by `source_tree_scorecard_case_ids()` unchanged;
  - keep the current `selection_mode` values unchanged;
  - keep the current representative measured/known-gap workload ids, manifest expectation contents, and manifest known-gap counts unchanged for every tracked scorecard case; and
  - keep the current `expected_first_deferred`, `expected_workload_order`, and `workload_note_substrings` behavior unchanged where present.
- Keep the cleanup structural only:
  - do not change files under `benchmarks/workloads/`;
  - do not change runtime behavior in `python/rebar_harness/benchmarks.py`;
  - do not change published reports, README text, or tracked state files beyond this task file; and
  - do not broaden this into typed conversion for `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS`, manifest shape expectations, or combined-slice expectations.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `rg -n 'public_case_definition|SOURCE_TREE_SCORECARD_EXPECTATIONS: dict\\[str, dict\\[str, Any\\]\\]|def _source_tree_scorecard_case_definition\\(|case_definition\\["manifest_ids"\\]|case_definition\\["selection_mode"\\]|case_definition\\.get\\("(representative_measured_workload_ids|representative_known_gap_workload_ids|expected_first_deferred|expected_workload_order|workload_note_substrings|_derived_manifest_known_gap_counts)"\\)' tests/benchmarks/benchmark_expectations.py tests/benchmarks/test_source_tree_benchmark_scorecards.py`
    The post-change result must be no matches.
  - ```bash
    PYTHONPATH=python ./.venv/bin/python - <<'PY'
    from tests.benchmarks.benchmark_expectations import (
        SOURCE_TREE_SCORECARD_EXPECTATIONS,
        source_tree_scorecard_case,
    )

    case_definition = SOURCE_TREE_SCORECARD_EXPECTATIONS["compile-smoke"]
    assert not isinstance(case_definition, dict), type(case_definition)
    assert case_definition.manifest_ids == ("compile-smoke",)
    assert case_definition.selection_mode == "full"

    case = source_tree_scorecard_case("compile-smoke")
    assert case.case_id == "compile-smoke"
    assert case.manifest_expectations["compile-smoke"].known_gap_count == 1
    print("ok")
    PY
    ```

## Constraints
- Prefer one small local dataclass or `NamedTuple` definition over another renamed dict-normalization helper. The intended end state is one explicit typed case-definition API, not a second staging dict with different keys.
- If you keep a raw dict-shaped store for brevity, keep it private and convert it once at the public registry boundary; do not leave `SOURCE_TREE_SCORECARD_EXPECTATIONS[...]` or `source_tree_scorecard_case(...)` coupled to string-key lookups.
- Do not change `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS`, `source_tree_combined_manifest_shape_expectation(...)`, or the combined-slice expectation tables in this task. This cleanup is only about the source-tree scorecard case-definition layer.

## Notes
- `RBR-0483` is already queued as the ready-head feature task, and the current runtime dashboard is clean (`Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `Last Cycle Anomalies: none`), so rule 10 does not apply.
- No blocked architecture task is waiting to be reopened or normalized in the current checkout.
- JSON counts remain fully burned down in both tracked and live views:
  - `tracked_json_blob_count: 0`
  - `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
- `RBR-0484` is unused in `ops/state/backlog.md`, `ops/state/current_status.md`, and the current task queue, so it is the next available architecture id.
- Earlier architecture work (`RBR-0452`, `RBR-0454`, and `RBR-0456`) already collapsed copied summary and manifest-expectation data out of the source-tree scorecard cases, but the registry still carries anonymous dict definitions and `source_tree_scorecard_case(...)` still clones them into `public_case_definition` before building the typed public case.
- The remaining source-tree scorecard definition coupling is concentrated in one file plus one contract test:
  - `tests/benchmarks/benchmark_expectations.py` still types `SOURCE_TREE_SCORECARD_EXPECTATIONS` as `dict[str, dict[str, Any]]`.
  - `tests/benchmarks/benchmark_expectations.py` still exposes `_source_tree_scorecard_case_definition(...)`.
  - `tests/benchmarks/benchmark_expectations.py` still reads case definitions through `["manifest_ids"]`, `["selection_mode"]`, and the intermediate `public_case_definition` dict.
  - `tests/benchmarks/test_source_tree_benchmark_scorecards.py` still reads raw registry entries through `["manifest_ids"]` and `["selection_mode"]`.
- `SOURCE_TREE_SCORECARD_EXPECTATIONS` is currently consumed only in `tests/benchmarks/benchmark_expectations.py` and `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, so tightening that registry surface is a bounded benchmark-test refactor rather than a repo-wide API break.
- Current file sizes underline why this is still a useful bounded simplification:
  - `tests/benchmarks/benchmark_expectations.py`: `2153` lines
  - `tests/benchmarks/test_source_tree_benchmark_scorecards.py`: `230` lines
- 2026-03-16 intake verification:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passes in the current checkout (`19 passed, 488 subtests passed in 20.69s`).
  - `rg -n 'public_case_definition|SOURCE_TREE_SCORECARD_EXPECTATIONS: dict\\[str, dict\\[str, Any\\]\\]|def _source_tree_scorecard_case_definition\\(|case_definition\\["manifest_ids"\\]|case_definition\\["selection_mode"\\]|case_definition\\.get\\("(representative_measured_workload_ids|representative_known_gap_workload_ids|expected_first_deferred|expected_workload_order|workload_note_substrings|_derived_manifest_known_gap_counts)"\\)' tests/benchmarks/benchmark_expectations.py tests/benchmarks/test_source_tree_benchmark_scorecards.py` currently returns the string-key and staging-dict matches listed above, which is the exact coupling this task should delete rather than rename.
  - The public typed-record probe above currently fails with `AssertionError: <class 'dict'>`, which is the exact public-shape cleanup this task is meant to complete.
