## RBR-1281: Move compiled-pattern helper standard anchor definitions onto owner support

Status: done
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Remove the remaining compiled-pattern helper standard-anchor definition block that still lives inside `tests/benchmarks/standard_benchmark_anchor_support.py`, so the benchmark layer keeps those compiled-pattern-helper-specific definition objects beside the existing selectors, signatures, dispatch helpers, and wrong-text-model support in `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py` instead of centralizing that family in the generic standard-support file.

## Deliverables
- `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`
- `tests/benchmarks/standard_benchmark_anchor_support.py`
- `tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py`
- `tests/benchmarks/test_standard_benchmark_anchor_support.py`

## Acceptance Criteria
- Extend `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py` so it becomes the single owner of a support-owned tuple named `COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS` covering this exact compiled-pattern helper definition family currently built inline in `tests/benchmarks/standard_benchmark_anchor_support.py`:
  - `module-workflow-compiled-pattern-literal-success`
  - `module-workflow-compiled-pattern-bounded-wildcard-success`
  - `module-workflow-compiled-pattern-verbose-bytes-success`
  - `module-workflow-compiled-pattern-wrong-text-model`
- Update `tests/benchmarks/standard_benchmark_anchor_support.py` so `_build_standard_benchmark_definitions()` imports and splices `COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS` into the overall `STANDARD_BENCHMARK_DEFINITIONS` inventory instead of defining those four compiled-pattern helper entries inline there.
- Preserve current behavior exactly:
  - keep the current definition order inside the full standard definition tuple;
  - keep the same manifest path, expected anchor case ids, include-workload selectors, correctness-case signatures, workload signatures, and callback-result parity flags for all moved definitions; and
  - do not introduce a new registry, generator, compatibility alias, or another broker layer between the two support files.
- Keep the ownership flow simple:
  - `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py` should own the compiled-pattern helper definition tuple because it already owns the adjacent compiled-pattern helper selectors, signatures, CPython dispatch helpers, and wrong-text-model support those definitions depend on; and
  - `tests/benchmarks/standard_benchmark_anchor_support.py` should remain the one place that assembles the full cross-domain standard definition inventory, but it should no longer carry the compiled-pattern-helper-specific definition bodies themselves.
- Add focused coverage in `tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py` that pins the new owner boundary directly:
  - assert the owner module exports `COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS` with the exact four definition names above in the current order; and
  - assert the matching entries in `tests/benchmarks/standard_benchmark_anchor_support.py` are the same definition objects reused from that support-owned tuple rather than fresh local copies.
- Add focused coverage in `tests/benchmarks/test_standard_benchmark_anchor_support.py` that pins the simplified central file directly:
  - assert the standard support source no longer contains inline `name="module-workflow-compiled-pattern-..."` definition literals for the moved family; and
  - keep the existing full-suite standard-definition parametrization and anchoring checks running unchanged against the assembled `STANDARD_BENCHMARK_DEFINITIONS`.
- Keep the cleanup structural and bounded to the four files above. Do not widen it into workload manifests, `python/rebar_harness/benchmarks.py`, scorecards, README text, or tracked `ops/state/` prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n 'name=\"(module-workflow-compiled-pattern-literal-success|module-workflow-compiled-pattern-bounded-wildcard-success|module-workflow-compiled-pattern-verbose-bytes-success|module-workflow-compiled-pattern-wrong-text-model)\"' tests/benchmarks/standard_benchmark_anchor_support.py"`

## Constraints
- Prefer moving the definition bodies onto the existing compiled-pattern helper owner module over introducing another shared helper layer. The point is to delete one remaining owner-specific block from the generic standard-support file, not to create a fresh registry abstraction.
- Keep imports direct and ordinary. If you need a tiny local factory or lazy import to avoid an import cycle, keep it file-local and structural; do not reintroduce a hidden ownership split or proxy object.
- Do not change definition semantics, manifest inventories, anchor expectations, or benchmark scope in this task.

## Notes
- `RBR-1281` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run;
  - the latest live task file is `RBR-1280` in `ops/tasks/done/`; and
  - `rg -n "RBR-12(8[0-9]|9[0-9])|RBR-13[0-9]{2}" ops/state/current_status.md ops/state/backlog.md` returned no reserved future ids in tracked state.
- No blocked architecture task exists to reopen or retire first in this run.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Queue and runtime state are not currently in the rule-10 stall case:
  - `.rebar/runtime/dashboard.md` reports a clean worktree, no ready tasks, no blocked tasks, and the last `architecture-implementation` run finished `done`; and
  - `.rebar/runtime/loop_state.json` shows no current environment issue or inherited-dirty retry state for either task worker.
- The ownership split is concrete in the live checkout:
  - `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py` already owns the compiled-pattern helper selectors and signature helpers for the four remaining standard definitions; and
  - `rg -n 'name=\"(module-workflow-compiled-pattern-literal-success|module-workflow-compiled-pattern-bounded-wildcard-success|module-workflow-compiled-pattern-verbose-bytes-success|module-workflow-compiled-pattern-wrong-text-model)\"' tests/benchmarks/standard_benchmark_anchor_support.py` matched only `tests/benchmarks/standard_benchmark_anchor_support.py` in this run.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py` passed with `259 passed`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py` passed with `292 passed`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed with `347 tests collected`; and
  - the negative `rg` check in `Verification` currently fails because those four compiled-pattern helper definition bodies still live inline in `tests/benchmarks/standard_benchmark_anchor_support.py`, and that failure belongs to the exact cleanup queued here.

## Completion
- Moved the four `module-workflow-compiled-pattern-*` standard anchor definitions onto `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py` behind the lazy cached owner export `COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS`, keeping their order and definition semantics unchanged.
- Simplified `tests/benchmarks/standard_benchmark_anchor_support.py` so the central inventory now splices the owner tuple directly instead of carrying inline compiled-pattern helper definition bodies.
- Added focused owner-boundary assertions in the compiled-pattern helper and standard-support benchmark tests, including direct source checks that the central file no longer inlines the moved `name="module-workflow-compiled-pattern-..."` literals.
- Verification in this implementation run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py` passed with `213 passed`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py` passed with `50 passed`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed with `351 tests collected`.
  - `bash -lc "! rg -n 'name=\"(module-workflow-compiled-pattern-literal-success|module-workflow-compiled-pattern-bounded-wildcard-success|module-workflow-compiled-pattern-verbose-bytes-success|module-workflow-compiled-pattern-wrong-text-model)\"' tests/benchmarks/standard_benchmark_anchor_support.py"` passed.
