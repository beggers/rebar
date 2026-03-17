## RBR-0559: Collapse zero-gap combined benchmark promotion tests onto one helper

Status: ready
Owner: architecture-implementation
Created: 2026-03-17

## Goal
- Remove the repeated source-tree benchmark runner and measured-workload contract boilerplate from the zero-gap combined-manifest promotion tests so one helper in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owns that end-to-end check instead of six test methods reimplementing it.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` grows one private helper on `SourceTreeCombinedBoundaryBenchmarkSuiteTest` named `_assert_zero_gap_manifest_workloads_measured(...)` that owns the repeated scorecard/workload verification block for a single-manifest combined case:
  - accept the already-built `case`, the `manifest_id`, the expected measured workload id tuple, and the expected measured-workload count;
  - run `run_source_tree_benchmark_scorecard([case.target_manifest.path])` once for that case;
  - assert `scorecard["manifests"][manifest_id]["known_gap_count"] == 0`;
  - assert `scorecard["manifests"][manifest_id]["measured_workloads"]` matches the provided count; and
  - assert every provided workload id stays `expected_status="measured"` through `assert_benchmark_workload_contract(...)` with the existing `find_workload_record(...)` / `find_workload_document(...)` path.
- Keep the task structural only:
  - do not add a second benchmark support module, registry, or dataclass;
  - do not move the manifest-specific raw expectation checks out of the test methods; and
  - do not change benchmark manifests, workload ids, benchmark expectation tables, harness runtime behavior, published reports, README text, or tracked state files outside this task.
- Route these six tests through the new helper and remove their open-coded runner/workload-contract block:
  - `test_literal_flag_manifest_no_longer_classifies_ascii_pair_as_known_gaps`
  - `test_grouped_named_manifest_promotes_legacy_grouped_segment_pair_to_measured`
  - `test_numbered_backreference_manifest_promotes_grouped_segment_pair_to_measured`
  - `test_nested_group_manifest_promotes_nested_pair_to_measured`
  - `test_optional_group_manifest_promotes_conditional_anchor_to_measured`
  - `test_counted_repeat_manifests_promote_legacy_upper_bound_rows_to_measured`
- Preserve current behavior exactly in those tests:
  - keep the same raw `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS[...]` assertions in each test;
  - keep the same public `case.manifest_expectation` assertions in each test;
  - keep the same measured workload ids and measured-workload counts (`10`, `13`, `5`, `8`, `7`, plus `13` and `8` in the counted-repeat loop);
  - keep `test_counted_repeat_manifests_promote_legacy_upper_bound_rows_to_measured` covering both `exact-repeat-quantified-group-boundary` and `ranged-repeat-quantified-group-boundary`; and
  - do not widen this cleanup into the broader bytes-row promotion tests below line 453 or the slice/shape helpers near the bottom of the file.
- After the refactor, those six tests no longer open-code any of the repeated benchmark runner/workload-contract plumbing:
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
- Keep the cleanup bounded to the six named tests. Do not refactor the wider/open-ended bytes-row promotion tests, the manifest-slice assertions, or the manifest-shape assertions in the same run.
- Preserve current subtest behavior and workload ordering exactly.

## Notes
- `RBR-0558` is already reserved in `ops/state/backlog.md` and `ops/state/current_status.md` for the next feature-owned broader-range open-ended `{2,}` grouped-alternation bytes benchmark catch-up, so `RBR-0559` is the next available architecture id.
- No blocked architecture task exists to reopen first, and rule 10 does not apply in the current checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - `git status --short` is empty in the current checkout.
- JSON burn-down remains complete and aligned in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l = 0`; and
  - `rg --files -g '*.json' | wc -l = 0`.
- The duplicate benchmark-test plumbing is concrete in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py:104-361` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py:389-451` each restate the same `run_source_tree_benchmark_scorecard(...)` plus measured-workload contract block for one zero-gap manifest or loop body; and
  - `rg -n "run_source_tree_benchmark_scorecard\\(|manifest_summary\\[\\\"known_gap_count\\\"\\]|assert_benchmark_workload_contract\\(|find_workload_record\\(|find_workload_document\\(" tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_scorecards.py | wc -l` currently returns `80`, so the benchmark assertion surface is still duplication-heavy even after the earlier expectation-data cleanups.
- 2026-03-17 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passes (`50 passed, 837 subtests passed in 22.11s`).
  - The AST probe above currently fails exactly on the missing helper cleanup with `missing-helper-definition` plus direct runner/workload-contract usage still present in the six targeted tests.
