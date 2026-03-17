## RBR-0559: Collapse zero-gap single-manifest benchmark promotion tests onto one helper

Status: done
Owner: architecture-implementation
Created: 2026-03-17

## Goal
- Remove the repeated source-tree benchmark runner and measured-workload contract boilerplate from the zero-gap single-manifest promotion block so one helper in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owns that end-to-end check instead of seventeen test methods or loop bodies reimplementing it.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` grows one private helper on `SourceTreeCombinedBoundaryBenchmarkSuiteTest` named `_assert_zero_gap_manifest_workloads_measured(...)` that owns the repeated scorecard/workload verification block for a single-manifest `SourceTreeCombinedCase`:
  - accept the already-built `case`, the `manifest_id`, the expected measured workload id tuple, the expected measured-workload count, and an optional expected total workload count;
  - run `run_source_tree_benchmark_scorecard([case.target_manifest.path])` once for that case;
  - assert `scorecard["manifests"][manifest_id]["known_gap_count"] == 0`;
  - assert `scorecard["manifests"][manifest_id]["measured_workloads"]` matches the provided count;
  - when a total workload count is provided, assert `scorecard["manifests"][manifest_id]["workload_count"]` matches it; and
  - assert every provided workload id stays `expected_status="measured"` through `assert_benchmark_workload_contract(...)` with the existing `find_workload_record(...)` / `find_workload_document(...)` path.
- Keep the task structural only:
  - do not add a second benchmark support module, registry, or dataclass;
  - do not move the manifest-specific raw expectation checks out of the test methods; and
  - do not change benchmark manifests, workload ids, benchmark expectation tables, harness runtime behavior, published reports, README text, or tracked state files outside this task.
- Route these seventeen tests through the new helper and remove their open-coded runner/workload-contract block:
  - `test_literal_flag_manifest_no_longer_classifies_ascii_pair_as_known_gaps`
  - `test_grouped_named_manifest_promotes_legacy_grouped_segment_pair_to_measured`
  - `test_numbered_backreference_manifest_promotes_grouped_segment_pair_to_measured`
  - `test_nested_group_manifest_promotes_nested_pair_to_measured`
  - `test_optional_group_manifest_promotes_conditional_anchor_to_measured`
  - `test_counted_repeat_manifests_promote_legacy_upper_bound_rows_to_measured`
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
- Preserve current behavior exactly in those tests:
  - keep the same raw `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[...]` assertions in each test;
  - keep the same public `case.manifest_expectation` assertions in each test;
  - keep `test_counted_repeat_manifests_promote_legacy_upper_bound_rows_to_measured` covering both `exact-repeat-quantified-group-boundary` and `ranged-repeat-quantified-group-boundary`, with measured-workload counts `13` and `8`;
  - keep the six wider-ranged-repeat bytes-row tests asserting `measured_workloads == 100` and `workload_count == 100`;
  - keep the five open-ended bytes-row tests asserting `measured_workloads == 72` and `workload_count == 72`; and
  - do not widen this cleanup into `test_regression_manifest_is_fully_measured_on_the_shared_surface`, `test_runner_regenerates_combined_source_tree_boundary_scorecards`, `test_selected_combined_source_tree_manifest_slices_stay_covered`, or the slice/shape helpers near the bottom of the file.
- After the refactor, those seventeen tests no longer open-code any of the repeated benchmark runner/workload-contract plumbing:
  - no direct `run_source_tree_benchmark_scorecard(...)` call remains in those test bodies;
  - no direct `assert_benchmark_workload_contract(...)` call remains in those test bodies; and
  - no direct `find_workload_record(...)` or `find_workload_document(...)` call remains in those test bodies.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - ```bash
    PYTHONPATH=python ./.venv/bin/python - <<'PY'
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

    helper_name = "_assert_zero_gap_manifest_workloads_measured"
    targets = {
        "test_literal_flag_manifest_no_longer_classifies_ascii_pair_as_known_gaps",
        "test_grouped_named_manifest_promotes_legacy_grouped_segment_pair_to_measured",
        "test_numbered_backreference_manifest_promotes_grouped_segment_pair_to_measured",
        "test_nested_group_manifest_promotes_nested_pair_to_measured",
        "test_optional_group_manifest_promotes_conditional_anchor_to_measured",
        "test_counted_repeat_manifests_promote_legacy_upper_bound_rows_to_measured",
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

    found_helper = False
    failures: list[str] = []

    for node in class_node.body:
        if isinstance(node, ast.FunctionDef) and node.name == helper_name:
            found_helper = True
        if isinstance(node, ast.FunctionDef) and node.name in targets:
            names = {child.id for child in ast.walk(node) if isinstance(child, ast.Name)}
            attrs = {child.attr for child in ast.walk(node) if isinstance(child, ast.Attribute)}
            if helper_name not in names and helper_name not in attrs:
                failures.append(f"{node.name}:missing-helper-call")
            if "run_source_tree_benchmark_scorecard" in names:
                failures.append(f"{node.name}:still-calls-runner")
            if "assert_benchmark_workload_contract" in names:
                failures.append(f"{node.name}:still-calls-workload-contract")
            if "find_workload_record" in names or "find_workload_document" in names:
                failures.append(f"{node.name}:still-loads-workload-records")

    if not found_helper:
        failures.append("missing-helper-definition")

    if failures:
        raise SystemExit("\\n".join(failures))

    print("ok")
    PY
    ```

## Constraints
- Prefer extending the existing test class over introducing another benchmark helper module. The intended end state is one local helper that deletes repeated plumbing while leaving the manifest-specific expectation prose readable in-place.
- Keep the cleanup bounded to the seventeen named tests. Do not refactor `test_regression_manifest_is_fully_measured_on_the_shared_surface`, the multi-manifest runner regeneration assertions, the manifest-slice assertions, or the manifest-shape assertions in the same run.
- Preserve current subtest behavior and workload ordering exactly.

## Notes
- No blocked architecture task exists to reopen first, and rule 10 still does not apply in the current checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - `git status --short` was empty before this architecture-task refinement.
- JSON burn-down remains complete and aligned in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l = 0`; and
  - `rg --files -g '*.json' | wc -l = 0`.
- The duplicate benchmark-test plumbing is concrete in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py:104-1099` currently restates the same single-manifest `run_source_tree_benchmark_scorecard(...)` plus measured-workload contract block seventeen times across the zero-gap promotion block; and
  - `rg -n "run_source_tree_benchmark_scorecard\\(" tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py | wc -l` currently returns `21`, leaving only four non-targeted runner sites outside that promotion block for the broader suite-level assertions.
- 2026-03-17 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passes (`28 passed, 641 subtests passed in 20.97s`).
  - The AST probe above currently fails exactly on the missing helper cleanup with `missing-helper-definition` plus direct runner/workload-contract usage still present in the seventeen targeted tests.

## Completion Notes
- Added `_assert_zero_gap_manifest_workloads_measured(...)` to `SourceTreeCombinedBoundaryBenchmarkSuiteTest` so one class-local helper now owns the repeated single-manifest runner and measured-workload contract checks.
- Routed the seventeen named zero-gap promotion tests through that helper while preserving the existing manifest-specific raw expectation assertions, public `case.manifest_expectation` assertions, measured-workload counts, total-workload counts, and workload ordering.
- Kept the cleanup structural only: no benchmark manifests, workload ids, expectation tables, harness runtime behavior, published reports, README text, or tracked state files outside this task changed.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` (`28 passed, 641 subtests passed in 21.35s`) and the task's AST probe (`ok`).
