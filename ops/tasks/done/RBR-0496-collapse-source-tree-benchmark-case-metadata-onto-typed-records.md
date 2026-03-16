# RBR-0496: Collapse source-tree benchmark case metadata onto typed records

Status: done
Owner: architecture-implementation
Created: 2026-03-16

## Goal
- Delete the remaining ad hoc dict metadata and dead note-plumbing on the source-tree benchmark scorecard case path so `tests/benchmarks/benchmark_expectations.py` stays on one typed representation instead of mixing typed dataclasses with `dict[str, ...]` payloads and `**kwargs` round-trips.

## Deliverables
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`

## Acceptance Criteria
- `tests/benchmarks/benchmark_expectations.py` stops using the remaining dict-shaped case metadata on the source-tree scorecard path:
  - `SourceTreeBenchmarkCommonCase.init_kwargs()` disappears; and
  - `SourceTreeScorecardCase.from_common_case(...)` plus `SourceTreeCombinedCase.from_common_case(...)` stop splatting `**common_case.init_kwargs()` and instead copy typed fields without a `dict[str, Any]` bridge.
- `_SourceTreeScorecardDefinition.expected_first_deferred` is no longer typed or stored as `dict[str, str] | None`:
  - the compile-only source-tree scorecard cases keep the same deferred `area` and `follow_up` values as today;
  - the stored representation becomes a typed local record, not a dict; and
  - `tests/benchmarks/test_source_tree_benchmark_scorecards.py` reads typed attributes instead of subscripting `expected_first_deferred["area"]` / `["follow_up"]`.
- `_SourceTreeScorecardDefinition._derived_manifest_known_gap_counts` no longer stores raw `dict[str, int] | None` payloads:
  - the compile-smoke known-gap override remains `1` for `compile-smoke`;
  - `_source_tree_manifest_known_gap_counts(...)` still preserves the current override behavior; and
  - the override representation becomes a typed local record or tuple of typed local records rather than an ad hoc dict.
- The unused `workload_note_substrings` plumbing is deleted from the source-tree scorecard case path:
  - remove `workload_note_substrings` from the source-tree case dataclasses and builders in `tests/benchmarks/benchmark_expectations.py`;
  - remove the `case.workload_note_substrings or {}` fallback path from `tests/benchmarks/test_source_tree_benchmark_scorecards.py`; and
  - preserve current behavior exactly, because no current source-tree scorecard case definition populates workload-note substring expectations.
- Keep the public source-tree benchmark expectation behavior unchanged for the green benchmark test slice in the current checkout:
  - keep every source-tree scorecard case id, manifest id order, selection mode, representative measured workload id, representative known-gap workload id, and deferred ordering unchanged;
  - keep compile-smoke reporting `known_gap_count == 1`; and
  - keep `source_tree_scorecard_case(...)` and `run_source_tree_benchmark_scorecard(...)` producing the same current summaries for the verification slice below.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py tests/benchmarks/test_python_benchmark_manifest_contract.py`
  - `rg -n 'def init_kwargs\\(|expected_first_deferred: dict\\[str, str\\] \\| None|_derived_manifest_known_gap_counts: dict\\[str, int\\] \\| None|workload_note_substrings: dict\\[str, str\\] \\| None|expected_first_deferred\\["|workload_note_substrings or \\{\\}|case_definition\\._derived_manifest_known_gap_counts' tests/benchmarks/benchmark_expectations.py tests/benchmarks/test_source_tree_benchmark_scorecards.py`
    The post-change result must be no matches.
  - ```bash
    PYTHONPATH=python ./.venv/bin/python - <<'PY'
    from tests.benchmarks.benchmark_expectations import (
        SourceTreeBenchmarkCommonCase,
        source_tree_scorecard_case,
    )

    assert not hasattr(SourceTreeBenchmarkCommonCase, "init_kwargs")

    case = source_tree_scorecard_case("compile-smoke")
    assert case.manifest_expectations["compile-smoke"].known_gap_count == 1
    assert case.expected_first_deferred is not None
    assert not isinstance(case.expected_first_deferred, dict)
    assert case.expected_first_deferred.area == "module-boundary"
    assert case.expected_first_deferred.follow_up == "RBR-0015"
    assert not hasattr(case, "workload_note_substrings")
    print("ok")
    PY
    ```

## Constraints
- Keep the cleanup structural only. Do not change files under `benchmarks/workloads/`, do not change `python/rebar_harness/benchmarks.py`, do not change `reports/benchmarks/latest.py`, and do not change tracked state files beyond this task file.
- Do not broaden this cleanup into the currently queued feature frontier:
  - leave `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS` and `SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS` behavior unchanged;
  - do not change `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`; and
  - do not fix or reclassify the adjacent grouped-alternation wrapper-template benchmark drift that is already blocked behind `RBR-0493` and `RBR-0495`.
- Prefer deleting dead metadata plumbing over renaming it. The intended end state is one typed source-tree scorecard case surface, not a second helper layer that rebuilds equivalent records from raw dicts.

## Notes
- Rule 10 does not apply in the current checkout: `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, and `Last Cycle Anomalies: none`, so the current bottleneck is not a stalled refresh/commit path.
- No blocked architecture task exists to reopen or normalize first. The only blocked task is feature-owned `ops/tasks/blocked/RBR-0493-republish-nested-grouped-alternation-replacement-benchmark-pair.md`, and its blocker is still the separate grouped-alternation wrapper-template frontier already queued as `RBR-0495`.
- JSON counts remain fully burned down in both tracked and live views:
  - `tracked_json_blob_count: 0`
  - `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
- `RBR-0495` is the only reserved future id in `ops/state/backlog.md` and `ops/state/current_status.md`, so `RBR-0496` is the next available architecture id.
- The remaining dynamic metadata surface is narrow and localized:
  - the `rg -n ...` probe above returns `12` matches in the current checkout, all in `tests/benchmarks/benchmark_expectations.py` and `tests/benchmarks/test_source_tree_benchmark_scorecards.py`;
  - the current compile-smoke case still exposes `expected_first_deferred` as `{'area': 'module-boundary', 'follow_up': 'RBR-0015'}`; and
  - `workload_note_substrings` is still present on the case object even though no source-tree scorecard definition populates it.
- 2026-03-16 architecture probe:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py tests/benchmarks/test_python_benchmark_manifest_contract.py` passes in the current checkout (`20 passed, 798 subtests passed in 1.50s`).
  - The `rg -n ...` command above currently returns the dead/dynamic metadata matches that this task should delete rather than wrap.
  - The typed-metadata probe above currently fails at `assert not hasattr(SourceTreeBenchmarkCommonCase, "init_kwargs")`, which is the exact constructor-plumbing cleanup this task should complete.

## Completion Note
- 2026-03-16: Replaced the remaining source-tree scorecard dict metadata with typed records, removed the `init_kwargs()` and `workload_note_substrings` plumbing, preserved the compile-smoke known-gap override through typed override records, and updated the scorecard test to read deferred metadata via attributes. Verified with the required pytest slice (`20 passed, 798 subtests passed`), the required `rg -n ...` probe (no matches), and the typed inline Python probe (`ok`).
