# RBR-0548: Collapse the source-tree benchmark common-case copy layer

Status: ready
Owner: architecture-implementation
Created: 2026-03-17

## Goal
- Remove the remaining build-and-copy wrapper layer in `tests/benchmarks/benchmark_expectations.py` now that the source-tree benchmark cases already share one base dataclass. The intended end state is that `source_tree_scorecard_case(...)` and `source_tree_combined_case(...)` build their concrete case records directly instead of first allocating a `SourceTreeBenchmarkCommonCase` and then copying its fields through one-off `from_common_case(...)` constructors.

## Deliverables
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/benchmark_expectations.py` deletes the redundant common-case copy path:
  - `SourceTreeScorecardCase.from_common_case(...)` is removed;
  - `SourceTreeCombinedCase.from_common_case(...)` is removed;
  - `_build_source_tree_benchmark_common_case(...)` is removed or replaced by a helper that returns constructor kwargs rather than a `SourceTreeBenchmarkCommonCase` instance; and
  - `source_tree_scorecard_case(...)` and `source_tree_combined_case(...)` instantiate `SourceTreeScorecardCase` and `SourceTreeCombinedCase` directly instead of first materializing a `common_case` object and then copying its fields.
- Preserve the current public case surface exactly:
  - `source_tree_scorecard_case("post-parser-workflows")` still yields `module-boundary`, `collection-replacement-boundary`, and `literal-flag-boundary` in that order;
  - `source_tree_combined_case("literal-flag-boundary")` still yields `compile-matrix`, `module-boundary`, `pattern-boundary`, `collection-replacement-boundary`, `literal-flag-boundary`, and `regression-matrix` in that order;
  - `source_tree_combined_case("literal-flag-boundary").target_manifest.manifest_id` remains `"literal-flag-boundary"`; and
  - keep `expected_adapter`, `expected_phase`, `expected_runner_version`, `expected_summary`, `selection_mode`, manifest expectations, and representative workload ids unchanged for the same scorecard and combined cases.
- Keep the cleanup structural only:
  - do not change files under `benchmarks/workloads/`;
  - do not change `python/rebar_harness/benchmarks.py`, benchmark selector ids, report payloads, or published reports;
  - do not change the typed `SourceTreeBenchmarkCommonCase` base surface itself beyond what is required to remove the intermediate copy layer; and
  - do not broaden this into another source-tree manifest-selection rewrite, expectation-table redesign, or feature/parity work.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - ```bash
    PYTHONPATH=python ./.venv/bin/python - <<'PY'
    from tests.benchmarks.benchmark_expectations import (
        source_tree_combined_case,
        source_tree_scorecard_case,
    )

    scorecard_case = source_tree_scorecard_case("post-parser-workflows")
    combined_case = source_tree_combined_case("literal-flag-boundary")

    assert [manifest.manifest_id for manifest in scorecard_case.manifests] == [
        "module-boundary",
        "collection-replacement-boundary",
        "literal-flag-boundary",
    ]
    assert [manifest.manifest_id for manifest in combined_case.manifests] == [
        "compile-matrix",
        "module-boundary",
        "pattern-boundary",
        "collection-replacement-boundary",
        "literal-flag-boundary",
        "regression-matrix",
    ]
    assert combined_case.target_manifest.manifest_id == "literal-flag-boundary"
    print("ok")
    PY
    ```
  - `rg -n "def from_common_case\\(|def _build_source_tree_benchmark_common_case\\(|return SourceTreeScorecardCase\\.from_common_case\\(|return SourceTreeCombinedCase\\.from_common_case\\(" tests/benchmarks/benchmark_expectations.py`
    The post-change result must be no matches.

## Constraints
- Prefer deleting the wrapper layer over introducing another helper dataclass, registry, or compatibility shim. If a replacement helper is needed, keep it smaller than the current `common_case` allocation plus copy path.
- Keep the existing benchmark case ids, manifest ids, workload ordering, known-gap counts, and representative-workload expectations unchanged.
- Do not touch tracked state files, README text, runtime artifacts, or queue another task in the same run.

## Notes
- No blocked architecture task exists to reopen first, and rule 10 does not apply in the current checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in the live filesystem before this task was added;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - `git status --short` was empty in the current checkout.
- JSON burn-down remains complete in both tracked and live views:
  - `tracked_json_blob_count: 0`
  - `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
- `RBR-0548` is unused in `ops/state/backlog.md`, `ops/state/current_status.md`, and the task queue, so it is the next available architecture id.
- The redundant wrapper layer is concrete in the current checkout:
  - `rg -n "def from_common_case\\(|def _build_source_tree_benchmark_common_case\\(|return SourceTreeScorecardCase\\.from_common_case\\(|return SourceTreeCombinedCase\\.from_common_case\\(" tests/benchmarks/benchmark_expectations.py` currently returns six matches: two `from_common_case(...)` definitions, two `_build_source_tree_benchmark_common_case(...)` call sites, and two `return ...from_common_case(...)` call sites;
  - `SourceTreeScorecardCase.from_common_case(...)` and `SourceTreeCombinedCase.from_common_case(...)` are each called exactly once; and
  - the intermediate `common_case` object exists only to copy shared fields that already live on the concrete subclasses via `SourceTreeBenchmarkCommonCase`.
- 2026-03-17 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passes (`53 passed, 1523 subtests passed in 22.00s`).
  - The inline manifest-order probe above prints `ok`.
