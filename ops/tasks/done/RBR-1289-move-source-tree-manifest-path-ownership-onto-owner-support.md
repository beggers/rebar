# RBR-1289: Move source-tree manifest-path ownership onto owner support

Status: done
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Remove the remaining source-tree-specific manifest-path registry leak from `tests/benchmarks/standard_benchmark_anchor_support.py` so the central standard assembler only splices the source-tree owner tuples instead of also owning the nine workload-path constants that only `tests/benchmarks/source_tree_benchmark_anchor_support.py` uses.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/standard_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_standard_benchmark_anchor_support.py`

## Acceptance Criteria
- Move source-tree manifest-path ownership into `tests/benchmarks/source_tree_benchmark_anchor_support.py`:
  - define these constants directly in that owner module:
    - `MODULE_BOUNDARY_MANIFEST_PATH`
    - `OPTIONAL_GROUP_MANIFEST_PATH`
    - `NESTED_GROUP_MANIFEST_PATH`
    - `EXACT_REPEAT_MANIFEST_PATH`
    - `RANGED_REPEAT_MANIFEST_PATH`
    - `GROUPED_ALTERNATION_MANIFEST_PATH`
    - `GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH`
    - `NESTED_GROUP_REPLACEMENT_MANIFEST_PATH`
    - `OPEN_ENDED_MANIFEST_PATH`
  - keep both `MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS` and `SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS` behavior unchanged, including definition order, manifest-path order, exact anchor-case mappings, workload selectors, callback-parity flags, excluded-workload sets, and any legacy/special-unanchored handling.
- Simplify `tests/benchmarks/standard_benchmark_anchor_support.py` so it no longer defines or mentions any of those nine source-tree manifest-path constants.
- Keep the ownership boundary simple:
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` should be the only tracked benchmark-support module that names those nine source-tree workload paths for the module-workflow and source-tree standard definition exports; and
  - `tests/benchmarks/standard_benchmark_anchor_support.py` should continue to import only `MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS` and `SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS` from that owner module, without reintroducing manifest-path aliases, a shared registry, or another broker layer.
- Update `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` so it pins the new owner boundary directly:
  - assert the owner module constants point to the current benchmark workload files;
  - assert the module-workflow and source-tree standard definition exports still reuse those owner-local constants in the same manifest-path order; and
  - keep the existing direct assertions over the exact definition names, anchor-case mappings, and owner-export reuse intact.
- Update `tests/benchmarks/test_standard_benchmark_anchor_support.py` so it pins the slimmer central boundary directly:
  - assert the standard-support source no longer contains any of the nine source-tree manifest-path constant names;
  - keep the existing source-tree owner import checks aligned with the slimmer boundary, with no direct source-tree manifest-path imports from the central assembler; and
  - keep the existing object-reuse checks proving the `module-workflow-keyword-*` and source-tree definition slices in `STANDARD_BENCHMARK_DEFINITIONS` still come from the owner exports rather than rebuilt copies.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n 'MODULE_BOUNDARY_MANIFEST_PATH|OPTIONAL_GROUP_MANIFEST_PATH|NESTED_GROUP_MANIFEST_PATH|EXACT_REPEAT_MANIFEST_PATH|RANGED_REPEAT_MANIFEST_PATH|GROUPED_ALTERNATION_MANIFEST_PATH|GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH|NESTED_GROUP_REPLACEMENT_MANIFEST_PATH|OPEN_ENDED_MANIFEST_PATH' tests/benchmarks/standard_benchmark_anchor_support.py"`

## Constraints
- Keep this cleanup structural and bounded to the four files above. Do not widen it into workload manifests, benchmark runner code, source-tree scorecard generation, published reports, README text, or tracked `ops/state/` prose.
- Prefer owner-local path constants over adding a new shared manifest-path helper. The point is to delete one more family-specific registry leak from the central assembler, not to create another common layer.
- Do not change benchmark scope, manifest inventories, definition names, or parity expectations in this task.

## Notes
- `RBR-1289` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this run; and
  - `rg -n "RBR-1289|RBR-1290|RBR-1291|RBR-1292|RBR-1293|RBR-1294|RBR-1295|RBR-1296|RBR-1297|RBR-1298|RBR-1299|RBR-13[0-9]{2}" ops/state/current_status.md ops/state/backlog.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done -g '*.md'` matched only historical mentions inside older done-task notes, not a live reservation for `RBR-1289`.
- No blocked architecture task exists to reopen or normalize first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Queue/runtime state is not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reports a clean worktree, no ready tasks, and no blocked tasks; and
  - the most recent `architecture-implementation` run finished `done`.
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` still imports nine source-tree manifest-path constants from `tests/benchmarks/standard_benchmark_anchor_support.py`;
  - `tests/benchmarks/standard_benchmark_anchor_support.py` still defines those nine constants even though it now only splices the source-tree owner tuples; and
  - the negative `rg` command in the verification section currently fails because those names still live in the central assembler, and that failure belongs exactly to this cleanup.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed with `36 passed`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py` passed with `243 passed`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed with `367 tests collected`; and
  - the negative `rg` command above currently fails because the central standard support file still defines the source-tree-specific manifest-path constants.

## Completion
- Moved the nine source-tree manifest-path constants into `tests/benchmarks/source_tree_benchmark_anchor_support.py` and kept the owner-local module-workflow and source-tree definition tuples unchanged.
- Removed the nine literal source-tree manifest-path names from `tests/benchmarks/standard_benchmark_anchor_support.py`; the central assembler now only imports and splices the two source-tree owner tuples.
- Updated `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` to pin the owner-local constants directly and assert both owner exports keep reusing those constants in the same manifest-path order.
- Updated `tests/benchmarks/test_standard_benchmark_anchor_support.py` to assert the central source no longer contains the nine source-tree manifest-path names and that the builder-only source-tree owner imports stay limited to the two owner tuples.
- Verified with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `bash -lc "! rg -n 'MODULE_BOUNDARY_MANIFEST_PATH|OPTIONAL_GROUP_MANIFEST_PATH|NESTED_GROUP_MANIFEST_PATH|EXACT_REPEAT_MANIFEST_PATH|RANGED_REPEAT_MANIFEST_PATH|GROUPED_ALTERNATION_MANIFEST_PATH|GROUPED_ALTERNATION_REPLACEMENT_MANIFEST_PATH|NESTED_GROUP_REPLACEMENT_MANIFEST_PATH|OPEN_ENDED_MANIFEST_PATH' tests/benchmarks/standard_benchmark_anchor_support.py"`
