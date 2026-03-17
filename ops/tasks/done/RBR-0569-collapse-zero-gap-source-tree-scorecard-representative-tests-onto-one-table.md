# RBR-0569: Collapse the zero-gap source-tree scorecard representative tests onto one table

Status: done
Owner: architecture-implementation
Created: 2026-03-17

## Goal
- Remove the remaining copy-pasted zero-gap representative-workload checks from `tests/benchmarks/test_source_tree_benchmark_scorecards.py` so one small data table plus one helper own the shared `source_tree_combined_case(...)` / public-representative assertion flow instead of eleven nearly identical test methods repeating it inline.

## Deliverables
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py` introduces one data-driven path for the repeated zero-gap representative subset checks:
  - add one module-level tuple named `ZERO_GAP_REPRESENTATIVE_BYTES_CASES` that captures the current `manifest_id` plus `expected_workload_ids` inputs for the eleven pure repeated subset checks listed in the Notes section;
  - add one helper method named `_assert_zero_gap_representative_workload_subset(...)` on `SourceTreeBenchmarkScorecardTest` that owns the repeated `source_tree_combined_case(...)`, `source_tree_combined_manifest_representative_measured_workload_ids(...)`, zero-known-gap, and representative-membership assertions; and
  - replace the eleven pure repeated `test_*exposes*_as_measured` methods with one loop-based test named `test_zero_gap_source_tree_manifests_keep_selected_bytes_representatives_publicly_measured(...)` that iterates `ZERO_GAP_REPRESENTATIVE_BYTES_CASES` and keeps per-manifest / per-workload `subTest(...)` labeling.
- Preserve the current scorecard contract exactly for those eleven slices:
  - keep every current `manifest_id` and `expected_workload_ids` tuple unchanged;
  - keep the `known_gap_count == 0` and `representative_known_gap_workload_ids == ()` assertions unchanged;
  - keep each expected workload asserted both against the public `source_tree_combined_manifest_representative_measured_workload_ids(...)` surface and the per-case `manifest_expectation.representative_measured_workload_ids`; and
  - do not reduce coverage for the open-ended, broader-range, grouped-conditional, grouped-backtracking-heavy, broader-range-backtracking-heavy, or nested broader-range slices that the removed methods currently pin.
- Keep the one richer quantified-alternation contract test as the dedicated special case:
  - `test_quantified_alternation_manifest_exposes_open_ended_bytes_rows_as_measured(...)` stays in place because it also asserts raw manifest-definition equality plus a rerun scorecard contract; and
  - do not fold that test into the new generic helper or weaken its current `run_source_tree_benchmark_scorecard(...)` assertions.
- Keep this cleanup local to the scorecard test module:
  - do not change `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, benchmark workload manifests, harness runtime code, or published reports in this run; and
  - do not broaden the task into another representative-workload policy rewrite or slice-expectation redesign.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py`
  - ```bash
    python3 - <<'PY'
    import ast
    from pathlib import Path

    path = Path("tests/benchmarks/test_source_tree_benchmark_scorecards.py")
    module = ast.parse(path.read_text())
    class_node = next(
        node
        for node in module.body
        if isinstance(node, ast.ClassDef)
        and node.name == "SourceTreeBenchmarkScorecardTest"
    )
    function_names = {
        node.name for node in class_node.body if isinstance(node, ast.FunctionDef)
    }
    old_pure_tests = {
        "test_wider_ranged_manifest_exposes_broader_range_conditional_bytes_rows_as_measured",
        "test_open_ended_manifest_exposes_grouped_alternation_bytes_rows_as_measured",
        "test_open_ended_manifest_exposes_broader_range_grouped_alternation_bytes_rows_as_measured",
        "test_open_ended_manifest_exposes_grouped_conditional_bytes_rows_as_measured",
        "test_open_ended_manifest_exposes_broader_range_backtracking_heavy_bytes_rows_as_measured",
        "test_open_ended_manifest_exposes_grouped_backtracking_heavy_bytes_rows_as_measured",
        "test_wider_ranged_manifest_exposes_broader_range_backtracking_heavy_bytes_rows_as_measured",
        "test_wider_ranged_manifest_exposes_nested_broader_range_backtracking_heavy_bytes_rows_as_measured",
        "test_wider_ranged_manifest_exposes_nested_broader_range_grouped_alternation_bytes_rows_as_measured",
        "test_wider_ranged_manifest_exposes_nested_broader_range_conditional_bytes_rows_as_measured",
        "test_wider_ranged_manifest_exposes_nested_open_ended_grouped_alternation_bytes_rows_as_measured",
    }
    required = {
        "_assert_zero_gap_representative_workload_subset",
        "test_zero_gap_source_tree_manifests_keep_selected_bytes_representatives_publicly_measured",
        "test_quantified_alternation_manifest_exposes_open_ended_bytes_rows_as_measured",
    }
    failures: list[str] = []

    module_assignments = {
        target.id
        for node in module.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    }
    if "ZERO_GAP_REPRESENTATIVE_BYTES_CASES" not in module_assignments:
        failures.append("module:missing:ZERO_GAP_REPRESENTATIVE_BYTES_CASES")

    missing = sorted(required - function_names)
    if missing:
        failures.append(f"class:missing:{','.join(missing)}")

    lingering = sorted(old_pure_tests & function_names)
    if lingering:
        failures.append(f"class:still-has-old-pure-tests:{','.join(lingering)}")

    loop_test = next(
        (
            node
            for node in class_node.body
            if isinstance(node, ast.FunctionDef)
            and node.name
            == "test_zero_gap_source_tree_manifests_keep_selected_bytes_representatives_publicly_measured"
        ),
        None,
    )
    if loop_test is None:
        failures.append("class:missing:new-loop-test")
    else:
        names = {child.id for child in ast.walk(loop_test) if isinstance(child, ast.Name)}
        attrs = {child.attr for child in ast.walk(loop_test) if isinstance(child, ast.Attribute)}
        referenced = names | attrs
        for symbol in (
            "ZERO_GAP_REPRESENTATIVE_BYTES_CASES",
            "_assert_zero_gap_representative_workload_subset",
            "subTest",
        ):
            if symbol not in referenced:
                failures.append(
                    f"class:test_zero_gap_source_tree_manifests_keep_selected_bytes_representatives_publicly_measured:missing:{symbol}"
                )

    if failures:
        raise SystemExit("\n".join(failures))

    print("ok")
    PY
    ```

## Constraints
- Prefer deleting the eleven repeated methods over introducing another support module, another expectation registry, or another benchmark-specific wrapper layer.
- Keep the new shared table/helper smaller than the current repeated method block; this task is about shrinking the scorecard test surface, not redistributing the same boilerplate.
- Preserve the current workload ids, manifest ids, and assertion depth exactly.

## Notes
- `RBR-0568` is already filed as the active feature task, and `ops/state/backlog.md`, `ops/state/current_status.md`, and the task queue do not reserve or use `RBR-0569`, so `RBR-0569` is the next available architecture id.
- No blocked architecture task exists to reopen first, and rule 10 does not apply in the live checkout:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the newest dashboard HEAD `97429765dabe00ffb77fb91379fb63b5d8f20b95` matches `git rev-parse HEAD`, so the tracked queue/runtime snapshot is current for this run.
- JSON burn-down remains complete and current:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l = 0`; and
  - `rg --files -g '*.json' | wc -l = 0`.
- The duplicate surface is concrete in the current checkout:
  - `tests/benchmarks/test_source_tree_benchmark_scorecards.py` is currently `780` lines long;
  - an AST probe against the live file reports `11` pure repeated `test_*exposes*_as_measured` methods that all differ only by `manifest_id` and `expected_workload_ids`, plus `1` richer special-case method (`test_quantified_alternation_manifest_exposes_open_ended_bytes_rows_as_measured`) that also reruns the scorecard and should stay separate; and
  - those eleven pure repeated methods are:
    - `test_wider_ranged_manifest_exposes_broader_range_conditional_bytes_rows_as_measured`
    - `test_open_ended_manifest_exposes_grouped_alternation_bytes_rows_as_measured`
    - `test_open_ended_manifest_exposes_broader_range_grouped_alternation_bytes_rows_as_measured`
    - `test_open_ended_manifest_exposes_grouped_conditional_bytes_rows_as_measured`
    - `test_open_ended_manifest_exposes_broader_range_backtracking_heavy_bytes_rows_as_measured`
    - `test_open_ended_manifest_exposes_grouped_backtracking_heavy_bytes_rows_as_measured`
    - `test_wider_ranged_manifest_exposes_broader_range_backtracking_heavy_bytes_rows_as_measured`
    - `test_wider_ranged_manifest_exposes_nested_broader_range_backtracking_heavy_bytes_rows_as_measured`
    - `test_wider_ranged_manifest_exposes_nested_broader_range_grouped_alternation_bytes_rows_as_measured`
    - `test_wider_ranged_manifest_exposes_nested_broader_range_conditional_bytes_rows_as_measured`
    - `test_wider_ranged_manifest_exposes_nested_open_ended_grouped_alternation_bytes_rows_as_measured`
- 2026-03-17 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py` passes (`25 passed, 228 subtests passed in 1.49s`).

## Completion Notes
- 2026-03-17: Collapsed the eleven repeated zero-gap representative workload checks in `tests/benchmarks/test_source_tree_benchmark_scorecards.py` onto the new module-level `ZERO_GAP_REPRESENTATIVE_BYTES_CASES` table, the shared `SourceTreeBenchmarkScorecardTest._assert_zero_gap_representative_workload_subset(...)` helper, and the looped `test_zero_gap_source_tree_manifests_keep_selected_bytes_representatives_publicly_measured(...)` test while keeping `test_quantified_alternation_manifest_exposes_open_ended_bytes_rows_as_measured(...)` as the dedicated richer special case.
- Verification:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py` (`15 passed, 239 subtests passed in 1.49s`)
  - Task acceptance AST probe (`ok`)
