# RBR-0863: Collapse module-workflow keyword workload-id mirrors onto live selectors

Status: done
Owner: architecture-implementation
Created: 2026-03-21

## Goal
- Remove the remaining module-workflow keyword workload-id mirror frozensets from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` where the live `module-boundary` rows already carry enough structure to identify the same bounded keyword-flags and keyword-error slices.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` stops defining or reading these detached workload-id mirrors:
  - `MODULE_WORKFLOW_KEYWORD_FLAGS_WORKLOAD_IDS`
  - `MODULE_WORKFLOW_KEYWORD_ERROR_WORKLOAD_IDS`
  - `MODULE_WORKFLOW_KEYWORD_WORKLOAD_IDS`
- The existing module-workflow keyword helpers derive the same bounded slices directly from live workload structure instead of top-level workload-id frozensets:
  - `_is_module_workflow_keyword_flags_workload(...)`
  - `_is_module_workflow_keyword_error_workload(...)`
  - `_module_workflow_keyword_workload_args(...)`
  - `_module_workflow_keyword_workload_signature(...)`
- Keep the current module-boundary keyword slice unchanged while deleting those mirrors:
  - the keyword-flags selector must still resolve, in manifest order, to `module-search-flags-keyword-warm-str`, `module-match-flags-keyword-purged-bytes`, and `module-fullmatch-flags-keyword-warm-str`;
  - the keyword-error selector must still resolve, in manifest order, to `module-search-duplicate-flags-keyword-warm-str` and `module-fullmatch-unexpected-keyword-purged-str`; and
  - the current standard anchor-contract expectations, callback-result parity checks, and zero-gap manifest counts for the `module-workflow-keyword-flags` and `module-workflow-keyword-errors` definitions must stay behaviorally unchanged.
- Do not broaden scope beyond this mirror deletion:
  - do not change benchmark manifests, correctness fixtures, harness modules, reports, README copy, or tracked project-state prose; and
  - do not widen into adjacent module keyword rows for `split`, `sub`, `subn`, compiled-pattern-first-argument carriers, or other keyword-error families in this run.
- Verification passes with:
  - `./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'module-workflow-keyword-flags or module-workflow-keyword-errors'`
  - `bash -lc "! rg -n '^(MODULE_WORKFLOW_KEYWORD_FLAGS_WORKLOAD_IDS|MODULE_WORKFLOW_KEYWORD_ERROR_WORKLOAD_IDS|MODULE_WORKFLOW_KEYWORD_WORKLOAD_IDS) =' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
import tests.benchmarks.test_source_tree_combined_boundary_benchmarks as mod

manifest = mod.source_tree_combined_case("module-boundary").target_manifest
flags_ids = tuple(
    workload.workload_id
    for workload in manifest.workloads
    if (
        workload.operation in {"module.search", "module.match", "module.fullmatch"}
        and bool(workload.kwargs)
        and "flags" in workload.kwargs
        and workload.expected_exception is None
        and not workload.use_compiled_pattern
    )
)
error_ids = tuple(
    workload.workload_id
    for workload in manifest.workloads
    if (
        workload.operation in {"module.search", "module.match", "module.fullmatch"}
        and bool(workload.kwargs)
        and workload.expected_exception is not None
        and workload.expected_exception.get("type") == "TypeError"
        and not workload.use_compiled_pattern
        and (
            (
                "flags" in workload.kwargs
                and "multiple values for argument"
                in workload.expected_exception.get("message_substring", "")
            )
            or (
                "missing" in workload.kwargs
                and "unexpected keyword argument"
                in workload.expected_exception.get("message_substring", "")
            )
        )
    )
)

assert flags_ids == (
    "module-search-flags-keyword-warm-str",
    "module-match-flags-keyword-purged-bytes",
    "module-fullmatch-flags-keyword-warm-str",
)
assert error_ids == (
    "module-search-duplicate-flags-keyword-warm-str",
    "module-fullmatch-unexpected-keyword-purged-str",
)
print("ok")
PY`

## Constraints
- Keep this cleanup structural only. The point is to delete the duplicated module-workflow keyword workload-id frozensets inside the combined benchmark test owner, not to reinterpret keyword semantics, reorder the manifest, or open another benchmark-helper layer.
- Keep scope limited to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.

## Notes
- `RBR-0863` is the next available architecture task id in the current checkout:
  - `RBR-0862` is already occupied by the ready feature task in `ops/tasks/ready/`; and
  - `ops/state/backlog.md` plus `ops/state/current_status.md` do not reserve `RBR-0863`.
- No blocked architecture task exists to reopen first, and the queue/runtime state does not trigger the queue-stall no-op rule:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete and bounded in the current checkout:
  - `./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'module-workflow-keyword-flags or module-workflow-keyword-errors'` currently passes (`7 passed, 335 deselected in 0.13s`);
  - the task-local selector-order probe in Acceptance already passes in the current checkout (`ok`), confirming that the live `module-boundary` rows already expose the same five keyword workloads without the top-level frozensets; and
  - `bash -lc "! rg -n '^(MODULE_WORKFLOW_KEYWORD_FLAGS_WORKLOAD_IDS|MODULE_WORKFLOW_KEYWORD_ERROR_WORKLOAD_IDS|MODULE_WORKFLOW_KEYWORD_WORKLOAD_IDS) =' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` currently fails exactly on this cleanup because those mirrored frozensets still exist.
- This stays on the same post-JSON benchmark-harness simplification track as the adjacent mirror removals in the same owner file:
  - `RBR-0859` already collapsed the collection-replacement keyword and positional workload-id mirrors onto live selectors; and
  - `RBR-0861` already removed the remaining pattern-boundary window workload-id mirrors from the same benchmark owner.

## Completion
- Replaced the module-workflow keyword workload-id mirrors with live structural selectors in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Kept the shared keyword workload-signature path bounded to the same five `module-boundary` rows by deriving the flags and TypeError slices from operation, kwargs, exception metadata, and compiled-pattern state instead of top-level frozensets.
- Verified with:
  - `./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'module-workflow-keyword-flags or module-workflow-keyword-errors'`
  - `bash -lc "! rg -n '^(MODULE_WORKFLOW_KEYWORD_FLAGS_WORKLOAD_IDS|MODULE_WORKFLOW_KEYWORD_ERROR_WORKLOAD_IDS|MODULE_WORKFLOW_KEYWORD_WORKLOAD_IDS) =' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
  - the task-local selector-order probe from the acceptance criteria (`ok`)
