## RBR-1265: Move source-tree optional, nested, and counted-repeat anchor signatures onto dedicated support suite

Status: ready
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Remove the remaining optional-group, nested-group, and counted-repeat standard-anchor signature ownership that still lives inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, so the 10k-line combined benchmark broker stops owning source-tree helper logic that belongs beside the existing `tests/benchmarks/source_tree_benchmark_anchor_support.py` support surface.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Move these eight inline helpers out of `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and rehome them into `tests/benchmarks/source_tree_benchmark_anchor_support.py`:
  - `_optional_group_correctness_case_signature(...)`
  - `_optional_group_workload_signature(...)`
  - `_is_optional_group_conditional_workload(...)`
  - `_nested_group_correctness_case_signature(...)`
  - `_nested_group_workload_signature(...)`
  - `_counted_repeat_correctness_case_signature(...)`
  - `_counted_repeat_workload_signature(...)`
  - `_is_non_alternation_counted_repeat_workload(...)`
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to import those helpers from `tests/benchmarks/source_tree_benchmark_anchor_support.py` and delete the local helper definitions.
- Add focused owner-suite coverage in `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` that pins the moved helper behavior directly:
  - keep the optional-group helper restricted to the existing `module-search-numbered-optional-group-conditional-cold-gap` route and preserve its `module.search` / no-pattern-owner signature shape;
  - keep the nested-group helper behavior covering the existing compile, `module.search`, and `pattern.fullmatch` routes for both numbered and named live rows;
  - keep counted-repeat helper behavior covering the existing non-alternation compile, `module.search`, and `pattern.fullmatch` routes used by the exact-repeat, ranged-repeat, and open-ended grouped manifests; and
  - keep alternation-bearing workloads out of `_is_non_alternation_counted_repeat_workload(...)`.
- Preserve the current bounded standard benchmark anchor behavior exactly:
  - the `optional-group-conditional`, `nested-group`, `exact-repeat`, `ranged-repeat`, and `open-ended` `StandardBenchmarkAnchorContractDefinition`s in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` must keep the same manifest paths, anchored workload ids, callback-parity flag, and excluded or special-unanchored workload inventories; and
  - do not introduce a new support module, copied workload-id inventories, or a second source-tree anchor ownership layer.
- Do not widen this cleanup into workload manifests, `python/rebar_harness/benchmarks.py`, reports, README text, or tracked `ops/state/` prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `bash -lc "! rg -n 'def (_optional_group_correctness_case_signature|_optional_group_workload_signature|_is_optional_group_conditional_workload|_nested_group_correctness_case_signature|_nested_group_workload_signature|_counted_repeat_correctness_case_signature|_counted_repeat_workload_signature|_is_non_alternation_counted_repeat_workload)\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep the cleanup structural and bounded to the three benchmark files listed above.
- Prefer the existing `tests/benchmarks/source_tree_benchmark_anchor_support.py` module and owner test suite over adding another broker file, wrapper helper, or ownership layer.
- Preserve the current optional-group filter, nested-group route coverage, counted-repeat route coverage, and standard-anchor contract behavior exactly.

## Notes
- `RBR-1265` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this run; and
  - `rg -n "RBR-1265|RBR-1266|RBR-1267|RBR-1268" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done -g '*.md'` found no reserved follow-on ids in tracked state or live queue files outside a historical note in an older done-task file.
- No blocked architecture task exists to reopen or retire first in this run.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The simplification is concrete in the live checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is `10174` lines in this run;
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` is `537` lines; and
  - `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` is `729` lines.
- The helper ownership is still uniquely inline in the combined broker in this run:
  - `rg -n '_optional_group_correctness_case_signature|_optional_group_workload_signature|_is_optional_group_conditional_workload|_nested_group_correctness_case_signature|_nested_group_workload_signature|_counted_repeat_correctness_case_signature|_counted_repeat_workload_signature|_is_non_alternation_counted_repeat_workload' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` matched only `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`; and
  - the only live call sites are the `optional-group-conditional`, `nested-group`, `exact-repeat`, `ranged-repeat`, and `open-ended` standard-anchor definitions in the combined broker.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed with `17 passed`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed with `105 tests collected`.
  - `bash -lc "! rg -n 'def (_optional_group_correctness_case_signature|_optional_group_workload_signature|_is_optional_group_conditional_workload|_nested_group_correctness_case_signature|_nested_group_workload_signature|_counted_repeat_correctness_case_signature|_counted_repeat_workload_signature|_is_non_alternation_counted_repeat_workload)\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` currently fails because those eight helpers still live inline in the combined suite, and that failure belongs to the exact cleanup queued here.
