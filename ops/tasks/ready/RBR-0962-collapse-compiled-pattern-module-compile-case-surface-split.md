# RBR-0962: Collapse compiled-pattern module.compile case surface split

Status: ready
Owner: architecture-implementation
Created: 2026-03-22

## Goal
- Remove the remaining success-versus-keyword type split inside the shared compiled-pattern-first-argument `module.compile` benchmark contract section of `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so that one file-local compile-contract case surface owns the entire manifest/workload/anchor/probe/callback pipeline instead of carrying two overlapping dataclass APIs plus union-typed helpers.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines or relies on a second compile-contract case type for the keyword rows:
  - remove `class CompiledPatternModuleCompileKeywordCaseGroup`;
  - keep `_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_CONTRACT_CASE` and `COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_CASE_GROUPS`, but make them instances of one shared file-local compile-contract case surface; and
  - remove `_compiled_pattern_module_compile_keyword_params()` if it only exists to bridge the split case types.
- The shared compile-contract helpers no longer carry success-versus-keyword union typing:
  - `_compiled_pattern_module_compile_contract_manifest_payload(...)`
  - `_compiled_pattern_module_compile_contract_workload(...)`
  - `_compiled_pattern_module_compile_contract_manifest(...)`
  - `test_standard_benchmark_manifest_preserves_compiled_pattern_module_compile_success_and_keyword_contract_rows_until_helper_invocation(...)`
  - `test_compiled_pattern_module_compile_success_and_keyword_contract_rows_stay_anchored_to_published_correctness_cases(...)`
  - `test_run_internal_workload_probe_measures_compiled_pattern_module_compile_success_and_keyword_contract_workloads(...)`
  - `test_compiled_pattern_module_compile_success_and_keyword_contract_callbacks_precompile_first_argument_before_timing(...)`
  all accept one compile-contract case type without `CompiledPatternModuleCompileContractCase | ...` unions.
- Preserve the current bounded compile-success source surface exactly:
  - `module-compile-literal-warm-str-compiled-pattern`
  - `module-compile-literal-purged-bytes-compiled-pattern`
  - `module-compile-named-group-warm-str-compiled-pattern`
  - `module-compile-named-group-purged-bytes-compiled-pattern`
- Preserve the current bounded compile-keyword case-group surfaces exactly and in the same order on `COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_CASE_GROUPS`:
  - `int-zero`
    - `module-compile-flags-int-zero-warm-str-compiled-pattern`
    - `module-compile-flags-int-zero-purged-bytes-compiled-pattern`
  - `int-zero-named-group`
    - `module-compile-flags-int-zero-warm-str-compiled-pattern-named-group`
    - `module-compile-flags-int-zero-purged-bytes-compiled-pattern-named-group`
  - `bool-false`
    - `module-compile-flags-bool-false-warm-str-compiled-pattern`
    - `module-compile-flags-bool-false-purged-bytes-compiled-pattern`
  - `bool-false-named-group`
    - `module-compile-flags-bool-false-warm-str-compiled-pattern-named-group`
    - `module-compile-flags-bool-false-purged-bytes-compiled-pattern-named-group`
  - `ignorecase`
    - `module-compile-flags-ignorecase-warm-str-compiled-pattern`
    - `module-compile-flags-ignorecase-purged-bytes-compiled-pattern`
  - `ignorecase-named-group`
    - `module-compile-flags-ignorecase-warm-str-compiled-pattern-named-group`
    - `module-compile-flags-ignorecase-purged-bytes-compiled-pattern-named-group`
- Preserve the current ordered combined contract frontier on `_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES`:
  - success
  - int-zero
  - int-zero-named-group
  - bool-false
  - bool-false-named-group
  - ignorecase
  - ignorecase-named-group
- The unified compile-contract case surface must preserve the current success-versus-keyword semantic split instead of flattening behavior:
  - success rows still compare against `re.compile(compiled_pattern, workload.flags)`;
  - keyword rows still compare against `re.compile(compiled_pattern, **workload.keyword_arguments())`;
  - ignorecase keyword rows still preserve the same `TypeError` type and exact message-substring matching;
  - both success and keyword rows still keep `use_compiled_pattern is True`, `timing_scope == "module-helper-call"`, and `haystack_text_model is None`;
  - warm rows still build exactly `[("compile", pattern, flags)]`;
  - purged rows still build exactly `[("compile", pattern, flags), ("purge",)]`; and
  - the callback path still makes the final recorded `compile` call against the precompiled pattern object, passing positional `flags` for success rows and keyword-carrier `flags` values for keyword rows.
- Keep the remaining keyword-only coverage explicit:
  - `test_compiled_pattern_module_compile_keyword_kwargs_materialize_at_callback_time(...)` stays present or is replaced by an equivalent focused assertion that still proves `kwargs.flags` is the only numeric field materialized at callback time; and
  - `test_standard_benchmark_compiled_pattern_module_compile_validation_accepts_bounded_ignorecase_rejection_rows(...)` stays green without broadening the cleanup into surrounding validation/reporting code.
- Keep the cleanup file-local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`; do not add a shared helper module, registry, or checked-in data layer.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_compile_success_and_keyword_contract or compiled_pattern_module_compile_keyword_kwargs_materialize_at_callback_time or compiled_pattern_module_compile_validation_accepts_bounded_ignorecase_rejection_rows'`
- `bash -lc "! rg -n 'class CompiledPatternModuleCompileKeywordCaseGroup|def _compiled_pattern_module_compile_keyword_params\\(|CompiledPatternModuleCompileContractCase\\s*\\|\\s*CompiledPatternModuleCompileKeywordCaseGroup' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -U"`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from tests.benchmarks.test_source_tree_combined_boundary_benchmarks import (
    COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_CASE_GROUPS,
    CompiledPatternModuleCompileContractCase,
    _COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_CONTRACT_CASE,
)

assert isinstance(
    _COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_CONTRACT_CASE,
    CompiledPatternModuleCompileContractCase,
)
assert all(
    isinstance(case, CompiledPatternModuleCompileContractCase)
    for case in COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_CASE_GROUPS
)

print(
    "ok",
    _COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_CONTRACT_CASE.case_id,
    tuple(case.case_id for case in COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_CASE_GROUPS),
)
PY`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from tests.benchmarks.test_source_tree_combined_boundary_benchmarks import (
    COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_CASE_GROUPS,
    _COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_CONTRACT_CASE,
)

success_ids = tuple(
    workload.workload_id
    for workload in _COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_CONTRACT_CASE.source_workloads()
)
keyword_group_ids = {
    case.case_id: tuple(workload.workload_id for workload in case.source_workloads())
    for case in COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_CASE_GROUPS
}

assert success_ids == (
    "module-compile-literal-warm-str-compiled-pattern",
    "module-compile-literal-purged-bytes-compiled-pattern",
    "module-compile-named-group-warm-str-compiled-pattern",
    "module-compile-named-group-purged-bytes-compiled-pattern",
)
assert keyword_group_ids == {
    "int-zero": (
        "module-compile-flags-int-zero-warm-str-compiled-pattern",
        "module-compile-flags-int-zero-purged-bytes-compiled-pattern",
    ),
    "int-zero-named-group": (
        "module-compile-flags-int-zero-warm-str-compiled-pattern-named-group",
        "module-compile-flags-int-zero-purged-bytes-compiled-pattern-named-group",
    ),
    "bool-false": (
        "module-compile-flags-bool-false-warm-str-compiled-pattern",
        "module-compile-flags-bool-false-purged-bytes-compiled-pattern",
    ),
    "bool-false-named-group": (
        "module-compile-flags-bool-false-warm-str-compiled-pattern-named-group",
        "module-compile-flags-bool-false-purged-bytes-compiled-pattern-named-group",
    ),
    "ignorecase": (
        "module-compile-flags-ignorecase-warm-str-compiled-pattern",
        "module-compile-flags-ignorecase-purged-bytes-compiled-pattern",
    ),
    "ignorecase-named-group": (
        "module-compile-flags-ignorecase-warm-str-compiled-pattern-named-group",
        "module-compile-flags-ignorecase-purged-bytes-compiled-pattern-named-group",
    ),
}

print("ok", len(success_ids), len(keyword_group_ids))
PY`

## Constraints
- Keep the cleanup structural and file-local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Do not edit `benchmarks/workloads/module_boundary.py`, `python/rebar_harness/benchmarks.py`, reports, README/current-status/backlog prose, or non-benchmark test files in this run.
- Prefer deleting the leftover split case surface over adding another detached representation layer.

## Notes
- `RBR-0962` is the next available task id in the current checkout:
  - `rg -n 'RBR-0962|RBR-0963|RBR-0964|RBR-0965|RBR-0966' ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` returned no reserved frontier match in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 12` currently ends at `RBR-0961-catch-up-pattern-replacement-count-alias-keyword-boundary-pair.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- This is a bounded follow-on to `RBR-0956`, not a duplicate of it:
  - `RBR-0956` already collapsed the duplicated compile-success versus compile-keyword helper/test stacks;
  - the live checkout still carries two overlapping compile-case dataclass APIs plus union-typed helper signatures in the same shared contract section; and
  - this task only removes that leftover split surface without reopening the already-merged helper/test families.
- The duplication target is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_compile_success_and_keyword_contract or compiled_pattern_module_compile_keyword_kwargs_materialize_at_callback_time or compiled_pattern_module_compile_validation_accepts_bounded_ignorecase_rejection_rows'` currently passes (`77 passed, 577 deselected`);
  - the source-surface probe in Verification currently passes (`ok 4 6`), proving the success rows plus the six keyword case groups already exist directly on the tracked manifest-selected workload path; and
  - the structural `rg` check plus unified-type probe in Verification currently fail only because `CompiledPatternModuleCompileKeywordCaseGroup`, `_compiled_pattern_module_compile_keyword_params()`, and the remaining split compile-case surface are still present in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
