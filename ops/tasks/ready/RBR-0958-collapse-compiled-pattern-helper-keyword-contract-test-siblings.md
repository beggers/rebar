# RBR-0958: Collapse compiled-pattern helper keyword contract test siblings

Status: ready
Owner: architecture-implementation
Created: 2026-03-22

## Goal
- Remove the remaining paired success-versus-keyword-error test stacks from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the compiled-pattern collection/replacement keyword contract runs through one shared file-local spec-driven manifest/probe/precompile test surface instead of maintaining two near-identical manifest-preservation, internal-probe, and precompile-first callback test bodies.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines or relies on these paired duplicate test bodies:
  - `test_standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_keyword_rows_until_helper_invocation(...)`
  - `test_standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_keyword_error_rows_until_helper_invocation(...)`
  - `test_run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_workloads(...)`
  - `test_run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_error_workloads(...)`
  - `test_compiled_pattern_module_helper_keyword_callbacks_precompile_first_argument_before_timing(...)`
  - `test_compiled_pattern_module_helper_callbacks_precompile_first_argument_before_timing(...)`
- Replace those paired test bodies with one explicit but smaller shared file-local contract-test surface:
  - it may extend `_CompiledPatternModuleHelperKeywordContractSpec` or add a tiny adjacent frozen helper spec;
  - keep the cleanup local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`;
  - preserve `_compiled_pattern_module_helper_keyword_source_workloads()`, `_compiled_pattern_module_helper_keyword_precompile_anchor_source_workloads()`, and `_compiled_pattern_module_helper_keyword_error_source_workloads()` as the live selector entry points unless a tiny file-local successor preserves the same verification surface; and
  - do not add a shared helper module, registry, or checked-in data layer.
- Preserve the current bounded source-workload surfaces exactly:
  - the success selector still resolves, in order, to:
    - `module-split-maxsplit-keyword-purged-str-compiled-pattern`
    - `module-split-maxsplit-indexlike-keyword-purged-bytes-compiled-pattern`
    - `module-split-maxsplit-bool-keyword-purged-bytes-compiled-pattern`
    - `module-sub-count-keyword-warm-str-compiled-pattern`
    - `module-sub-count-indexlike-keyword-warm-bytes-compiled-pattern`
    - `module-sub-count-bool-keyword-warm-str-compiled-pattern`
    - `module-sub-count-bool-false-keyword-warm-str-compiled-pattern`
    - `module-subn-count-keyword-purged-bytes-compiled-pattern`
    - `module-subn-count-indexlike-keyword-purged-str-compiled-pattern`
    - `module-subn-count-bool-keyword-purged-bytes-compiled-pattern`
    - `module-subn-count-bool-true-keyword-purged-bytes-compiled-pattern`
  - the keyword-error selector still resolves, in order, to:
    - `module-split-duplicate-maxsplit-keyword-purged-str-compiled-pattern`
    - `module-split-unexpected-keyword-purged-bytes-compiled-pattern`
    - `module-sub-duplicate-count-keyword-warm-str-compiled-pattern`
    - `module-sub-unexpected-keyword-purged-str-compiled-pattern`
    - `module-sub-unexpected-keyword-after-positional-count-purged-str-compiled-pattern`
    - `module-sub-count-alias-keyword-purged-str-compiled-pattern`
    - `module-subn-duplicate-count-keyword-warm-bytes-compiled-pattern`
    - `module-subn-unexpected-keyword-purged-bytes-compiled-pattern`
    - `module-subn-unexpected-keyword-after-positional-count-purged-bytes-compiled-pattern`
    - `module-subn-count-alias-keyword-purged-bytes-compiled-pattern`
  - the success precompile-anchor selector still resolves, in order, to:
    - `module-split-maxsplit-keyword-purged-str-compiled-pattern`
    - `module-sub-count-keyword-warm-str-compiled-pattern`
    - `module-subn-count-keyword-purged-bytes-compiled-pattern`
  - both contract surfaces still use manifest id `collection-replacement-boundary`;
  - both generated contract surfaces still append `-contract` to the live source workload ids in the same order; and
  - both contract surfaces still keep `use_compiled_pattern is True` and `haystack_text_model is None`.
- The shared contract-test surface must preserve the current success-versus-keyword-error semantic split instead of flattening behavior:
  - success manifest rows still compare against `run_benchmark_workload_with_cpython(source_workload)`, still drop `expected_exception`, and still use `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC`;
  - keyword-error manifest rows still preserve `expected_exception`, still compare exact `TypeError` text against `_run_cpython_compiled_pattern_module_helper_keyword_workload(workload)` plus `run_benchmark_workload_with_cpython(round_tripped)`, and still use `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC`;
  - the shared internal-probe surface still measures both adapters on every success and keyword-error contract row and still requires `probe["status"] == "measured"` plus `probe["median_ns"] > 0`;
  - the success precompile-first callback path still covers only the three anchor rows from `_compiled_pattern_module_helper_keyword_precompile_anchor_source_workloads()`;
  - the keyword-error precompile-first callback path still covers all ten keyword-error rows from `_compiled_pattern_module_helper_keyword_error_source_workloads()`; and
  - both callback paths still prove the same precompile-first contract through `_compiled_pattern_module_helper_contract_expected_build_calls(...)`, `_compiled_pattern_module_helper_contract_expected_callback_call(...)`, and `_compiled_pattern_module_helper_contract_expected_callback_result(...)`.
- Keep the remaining keyword-only behavior coverage explicit:
  - `test_compiled_pattern_module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time(...)` stays present or is replaced by an equivalent targeted assertion that still proves success rows materialize only the expected keyword fields at callback time;
  - `test_compiled_pattern_module_helper_keyword_error_callbacks_match_cpython_exceptions(...)` stays present or is replaced by an equivalent targeted assertion that still proves keyword-error rows match exact CPython `TypeError` text and materialize the expected numeric fields at callback time; and
  - do not broaden into the surrounding wrong-text-model, success-owner, compile-contract, or validation sections except for minimal mechanical renames needed to keep the shared helper-keyword contract tests wired up.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_collection_replacement_keyword or compiled_pattern_module_helper_keyword or compiled_pattern_module_helper_callbacks_precompile_first_argument_before_timing'`
- `bash -lc "! rg -n 'test_standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_keyword_rows_until_helper_invocation|test_standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_keyword_error_rows_until_helper_invocation|test_run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_workloads|test_run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_error_workloads|test_compiled_pattern_module_helper_keyword_callbacks_precompile_first_argument_before_timing|test_compiled_pattern_module_helper_callbacks_precompile_first_argument_before_timing' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from tests.benchmarks.test_source_tree_combined_boundary_benchmarks import (
    _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC,
    _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC,
    _compiled_pattern_module_helper_keyword_error_source_workloads,
    _compiled_pattern_module_helper_keyword_precompile_anchor_source_workloads,
    _compiled_pattern_module_helper_keyword_source_workloads,
)

keyword_ids = tuple(
    workload.workload_id
    for workload in _compiled_pattern_module_helper_keyword_source_workloads()
)
error_ids = tuple(
    workload.workload_id
    for workload in _compiled_pattern_module_helper_keyword_error_source_workloads()
)
anchor_ids = tuple(
    workload.workload_id
    for workload in _compiled_pattern_module_helper_keyword_precompile_anchor_source_workloads()
)

assert keyword_ids == _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC.expected_source_workload_ids
assert error_ids == _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC.expected_source_workload_ids
assert anchor_ids == _COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC.precompile_anchor_ids

print("ok", len(keyword_ids), len(error_ids), len(anchor_ids))
PY`

## Constraints
- Keep the cleanup structural and file-local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Do not edit `benchmarks/workloads/collection_replacement_boundary.py`, `python/rebar_harness/benchmarks.py`, reports, README/current-status/backlog prose, or non-benchmark test files in this run.
- Prefer deleting duplicate test plumbing over introducing another detached representation layer.

## Notes
- `RBR-0958` is the next available task id in the current checkout:
  - `rg -n 'RBR-0958|RBR-0959|RBR-0960|RBR-0961|RBR-0962' ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` returned no reserved frontier match in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 12` currently ends at `RBR-0957-catch-up-compiled-pattern-module-replacement-count-alias-keyword-boundary-pair.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_collection_replacement_keyword or compiled_pattern_module_helper_keyword or compiled_pattern_module_helper_callbacks_precompile_first_argument_before_timing'` currently passes (`69 passed, 563 deselected, 10 subtests passed`);
  - the selector probe in Verification currently passes (`ok 11 10 3`), proving the success, keyword-error, and success-precompile-anchor surfaces already exist directly on the live manifest-selected path; and
  - the `rg -n` pattern in Verification currently finds the six paired duplicate test bodies named in this task, which is the exact cleanup this task queues.
