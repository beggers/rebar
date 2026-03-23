# RBR-1066: Collapse compiled-pattern module success anchor singletons

Status: done
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining one-off compiled-pattern module-helper success anchor-contract tests in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the collection/replacement and module-boundary success anchor coverage derives from one same-file success-owner lane instead of two standalone hard-coded anchor test bodies.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines either of these singleton anchor tests:
  - `test_compiled_pattern_module_collection_replacement_success_rows_stay_anchored_to_published_correctness_cases`
  - `test_compiled_pattern_module_boundary_verbose_bytes_success_rows_stay_anchored_to_published_correctness_cases`
- Replace that split with one explicit same-file success-anchor carrier, or a strictly smaller equivalent, reused by a shared success-anchor pytest body:
  - keep it file-local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`;
  - route through `CompiledPatternModuleSuccessOwnerSpec`, or an equivalently small adjacent frozen carrier, instead of introducing a new support module, registry file, or generated artifact; and
  - keep the existing success manifest/probe/precompile tests on the current owner-spec lane rather than forking a second detached contract path.
- Keep the collection/replacement success anchor contract intact after the cleanup:
  - the contract filename still stays `python_benchmark_compiled_pattern_collection_replacement_success_anchor_contract.py`;
  - the anchored workload ids still stay exactly, in order:
    - `module-split-literal-warm-str-compiled-pattern-contract`
    - `module-findall-literal-purged-bytes-compiled-pattern-contract`
    - `module-finditer-literal-warm-str-compiled-pattern-contract`
    - `module-sub-literal-warm-str-compiled-pattern-contract`
    - `module-subn-literal-purged-bytes-compiled-pattern-contract`
  - the anchored correctness case ids still stay exactly, in order:
    - `workflow-module-split-str-compiled-pattern`
    - `workflow-module-findall-bytes-compiled-pattern`
    - `workflow-module-finditer-str-compiled-pattern`
    - `workflow-module-sub-str-compiled-pattern`
    - `workflow-module-subn-bytes-compiled-pattern`
- Keep the module-boundary verbose-bytes success anchor contract intact after the cleanup:
  - the contract filename still stays `python_benchmark_compiled_pattern_module_boundary_verbose_bytes_contract.py`;
  - the anchored workload ids still stay exactly, in order:
    - `module-search-verbose-regression-warm-hit-bytes-compiled-pattern-contract`
    - `module-fullmatch-verbose-regression-purged-hit-bytes-compiled-pattern-contract`
  - the anchored correctness case ids still stay exactly, in order:
    - `workflow-module-search-bytes-verbose-regression-compiled-pattern`
    - `workflow-module-fullmatch-bytes-verbose-regression-compiled-pattern`
- Preserve the current compiled-pattern success owner surfaces exactly after the cleanup:
  - `_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC` still resolves the same five source workloads in the same order;
  - `_COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC` still resolves the same eight source workloads in the same order;
  - `test_standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_rows_until_helper_invocation` still covers both owner specs;
  - `test_run_internal_workload_probe_measures_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_workloads` still covers both owner specs; and
  - `test_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_callbacks_precompile_first_argument_before_timing` still covers both owner specs.
- Keep the cleanup structural only:
  - do not widen into `STANDARD_BENCHMARK_ANCHOR_CONTRACT_DEFINITIONS`, the compiled-pattern `module.compile` success/keyword contract family, wrong-text-model owner specs, workload manifests under `benchmarks/workloads/`, harness code under `python/rebar_harness/`, implementation code, reports, or tracked state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_rows_until_helper_invocation or compiled_pattern_module_collection_replacement_success_rows_stay_anchored_to_published_correctness_cases or compiled_pattern_module_boundary_verbose_bytes_success_rows_stay_anchored_to_published_correctness_cases or run_internal_workload_probe_measures_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_workloads or compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_callbacks_precompile_first_argument_before_timing'`
- `bash -lc \"! rg -n '^def test_compiled_pattern_module_collection_replacement_success_rows_stay_anchored_to_published_correctness_cases\\(|^def test_compiled_pattern_module_boundary_verbose_bytes_success_rows_stay_anchored_to_published_correctness_cases\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py\"`

## Constraints
- Keep the change limited to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Prefer deleting the standalone anchor-test plumbing over adding another detached id-keyed helper layer.
- Preserve the current anchored workload ids, correctness case ids, manifest filenames, source workload ordering, and owner-spec semantics exactly.

## Notes
- `RBR-1066` is the next available unreserved architecture-task id in this checkout:
  - `ops/tasks/ready/` currently contains only the feature task `RBR-1065-publish-pattern-subn-str-single-match.md`; and
  - `rg -n 'RBR-1066|RBR-1067|RBR-1068' ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked` returned only a historical note inside `ops/tasks/done/RBR-1064-collapse-direct-literal-replacement-surface-case-tables.md`, not a live reservation or task file for those ids.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-ready-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest runtime cycle shows both task workers finishing `done`, with no inherited-dirty checkpoint churn or stalled post-task refresh path.
- The singleton target is concrete in the live checkout:
  - `CompiledPatternModuleSuccessOwnerSpec` already owns the shared success contract path at line `16387`;
  - the remaining collection/replacement-only success anchor test still sits at line `16767`; and
  - the remaining module-boundary verbose-bytes success anchor test still sits at line `17603`.
- The focused benchmark slice already passes in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_rows_until_helper_invocation or compiled_pattern_module_collection_replacement_success_rows_stay_anchored_to_published_correctness_cases or compiled_pattern_module_boundary_verbose_bytes_success_rows_stay_anchored_to_published_correctness_cases or run_internal_workload_probe_measures_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_workloads or compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_callbacks_precompile_first_argument_before_timing'` returned `43 passed, 680 deselected` in this run.

## Completion Note
- Replaced the two one-off compiled-pattern success anchor tests with one file-local `_CompiledPatternModuleSuccessAnchorSpec` carrier plus a shared parametrized anchor test, while keeping the existing `CompiledPatternModuleSuccessOwnerSpec` lane for the manifest, probe, and precompile contract coverage.
- Preserved the anchored contract filenames, workload ids, correctness case ids, and the owner-spec source workload ordering exactly for the collection/replacement and module-boundary verbose-bytes slices.
- Verified with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_rows_until_helper_invocation or compiled_pattern_module_success_rows_stay_anchored_to_published_correctness_cases or run_internal_workload_probe_measures_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_workloads or compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_callbacks_precompile_first_argument_before_timing'` -> `43 passed, 680 deselected`
  - `bash -lc "! rg -n '^def test_compiled_pattern_module_collection_replacement_success_rows_stay_anchored_to_published_correctness_cases\\(|^def test_compiled_pattern_module_boundary_verbose_bytes_success_rows_stay_anchored_to_published_correctness_cases\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` -> success
