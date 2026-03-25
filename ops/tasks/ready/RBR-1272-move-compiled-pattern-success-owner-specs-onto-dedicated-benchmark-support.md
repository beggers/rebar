## RBR-1272: Move compiled-pattern success owner specs onto dedicated benchmark support

Status: ready
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Remove the remaining compiled-pattern success contract owner-spec layer from `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`, so the benchmark harness keeps support/configuration machinery in a dedicated support module and leaves the test file focused on assertions.

## Deliverables
- `tests/benchmarks/compiled_pattern_module_success_benchmark_support.py`
- `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`

## Acceptance Criteria
- Add `tests/benchmarks/compiled_pattern_module_success_benchmark_support.py` as the single owner of the compiled-pattern success owner-spec surface currently defined in the test module:
  - `CompiledPatternModuleSuccessOwnerSpec`
  - `_COMPILED_PATTERN_MODULE_SUCCESS_CONTRACT_EXCLUDED_FIELDS`
  - `_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC`
  - `_COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC`
  - `_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS`
- Update `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py` to import and use that support surface instead of defining the owner spec and inventory locally.
- Preserve current behavior exactly for both success owners:
  - keep the same manifest paths, contract manifest ids, contract filenames, note text, expected source workload ids, preserved payload fields, and replacement-typing behavior;
  - keep `source_workloads()`, `contract_builder_spec()`, `expected_build_calls()`, `expected_callback_result()`, and `expected_callback_call()` returning the same values as before; and
  - keep `_compiled_pattern_module_helper_route(...)` as the route owner for callback expectations instead of introducing a new wrapper or registry layer.
- Keep the cleanup structural and bounded to the two files above. Do not widen it into harness implementation code, workload manifests, README/state docs, or a second generic support abstraction.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py tests/benchmarks/test_source_tree_contract_benchmark_support.py`
- `bash -lc "! rg -n 'class CompiledPatternModuleSuccessOwnerSpec|def contract_builder_spec\\(|def source_workloads\\(|def expected_build_calls\\(|def expected_callback_result\\(|def expected_callback_call\\(' tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py"`

## Constraints
- Prefer a dedicated compiled-pattern success support module over adding another generic contract-helper layer. The point is to finish moving support ownership out of the test file, not to introduce a broader abstraction.
- Keep imports direct. Do not leave compatibility aliases or forwarding wrappers in `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`.
- Do not change compiled-pattern success workload selection, contract payload shape, callback dispatch behavior, or assertion semantics in this task.

## Notes
- `RBR-1272` is the next available unreserved task id in this checkout:
  - `rg -n "RBR-1272|RBR-1273|RBR-1274|RBR-1275|RBR-1276" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked -g '*.md'` returned no matches in this run.
- No blocked architecture task exists to reopen or retire first in this run.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The support/test split drift is concrete in the live checkout:
  - `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py` is `432` lines in this run and still defines `CompiledPatternModuleSuccessOwnerSpec` plus five owner-surface methods locally;
  - `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py` is `1110` lines and already keeps analogous compiled-pattern contract support outside its test modules;
  - `tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py` is `853` lines and still shows the same support-versus-test split pressure, but leave that follow-on out of this task; and
  - `tests/benchmarks/source_tree_contract_benchmark_support.py` is only `140` lines, so this cleanup should reuse that existing contract helper surface rather than expanding the test file further.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py tests/benchmarks/test_source_tree_contract_benchmark_support.py` passed with `54 passed`; and
  - the negative `rg` check in `Verification` currently fails because the success owner-spec surface still lives in `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`, and that failure belongs to the exact cleanup queued here.
