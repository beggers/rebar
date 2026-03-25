## RBR-1286: Export compiled-pattern module.compile standard definitions from owner support

Status: ready
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Remove the remaining compiled-pattern `module.compile` owner-spec assembly details that still leak into `tests/benchmarks/standard_benchmark_anchor_support.py`, so the standard benchmark inventory imports one ordinary owner tuple from `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py` instead of reaching into that module's private owner-spec lists and rebuilding the tuple itself.

## Deliverables
- `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py`
- `tests/benchmarks/standard_benchmark_anchor_support.py`
- `tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py`
- `tests/benchmarks/test_standard_benchmark_anchor_support.py`

## Acceptance Criteria
- Add one cached owner-tuple builder in `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py` for the standard benchmark inventory, exposed lazily via `__getattr__` as `COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS`.
- Build that new owner tuple directly from the existing private owner specs already defined in `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py`, in this exact order:
  - `module-workflow-compiled-pattern-module-compile-literal-success`
  - `module-workflow-compiled-pattern-module-compile-named-group-success`
  - `module-workflow-compiled-pattern-module-compile-flags-int-zero-keyword`
  - `module-workflow-compiled-pattern-module-compile-flags-int-zero-keyword-named-group`
  - `module-workflow-compiled-pattern-module-compile-flags-bool-false-keyword`
  - `module-workflow-compiled-pattern-module-compile-flags-bool-false-keyword-named-group`
  - `module-workflow-compiled-pattern-module-compile-flags-ignorecase-keyword-rejection`
  - `module-workflow-compiled-pattern-module-compile-flags-ignorecase-keyword-rejection-named-group`
- Keep the ownership flow simple:
  - `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py` should remain the only file that knows how those private owner specs turn into standard benchmark anchor definitions; and
  - `tests/benchmarks/standard_benchmark_anchor_support.py` should only import and splice `COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS`, without importing `_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS`, `_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS`, or calling `owner_spec.anchor_definition()` itself.
- Update `tests/benchmarks/standard_benchmark_anchor_support.py` so `_build_standard_benchmark_definitions()` splices `COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS` in the same current position between `MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS` and `COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS`, preserving the current full `STANDARD_BENCHMARK_DEFINITIONS` order exactly.
- Preserve behavior exactly:
  - keep the same eight definition names, manifest paths, expected anchor case ids, include-workload selectors, correctness-case signatures, workload signatures, callback-result parity flags, and all current contract coverage unchanged;
  - keep `_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS` and `_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS` available for the existing contract-focused tests and builders inside the owner module; and
  - do not add another registry, alias layer, or second copy of the same tuple in the standard support file.
- Add focused coverage in `tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py` that pins the new owner export directly:
  - assert the module exposes `COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS` lazily and cached, like the other owner modules;
  - assert that export contains the exact eight definition names above in the exact order above; and
  - assert the exported tuple matches the tuple produced from the existing private owner specs rather than a divergent second inventory.
- Add focused coverage in `tests/benchmarks/test_standard_benchmark_anchor_support.py` that pins the simplified central assembler directly:
  - assert `tests/benchmarks/standard_benchmark_anchor_support.py` no longer imports the private compiled-pattern module.compile owner-spec names or calls `owner_spec.anchor_definition()`;
  - assert the central file imports and splices `COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS`; and
  - assert the matching compiled-pattern module.compile entries inside `STANDARD_BENCHMARK_DEFINITIONS` are the same definition objects reused from that new owner-owned tuple.
- Keep the cleanup structural and bounded to the four files above. Do not widen it into workload manifests, harness runners, scorecards, README text, or tracked `ops/state/` prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n '_COMPILED_PATTERN_MODULE_COMPILE_(SUCCESS|KEYWORD)_OWNER_SPECS|owner_spec\\.anchor_definition\\(' tests/benchmarks/standard_benchmark_anchor_support.py"`

## Constraints
- Prefer extending the existing owner-module pattern over adding a new support file. The point is to make compiled-pattern `module.compile` definitions behave like the other standard benchmark owner tuples, not to create another indirection layer.
- Keep imports direct and ordinary. If a tiny local cached builder or `__getattr__` export is needed, keep it inside `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py`; do not reintroduce central-file knowledge of private owner specs.
- Do not change benchmark scope, manifest inventories, contract payload shape, or parity expectations in this task.

## Notes
- `RBR-1286` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run;
  - the latest live task file is `RBR-1285` in `ops/tasks/done/`; and
  - `rg -n "RBR-1286|RBR-1287|RBR-1288|RBR-1289|RBR-1290|RBR-129[1-9]|RBR-13[0-9]{2}" ops/state/current_status.md ops/state/backlog.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done -g '*.md'` matched only historical mentions inside older done-task notes, not a live reservation for `RBR-1286`.
- JSON burn-down remains complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Queue and runtime state are not in the rule-10 stall case in this run:
  - `.rebar/runtime/dashboard.md` reports a clean worktree, no ready tasks, and no blocked tasks; and
  - `.rebar/runtime/loop_state.json` shows the most recent `architecture-implementation` run finished `done` without an environment issue.
- The current architecture leak is concrete in the live checkout:
  - `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py` already owns the private success and keyword owner specs and the logic that turns them into `StandardBenchmarkAnchorContractDefinition` objects;
  - `tests/benchmarks/standard_benchmark_anchor_support.py` still imports `_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS` and `_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS` and still calls `owner_spec.anchor_definition()` inline; and
  - `bash -lc "! rg -n '_COMPILED_PATTERN_MODULE_COMPILE_(SUCCESS|KEYWORD)_OWNER_SPECS|owner_spec\\.anchor_definition\\(' tests/benchmarks/standard_benchmark_anchor_support.py"` currently fails because those private owner-spec imports and calls still live in the central assembler, and that failure belongs to the exact cleanup queued here.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py` passed with `225 passed`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py` passed with `81 passed`; and
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed with `394 tests collected`.
