# RBR-1033: Collapse source-tree compiled-pattern contract-builder triplets

Status: ready
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining repeated contract-manifest payload/workload/manifest builder triplets from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the compiled-pattern helper-keyword, compiled-pattern success-owner, and wrong-text-model benchmark contract coverage all route through one file-local contract-builder path instead of three near-identical helper families.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines these three parallel contract-builder triplets:
  - helper-keyword triplet:
    - `def _compiled_pattern_module_helper_contract_manifest_payload(...)`
    - `def _compiled_pattern_module_helper_contract_workload(...)`
    - `def _compiled_pattern_module_helper_contract_manifest(...)`
  - success-owner triplet:
    - `def _compiled_pattern_module_contract_manifest_payload(...)`
    - `def _compiled_pattern_module_contract_workload(...)`
    - `def _compiled_pattern_module_contract_manifest(...)`
  - wrong-text-model triplet:
    - `def _wrong_text_model_contract_manifest_payload(...)`
    - `def _wrong_text_model_contract_workload(...)`
    - `def _wrong_text_model_contract_manifest(...)`
- Replace those nine helpers with one canonical file-local contract-builder route, or an equivalently smaller same-file structure, that is reused by all three existing owner/spec surfaces without adding a support module, registry file, or checked-in data layer:
  - `_CompiledPatternModuleHelperKeywordContractSpec` / `_CompiledPatternModuleHelperKeywordContractSurface`
  - `CompiledPatternModuleSuccessOwnerSpec`
  - `WrongTextModelOwnerSpec`
- Keep the current owner-specific semantics intact while sharing the builder path:
  - helper-keyword contracts still preserve `spec.manifest_timed_samples`, `spec.notes`, and the current `preserve_expected_exception` behavior;
  - success-owner contracts still keep `timing_scope="module-helper-call"`, still strip `expected_exception`, and still preserve replacement payload typing only when `owner_spec.preserve_replacement_payload_typing` is true;
  - wrong-text-model contracts still keep `owner_spec.contract_manifest_id`, `owner_spec.timing_scope`, `owner_spec.excluded_fields`, and optional `owner_spec.note_surface`;
  - all three surfaces still append `-contract` to the same live source workload ids in the same order and still use `workload_to_payload(...)` / `workload_from_payload(...)` to round-trip the generated contract workloads.
- Keep the existing live source-workload entry points and owner routes instead of widening the cleanup into tracked workload changes:
  - `_compiled_pattern_module_helper_keyword_source_workloads()`
  - `_compiled_pattern_module_helper_keyword_precompile_anchor_source_workloads()`
  - `_compiled_pattern_module_helper_keyword_error_source_workloads()`
  - `_compiled_pattern_module_contract_source_workloads(...)`
  - `_wrong_text_model_source_workloads(...)`
- Preserve the current benchmark-owner behavior that the existing targeted tests assert:
  - helper-keyword contracts still cover the same success and keyword-error rows, still preserve `count`/`maxsplit` and `kwargs`, and still keep the same precompile-first callback expectations;
  - success-owner contracts still preserve the same collection/replacement and module-boundary source row order, payload typing, manifest ids, probe coverage, and callback-result shapes;
  - wrong-text-model contracts still preserve the same direct-`Pattern` versus compiled-pattern-module semantic split, `TypeError` comparison path, `timing_scope`, `haystack_text_model`, and callback/precompile expectations.
- Keep the cleanup structural and bounded:
  - do not widen into the adjacent compiled-pattern `module.compile` contract family rooted at `_compiled_pattern_module_compile_contract_manifest_payload(...)`, `_compiled_pattern_module_compile_contract_workload(...)`, and `_compiled_pattern_module_compile_contract_manifest(...)`;
  - do not edit `benchmarks/workloads/*.py`, `python/rebar_harness/benchmarks.py`, reports, README/current-status/backlog prose, or non-benchmark test files in this run.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_keyword_contract or compiled_pattern_module_collection_replacement_success or compiled_pattern_module_boundary_success or wrong_text_model_contract or wrong_text_model_callbacks_preserve_precompile_contract or run_internal_workload_probe_measures_wrong_text_model_contract_workloads'`
- `bash -lc "! rg -n 'def _compiled_pattern_module_helper_contract_manifest_payload\\(|def _compiled_pattern_module_helper_contract_workload\\(|def _compiled_pattern_module_helper_contract_manifest\\(|def _compiled_pattern_module_contract_manifest_payload\\(|def _compiled_pattern_module_contract_workload\\(|def _compiled_pattern_module_contract_manifest\\(|def _wrong_text_model_contract_manifest_payload\\(|def _wrong_text_model_contract_workload\\(|def _wrong_text_model_contract_manifest\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep the cleanup file-local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Prefer deleting duplicate contract-builder plumbing over introducing another detached abstraction layer.

## Notes
- `RBR-1033` is the next available unreserved task id in the current checkout:
  - `rg -n "RBR-1033|RBR-1034|RBR-1035|RBR-1036|RBR-1037|RBR-1038|RBR-1039" ops/state/current_status.md ops/state/backlog.md` returned no matches in this run; and
  - `ops/tasks/done/` currently ends at `RBR-1032-catch-up-pattern-replacement-bytes-negative-count-pair.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-ready-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh/commit path to yield to.
- The duplication target is concrete in the live checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently keeps three separate contract-builder triplets rooted at lines `15830`, `15853`, `15877`; `16522`, `16546`, `16603`; and `17868`, `17893`, `17917`;
  - the negative `rg` check in Verification currently fails only because those exact duplicated helpers are still present; and
  - the targeted pytest slice in Verification currently passes (`139 passed, 581 deselected in 0.25s`).
