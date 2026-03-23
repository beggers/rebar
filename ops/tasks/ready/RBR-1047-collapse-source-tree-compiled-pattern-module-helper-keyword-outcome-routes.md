## RBR-1047: Collapse source-tree compiled-pattern module-helper keyword outcome routes

Status: ready
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining detached compiled-pattern module-helper keyword CPython-dispatch and outcome-assertion helpers from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the success and keyword-error contract surfaces derive that behavior through one canonical same-file route instead of three parallel free functions.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines these detached helpers:
  - `def _run_cpython_compiled_pattern_module_helper_keyword_workload(...)`
  - `def _assert_compiled_pattern_module_helper_keyword_contract_success_outcome(...)`
  - `def _assert_compiled_pattern_module_helper_keyword_contract_error_outcome(...)`
- Replace those three helpers with one canonical same-file route on `_CompiledPatternModuleHelperKeywordContractSurface`, or an equivalently smaller file-local structure, reused by both existing contract surfaces without adding a support module, registry file, or checked-in data layer:
  - the `"success"` entry in `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES`
  - the `"keyword-error"` entry in `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES`
- Keep the current success-surface outcome semantics intact while moving them onto that route:
  - `test_standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_keyword_contract_rows_until_helper_invocation` still compares each round-tripped workload against `run_benchmark_workload_with_cpython(source_workload)` through the owner-surface route;
  - `test_compiled_pattern_module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time` still sees the current successful `module.split`, `module.sub`, and `module.subn` results; and
  - `test_compiled_pattern_module_helper_keyword_cases_cover_bool_count_complements` still observes the same bounded bool-count complement results for the existing four workloads.
- Keep the current keyword-error CPython-dispatch and exception semantics intact while moving them onto that route:
  - the route still compiles `re.compile(workload.pattern_payload(), workload.flags)` before dispatching the helper call;
  - `module.split` still dispatches the compiled pattern plus `haystack_payload()`, and still appends the positional `maxsplit` argument only when `_collection_replacement_positional_keyword_field(workload) == "maxsplit"`;
  - `module.sub` and `module.subn` still dispatch the compiled pattern plus `replacement_payload()` and `haystack_payload()`, and still append the positional `count` argument only when `_collection_replacement_positional_keyword_field(workload) == "count"`;
  - keyword kwargs still round-trip through `dict(workload.kwargs)` before the CPython helper call; and
  - unexpected operations still fail locally instead of silently widening behavior.
- Update the current call sites to use that canonical route while preserving the existing local behavior asserted by these tests:
  - `test_standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_keyword_contract_rows_until_helper_invocation`
  - `test_run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_contract_workloads`
  - `test_compiled_pattern_module_helper_keyword_contract_callbacks_precompile_first_argument_before_timing`
  - `test_compiled_pattern_module_helper_keyword_error_callbacks_match_cpython_exceptions`

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_keyword_contract or compiled_pattern_module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time or compiled_pattern_module_helper_keyword_cases_cover_bool_count_complements or compiled_pattern_module_helper_keyword_error_callbacks_match_cpython_exceptions'`
- `bash -lc "! rg -n 'def _run_cpython_compiled_pattern_module_helper_keyword_workload\\(|def _assert_compiled_pattern_module_helper_keyword_contract_success_outcome\\(|def _assert_compiled_pattern_module_helper_keyword_contract_error_outcome\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep the cleanup file-local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Do not widen into wrong-text-model owner routes, compiled-pattern success-owner routes, compiled-pattern `module.compile` contract cases, workload manifests under `benchmarks/workloads/`, harness code under `python/rebar_harness/`, or non-benchmark test files.
- Prefer deleting detached outcome-routing plumbing over introducing another abstraction layer.
- Do not edit README/current-status/backlog prose, reports, or implementation code.

## Notes
- `RBR-1047` is the next available unreserved task id in the current checkout:
  - `ops/tasks/done/` currently ends at `RBR-1046-publish-module-sub-str-count-one-singleton.md`; and
  - `rg -n 'RBR-1047|RBR-1048|RBR-1049|RBR-1050' ops/state/backlog.md ops/state/current_status.md` returned no matches in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-ready-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest dashboard shows both task workers finishing `done`, with no inherited-dirty checkpoint churn or stalled post-task refresh path.
- The duplication target is concrete in the live checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently defines `_run_cpython_compiled_pattern_module_helper_keyword_workload(...)` at line `15953`, `_assert_compiled_pattern_module_helper_keyword_contract_success_outcome(...)` at line `15985`, `_assert_compiled_pattern_module_helper_keyword_contract_error_outcome(...)` at line `15997`, and `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES` at line `16012`;
  - the targeted pytest slice in Verification already passes (`77 passed, 644 deselected in 0.18s`); and
  - the negative `rg` check in Verification fails only because those exact helper definitions are still present.
- A broader `-k 'compiled_pattern_module_helper_keyword or compiled_pattern_module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time'` slice is currently red for unrelated drift in `test_collection_replacement_manifest_keeps_compiled_pattern_module_helper_keyword_error_rows_measured` (`10 != 12` measured rows), so the acceptance command is intentionally narrowed to the green slice above.
