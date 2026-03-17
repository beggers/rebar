# RBR-0571: Collapse the source-tree combined zero-gap bytes promotion tests onto one table

Status: done
Owner: architecture-implementation
Created: 2026-03-17

## Goal
- Remove the remaining copy-pasted zero-gap bytes representative-promotion checks from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so one small case table plus one helper own the repeated raw/public representative-membership assertions instead of eleven near-identical test methods.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` introduces one data-driven path for the repeated zero-gap bytes promotion checks:
  - add one module-level tuple named `ZERO_GAP_BYTES_PROMOTION_CASES` that captures the current `manifest_id`, `expected_workload_ids`, `expected_measured_workload_count`, and `expected_total_workload_count` inputs for the eleven pure repeated bytes-promotion checks listed in the Notes section;
  - add one helper method named `_assert_zero_gap_bytes_representative_subset(...)` on `SourceTreeCombinedBoundaryBenchmarkSuiteTest` that owns the repeated raw/public assertions by:
    - loading the raw manifest definition from `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]`;
    - asserting `known_gap_workload_ids is None` and `representative_known_gap_workload_ids is None` on that raw definition;
    - asserting every expected workload id is present in the raw `representative_measured_workload_ids`;
    - loading the public case via `source_tree_combined_case(manifest_id)`;
    - asserting `case.manifest_expectation.known_gap_count == 0` and `case.manifest_expectation.representative_known_gap_workload_ids == ()`; and
    - asserting every expected workload id is present in the public `representative_measured_workload_ids` before delegating to `_assert_zero_gap_manifest_workloads_measured(...)`; and
  - replace the eleven pure repeated test methods with one loop-based test named `test_zero_gap_bytes_manifest_promotions_keep_selected_rows_publicly_measured(...)` that iterates `ZERO_GAP_BYTES_PROMOTION_CASES` and keeps `subTest(manifest_id=...)` labeling.
- Preserve the current scorecard contract exactly for those eleven slices:
  - keep every current `manifest_id`, `expected_workload_ids`, `expected_measured_workload_count`, and `expected_total_workload_count` value unchanged;
  - keep the current wider-ranged-repeat rows on `WIDER_RANGED_REPEAT_MANIFEST_ID` and the open-ended rows on `"open-ended-quantified-group-boundary"`; and
  - keep the delegated `_assert_zero_gap_manifest_workloads_measured(...)` call on every case so the measured-workload/status assertions remain unchanged.
- Keep the richer quantified-alternation case as the dedicated special case:
  - `test_quantified_alternation_manifest_promotes_open_ended_bytes_rows_to_measured(...)` stays in place because it also pins exact raw and public `representative_measured_workload_ids == expected_workload_ids`, not just subset membership; and
  - do not fold that test into the new generic table/helper or weaken its current exact-equality assertions.
- Keep this cleanup local to the combined source-tree boundary benchmark test module:
  - do not change `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, harness runtime code, benchmark workload manifests, or published reports in this run; and
  - do not broaden the task into another representative-workload policy rewrite, source-tree scorecard refactor, or feature/benchmark catch-up change.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - ```bash
    python3 - <<'PY'
    import ast
    from pathlib import Path

    path = Path("tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py")
    module = ast.parse(path.read_text())
    class_node = next(
        node
        for node in module.body
        if isinstance(node, ast.ClassDef)
        and node.name == "SourceTreeCombinedBoundaryBenchmarkSuiteTest"
    )
    function_names = {
        node.name for node in class_node.body if isinstance(node, ast.FunctionDef)
    }
    old_pure_tests = {
        "test_wider_ranged_repeat_manifest_promotes_broader_range_conditional_bytes_rows_to_measured",
        "test_wider_ranged_repeat_manifest_promotes_broader_range_backtracking_heavy_bytes_rows_to_measured",
        "test_wider_ranged_repeat_manifest_promotes_nested_broader_range_backtracking_heavy_bytes_rows_to_measured",
        "test_wider_ranged_repeat_manifest_promotes_nested_broader_range_grouped_alternation_bytes_rows_to_measured",
        "test_wider_ranged_repeat_manifest_promotes_nested_broader_range_conditional_bytes_rows_to_measured",
        "test_wider_ranged_repeat_manifest_promotes_nested_open_ended_grouped_alternation_bytes_rows_to_measured",
        "test_open_ended_manifest_promotes_grouped_conditional_bytes_rows_to_measured",
        "test_open_ended_manifest_promotes_grouped_alternation_bytes_rows_to_measured",
        "test_open_ended_manifest_promotes_broader_range_grouped_alternation_bytes_rows_to_measured",
        "test_open_ended_manifest_promotes_grouped_backtracking_heavy_bytes_rows_to_measured",
        "test_open_ended_manifest_promotes_broader_range_backtracking_heavy_bytes_rows_to_measured",
    }
    required = {
        "_assert_zero_gap_bytes_representative_subset",
        "test_zero_gap_bytes_manifest_promotions_keep_selected_rows_publicly_measured",
        "test_quantified_alternation_manifest_promotes_open_ended_bytes_rows_to_measured",
    }
    failures: list[str] = []

    module_assignments = {
        target.id
        for node in module.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    }
    if "ZERO_GAP_BYTES_PROMOTION_CASES" not in module_assignments:
        failures.append("module:missing:ZERO_GAP_BYTES_PROMOTION_CASES")

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
            == "test_zero_gap_bytes_manifest_promotions_keep_selected_rows_publicly_measured"
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
            "ZERO_GAP_BYTES_PROMOTION_CASES",
            "_assert_zero_gap_bytes_representative_subset",
            "subTest",
        ):
            if symbol not in referenced:
                failures.append(
                    f"class:test_zero_gap_bytes_manifest_promotions_keep_selected_rows_publicly_measured:missing:{symbol}"
                )

    if failures:
        raise SystemExit("\n".join(failures))

    print("ok")
    PY
    ```

## Constraints
- Prefer deleting the eleven repeated methods over adding another support module, another benchmark expectation registry, or another source-tree wrapper layer.
- Keep the new table/helper smaller than the repeated method block it replaces; this task is about shrinking the test surface, not redistributing the same boilerplate.
- Preserve the current workload ids, manifest ids, assertion depth, and measured-workload counts exactly.

## Notes
- `RBR-0570` is already filed as the active feature task, and `ops/state/backlog.md`, `ops/state/current_status.md`, and the task queue do not reserve any `RBR-0571+` ids, so `RBR-0571` is the next available architecture id.
- No blocked architecture task exists to reopen first, and rule 10 does not apply in the live checkout:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the dashboard HEAD `9117fe62aa1f37a4f661a6809363ea9b949d4516` matches `git rev-parse HEAD`, so the tracked queue/runtime snapshot is current for this run.
- JSON burn-down remains complete and current:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l = 0`; and
  - `rg --files -g '*.json' | wc -l = 0`.
- The duplicate surface is concrete in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is currently `1360` lines long;
  - the eleven pure repeated bytes-promotion tests listed below occupy `509` lines in aggregate; and
  - those eleven methods are:
    - `test_wider_ranged_repeat_manifest_promotes_broader_range_conditional_bytes_rows_to_measured`
    - `test_wider_ranged_repeat_manifest_promotes_broader_range_backtracking_heavy_bytes_rows_to_measured`
    - `test_wider_ranged_repeat_manifest_promotes_nested_broader_range_backtracking_heavy_bytes_rows_to_measured`
    - `test_wider_ranged_repeat_manifest_promotes_nested_broader_range_grouped_alternation_bytes_rows_to_measured`
    - `test_wider_ranged_repeat_manifest_promotes_nested_broader_range_conditional_bytes_rows_to_measured`
    - `test_wider_ranged_repeat_manifest_promotes_nested_open_ended_grouped_alternation_bytes_rows_to_measured`
    - `test_open_ended_manifest_promotes_grouped_conditional_bytes_rows_to_measured`
    - `test_open_ended_manifest_promotes_grouped_alternation_bytes_rows_to_measured`
    - `test_open_ended_manifest_promotes_broader_range_grouped_alternation_bytes_rows_to_measured`
    - `test_open_ended_manifest_promotes_grouped_backtracking_heavy_bytes_rows_to_measured`
    - `test_open_ended_manifest_promotes_broader_range_backtracking_heavy_bytes_rows_to_measured`
- 2026-03-17 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passes (`29 passed, 675 subtests passed in 20.97s`);
  - the AST probe above currently fails exactly on this cleanup with:
    - `module:missing:ZERO_GAP_BYTES_PROMOTION_CASES`
    - `class:missing:_assert_zero_gap_bytes_representative_subset,test_zero_gap_bytes_manifest_promotions_keep_selected_rows_publicly_measured`
    - `class:still-has-old-pure-tests:...` for the eleven listed methods.

## Completion Notes
- 2026-03-17: Collapsed the eleven repeated zero-gap bytes-promotion checks in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` onto the new module-level `ZERO_GAP_BYTES_PROMOTION_CASES` table, the shared `SourceTreeCombinedBoundaryBenchmarkSuiteTest._assert_zero_gap_bytes_representative_subset(...)` helper, and the looped `test_zero_gap_bytes_manifest_promotions_keep_selected_rows_publicly_measured(...)` method while keeping `test_quantified_alternation_manifest_promotes_open_ended_bytes_rows_to_measured(...)` as the richer exact-equality special case.
- Verification:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` (`19 passed, 686 subtests passed in 20.96s`)
  - Task acceptance AST probe (`ok`)
