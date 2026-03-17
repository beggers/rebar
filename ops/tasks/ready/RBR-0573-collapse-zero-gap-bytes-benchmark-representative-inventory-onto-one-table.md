# RBR-0573: Collapse the zero-gap bytes benchmark representative inventory onto one table

Status: ready
Owner: architecture-implementation
Created: 2026-03-17

## Goal
- Remove the duplicated 11-case zero-gap bytes representative inventory that now lives in both `tests/benchmarks/test_source_tree_benchmark_scorecards.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, so one canonical tuple in benchmark test support owns the shared workload ids and counts.

## Deliverables
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/benchmark_expectations.py` becomes the single source of truth for this shared zero-gap bytes inventory:
  - add one module-level tuple named `ZERO_GAP_BYTES_CASES`;
  - store the current 11 live zero-gap bytes slices as plain tuples containing `manifest_id`, `expected_workload_ids`, `expected_measured_workload_count`, and `expected_total_workload_count`; and
  - preserve every current workload id and count already asserted by `ZERO_GAP_REPRESENTATIVE_BYTES_CASES` and `ZERO_GAP_BYTES_PROMOTION_CASES`.
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py` stops owning a parallel local inventory:
  - delete the local `ZERO_GAP_REPRESENTATIVE_BYTES_CASES` constant;
  - import `ZERO_GAP_BYTES_CASES` from `tests.benchmarks.benchmark_expectations`;
  - keep `_assert_zero_gap_representative_workload_subset(...)` and `test_zero_gap_source_tree_manifests_keep_selected_bytes_representatives_publicly_measured(...)`; and
  - make the loop test project only `manifest_id` plus `expected_workload_ids` from the shared four-field tuples instead of redefining the 11-case list locally.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` also stops owning a parallel local inventory:
  - delete the local `ZERO_GAP_BYTES_PROMOTION_CASES` constant;
  - import `ZERO_GAP_BYTES_CASES` from `tests.benchmarks.benchmark_expectations`; and
  - keep `_assert_zero_gap_bytes_representative_subset(...)` and `test_zero_gap_bytes_manifest_promotions_keep_selected_rows_publicly_measured(...)`, but drive that loop directly from `ZERO_GAP_BYTES_CASES`.
- Preserve the current benchmark-test contract exactly:
  - keep the same 11 manifest/workload slices currently covered by the two loop tests;
  - keep the same `known_gap_count == 0` and empty representative-known-gap assertions in both helpers;
  - keep the same measured-workload and total-workload count assertions in the combined-boundary test; and
  - keep `test_quantified_alternation_manifest_exposes_broader_range_and_open_ended_bytes_rows_as_measured(...)` in `tests/benchmarks/test_source_tree_benchmark_scorecards.py` and `test_quantified_alternation_manifest_promotes_broader_range_and_open_ended_bytes_rows_to_measured(...)` in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` as dedicated special cases rather than folding them into the shared table.
- Keep this cleanup local to benchmark test support:
  - do not change `python/rebar_harness/benchmarks.py`, workload manifests under `benchmarks/workloads/`, runtime harness code, README/status files, or published reports; and
  - do not broaden the task into another representative-policy rewrite or a second helper module.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - ```bash
    python3 - <<'PY'
    import ast
    from pathlib import Path

    shared_path = Path('tests/benchmarks/benchmark_expectations.py')
    score_path = Path('tests/benchmarks/test_source_tree_benchmark_scorecards.py')
    combined_path = Path('tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py')

    failures = []

    shared_module = ast.parse(shared_path.read_text())
    shared_assignments = {
        target.id
        for node in shared_module.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    }
    if 'ZERO_GAP_BYTES_CASES' not in shared_assignments:
        failures.append(f'{shared_path}:missing:ZERO_GAP_BYTES_CASES')

    for path, local_name in [
        (score_path, 'ZERO_GAP_REPRESENTATIVE_BYTES_CASES'),
        (combined_path, 'ZERO_GAP_BYTES_PROMOTION_CASES'),
    ]:
        module = ast.parse(path.read_text())
        module_assignments = {
            target.id
            for node in module.body
            if isinstance(node, ast.Assign)
            for target in node.targets
            if isinstance(target, ast.Name)
        }
        import_from_shared = any(
            isinstance(node, ast.ImportFrom)
            and node.module == 'tests.benchmarks.benchmark_expectations'
            and any(alias.name == 'ZERO_GAP_BYTES_CASES' for alias in node.names)
            for node in module.body
        )
        if local_name in module_assignments:
            failures.append(f'{path}:still-defines:{local_name}')
        if not import_from_shared:
            failures.append(f'{path}:missing-import:ZERO_GAP_BYTES_CASES')

    if failures:
        raise SystemExit('\n'.join(failures))

    print('ok')
    PY
    ```

## Constraints
- Prefer one shared plain tuple over another dataclass layer, helper module, or benchmark-specific wrapper. This task is about deleting duplicated inventory, not replacing it with more machinery.
- Keep the shared tuple smaller than the two current local constants combined.
- Preserve the current workload ids, manifest ids, and count values exactly.

## Notes
- `RBR-0572` is the only live ready task and is feature work; `ops/state/backlog.md`, `ops/state/current_status.md`, and `ops/tasks/` do not reserve `RBR-0573`, so `RBR-0573` is the next available architecture id.
- No blocked architecture task exists to reopen first, and rule 10 does not apply in the live checkout:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the dashboard HEAD `03a934acbfed7c8634718c151053c55430309a86` matches `git rev-parse HEAD`.
- JSON burn-down remains complete and current:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l = 0`; and
  - `rg --files -g '*.json' | wc -l = 0`.
- The duplicate surface is concrete in the current checkout:
  - `tests/benchmarks/test_source_tree_benchmark_scorecards.py` is `613` lines and still defines `ZERO_GAP_REPRESENTATIVE_BYTES_CASES`;
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is `1057` lines and still defines `ZERO_GAP_BYTES_PROMOTION_CASES`; and
  - a live import probe on 2026-03-17 shows both constants cover the same 11-case set (`set_match=True`), split across `6` wider-ranged-repeat entries and `5` open-ended entries, but they still duplicate the same manifest/workload inventory in two places.
- 2026-03-17 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passes (`34 passed, 937 subtests passed in 23.08s`);
  - the AST probe above currently fails exactly on this cleanup with:
    - `tests/benchmarks/benchmark_expectations.py:missing:ZERO_GAP_BYTES_CASES`
    - `tests/benchmarks/test_source_tree_benchmark_scorecards.py:still-defines:ZERO_GAP_REPRESENTATIVE_BYTES_CASES`
    - `tests/benchmarks/test_source_tree_benchmark_scorecards.py:missing-import:ZERO_GAP_BYTES_CASES`
    - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py:still-defines:ZERO_GAP_BYTES_PROMOTION_CASES`
    - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py:missing-import:ZERO_GAP_BYTES_CASES`
