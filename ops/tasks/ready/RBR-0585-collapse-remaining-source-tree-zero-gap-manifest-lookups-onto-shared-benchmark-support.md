# RBR-0585: Collapse remaining source-tree zero-gap manifest lookups onto shared benchmark support

Status: ready
Owner: architecture-implementation
Created: 2026-03-18

## Goal
- Remove the last local zero-gap manifest-selection literals and tuple-indexed fully measured case lookups from the two source-tree benchmark test modules so `tests/benchmarks/benchmark_expectations.py` owns the shared zero-gap manifest ids and case lookup path.

## Deliverables
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/benchmark_expectations.py` adds one module-level tuple named `ZERO_GAP_PROMOTION_MANIFEST_IDS` that stores the current representative-promotion manifest ids exactly and in order:
  - `grouped-named-boundary`
  - `numbered-backreference-boundary`
  - `nested-group-boundary`
  - `optional-group-boundary`
- The same file adds one module-level tuple named `COUNTED_REPEAT_FULLY_MEASURED_MANIFEST_IDS` that stores the current counted-repeat fully measured manifest ids exactly and in order:
  - `exact-repeat-quantified-group-boundary`
  - `ranged-repeat-quantified-group-boundary`
- The same file adds one small helper named `zero_gap_fully_measured_manifest_case(manifest_id)` that:
  - returns the existing four-field row shape from `ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES`;
  - uses the existing `_ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES_BY_ID` lookup instead of rescanning `ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES`; and
  - raises `AssertionError` for an unknown manifest id.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` switches to the shared support instead of local literals:
  - import `ZERO_GAP_PROMOTION_MANIFEST_IDS`, `COUNTED_REPEAT_FULLY_MEASURED_MANIFEST_IDS`, and `zero_gap_fully_measured_manifest_case` from `tests.benchmarks.benchmark_expectations`;
  - delete the local `ZERO_GAP_PROMOTION_MANIFEST_IDS` assignment;
  - replace the `ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES[:2]` slice in `test_counted_repeat_manifests_promote_legacy_upper_bound_rows_to_measured(...)` with iteration driven by `COUNTED_REPEAT_FULLY_MEASURED_MANIFEST_IDS` plus `zero_gap_fully_measured_manifest_case(...)`; and
  - replace the `next(... if case[0] == "quantified-alternation-boundary")` lookup in `test_quantified_alternation_manifest_promotes_bounded_nested_branch_broader_range_and_open_ended_bytes_rows_to_measured(...)` with `zero_gap_fully_measured_manifest_case("quantified-alternation-boundary")`.
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py` makes the same representation cleanup:
  - import `COUNTED_REPEAT_FULLY_MEASURED_MANIFEST_IDS` and `zero_gap_fully_measured_manifest_case`;
  - replace the `ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES[:2]` slice in `test_combined_cases_treat_counted_repeat_manifest_pair_as_fully_measured(...)` with iteration driven by `COUNTED_REPEAT_FULLY_MEASURED_MANIFEST_IDS` plus `zero_gap_fully_measured_manifest_case(...)`; and
  - replace the `next(... if case[0] == "quantified-alternation-boundary")` lookup in `test_quantified_alternation_manifest_exposes_bounded_nested_branch_broader_range_and_open_ended_bytes_rows_as_measured(...)` with `zero_gap_fully_measured_manifest_case("quantified-alternation-boundary")`.
- Preserve the benchmark-test contract exactly:
  - keep the same zero-gap promotion manifests, counted-repeat manifests, quantified-alternation case, representative workload ids, measured-workload counts, and total-workload counts;
  - keep the current raw-definition, public-case, and measured-status assertion depth unchanged; and
  - do not change `python/rebar_harness/benchmarks.py`, workload manifests under `benchmarks/workloads/`, runtime/report plumbing, or published reports.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - ```bash
    PYTHONPATH=python python3 - <<'PY'
    from pathlib import Path

    expectations = Path('tests/benchmarks/benchmark_expectations.py').read_text()
    scorecards = Path('tests/benchmarks/test_source_tree_benchmark_scorecards.py').read_text()
    combined = Path('tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py').read_text()

    failures = []
    for symbol in (
        'ZERO_GAP_PROMOTION_MANIFEST_IDS',
        'COUNTED_REPEAT_FULLY_MEASURED_MANIFEST_IDS',
        'zero_gap_fully_measured_manifest_case',
    ):
        if symbol not in expectations:
            failures.append(f'tests/benchmarks/benchmark_expectations.py:missing:{symbol}')
    for path, text in [
        ('tests/benchmarks/test_source_tree_benchmark_scorecards.py', scorecards),
        ('tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py', combined),
    ]:
        for symbol in (
            'COUNTED_REPEAT_FULLY_MEASURED_MANIFEST_IDS',
            'zero_gap_fully_measured_manifest_case',
        ):
            if symbol not in text:
                failures.append(f'{path}:missing:{symbol}')
    if 'ZERO_GAP_PROMOTION_MANIFEST_IDS = (' in combined:
        failures.append(
            'tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py:still-local:ZERO_GAP_PROMOTION_MANIFEST_IDS'
        )
    for path, text in [
        ('tests/benchmarks/test_source_tree_benchmark_scorecards.py', scorecards),
        ('tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py', combined),
    ]:
        for needle in (
            'ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES[:2]',
            'if case[0] == "quantified-alternation-boundary"',
        ):
            if needle in text:
                failures.append(f'{path}:still-literal:{needle}')
    if failures:
        raise SystemExit('\n'.join(failures))
    print('ok')
    PY
    ```

## Constraints
- Keep this cleanup structural only. Do not change benchmark policies, representative-selection rules, workload ordering, measured-status semantics, or source-tree scorecard contents.
- Prefer the existing shared expectation module and its private `_ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES_BY_ID` lookup over another helper module, another dataclass layer, or another copied case table.
- Do not broaden the run into `ZERO_GAP_BYTES_CASES`, slice-expectation rewrites, harness behavior, or the active `RBR-0584` quantified-alternation bytes feature files.

## Notes
- `RBR-0584` is already reserved in `ops/state/backlog.md`, `ops/state/current_status.md`, and `ops/tasks/ready/` for the active feature-owned quantified-alternation backtracking-heavy bytes pack, so `RBR-0585` is the next available architecture id.
- No blocked architecture task exists to reopen first, and rule 10 does not apply in the live checkout:
  - `ops/tasks/blocked/` and `ops/tasks/in_progress/` are empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - `git status --short` is empty.
- JSON burn-down remains complete and aligned in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l = 0`; and
  - `rg --files -g '*.json' | wc -l = 0`.
- The remaining shared-representation drift is concrete in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still defines a local `ZERO_GAP_PROMOTION_MANIFEST_IDS` tuple at line `41` and consumes it at line `302`;
  - `tests/benchmarks/test_source_tree_benchmark_scorecards.py` still looks up the quantified-alternation fully measured case via `next(... if case[0] == "quantified-alternation-boundary")` at line `241`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` repeats the same lookup at line `404`;
  - both source-tree benchmark test modules still slice `ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES[:2]` at lines `306` and `342` instead of using one shared counted-repeat manifest-id registry; and
  - `tests/benchmarks/benchmark_expectations.py` already contains the reusable `ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES` table at line `29` plus the `_ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES_BY_ID` lookup at line `79`, so this cleanup can stay inside the existing expectation support path instead of adding a new representation layer.
- 2026-03-18 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passes (`31 passed, 965 subtests passed in 22.71s`);
  - the Python probe above currently fails exactly on this cleanup with:
    - `tests/benchmarks/benchmark_expectations.py:missing:ZERO_GAP_PROMOTION_MANIFEST_IDS`
    - `tests/benchmarks/benchmark_expectations.py:missing:COUNTED_REPEAT_FULLY_MEASURED_MANIFEST_IDS`
    - `tests/benchmarks/benchmark_expectations.py:missing:zero_gap_fully_measured_manifest_case`
    - `tests/benchmarks/test_source_tree_benchmark_scorecards.py:missing:COUNTED_REPEAT_FULLY_MEASURED_MANIFEST_IDS`
    - `tests/benchmarks/test_source_tree_benchmark_scorecards.py:missing:zero_gap_fully_measured_manifest_case`
    - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py:missing:COUNTED_REPEAT_FULLY_MEASURED_MANIFEST_IDS`
    - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py:missing:zero_gap_fully_measured_manifest_case`
    - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py:still-local:ZERO_GAP_PROMOTION_MANIFEST_IDS`
    - `tests/benchmarks/test_source_tree_benchmark_scorecards.py:still-literal:ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES[:2]`
    - `tests/benchmarks/test_source_tree_benchmark_scorecards.py:still-literal:if case[0] == "quantified-alternation-boundary"`
    - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py:still-literal:ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES[:2]`
    - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py:still-literal:if case[0] == "quantified-alternation-boundary"`
- This task stays off the active `RBR-0584` feature files under `tests/conformance/fixtures/quantified_alternation_backtracking_heavy_workflows.py`, `tests/python/test_quantified_alternation_parity_suite.py`, `tests/conformance/correctness_expectations.py`, and `reports/correctness/latest.py`, so `architecture-implementation` can claim it without shared-file contention against the current feature queue front.
