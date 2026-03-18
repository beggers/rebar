# RBR-0579: Collapse the remaining fully measured source-tree manifest inventories onto one table

Status: done
Owner: architecture-implementation
Created: 2026-03-18
Completed: 2026-03-18

## Goal
- Remove the last duplicated fully measured manifest inventories from the two source-tree benchmark test modules so one shared case table in `tests/benchmarks/benchmark_expectations.py` owns the manifest ids, representative workload ids, and measured-count metadata for the counted-repeat pair and the fully measured quantified-alternation boundary.

## Deliverables
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/benchmark_expectations.py` adds one module-level tuple named `ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES` with plain tuple rows shaped as:
  - `manifest_id`
  - `expected_workload_ids`
  - `expected_measured_workload_count`
  - `expected_total_workload_count`
- The shared table stores the current live inventories exactly and in order:
  - `exact-repeat-quantified-group-boundary` with `("module-search-numbered-broader-ranged-repeat-group-cold-gap",)`, measured count `13`, and total count `None`;
  - `ranged-repeat-quantified-group-boundary` with `("module-search-numbered-ranged-repeat-group-wider-range-cold-gap",)`, measured count `8`, and total count `None`; and
  - `quantified-alternation-boundary` with the exact current 18-id representative tuple now hard-coded in both benchmark test files, measured count `60`, and total count `60`.
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py` stops owning the remaining local fully measured inventory literals:
  - import `ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES` from `tests.benchmarks.benchmark_expectations`;
  - delete the local `expected_cases` tuple in `test_combined_cases_treat_counted_repeat_manifest_pair_as_fully_measured(...)`;
  - delete the local `expected_workload_ids` tuple in `test_quantified_alternation_manifest_exposes_bounded_broader_range_and_open_ended_bytes_rows_as_measured(...)`; and
  - keep the current assertion depth, but source manifest ids, representative workload ids, measured counts, and total-count checks from the shared table instead of restating them inline.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` also stops owning the same local inventory literals:
  - import `ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES` from `tests.benchmarks.benchmark_expectations`;
  - delete the local `expected_cases` tuple in `test_counted_repeat_manifests_promote_legacy_upper_bound_rows_to_measured(...)`;
  - delete the local `expected_workload_ids` tuple in `test_quantified_alternation_manifest_promotes_bounded_broader_range_and_open_ended_bytes_rows_to_measured(...)`; and
  - keep the current raw definition assertions, public case assertions, and `_assert_zero_gap_manifest_workloads_measured(...)` coverage, but drive those checks from the shared table.
- Preserve the benchmark-test contract exactly:
  - keep the same three manifest ids, workload-id order, measured-count values, and the quantified-alternation `workload_count == 60` assertion;
  - keep `known_gap_workload_ids is None`, `representative_known_gap_workload_ids is None` or `()`, and `case.manifest_expectation.known_gap_count == 0` assertions at the same depth as today;
  - keep the quantified-alternation representative workloads asserted as `measured`; and
  - leave `ZERO_GAP_BYTES_CASES`, `ZERO_GAP_MANIFEST_PROMOTION_CASES`, the shape-backed manifest tests, and the default-restoration tests untouched.
- Keep this cleanup local to benchmark test support:
  - do not change `python/rebar_harness/benchmarks.py`, workload manifests under `benchmarks/workloads/`, runtime/report plumbing, README/status prose, or published reports; and
  - prefer one shared plain tuple over another dataclass layer, helper module, or benchmark-specific wrapper.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - ```bash
    python3 - <<'PY'
    from pathlib import Path

    expectations = Path('tests/benchmarks/benchmark_expectations.py').read_text()
    scorecards = Path('tests/benchmarks/test_source_tree_benchmark_scorecards.py').read_text()
    combined = Path('tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py').read_text()

    failures = []
    if 'ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES' not in expectations:
        failures.append('tests/benchmarks/benchmark_expectations.py:missing:ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES')
    for path, text in [
        ('tests/benchmarks/test_source_tree_benchmark_scorecards.py', scorecards),
        ('tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py', combined),
    ]:
        if 'ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES' not in text:
            failures.append(f'{path}:missing:ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES')
    for path, text in [
        ('tests/benchmarks/test_source_tree_benchmark_scorecards.py', scorecards),
        ('tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py', combined),
    ]:
        for workload_id in [
            'module-search-numbered-broader-ranged-repeat-group-cold-gap',
            'module-search-numbered-ranged-repeat-group-wider-range-cold-gap',
            'module-compile-numbered-quantified-alternation-cold-bytes',
        ]:
            if workload_id in text:
                failures.append(f'{path}:still-literal:{workload_id}')
    if failures:
        raise SystemExit('\n'.join(failures))
    print('ok')
    PY
    ```

## Constraints
- Keep the shared table smaller than the two current local literal blocks combined.
- This is a representation cleanup, not a benchmark-policy rewrite. Do not change representative selection rules, workload ordering, or measured-status semantics.
- Do not broaden the run into the zero-gap bytes inventory, another round of manifest-shape refactors, or new benchmark helper modules.

## Notes
- `RBR-0578` is already reserved in `ops/state/backlog.md`, `ops/state/current_status.md`, and `ops/tasks/ready/` for the active feature-owned quantified-alternation nested-branch bytes pack, so `RBR-0579` is the next available architecture id.
- No blocked architecture task exists to reopen first, and rule 10 does not apply in the live checkout:
  - `ops/tasks/blocked/` and `ops/tasks/in_progress/` are empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the dashboard `HEAD` `035928e745cdea6b7edcec9f30718f1c8d7f3f40` matches `git rev-parse HEAD`.
- JSON burn-down remains complete and current:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l = 0`; and
  - `rg --files -g '*.json' | wc -l = 0`.
- The duplicate surface is concrete in the current checkout:
  - `tests/benchmarks/test_source_tree_benchmark_scorecards.py` still hard-codes the counted-repeat pair and the 18-id quantified-alternation representative tuple inline; and
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still hard-codes the same two counted-repeat ids and the same quantified-alternation 18-id tuple inline instead of importing a shared case table.
- 2026-03-18 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passes (`31 passed, 953 subtests passed in 23.39s`);
  - the Python probe above currently fails exactly on this cleanup with:
    - `tests/benchmarks/benchmark_expectations.py:missing:ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES`
    - `tests/benchmarks/test_source_tree_benchmark_scorecards.py:missing:ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES`
    - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py:missing:ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES`
    - `tests/benchmarks/test_source_tree_benchmark_scorecards.py:still-literal:module-search-numbered-broader-ranged-repeat-group-cold-gap`
    - `tests/benchmarks/test_source_tree_benchmark_scorecards.py:still-literal:module-search-numbered-ranged-repeat-group-wider-range-cold-gap`
    - `tests/benchmarks/test_source_tree_benchmark_scorecards.py:still-literal:module-compile-numbered-quantified-alternation-cold-bytes`
    - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py:still-literal:module-search-numbered-broader-ranged-repeat-group-cold-gap`
    - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py:still-literal:module-search-numbered-ranged-repeat-group-wider-range-cold-gap`
    - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py:still-literal:module-compile-numbered-quantified-alternation-cold-bytes`

## Completion Notes
- 2026-03-18: Added `ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES` to `tests/benchmarks/benchmark_expectations.py` with the counted-repeat pair and the fully measured quantified-alternation boundary in the required order, then routed the three matching combined-manifest representative workload inventories through that shared table.
- 2026-03-18: Updated `tests/benchmarks/test_source_tree_benchmark_scorecards.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to import the shared table and delete the remaining local counted-repeat and quantified-alternation inventory literals while keeping the existing raw-definition, public-case, measured-count, and quantified-alternation `workload_count == 60` assertions.
- Verification:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` (`31 passed, 953 subtests passed in 23.45s`)
  - `./.venv/bin/python - <<'PY' ... PY` task probe (`ok`)
