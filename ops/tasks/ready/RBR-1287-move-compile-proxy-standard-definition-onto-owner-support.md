# RBR-1287: Move compile-proxy standard definition onto owner support

Status: ready
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Remove the last inline `compile-proxy` standard benchmark definition from `tests/benchmarks/standard_benchmark_anchor_support.py` so the central standard inventory only splices owner-owned tuples instead of still knowing one benchmark family's definition details directly.

## Deliverables
- `tests/benchmarks/compile_proxy_benchmark_support.py`
- `tests/benchmarks/standard_benchmark_anchor_support.py`
- `tests/benchmarks/test_compile_proxy_benchmark_support.py`
- `tests/benchmarks/test_standard_benchmark_anchor_support.py`

## Acceptance Criteria
- Add a new owner support module at `tests/benchmarks/compile_proxy_benchmark_support.py` that exposes one lazy cached tuple named `COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS` via `__getattr__`, following the same owner-export pattern already used by the other benchmark support modules.
- Keep that owner export structural and exact:
  - the tuple must contain exactly one `StandardBenchmarkAnchorContractDefinition` named `compile-proxy`;
  - it must preserve the current `manifest_paths` order of `COMPILE_MATRIX_MANIFEST_PATH` then `REGRESSION_MATRIX_MANIFEST_PATH`;
  - it must preserve the current exact `expected_anchor_case_ids` mapping:
    - `compile_matrix.py`:
      - `compile-inline-locale-bytes-warm` -> `bytes-inline-locale-flag-success`
      - `compile-lookbehind-cold` -> `str-fixed-width-lookbehind-success`
      - `compile-character-class-ignorecase-warm` -> `str-character-class-ignorecase-success`
      - `compile-possessive-quantifier-cold` -> `str-possessive-quantifier-success`
      - `compile-atomic-group-purged` -> `str-atomic-group-success`
      - `compile-parser-stress-cold` -> `str-parser-stress-compile-proxy-success`
    - `regression_matrix.py`:
      - `regression-parser-atomic-lookbehind-cold` -> `str-parser-stress-compile-proxy-success`
      - `regression-parser-bytes-backreference-purged` -> `bytes-named-backreference-compile-proxy-success`
      - `regression-module-compile-verbose-purged` -> `workflow-compile-str-verbose-regression`
      - `regression-module-compile-multiline-purged` -> `workflow-compile-str-multiline-regression`
      - `regression-module-compile-multiline-purged-bytes` -> `workflow-compile-bytes-multiline-regression`
      - `regression-module-compile-verbose-purged-bytes` -> `workflow-compile-bytes-verbose-regression`
  - it must preserve the current `include_workload`, `correctness_case_signature`, and `workload_signature` behavior by reusing the existing `is_compile_proxy_workload`, `compile_proxy_correctness_case_signature`, and `compile_proxy_workload_signature` helpers from `tests/benchmarks/benchmark_test_support.py` rather than duplicating them.
- Simplify `tests/benchmarks/standard_benchmark_anchor_support.py` so `_build_standard_benchmark_definitions()` imports and splices `COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS` first, before `COLLECTION_REPLACEMENT_STANDARD_BENCHMARK_DEFINITIONS`, and no longer imports `compile_proxy_correctness_case_signature`, `compile_proxy_workload_signature`, or `is_compile_proxy_workload` into the central assembler.
- Remove the inline `StandardBenchmarkAnchorContractDefinition(name="compile-proxy", ...)` block from `tests/benchmarks/standard_benchmark_anchor_support.py`; after the cleanup, the central file should not contain `name="compile-proxy"` or any compile-proxy-specific helper references.
- Add focused coverage in `tests/benchmarks/test_compile_proxy_benchmark_support.py` that pins the new owner module directly:
  - assert `COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS` is lazy and cached;
  - assert the export contains exactly one definition named `compile-proxy`;
  - assert that definition preserves the exact manifest-path order and anchor-case mapping listed above; and
  - assert the definition reuses the existing helper functions from `tests/benchmarks/benchmark_test_support.py` instead of diverging through a second helper layer.
- Update `tests/benchmarks/test_standard_benchmark_anchor_support.py` so it covers the new owner module boundary directly:
  - include the compile-proxy owner module in the lazy-export and missing-export parametrized checks;
  - assert the standard support source imports and splices `COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS`;
  - assert the central source no longer mentions `compile_proxy_correctness_case_signature`, `compile_proxy_workload_signature`, `is_compile_proxy_workload`, or `name="compile-proxy"`; and
  - assert the leading `compile-proxy` entry inside `STANDARD_BENCHMARK_DEFINITIONS` is the same definition object reused from `COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS`, not a rebuilt copy.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compile_proxy_benchmark_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_compile_proxy_benchmark_support.py tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n 'compile_proxy_correctness_case_signature|compile_proxy_workload_signature|is_compile_proxy_workload|name=\\\"compile-proxy\\\"' tests/benchmarks/standard_benchmark_anchor_support.py"`

## Constraints
- Keep this task structural and bounded to the four files above. Do not widen it into workload manifests, benchmark runner code, published scorecards, README/status prose, or unrelated benchmark families.
- Reuse the existing helper functions in `tests/benchmarks/benchmark_test_support.py`; do not move or rename those generic compile-proxy helpers in this task.
- Follow the existing owner-module pattern already used in `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`, `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py`, `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`, `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py`, and `tests/benchmarks/source_tree_benchmark_anchor_support.py`. Do not add another registry or alias layer.

## Notes
- `RBR-1287` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this run;
  - the newest live task file before this change was `ops/tasks/done/RBR-1286-export-compiled-pattern-module-compile-standard-definitions-from-owner-support.md`; and
  - `rg -n "RBR-1287|RBR-1288|RBR-1289|RBR-1290|RBR-129[1-9]|RBR-13[0-9]{2}" ops/state/current_status.md ops/state/backlog.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done -g '*.md'` matched only historical mentions inside older done-task notes, not a live reservation for `RBR-1287`.
- JSON burn-down remains complete in the live checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Queue/runtime state is not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reports a clean worktree, no ready tasks, no blocked tasks, and the most recent `architecture-implementation` run finished `done`; and
  - there is no newer blocked architecture task to reopen or normalize before seeding this cleanup.
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/standard_benchmark_anchor_support.py` still imports `compile_proxy_correctness_case_signature`, `compile_proxy_workload_signature`, and `is_compile_proxy_workload`;
  - the central file still contains an inline `StandardBenchmarkAnchorContractDefinition(name="compile-proxy", ...)`; and
  - `bash -lc "! rg -n 'compile_proxy_correctness_case_signature|compile_proxy_workload_signature|is_compile_proxy_workload|name=\\\"compile-proxy\\\"' tests/benchmarks/standard_benchmark_anchor_support.py"` currently fails exactly because that leak is still present.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py` passed with `236 passed`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compile_proxy_benchmark_support.py` currently fails because the file does not exist yet, which belongs exactly to this cleanup;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_compile_proxy_benchmark_support.py tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently fails because the new compile-proxy support test file does not exist yet, which belongs exactly to this cleanup; and
  - the negative `rg` command above currently fails because the central standard support file still inlines compile-proxy-specific ownership details.
