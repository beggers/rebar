# RBR-1056: Collapse the compiled-pattern `module.compile` success owner split

Status: ready
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining literal-versus-named-group success split in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the compiled-pattern `module.compile` success surface derives its two bounded slices through one canonical same-file owner-spec route instead of separate selector functions plus duplicated anchor-definition blocks.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines either of these one-off success selector functions:
  - `def _is_module_workflow_compiled_pattern_compile_literal_success_workload(...)`
  - `def _is_module_workflow_compiled_pattern_compile_named_group_success_workload(...)`
- Replace that split with one explicit same-file success-owner spec surface, or a strictly smaller equivalent, reused by both of these consumers:
  - the two compiled-pattern `module.compile` success `StandardBenchmarkAnchorContractDefinition` entries in the module-boundary anchor section;
  - `_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_CONTRACT_CASE`.
- Keep the current two success slices intact while routing them through that shared surface:
  - `literal`
  - `named-group`
- Preserve the current per-slice semantics exactly after the refactor:
  - both slices still route through `_module_workflow_compiled_pattern_compile_correctness_case_signature(...)`, `_module_workflow_compiled_pattern_compile_workload_signature(...)`, and `_is_module_workflow_compiled_pattern_compile_workload(...)`;
  - both slices still keep `expected_exception is None`, `kwargs == {}`, `use_compiled_pattern is True`, and `flags == 0`;
  - the literal slice still remains pinned to pattern `"abc"`;
  - the named-group slice still remains pinned to pattern `"(?P<word>abc)"`;
  - the two anchor-definition names stay unchanged:
    - `module-workflow-compiled-pattern-module-compile-literal-success`
    - `module-workflow-compiled-pattern-module-compile-named-group-success`
  - the success contract case still keeps the same four anchor pairs, contract filename, anchor contract filename, note text, excluded fields, and callback/CPython dispatch behavior.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'module_boundary_manifest_keeps_compiled_pattern_module_compile_keyword_rows_measured or standard_benchmark_manifest_preserves_compiled_pattern_module_compile_success_and_keyword_contract_rows_until_helper_invocation or compiled_pattern_module_compile_success_and_keyword_contract_rows_stay_anchored_to_published_correctness_cases or compiled_pattern_module_compile_keyword_kwargs_materialize_at_callback_time or run_internal_workload_probe_measures_compiled_pattern_module_compile_success_and_keyword_contract_workloads or compiled_pattern_module_compile_success_and_keyword_contract_callbacks_precompile_first_argument_before_timing'`
- `bash -lc "! rg -n '^def _is_module_workflow_compiled_pattern_compile_(literal|named_group)_success_workload\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep the cleanup file-local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Prefer deleting the remaining duplicated success split over introducing another support module, registry file, or checked-in data layer.
- Do not widen into keyword owner specs, wrong-text-model owner specs, workload manifests under `benchmarks/workloads/`, harness code under `python/rebar_harness/`, implementation code, reports, or tracked state prose.

## Notes
- `RBR-1056` is the next available unreserved task id in the current checkout:
  - `RBR-1055` is already occupied by the live feature task in `ops/tasks/ready/RBR-1055-catch-up-module-subn-bytes-single-match.md`; and
  - `rg -n 'RBR-1055|RBR-1056|RBR-1057|RBR-1058|RBR-1059' ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked` returned matches only for `RBR-1055` in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-ready-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `ready: 1`, `in_progress: 0`, and `blocked: 0`;
  - the newest dashboard shows both task workers finishing `done`, with no inherited-dirty checkpoint churn or stalled post-task refresh path; and
  - the focused benchmark-contract pytest slice above already passes in the live checkout (`75 passed, 647 deselected, 18 subtests passed`).
- The duplication target is concrete in the live checkout:
  - `_is_module_workflow_compiled_pattern_compile_literal_success_workload(...)` and `_is_module_workflow_compiled_pattern_compile_named_group_success_workload(...)` still sit at lines `7353` and `7364`;
  - the two success anchor-definition blocks still sit at lines `9819` and `9844`; and
  - `_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_CONTRACT_CASE` still hard-codes the paired selector split at line `17162`.
