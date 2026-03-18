# RBR-0575: Collapse the combined source-tree zero-gap manifest promotion checks onto one table

Status: ready
Owner: architecture-implementation
Created: 2026-03-18

## Goal
- Remove the remaining copy-pasted zero-gap manifest promotion checks from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so one small case table plus one helper own the repeated raw/public representative assertions instead of four near-identical test methods.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` introduces one data-driven path for the repeated zero-gap manifest promotion checks:
  - add one module-level tuple named `ZERO_GAP_MANIFEST_PROMOTION_CASES`;
  - store the current `manifest_id`, `expected_workload_ids`, and `expected_measured_workload_count` inputs for these four pure repeated checks:
    - `grouped-named-boundary` with `("module-search-grouped-segment-cold-gap", "pattern-search-grouped-segment-warm-gap")` and measured count `13`;
    - `numbered-backreference-boundary` with `("module-search-numbered-backreference-segment-cold-gap", "pattern-search-numbered-backreference-prefix-purged-gap")` and measured count `5`;
    - `nested-group-boundary` with `("module-search-triple-nested-group-cold-gap", "pattern-fullmatch-named-quantified-nested-group-purged-gap")` and measured count `8`; and
    - `optional-group-boundary` with `("module-search-numbered-optional-group-conditional-cold-gap",)` and measured count `7`.
- Add one helper method named `_assert_zero_gap_manifest_representative_promotion(...)` on `SourceTreeCombinedBoundaryBenchmarkSuiteTest` that owns the repeated assertions by:
  - loading the raw manifest definition from `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[manifest_id]`;
  - asserting `known_gap_workload_ids is None`;
  - asserting `representative_measured_workload_ids == expected_workload_ids`;
  - asserting `representative_known_gap_workload_ids == ()`;
  - loading the public case via `source_tree_combined_case(manifest_id)`;
  - asserting `case.manifest_expectation.known_gap_count == 0`;
  - asserting `case.manifest_expectation.representative_measured_workload_ids == expected_workload_ids`;
  - asserting `case.manifest_expectation.representative_known_gap_workload_ids == ()`; and
  - delegating to `_assert_zero_gap_manifest_workloads_measured(...)` with the exact `expected_measured_workload_count` from the case table.
- Replace these four pure repeated test methods with one loop-based test named `test_zero_gap_manifest_representative_promotions_keep_selected_rows_measured(...)` that iterates `ZERO_GAP_MANIFEST_PROMOTION_CASES` and keeps `subTest(manifest_id=...)` labeling:
  - `test_grouped_named_manifest_promotes_legacy_grouped_segment_pair_to_measured`
  - `test_numbered_backreference_manifest_promotes_grouped_segment_pair_to_measured`
  - `test_nested_group_manifest_promotes_nested_pair_to_measured`
  - `test_optional_group_manifest_promotes_conditional_anchor_to_measured`
- Keep the adjacent special cases separate:
  - `test_literal_flag_manifest_no_longer_classifies_ascii_pair_as_known_gaps(...)` stays in place because it intentionally proves the zero-gap default-restoration path without pinning an exact raw representative tuple;
  - `test_counted_repeat_manifests_promote_legacy_upper_bound_rows_to_measured(...)` stays in place because it covers a two-manifest pair rather than the single-manifest repeated shape above; and
  - `test_quantified_alternation_manifest_promotes_broader_range_and_open_ended_bytes_rows_to_measured(...)` plus the zero-default restoration tests stay in place because they pin richer exact-equality or default-restoration behavior than the new generic table/helper should own.
- Preserve the current contract exactly for the four collapsed slices:
  - keep every current `manifest_id`, `expected_workload_ids`, and `expected_measured_workload_count` value unchanged;
  - keep the raw `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS` assertions and the public `source_tree_combined_case(...)` assertions at the same depth as today; and
  - keep the delegated `_assert_zero_gap_manifest_workloads_measured(...)` call on every case so the measured-workload and total-workload checks remain unchanged.
- Keep this cleanup local to the combined source-tree benchmark test module:
  - do not change `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, `python/rebar_harness/benchmarks.py`, workload manifests under `benchmarks/workloads/`, or published reports; and
  - do not broaden the task into another benchmark expectation registry, another support module, or a representative-policy rewrite.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - ```bash
    python3 - <<'PY'
    import ast
    from pathlib import Path

    path = Path('tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py')
    module = ast.parse(path.read_text())
    class_node = next(
        node
        for node in module.body
        if isinstance(node, ast.ClassDef)
        and node.name == 'SourceTreeCombinedBoundaryBenchmarkSuiteTest'
    )
    function_names = {
        node.name for node in class_node.body if isinstance(node, ast.FunctionDef)
    }
    old_pure_tests = {
        'test_grouped_named_manifest_promotes_legacy_grouped_segment_pair_to_measured',
        'test_numbered_backreference_manifest_promotes_grouped_segment_pair_to_measured',
        'test_nested_group_manifest_promotes_nested_pair_to_measured',
        'test_optional_group_manifest_promotes_conditional_anchor_to_measured',
    }
    required = {
        'test_literal_flag_manifest_no_longer_classifies_ascii_pair_as_known_gaps',
        '_assert_zero_gap_manifest_representative_promotion',
        'test_zero_gap_manifest_representative_promotions_keep_selected_rows_measured',
    }
    failures = []

    module_assignments = {
        target.id
        for node in module.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    }
    if 'ZERO_GAP_MANIFEST_PROMOTION_CASES' not in module_assignments:
        failures.append('module:missing:ZERO_GAP_MANIFEST_PROMOTION_CASES')

    missing = sorted(required - function_names)
    if missing:
        failures.append(f'class:missing:{",".join(missing)}')

    lingering = sorted(old_pure_tests & function_names)
    if lingering:
        failures.append(f'class:still-has-old-pure-tests:{",".join(lingering)}')

    loop_test = next(
        (
            node
            for node in class_node.body
            if isinstance(node, ast.FunctionDef)
            and node.name
            == 'test_zero_gap_manifest_representative_promotions_keep_selected_rows_measured'
        ),
        None,
    )
    if loop_test is None:
        failures.append('class:missing:new-loop-test')
    else:
        names = {child.id for child in ast.walk(loop_test) if isinstance(child, ast.Name)}
        attrs = {child.attr for child in ast.walk(loop_test) if isinstance(child, ast.Attribute)}
        referenced = names | attrs
        for symbol in (
            'ZERO_GAP_MANIFEST_PROMOTION_CASES',
            '_assert_zero_gap_manifest_representative_promotion',
            'subTest',
        ):
            if symbol not in referenced:
                failures.append(
                    'class:test_zero_gap_manifest_representative_promotions_keep_selected_rows_measured:missing:'
                    + symbol
                )

    if failures:
        raise SystemExit('\n'.join(failures))

    print('ok')
    PY
    ```

## Constraints
- Prefer deleting the four repeated methods over adding another support module, another expectation registry, or another wrapper layer.
- Keep the new table/helper smaller than the repeated method block it replaces. This task is about shrinking the benchmark test surface, not redistributing the same boilerplate.
- Preserve the current workload ids, manifest ids, and measured-workload counts exactly.

## Notes
- `RBR-0574` is the only live ready task and is feature work; `ops/state/backlog.md`, `ops/state/current_status.md`, and the task queue do not reserve `RBR-0575`, so `RBR-0575` is the next available architecture id.
- No blocked architecture task exists to reopen first, and rule 10 does not apply in the live checkout:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the dashboard HEAD `14ada90855242dc2718a1d5f0dac81577f0f3c1c` matches `git rev-parse HEAD`, so the tracked queue/runtime snapshot is current for this run.
- JSON burn-down remains complete and current:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l = 0`; and
  - `rg --files -g '*.json' | wc -l = 0`.
- The duplicate surface is concrete in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is currently `905` lines long;
  - the four pure repeated manifest-promotion tests listed above occupy `162` lines in aggregate; and
  - those four methods are the only adjacent single-manifest zero-gap promotion checks in the file that repeat the same raw/public representative assertion shape with only `manifest_id`, `expected_workload_ids`, and measured count changed.
- 2026-03-18 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passes (`19 passed, 692 subtests passed in 21.84s`);
  - the AST probe above currently fails exactly on this cleanup with:
    - `module:missing:ZERO_GAP_MANIFEST_PROMOTION_CASES`
    - `class:missing:_assert_zero_gap_manifest_representative_promotion,test_zero_gap_manifest_representative_promotions_keep_selected_rows_measured`
    - `class:still-has-old-pure-tests:test_grouped_named_manifest_promotes_legacy_grouped_segment_pair_to_measured,test_nested_group_manifest_promotes_nested_pair_to_measured,test_numbered_backreference_manifest_promotes_grouped_segment_pair_to_measured,test_optional_group_manifest_promotes_conditional_anchor_to_measured`
    - `class:missing:new-loop-test`
