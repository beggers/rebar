## RBR-1283: Move module-workflow keyword standard anchor definitions onto source-tree support

Status: ready
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Remove the remaining module-workflow keyword standard-anchor definition block that still lives inside `tests/benchmarks/standard_benchmark_anchor_support.py`, so the benchmark layer keeps those module-keyword-specific definition objects beside the existing selectors, argument/signature helpers, and keyword-error classification logic in `tests/benchmarks/source_tree_benchmark_anchor_support.py` instead of centralizing that family in the generic standard-support file.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/standard_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_standard_benchmark_anchor_support.py`

## Acceptance Criteria
- Extend `tests/benchmarks/source_tree_benchmark_anchor_support.py` so it becomes the single owner of a support-owned tuple named `MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS` covering this exact module-workflow keyword definition family currently built inline in `tests/benchmarks/standard_benchmark_anchor_support.py`, in this exact order:
  - `module-workflow-keyword-flags`
  - `module-workflow-keyword-errors`
- Update `tests/benchmarks/standard_benchmark_anchor_support.py` so `_build_standard_benchmark_definitions()` imports and splices `MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS` into the overall `STANDARD_BENCHMARK_DEFINITIONS` inventory immediately after `COLLECTION_REPLACEMENT_STANDARD_BENCHMARK_DEFINITIONS`, instead of defining those two module-workflow keyword entries inline there.
- Preserve current behavior exactly:
  - keep the current definition order inside the full standard definition tuple;
  - keep the same manifest path, expected anchor case ids, include-workload selectors, correctness-case signatures, workload signatures, and callback-result parity flags for both moved definitions; and
  - do not introduce a new benchmark-definition registry, compatibility alias, second keyword-owner export, or another broker layer between the two support files.
- Keep the ownership flow simple:
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` should own the module-workflow keyword definition tuple because it already owns `_is_module_workflow_keyword_flags_workload`, `_is_module_workflow_keyword_error_workload`, `_module_workflow_keyword_correctness_case_signature`, and `_module_workflow_keyword_workload_signature`, which are the exact selectors and signature helpers those definitions depend on; and
  - `tests/benchmarks/standard_benchmark_anchor_support.py` should remain the one place that assembles the full cross-domain standard definition inventory, but it should no longer carry the module-workflow-keyword-specific definition bodies themselves.
- Add focused coverage in `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` that pins the new owner boundary directly:
  - assert the owner module exports `MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS` with the exact two definition names above in the current order; and
  - assert the matching entries in `tests/benchmarks/standard_benchmark_anchor_support.py` are the same definition objects reused from that owner-owned tuple rather than fresh local copies.
- Add focused coverage in `tests/benchmarks/test_standard_benchmark_anchor_support.py` that pins the simplified central file directly:
  - assert the standard support source no longer contains inline `name="module-workflow-keyword-..."` definition literals;
  - assert the central file now imports and splices `MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS`; and
  - keep the existing full-suite standard-definition parametrization and anchoring checks running unchanged against the assembled `STANDARD_BENCHMARK_DEFINITIONS`.
- Keep the cleanup structural and bounded to the four files above. Do not widen it into workload manifests, `python/rebar_harness/benchmarks.py`, scorecards, README text, or tracked `ops/state/` prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n 'name=\"(module-workflow-keyword-flags|module-workflow-keyword-errors)\"' tests/benchmarks/standard_benchmark_anchor_support.py"`

## Constraints
- Prefer moving the definition bodies onto the existing source-tree owner module over introducing another shared helper layer. The point is to delete one remaining owner-specific block from the generic standard-support file, not to create a fresh registry abstraction.
- Keep imports direct and ordinary. If a tiny local cached builder or `__getattr__` export is needed to avoid an import cycle, keep it file-local and structural; do not reintroduce a hidden ownership split or proxy object.
- Do not change definition semantics, manifest inventories, anchor expectations, or benchmark scope in this task.

## Notes
- `RBR-1283` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run;
  - the latest live task file is `RBR-1282` in `ops/tasks/done/`; and
  - `rg -n "RBR-1283|RBR-1284|RBR-1285|RBR-1286|RBR-1287|RBR-1288|RBR-1289|RBR-1290|RBR-13[0-9]{2}" ops/state/current_status.md ops/state/backlog.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done -g '*.md'` found only historical mentions inside older done-task notes, not a live reservation for `RBR-1283`.
- No blocked architecture task exists to reopen or retire first in this run.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Queue and runtime state are not currently in the rule-10 stall case:
  - `.rebar/runtime/dashboard.md` reports a clean worktree, no ready tasks, no blocked tasks, and the last `architecture-implementation` run finished `done`; and
  - `.rebar/runtime/loop_state.json` shows `tracked_json_blob_count: 0` with no current environment-issue note in this run.
- The ownership split is concrete in the live checkout:
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` already owns `_is_module_workflow_keyword_flags_workload`, `_is_module_workflow_keyword_error_workload`, `_module_workflow_keyword_correctness_case_signature`, and `_module_workflow_keyword_workload_signature`; and
  - `rg -n 'name=\"(module-workflow-keyword-flags|module-workflow-keyword-errors)\"' tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/standard_benchmark_anchor_support.py` matched only `tests/benchmarks/standard_benchmark_anchor_support.py` in this run.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py` passed with `216 passed`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed with `26 passed`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed with `330 tests collected`; and
  - the negative `rg` check in `Verification` currently fails because those two module-workflow keyword definition bodies still live inline in `tests/benchmarks/standard_benchmark_anchor_support.py`, and that failure belongs to the exact cleanup queued here.
