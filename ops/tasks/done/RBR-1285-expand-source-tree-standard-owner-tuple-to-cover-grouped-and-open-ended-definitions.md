## RBR-1285: Expand source-tree standard owner tuple to cover grouped and open-ended definitions

Status: done
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Remove the remaining grouped/replacement/open-ended source-tree standard-anchor definition block that still lives inline inside `tests/benchmarks/standard_benchmark_anchor_support.py`, so the benchmark support layer keeps those source-tree-specific definition objects beside the existing grouped-alternation and counted-repeat selector/signature helpers in `tests/benchmarks/source_tree_benchmark_anchor_support.py` instead of splitting one source-tree family across two support files.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/standard_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_standard_benchmark_anchor_support.py`

## Acceptance Criteria
- Extend `tests/benchmarks/source_tree_benchmark_anchor_support.py` so the existing lazy cached tuple `SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS` becomes the single owner of this exact eight-definition source-tree block, in this exact order:
  - `optional-group-conditional`
  - `nested-group`
  - `exact-repeat`
  - `ranged-repeat`
  - `grouped-alternation`
  - `grouped-alternation-replacement`
  - `nested-group-replacement`
  - `open-ended-grouped-alternation`
- Move the four currently inline grouped/replacement/open-ended definitions from `tests/benchmarks/standard_benchmark_anchor_support.py` onto that owner tuple in `tests/benchmarks/source_tree_benchmark_anchor_support.py`:
  - `grouped-alternation`
  - `grouped-alternation-replacement`
  - `nested-group-replacement`
  - `open-ended-grouped-alternation`
- Build those moved definitions in `tests/benchmarks/source_tree_benchmark_anchor_support.py` using the existing source-tree-owned helper surface they already depend on, including:
  - `_grouped_alternation_correctness_case_signature`
  - `_grouped_alternation_workload_signature`
  - `_grouped_alternation_replacement_correctness_case_signature`
  - `_counted_repeat_correctness_case_signature`
  - `_counted_repeat_workload_signature`
  - any manifest-path constants and direct-parity supplemental-case imports needed to keep those definitions self-owned in the source-tree support file
- Update `tests/benchmarks/standard_benchmark_anchor_support.py` so `_build_standard_benchmark_definitions()` splices the expanded `SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS` tuple immediately after `PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS` and no longer defines those four grouped/replacement/open-ended source-tree entries inline.
- Preserve current behavior exactly:
  - keep the current full `STANDARD_BENCHMARK_DEFINITIONS` order unchanged;
  - keep the same manifest paths, expected anchor case ids, include-workload selectors, correctness-case signatures, workload signatures, callback-result parity flags, legacy-anchor subsets, special-unanchored workload ids, direct-parity supplemental cases, and any other current definition metadata for all four moved definitions; and
  - do not introduce a new registry, second source-tree owner tuple for this same family, compatibility alias, or another broker layer between the two support files.
- Keep the ownership flow simple:
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` should own this expanded eight-definition tuple because it already owns the grouped-alternation and counted-repeat signature helpers the remaining inline definitions depend on; and
  - `tests/benchmarks/standard_benchmark_anchor_support.py` should remain the single cross-domain inventory assembler, but it should no longer carry any source-tree-specific definition bodies for this family.
- Add focused coverage in `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` that pins the expanded owner boundary directly:
  - assert the owner module exports `SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS` with the exact eight definition names above in the current order; and
  - assert the matching entries in `tests/benchmarks/standard_benchmark_anchor_support.py` are the same definition objects reused from that expanded owner-owned tuple rather than fresh local copies.
- Add focused coverage in `tests/benchmarks/test_standard_benchmark_anchor_support.py` that pins the simplified central file directly:
  - assert the standard support source no longer contains inline `name="grouped-alternation"`, `name="grouped-alternation-replacement"`, `name="nested-group-replacement"`, or `name="open-ended-grouped-alternation"` literals;
  - assert the central file still imports and splices `SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS`; and
  - keep the existing full-suite standard-definition parametrization and anchoring checks running unchanged against the assembled `STANDARD_BENCHMARK_DEFINITIONS`.
- Keep the cleanup structural and bounded to the four files above. Do not widen it into workload manifests, `python/rebar_harness/benchmarks.py`, scorecards, README text, or tracked `ops/state/` prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n 'name=\"(grouped-alternation|grouped-alternation-replacement|nested-group-replacement|open-ended-grouped-alternation)\"' tests/benchmarks/standard_benchmark_anchor_support.py"`

## Constraints
- Prefer expanding the existing `SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS` owner tuple over adding another owner export or helper layer. The point is to delete the last inline source-tree definition block from the generic standard-support file, not to create another split.
- Keep imports direct and ordinary. If a tiny local cached builder or `__getattr__` export is needed to avoid an import cycle, keep it file-local and structural; do not reintroduce a hidden ownership split or proxy object.
- Do not change definition semantics, manifest inventories, benchmark scope, or parity expectations in this task.

## Notes
- `RBR-1285` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run;
  - the latest live task file is `RBR-1284` in `ops/tasks/done/`; and
  - `rg -n "RBR-1285|RBR-1286|RBR-1287|RBR-1288|RBR-1289|RBR-1290|RBR-13[0-9]{2}" ops/state/current_status.md ops/state/backlog.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done -g '*.md'` matched only historical mentions inside older done-task notes, not a live reservation for `RBR-1285`.
- No blocked architecture task exists to reopen or retire first in this run.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Queue and runtime state are not currently in the rule-10 stall case:
  - `.rebar/runtime/dashboard.md` reports a clean worktree, no ready tasks, no blocked tasks, and the last `architecture-implementation` run finished `done`; and
  - `.rebar/runtime/loop_state.json` shows no current environment issue or inherited-dirty retry state for either task worker.
- The remaining split is concrete in the live checkout:
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` already owns `_grouped_alternation_correctness_case_signature`, `_grouped_alternation_workload_signature`, `_grouped_alternation_replacement_correctness_case_signature`, `_counted_repeat_correctness_case_signature`, and `_counted_repeat_workload_signature`;
  - `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` already carries focused grouped-alternation and open-ended helper coverage; and
  - `bash -lc "! rg -n 'name=\"(grouped-alternation|grouped-alternation-replacement|nested-group-replacement|open-ended-grouped-alternation)\"' tests/benchmarks/standard_benchmark_anchor_support.py"` currently fails because those four definition bodies still live inline in `tests/benchmarks/standard_benchmark_anchor_support.py`, and that failure belongs to the exact cleanup queued here.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py` passed with `225 passed`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed with `28 passed`; and
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed with `341 tests collected`.

## Completion
- Expanded `tests/benchmarks/source_tree_benchmark_anchor_support.py` so `SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS` now owns the full eight-definition source-tree block, including the grouped-alternation, grouped-alternation-replacement, nested-group-replacement, and open-ended-grouped-alternation definitions with their existing manifest metadata and direct-parity supplemental cases.
- Simplified `tests/benchmarks/standard_benchmark_anchor_support.py` to splice the expanded owner tuple immediately after `PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS` and removed the last inline source-tree definition bodies from the central assembler.
- Updated the focused benchmark-support tests to pin the new eight-name owner tuple order, object reuse inside `STANDARD_BENCHMARK_DEFINITIONS`, the absence of the moved inline literals in the central file, and the unchanged owner-boundary assembly behavior.
