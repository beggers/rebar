# RBR-1288: Move compile-proxy manifest-path ownership onto owner support

Status: ready
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Remove the last compile-proxy-specific manifest-path registry leak from `tests/benchmarks/standard_benchmark_anchor_support.py` so the central standard assembler only splices the compile-proxy owner tuple instead of also owning the `compile_matrix.py` and `regression_matrix.py` path constants that only the compile-proxy family uses.

## Deliverables
- `tests/benchmarks/compile_proxy_benchmark_support.py`
- `tests/benchmarks/standard_benchmark_anchor_support.py`
- `tests/benchmarks/test_compile_proxy_benchmark_support.py`
- `tests/benchmarks/test_standard_benchmark_anchor_support.py`

## Acceptance Criteria
- Move compile-proxy manifest-path ownership into `tests/benchmarks/compile_proxy_benchmark_support.py`:
  - define `COMPILE_MATRIX_MANIFEST_PATH` and `REGRESSION_MATRIX_MANIFEST_PATH` directly in that owner module;
  - build `COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS` from those local constants; and
  - keep the owner tuple's exact current behavior unchanged, including manifest-path order, expected anchor-case mapping, `include_workload`, `correctness_case_signature`, and `workload_signature`.
- Simplify `tests/benchmarks/standard_benchmark_anchor_support.py` so it no longer defines or mentions `COMPILE_MATRIX_MANIFEST_PATH` or `REGRESSION_MATRIX_MANIFEST_PATH`.
- Keep the ownership flow simple:
  - `tests/benchmarks/compile_proxy_benchmark_support.py` should be the only tracked benchmark-support module that names the compile and regression manifest paths used by the `compile-proxy` standard definition; and
  - `tests/benchmarks/standard_benchmark_anchor_support.py` should continue to import only `COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS` from that owner module, without reintroducing manifest-path aliases, a shared registry, or another broker layer.
- Update `tests/benchmarks/test_compile_proxy_benchmark_support.py` so it pins the new owner boundary directly:
  - assert the owner module's `COMPILE_MATRIX_MANIFEST_PATH` and `REGRESSION_MATRIX_MANIFEST_PATH` constants point to the current `benchmarks/workloads/compile_matrix.py` and `benchmarks/workloads/regression_matrix.py` files;
  - assert the `compile-proxy` definition still uses those owner-local constants in the same order; and
  - keep the existing direct assertions over the exact anchor-case mapping and helper-function reuse unchanged.
- Update `tests/benchmarks/test_standard_benchmark_anchor_support.py` so it pins the slimmer central boundary directly:
  - assert the standard-support source no longer contains `COMPILE_MATRIX_MANIFEST_PATH` or `REGRESSION_MATRIX_MANIFEST_PATH`;
  - keep the existing `test_standard_support_imports_only_compile_proxy_owner_tuple` check aligned with the slimmer owner boundary; and
  - keep the existing object-reuse assertion proving the leading `compile-proxy` entry in `STANDARD_BENCHMARK_DEFINITIONS` still comes from `COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS`.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compile_proxy_benchmark_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_compile_proxy_benchmark_support.py tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n 'COMPILE_MATRIX_MANIFEST_PATH|REGRESSION_MATRIX_MANIFEST_PATH' tests/benchmarks/standard_benchmark_anchor_support.py"`

## Constraints
- Keep this cleanup structural and bounded to the four files above. Do not widen it into `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, other owner modules, harness runners, workload manifests, published scorecards, README text, or tracked `ops/state/` prose.
- Prefer owner-local constants over introducing another shared manifest-path helper. The point is to delete one family-specific registry leak from the central assembler, not to create a new common layer.
- Do not change benchmark scope, manifest inventories, definition names, or parity expectations in this task.

## Notes
- `RBR-1288` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run;
  - the newest live task file before this change was `ops/tasks/done/RBR-1287-move-compile-proxy-standard-definition-onto-owner-support.md`; and
  - `rg -n "RBR-1288|RBR-1289|RBR-1290|RBR-129[1-9]|RBR-13[0-9]{2}" ops/state/current_status.md ops/state/backlog.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done -g '*.md'` matched only historical mentions inside older done-task notes, not a live reservation for `RBR-1288`.
- No blocked architecture task exists to reopen or normalize first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Queue/runtime state is not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reports a clean worktree, no ready tasks, and no blocked tasks; and
  - `.rebar/runtime/loop_state.json` shows the most recent `architecture-implementation` run finished `done` without an environment issue.
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/compile_proxy_benchmark_support.py` still imports `COMPILE_MATRIX_MANIFEST_PATH` and `REGRESSION_MATRIX_MANIFEST_PATH` from `tests/benchmarks/standard_benchmark_anchor_support.py`;
  - `tests/benchmarks/standard_benchmark_anchor_support.py` still defines those two compile-proxy-specific manifest constants even though the central file now only splices `COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS`; and
  - `bash -lc "! rg -n 'COMPILE_MATRIX_MANIFEST_PATH|REGRESSION_MATRIX_MANIFEST_PATH' tests/benchmarks/standard_benchmark_anchor_support.py"` currently fails because those constants still live in the central assembler, and that failure belongs exactly to this cleanup.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compile_proxy_benchmark_support.py` passed with `3 passed`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py` passed with `243 passed`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_compile_proxy_benchmark_support.py tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed with `334 tests collected`; and
  - the negative `rg` command above currently fails because `tests/benchmarks/standard_benchmark_anchor_support.py` still defines the compile-proxy-specific manifest-path constants.
