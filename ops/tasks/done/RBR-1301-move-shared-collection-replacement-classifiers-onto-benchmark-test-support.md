## RBR-1301: Move shared collection-replacement classifiers onto benchmark_test_support

Status: done
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Stop using `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` as the owner for shared benchmark argument-classification helpers by moving the remaining cross-owner helper surface onto `tests/benchmarks/benchmark_test_support.py`, so the collection-replacement module is left owning only collection/replacement-specific routes, selectors, and anchor definitions.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`
- `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py`
- `tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py`
- `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Move this shared helper surface off `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` and onto `tests/benchmarks/benchmark_test_support.py` without changing behavior:
  - `_is_encoded_indexlike_payload`
  - `_collection_replacement_keyword_parameter_name`
  - `_collection_replacement_positional_keyword_field`
  - `_is_collection_replacement_keyword_workload`
  - `_is_collection_replacement_wrong_text_model_workload`
- Update the non-owner import sites so they consume the moved helpers from `tests/benchmarks/benchmark_test_support.py` instead of `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`. This includes:
  - `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`
  - `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py`
  - `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py`
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- Move the ownership and identity assertions for the moved helper surface onto `tests/benchmarks/test_benchmark_test_support.py`. After this cleanup, `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` should keep only collection/replacement-specific owner assertions, not shared-helper ownership checks.
- Preserve the current keyword-routing, wrong-text-model classification, and encoded-indexlike detection behavior for:
  - collection/replacement benchmark routes;
  - compiled-pattern module-helper benchmark routes; and
  - pattern-boundary positional-window benchmark routes.
- Remove the moved definitions from `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` instead of leaving compatibility aliases, forwarding re-exports, or duplicated implementations behind.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n -U -P \"from tests\\.benchmarks\\.collection_replacement_benchmark_anchor_support import \\([\\s\\S]*?(_is_encoded_indexlike_payload|_collection_replacement_keyword_parameter_name|_collection_replacement_positional_keyword_field|_is_collection_replacement_keyword_workload|_is_collection_replacement_wrong_text_model_workload)\" tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep this cleanup structural and bounded to the benchmark support/test layer above. Do not change benchmark manifests, harness runtime behavior, scorecard publication logic, README text, or tracked `ops/state/` prose.
- Do not add a new helper broker module or leave a compatibility wrapper behind. The point is to centralize genuinely shared support in `tests/benchmarks/benchmark_test_support.py` and trim cross-owner leakage from the collection-replacement module.
- Keep `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` focused on collection/replacement-specific routes and definitions after the move; do not fold unrelated owner-specific expectation tables into `benchmark_test_support.py`.

## Notes
- `RBR-1301` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this run;
  - `rg -n "RBR-1301|RBR-1302|RBR-1303" ops/state/current_status.md ops/state/backlog.md` returned no live reservation for `RBR-1301`; and
  - the newest live task before this file was `ops/tasks/done/RBR-1300-move-generic-benchmark-broker-helpers-onto-benchmark-test-support.md`.
- No blocked architecture task existed to reopen or retire first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Queue/runtime state was not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reported a clean worktree, no ready tasks, no blocked tasks, and the most recent `architecture-implementation` run finished `done`; and
  - `.rebar/runtime/dashboard.md` showed no inherited-dirty or refresh/commit anomaly in the latest cycle snapshot.
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py` still imports `_collection_replacement_keyword_parameter_name`, `_collection_replacement_positional_keyword_field`, `_is_collection_replacement_keyword_workload`, and `_is_collection_replacement_wrong_text_model_workload` from `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`;
  - `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py` still imports `_is_encoded_indexlike_payload` from that same collection-replacement module; and
  - `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py` plus `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still reach into the collection-replacement owner module for pieces of this shared helper surface.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed with `383 passed, 3471 subtests passed in 39.67s`;
  - `bash -lc "! rg -n -U -P \"from tests\\.benchmarks\\.collection_replacement_benchmark_anchor_support import \\([\\s\\S]*?(_is_encoded_indexlike_payload|_collection_replacement_keyword_parameter_name|_collection_replacement_positional_keyword_field|_is_collection_replacement_keyword_workload|_is_collection_replacement_wrong_text_model_workload)\" tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` currently fails because those shared helpers still import from `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`, and that failure belongs exactly to this cleanup.

## Completion Note
- Moved `_is_encoded_indexlike_payload`, `_collection_replacement_keyword_parameter_name`, `_collection_replacement_positional_keyword_field`, `_is_collection_replacement_keyword_workload`, and `_is_collection_replacement_wrong_text_model_workload` onto `tests/benchmarks/benchmark_test_support.py`, updated the non-owner support/test import sites, and removed the moved definitions from `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`.
- Shifted the shared-helper ownership assertions onto `tests/benchmarks/test_benchmark_test_support.py`, kept the collection/replacement owner tests focused on owner-specific surfaces, and preserved the benchmark classification/signature behavior through the existing support tests.
- Verified with `./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` (`387 passed, 3471 subtests passed in 39.68s`) and with the task grep check, which now exits successfully.
