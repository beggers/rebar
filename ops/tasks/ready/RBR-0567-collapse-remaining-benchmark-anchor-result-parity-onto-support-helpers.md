# RBR-0567: Collapse the remaining benchmark anchor result-parity plumbing onto support helpers

Status: ready
Owner: architecture-implementation
Created: 2026-03-17

## Goal
- Remove the last open-coded benchmark-anchor CPython result-parity plumbing from the grouped-alternation and open-ended benchmark anchor-contract tests so `tests/benchmarks/correctness_anchor_support.py` owns the workload execution plus operation-specific comparison policy instead of each file reimplementing adjacent pieces of it.

## Deliverables
- `tests/benchmarks/correctness_anchor_support.py`
- `tests/benchmarks/test_grouped_alternation_benchmark_correctness_anchor_contract.py`
- `tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py`

## Acceptance Criteria
- `tests/benchmarks/correctness_anchor_support.py` grows one helper named `assert_benchmark_workload_matches_expected_result(...)` that owns benchmark-workload execution plus result comparison for the remaining anchor-contract cases:
  - accept the benchmark workload plus an already-computed expected result;
  - call `run_benchmark_workload_with_cpython(...)` exactly once per assertion;
  - keep `module.compile` comparisons routed through `assert_pattern_parity("stdlib", ...)`;
  - keep `module.search` and `pattern.fullmatch` comparisons routed through `assert_match_result_parity("stdlib", ..., check_regs=True)`; and
  - treat `module.sub`, `module.subn`, `pattern.sub`, and `pattern.subn` as plain value-equality comparisons so grouped replacement workloads stop open-coding that last dispatch path.
- `assert_anchored_workload_case_result_parity(...)` delegates to `assert_benchmark_workload_matches_expected_result(...)` instead of inlining its own operation switch, while preserving the current correctness-case lookup flow and the existing `module.compile` / `module.search` / `pattern.fullmatch` behavior exactly.
- `tests/benchmarks/test_grouped_alternation_benchmark_correctness_anchor_contract.py` stops open-coding workload/case lookup plus direct CPython result equality in `test_grouped_alternation_workload_callbacks_match_anchor_case_results()`:
  - route that test through `expected_anchored_workload_case_pairs(...)` and `assert_anchored_workload_case_result_parity(...)`;
  - preserve the current `GROUPED_ALTERNATION_DEFINITIONS`, `callback_anchor_case_ids`, legacy-workload expectations, and manifest scope exactly; and
  - do not change any expected anchor-case ids or workload ids in this run.
- `tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py` stops open-coding both remaining result-parity blocks:
  - `test_open_ended_anchored_workloads_match_anchor_case_results()` routes through `expected_anchored_workload_case_pairs(...)` and `assert_anchored_workload_case_result_parity(...)`, while preserving the existing exclusion of `EXPECTED_SPECIAL_UNANCHORED_WORKLOAD_IDS`;
  - `test_open_ended_special_unanchored_workloads_match_manual_cpython_dispatch()` routes through `assert_benchmark_workload_matches_expected_result(workload, _manual_expected_result(workload))`; and
  - keep `_manual_expected_result(...)`, `EXPECTED_SPECIAL_UNANCHORED_WORKLOAD_IDS`, the direct-parity bytes coverage checks, and the current anchored/unanchored split unchanged.
- Preserve current behavior exactly:
  - do not change benchmark manifests, correctness fixtures, expected anchor-case ids, workload ids, direct-parity bytes lookup logic, published reports, README/current-status/backlog prose, or Rust/Python runtime behavior outside this cleanup;
  - keep grouped-alternation replacement workloads compared by their current concrete return values; and
  - do not broaden this task into another signature-builder refactor, manifest cleanup, or feature/parity milestone.
- After the refactor, the two targeted test files no longer directly reference `published_cases_by_id`, `run_benchmark_workload_with_cpython`, `run_correctness_case_with_cpython`, `assert_pattern_parity`, or `assert_match_result_parity`; that dependency should live only in `tests/benchmarks/correctness_anchor_support.py` for this cleanup.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_grouped_alternation_benchmark_correctness_anchor_contract.py tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py`
  - ```bash
    python3 - <<'PY'
    import ast
    from pathlib import Path

    support_path = Path("tests/benchmarks/correctness_anchor_support.py")
    grouped_path = Path(
        "tests/benchmarks/test_grouped_alternation_benchmark_correctness_anchor_contract.py"
    )
    open_ended_path = Path(
        "tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py"
    )

    helper_name = "assert_benchmark_workload_matches_expected_result"
    disallowed = {
        "published_cases_by_id",
        "run_benchmark_workload_with_cpython",
        "run_correctness_case_with_cpython",
        "assert_pattern_parity",
        "assert_match_result_parity",
    }
    failures: list[str] = []

    support_module = ast.parse(support_path.read_text())
    support_functions = {
        node.name: node
        for node in support_module.body
        if isinstance(node, ast.FunctionDef)
    }
    helper = support_functions.get(helper_name)
    if helper is None:
        failures.append(f"support:missing:{helper_name}")
    anchored_helper = support_functions.get("assert_anchored_workload_case_result_parity")
    if anchored_helper is None:
        failures.append("support:missing:assert_anchored_workload_case_result_parity")
    else:
        names = {
            child.id
            for child in ast.walk(anchored_helper)
            if isinstance(child, ast.Name)
        }
        attrs = {
            child.attr
            for child in ast.walk(anchored_helper)
            if isinstance(child, ast.Attribute)
        }
        if helper_name not in names and helper_name not in attrs:
            failures.append(
                "support:assert_anchored_workload_case_result_parity:missing-helper-call"
            )

    for path, function_expectations in [
        (
            grouped_path,
            {
                "test_grouped_alternation_workload_callbacks_match_anchor_case_results": {
                    "must_reference": {
                        "expected_anchored_workload_case_pairs",
                        "assert_anchored_workload_case_result_parity",
                    },
                },
            },
        ),
        (
            open_ended_path,
            {
                "test_open_ended_anchored_workloads_match_anchor_case_results": {
                    "must_reference": {
                        "expected_anchored_workload_case_pairs",
                        "assert_anchored_workload_case_result_parity",
                    },
                },
                "test_open_ended_special_unanchored_workloads_match_manual_cpython_dispatch": {
                    "must_reference": {helper_name},
                },
            },
        ),
    ]:
        module = ast.parse(path.read_text())
        functions = {
            node.name: node
            for node in module.body
            if isinstance(node, ast.FunctionDef)
        }
        for function_name, expectation in function_expectations.items():
            node = functions.get(function_name)
            if node is None:
                failures.append(f"{path}:{function_name}:missing")
                continue
            names = {child.id for child in ast.walk(node) if isinstance(child, ast.Name)}
            attrs = {
                child.attr for child in ast.walk(node) if isinstance(child, ast.Attribute)
            }
            referenced = names | attrs
            missing = sorted(expectation["must_reference"] - referenced)
            if missing:
                failures.append(
                    f"{path}:{function_name}:missing:{','.join(missing)}"
                )
            lingering = sorted(disallowed & referenced)
            if lingering:
                failures.append(
                    f"{path}:{function_name}:still-uses:{','.join(lingering)}"
                )

    if failures:
        raise SystemExit("\n".join(failures))

    print("ok")
    PY
    ```

## Constraints
- Keep this cleanup local to the existing benchmark anchor-support layer and the two targeted test files. Do not broaden it into `tests/benchmarks/test_counted_repeat_benchmark_correctness_anchor_contract.py`, `tests/benchmarks/test_nested_group_benchmark_correctness_anchor_contract.py`, benchmark manifests, harness runtime code, or report publication.
- Prefer extending `tests/benchmarks/correctness_anchor_support.py` over adding another support module, helper registry, or benchmark-specific adapter layer.
- Preserve the current anchored/unanchored split, workload ordering, and expected ids exactly.

## Notes
- `RBR-0566` is already filed as the active feature task in `ops/tasks/ready/`, and `ops/state/backlog.md` plus `ops/state/current_status.md` do not reserve any `RBR-0567+` ids, so `RBR-0567` is the next available architecture id.
- No blocked architecture task exists to reopen first, and rule 10 does not apply in the live checkout:
  - `ops/tasks/blocked/` is empty;
  - the live queue on disk is `ready: 1`, `in_progress: 0`, `blocked: 0`;
  - the newest runtime dashboard still reports `Last Cycle Anomalies: none`; and
  - the most recent cycle completed both `architecture-implementation` and `feature-implementation` tasks as `done`, so there is no inherited-dirty or post-task refresh/commit stall to yield to.
- JSON burn-down remains complete, but the tracked dashboard is one commit behind `HEAD`, so the live filesystem counts are the source of truth for this run:
  - `.rebar/runtime/dashboard.md` reports HEAD `25874e366174bfd836876761c53a8ae930bd0090`;
  - `git rev-parse HEAD` is `7a418863174aeab00772d9824c0d7839376a6ee0`;
  - `git ls-files '*.json' | wc -l = 0`; and
  - `rg --files -g '*.json' | wc -l = 0`.
- `RBR-0565` explicitly left grouped-alternation and open-ended anchor coverage out of scope, and the remaining duplicate surface is concrete in the current checkout:
  - `tests/benchmarks/test_grouped_alternation_benchmark_correctness_anchor_contract.py` still open-codes one workload/case lookup plus direct `run_benchmark_workload_with_cpython(...) == run_correctness_case_with_cpython(...)` block in `test_grouped_alternation_workload_callbacks_match_anchor_case_results()`;
  - `tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py` still open-codes one anchored workload/case parity loop plus one manual compile-vs-match comparison block for the explicit unanchored workloads; and
  - the AST probe above currently fails exactly on that cleanup with the missing helper plus lingering direct-parity references in those three targeted test functions.
- 2026-03-17 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_grouped_alternation_benchmark_correctness_anchor_contract.py tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py` passes (`40 passed in 0.11s`).
