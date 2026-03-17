# RBR-0562: Collapse combined benchmark workload contract checks onto one helper

Status: done
Owner: architecture-implementation
Created: 2026-03-17

## Goal
- Remove the remaining repeated workload-record lookup and workload-contract assertion plumbing from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so one class-local helper owns those checks instead of five methods reimplementing them.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `SourceTreeCombinedBoundaryBenchmarkSuiteTest` grows one private helper named `_assert_manifest_workload_contracts(...)` that owns the repeated workload assertion block for a single `BenchmarkManifest`:
  - accept the manifest document, the scorecard, an ordered iterable of `(workload_id, expected_status)` pairs, and an optional `subtest_label`;
  - derive `manifest_id` from `manifest.manifest_id`;
  - route every pair through `assert_benchmark_workload_contract(...)` using `find_workload_record(...)` and `find_workload_document(...)`;
  - preserve the input order exactly; and
  - when `subtest_label` is passed, wrap each pair in `self.subTest(**{subtest_label: workload_id})`.
- `_assert_zero_gap_manifest_workloads_measured(...)` keeps the current manifest-summary count assertions and the existing `workload_id` versus `measured_workload_id` subtest-label behavior, but stops open-coding `assert_benchmark_workload_contract(...)`, `find_workload_record(...)`, and `find_workload_document(...)`; it delegates those checks through `_assert_manifest_workload_contracts(...)`.
- These four sites route their workload contract checks through `_assert_manifest_workload_contracts(...)` and no longer call `assert_benchmark_workload_contract(...)`, `find_workload_record(...)`, or `find_workload_document(...)` directly:
  - `test_regression_manifest_is_fully_measured_on_the_shared_surface`
  - `test_runner_regenerates_combined_source_tree_boundary_scorecards`
  - `_assert_source_tree_combined_manifest_slice`
  - `test_wider_ranged_repeat_manifest_shape_stays_covered_in_combined_suite`
- Preserve current behavior exactly:
  - `test_runner_regenerates_combined_source_tree_boundary_scorecards` still deduplicates representative ids in first-seen order before asserting statuses, and still keeps measured rows versus `representative_known_gap_workload_ids` split exactly as today;
  - `_assert_source_tree_combined_manifest_slice` still verifies matched row ids, patterns, operations, haystacks, and required row categories before workload contract checks;
  - `test_wider_ranged_repeat_manifest_shape_stays_covered_in_combined_suite` still asserts zero known gaps and full measured coverage before checking representative ids and pattern groups; and
  - do not change benchmark manifests, workload ids, manifest expectations, scorecard payloads, harness runtime behavior, published reports, README text, or tracked state files outside this task.
- After the refactor, only `_assert_manifest_workload_contracts(...)` may contain direct calls to `assert_benchmark_workload_contract(...)`, `find_workload_record(...)`, and `find_workload_document(...)` in this file. `_assert_zero_gap_manifest_workloads_measured(...)` and the four targeted sites above must not.
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

    helper_name = "_assert_manifest_workload_contracts"
    targets = {
        "_assert_zero_gap_manifest_workloads_measured",
        "test_regression_manifest_is_fully_measured_on_the_shared_surface",
        "test_runner_regenerates_combined_source_tree_boundary_scorecards",
        "_assert_source_tree_combined_manifest_slice",
        "test_wider_ranged_repeat_manifest_shape_stays_covered_in_combined_suite",
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
            if "assert_benchmark_workload_contract" in names:
                failures.append(f"{node.name}:still-calls-workload-contract")
            if "find_workload_record" in names or "find_workload_document" in names:
                failures.append(f"{node.name}:still-loads-workload-records")

    if not found_helper:
        failures.append("missing-helper-definition")

    if failures:
        raise SystemExit("\n".join(failures))

    print("ok")
    PY
    ```

## Constraints
- Keep this cleanup local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`. Do not broaden it into `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, `tests/benchmarks/benchmark_expectations.py`, benchmark workloads, harness runtime code, or published reports.
- Prefer extending `SourceTreeCombinedBoundaryBenchmarkSuiteTest` over adding another benchmark support module.
- Preserve workload ordering, expected statuses, and current subtest labeling exactly.

## Notes
- `RBR-0561` is already reserved in `ops/state/backlog.md` for the next quantified-alternation bytes parity follow-on, so `RBR-0562` is the next available architecture id.
- No blocked architecture task exists to reopen first, and rule 10 does not apply in the current checkout:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - `git status --short` was empty before this task was added.
- JSON burn-down remains complete and aligned in tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l = 0`; and
  - `rg --files -g '*.json' | wc -l = 0`.
- The duplicate workload-contract plumbing is concrete in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still carries direct `assert_benchmark_workload_contract(...)`, `find_workload_record(...)`, and `find_workload_document(...)` calls in `_assert_zero_gap_manifest_workloads_measured(...)`, `test_regression_manifest_is_fully_measured_on_the_shared_surface`, `test_runner_regenerates_combined_source_tree_boundary_scorecards`, `_assert_source_tree_combined_manifest_slice`, and `test_wider_ranged_repeat_manifest_shape_stays_covered_in_combined_suite`; and
  - the AST probe above currently fails exactly on that cleanup with `missing-helper-definition` plus direct workload-contract usage in each targeted method.
- 2026-03-17 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passes (`28 passed, 641 subtests passed in 20.86s`).

## Completion Notes
- Added `_assert_manifest_workload_contracts(...)` to `SourceTreeCombinedBoundaryBenchmarkSuiteTest` so one class-local helper now owns the repeated workload lookup and workload-contract assertions for a single `BenchmarkManifest`.
- Routed `_assert_zero_gap_manifest_workloads_measured(...)`, `test_regression_manifest_is_fully_measured_on_the_shared_surface`, `test_runner_regenerates_combined_source_tree_boundary_scorecards`, `_assert_source_tree_combined_manifest_slice`, and `test_wider_ranged_repeat_manifest_shape_stays_covered_in_combined_suite` through that helper while preserving manifest-summary checks, representative-id ordering, and the existing `measured_workload_id` versus `workload_id` subtest labeling behavior.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` (`28 passed, 669 subtests passed in 21.28s`) and the task AST probe (`ok`).
