## RBR-1156: Extract compile-proxy benchmark anchor support module

Status: done
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the compile-proxy benchmark-anchor helper layer that still lives inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by moving that shared support and its focused contract checks into dedicated benchmark-support files, so the combined owner file stops carrying both the compile-proxy signature logic and the standard-benchmark assertions that consume it.

## Deliverables
- `tests/benchmarks/compile_proxy_benchmark_anchor_support.py`
- `tests/benchmarks/test_compile_proxy_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Add one bounded shared benchmark-support module at `tests/benchmarks/compile_proxy_benchmark_anchor_support.py` for the compile-proxy anchor helpers that currently live inline in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`:
  - move `_compile_proxy_signature(...)`, `_compile_proxy_correctness_case_signature(...)`, `_compile_proxy_workload_signature(...)`, and `_is_compile_proxy_workload(...)` onto that module;
  - keep the helper surface ordinary Python support code that stays focused on the existing compile-proxy contract across `benchmarks/workloads/compile_matrix.py` and `benchmarks/workloads/regression_matrix.py`; and
  - do not introduce a new benchmark-definition abstraction, registry, or another wrapper layer over the standard benchmark definitions.
- Add focused contract coverage at `tests/benchmarks/test_compile_proxy_benchmark_anchor_support.py` for the moved helper surface:
  - cover the shared compile-proxy signature shape for both correctness cases and benchmark workloads;
  - cover the current inclusion rule that keeps both `compile` and `module.compile` workloads in scope while excluding non-compile operations; and
  - keep the support tests focused on the extracted helper behavior instead of re-copying the full owner-file standard-benchmark matrix.
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so it imports and uses the new support module instead of defining the compile-proxy helper layer inline:
  - keep the existing `compile-proxy` entry in `STANDARD_BENCHMARK_DEFINITIONS` on the same `compile_matrix.py` and `regression_matrix.py` manifest paths with the same anchored case ids;
  - remove the moved helper definitions from this file once the new support module and support-test file fully cover them; and
  - leave the compile-proxy anchor mapping, manifest inventory, and standard-benchmark owner assertions in the owner file unless the extraction proves they are shared beyond this owner path in the current checkout.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q "tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::test_standard_benchmark_manifest_keeps_expected_workloads_in_scope[compile-proxy:compile_matrix.py]" "tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::test_standard_benchmark_manifest_keeps_expected_workloads_in_scope[compile-proxy:regression_matrix.py]" "tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::test_standard_benchmark_workloads_stay_anchored_to_published_correctness_cases[compile-proxy:compile_matrix.py]" "tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::test_standard_benchmark_workloads_stay_anchored_to_published_correctness_cases[compile-proxy:regression_matrix.py]" "tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::test_standard_benchmark_workloads_stay_pinned_to_exact_case_ids[compile-proxy]"`

## Constraints
- Keep the cleanup structural and limited to the three files above. Do not widen it into benchmark manifests, harness implementation code, correctness fixtures, README text, or tracked ops state prose.
- Prefer deleting the inline compile-proxy helper layer from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` over adding a wrapper module that simply re-exports the same names back into that file.
- Preserve the current compile-proxy workload inclusion rule, signature shape, and anchored case-id mapping exactly.

## Notes
- `RBR-1156` is the next available unreserved architecture task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run; and
  - `rg -n 'RBR-1156|RBR-1157|RBR-1158|RBR-1159' ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` matched only historical mentions inside completed task files and did not reveal a live reservation at `RBR-1156`.
- No blocked architecture task exists to reopen or retire first in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining simplification is concrete and benchmark-side in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is `21068` lines in this run;
  - `rg -n '^def (_compile_proxy_signature|_compile_proxy_correctness_case_signature|_compile_proxy_workload_signature|_is_compile_proxy_workload)\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` returns the inline helper block at lines `7321` through `7357`; and
  - those helpers currently feed the `compile-proxy` standard-benchmark definition at lines `9954` through `9956`, which keeps the extraction bounded to one support family rather than another owner-wide refactor.
- Verification status in this run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compile-proxy and standard_benchmark'` collected the five exact node ids used above in this run; and
  - the `Verification` command above returned `5 passed` in this run.

## Completion
- Extracted the inline compile-proxy helper block from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` into `tests/benchmarks/compile_proxy_benchmark_anchor_support.py` and updated the owner definition to import that support directly.
- Added focused support-contract coverage in `tests/benchmarks/test_compile_proxy_benchmark_anchor_support.py` for signature shape and the compile/module.compile workload inclusion rule.
- Verified the new support tests plus the five required compile-proxy owner-file benchmark-anchor tests with `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q`.
