## RBR-1313: Delete duplicate source-tree benchmark test manifest-path owners

Status: ready
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Delete the remaining duplicate manifest-path constants from the source-tree benchmark test files so those suites reuse the existing owner constants from the shared benchmark support modules instead of rebuilding the same repo paths locally.

## Deliverables
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Remove the local source-tree manifest-path assignments from `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` and import or reuse the existing owner constants from `tests.benchmarks.source_tree_benchmark_anchor_support` instead:
  - `OPTIONAL_GROUP_MANIFEST_PATH`
  - `NESTED_GROUP_MANIFEST_PATH`
  - `EXACT_REPEAT_MANIFEST_PATH`
  - `RANGED_REPEAT_MANIFEST_PATH`
  - `GROUPED_ALTERNATION_MANIFEST_PATH`
  - `GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH`
  - `NESTED_GROUP_REPLACEMENT_MANIFEST_PATH`
  - `OPEN_ENDED_MANIFEST_PATH`
- Remove the local manifest-path assignments from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and reuse the current owners instead of redefining the same paths in the suite:
  - `PATTERN_BOUNDARY_MANIFEST_PATH` should come from `tests.benchmarks.benchmark_test_support`
  - the eight source-tree slice manifest-path constants above should come from `tests.benchmarks.source_tree_benchmark_anchor_support`
- Keep the ownership boundary explicit and unchanged:
  - do not move `PATTERN_BOUNDARY_MANIFEST_PATH` off `tests/benchmarks/benchmark_test_support.py`
  - do not move the eight source-tree slice manifest-path constants off `tests/benchmarks/source_tree_benchmark_anchor_support.py`
  - do not add a new helper module, alias layer, or compatibility wrapper
- Preserve the current benchmark suite behavior and coverage:
  - keep the current workload ids, manifest-selection behavior, anchored-case assertions, and collected test count stable
  - keep the existing manifest-path equality assertions and manifest-owner AST checks passing after the duplicate local assignments are deleted

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py::test_source_tree_owner_manifest_path_constants_point_to_current_workload_files`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n '^(PATTERN_BOUNDARY_MANIFEST_PATH|OPTIONAL_GROUP_MANIFEST_PATH|NESTED_GROUP_MANIFEST_PATH|EXACT_REPEAT_MANIFEST_PATH|RANGED_REPEAT_MANIFEST_PATH|GROUPED_ALTERNATION_MANIFEST_PATH|GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH|NESTED_GROUP_REPLACEMENT_MANIFEST_PATH|OPEN_ENDED_MANIFEST_PATH) =' tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep this cleanup structural and bounded to the benchmark test/support ownership layer above. Do not change workload manifests, benchmark runtime behavior, published scorecards, README text, or tracked `ops/state/` prose.
- Prefer deleting duplicate test-local constants over adding a second shared helper surface. The point is to leave one owner per manifest path, not another indirection layer.

## Notes
- `RBR-1313` is the next available unreserved task id in this checkout:
  - `rg -n "RBR-1313|RBR-1314|RBR-1315|RBR-1316" ops/state/current_status.md ops/state/backlog.md` returned no matches in this run; and
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was queued.
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
- Queue/runtime state was not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reported a clean worktree, no ready tasks, no blocked tasks, and the most recent `architecture-implementation` run finished `done`
  - the latest runtime dashboard showed no inherited-dirty, refresh, or commit anomaly
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` still defines eight source-tree manifest-path constants that are already owned by `tests/benchmarks/source_tree_benchmark_anchor_support.py`
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still defines `PATTERN_BOUNDARY_MANIFEST_PATH` plus the same eight source-tree manifest-path constants even though those owners already exist on the shared benchmark support paths
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py::test_source_tree_owner_manifest_path_constants_point_to_current_workload_files` passed with `1 passed in 0.09s`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed with `279 tests collected in 0.10s`
  - `bash -lc "! rg -n '^(PATTERN_BOUNDARY_MANIFEST_PATH|OPTIONAL_GROUP_MANIFEST_PATH|NESTED_GROUP_MANIFEST_PATH|EXACT_REPEAT_MANIFEST_PATH|RANGED_REPEAT_MANIFEST_PATH|GROUPED_ALTERNATION_MANIFEST_PATH|GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH|NESTED_GROUP_REPLACEMENT_MANIFEST_PATH|OPEN_ENDED_MANIFEST_PATH) =' tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` currently fails because both files still carry those duplicate assignments, and that failure belongs exactly to this cleanup.
