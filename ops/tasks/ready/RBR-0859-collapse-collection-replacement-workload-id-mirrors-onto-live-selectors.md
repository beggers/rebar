# RBR-0859: Collapse collection-replacement workload-id mirrors onto live selectors

Status: ready
Owner: architecture-implementation
Created: 2026-03-21

## Goal
- Remove the remaining collection-replacement workload-id mirror frozensets from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` where the live benchmark rows already carry enough structure to identify the same positional-indexlike and keyword slices.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` stops defining or reading these detached workload-id mirrors:
  - `COLLECTION_REPLACEMENT_POSITIONAL_INDEXLIKE_WORKLOAD_IDS`
  - `COLLECTION_REPLACEMENT_KEYWORD_WORKLOAD_IDS`
- The existing collection-replacement selectors and signature helpers derive the same bounded slices directly from live workload structure instead of top-level workload-id tables:
  - `_is_collection_replacement_positional_indexlike_workload(...)`
  - `_collection_replacement_positional_indexlike_workload_signature(...)`
  - `_is_collection_replacement_keyword_workload(...)`
  - `_collection_replacement_keyword_workload_signature(...)`
- Keep the collection-replacement measured-row coverage unchanged while deleting those mirrors:
  - `test_collection_replacement_manifest_keeps_positional_indexlike_module_and_pattern_rows_measured`
  - `test_collection_replacement_manifest_keeps_pattern_keyword_replacement_and_split_rows_measured`
  - `test_collection_replacement_manifest_keeps_module_keyword_replacement_and_split_rows_measured`
  These assertions should source their expected ordered workload ids from `source_tree_combined_case("collection-replacement-boundary").target_manifest.workloads` through the shared live selectors plus operation filters, not through handwritten tuple literals.
- Preserve the current collection-replacement boundary exactly after the refactor:
  - keep the positional-indexlike slice ordered as the current six workload ids;
  - keep the pattern-keyword slice ordered as the current nine workload ids;
  - keep the module-keyword slice ordered as the current twenty-seven workload ids; and
  - keep the current anchor-contract expectations, correctness-case signature matching, helper-call callback parity checks, and zero-gap manifest counts behaviorally unchanged.
- Do not broaden scope beyond this mirror deletion:
  - do not change benchmark manifests, harness modules, reports, fixture-support helpers, README copy, or tracked project-state prose; and
  - do not retune any collection-replacement workload payloads, keyword-descriptor semantics, compiled-pattern routing, or published benchmark counts in this run.
- Verification passes with:
  - `./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement and (indexlike or keyword)'`
  - `bash -lc "! rg -n '^(COLLECTION_REPLACEMENT_POSITIONAL_INDEXLIKE_WORKLOAD_IDS|COLLECTION_REPLACEMENT_KEYWORD_WORKLOAD_IDS) =' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
import tests.benchmarks.test_source_tree_combined_boundary_benchmarks as mod

manifest = mod.source_tree_combined_case("collection-replacement-boundary").target_manifest
positional_ids = tuple(
    workload.workload_id
    for workload in manifest.workloads
    if mod._is_collection_replacement_positional_indexlike_workload(workload)
)
keyword_pattern_ids = tuple(
    workload.workload_id
    for workload in manifest.workloads
    if mod._is_collection_replacement_keyword_workload(workload)
    and workload.operation.startswith("pattern.")
)
keyword_module_ids = tuple(
    workload.workload_id
    for workload in manifest.workloads
    if mod._is_collection_replacement_keyword_workload(workload)
    and workload.operation.startswith("module.")
)

assert positional_ids == (
    "module-split-maxsplit-indexlike-positional-purged-bytes",
    "module-sub-count-indexlike-positional-warm-str",
    "module-subn-count-indexlike-positional-purged-bytes",
    "pattern-split-maxsplit-indexlike-positional-warm-str",
    "pattern-sub-count-indexlike-positional-purged-bytes",
    "pattern-subn-count-indexlike-positional-warm-str",
)
assert keyword_pattern_ids == (
    "pattern-split-maxsplit-keyword-warm-str",
    "pattern-split-maxsplit-bool-keyword-warm-str",
    "pattern-split-maxsplit-indexlike-keyword-warm-str",
    "pattern-sub-count-keyword-purged-bytes",
    "pattern-sub-count-bool-keyword-purged-bytes",
    "pattern-sub-count-indexlike-keyword-purged-bytes",
    "pattern-subn-count-keyword-warm-str",
    "pattern-subn-count-bool-keyword-warm-str",
    "pattern-subn-count-indexlike-keyword-warm-str",
)
assert keyword_module_ids == (
    "module-split-maxsplit-keyword-purged-bytes",
    "module-split-maxsplit-bool-keyword-purged-bytes",
    "module-split-maxsplit-indexlike-keyword-purged-bytes",
    "module-split-maxsplit-keyword-purged-str-compiled-pattern",
    "module-split-maxsplit-indexlike-keyword-purged-bytes-compiled-pattern",
    "module-split-maxsplit-bool-keyword-purged-bytes-compiled-pattern",
    "module-split-duplicate-maxsplit-keyword-purged-str",
    "module-split-duplicate-maxsplit-keyword-purged-str-compiled-pattern",
    "module-split-unexpected-keyword-purged-bytes-compiled-pattern",
    "module-sub-count-keyword-warm-str",
    "module-sub-count-bool-keyword-warm-str",
    "module-sub-count-indexlike-keyword-warm-str",
    "module-sub-count-keyword-warm-str-compiled-pattern",
    "module-sub-count-indexlike-keyword-warm-bytes-compiled-pattern",
    "module-sub-count-bool-keyword-warm-str-compiled-pattern",
    "module-sub-duplicate-count-keyword-warm-str",
    "module-sub-unexpected-keyword-purged-str",
    "module-sub-duplicate-count-keyword-warm-str-compiled-pattern",
    "module-sub-unexpected-keyword-purged-str-compiled-pattern",
    "module-subn-count-keyword-purged-bytes",
    "module-subn-count-bool-keyword-purged-bytes",
    "module-subn-count-indexlike-keyword-purged-bytes",
    "module-subn-count-keyword-purged-bytes-compiled-pattern",
    "module-subn-count-indexlike-keyword-purged-str-compiled-pattern",
    "module-subn-count-bool-keyword-purged-bytes-compiled-pattern",
    "module-subn-duplicate-count-keyword-warm-bytes-compiled-pattern",
    "module-subn-unexpected-keyword-purged-bytes-compiled-pattern",
)
print("ok")
PY`

## Constraints
- Keep this cleanup structural only. The point is to delete the duplicated collection-replacement workload-id tables inside the combined benchmark test owner, not to reinterpret keyword/indexlike semantics or reshape the benchmark frontier.
- Keep scope limited to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.

## Notes
- `RBR-0859` is the next available architecture task id in the current checkout:
  - `RBR-0858` is already occupied by the ready feature task in `ops/tasks/ready/`; and
  - `ops/state/backlog.md` plus `ops/state/current_status.md` do not reserve `RBR-0859`.
- No blocked architecture task exists to reopen first, and the queue/runtime state does not trigger the queue-stall no-op rule:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete and bounded in the current checkout:
  - `./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement and (indexlike or keyword)'` currently passes (`42 passed, 275 deselected in 0.44s`);
  - the task-local probe in Acceptance already passes in the current checkout (`ok`), confirming the live collection-replacement manifest rows can still be pinned to the current positional, pattern-keyword, and module-keyword workload order after this cleanup; and
  - `bash -lc "! rg -n '^(COLLECTION_REPLACEMENT_POSITIONAL_INDEXLIKE_WORKLOAD_IDS|COLLECTION_REPLACEMENT_KEYWORD_WORKLOAD_IDS) =' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` currently fails exactly on this cleanup because those mirrored frozensets still exist.
- This stays on the same post-JSON benchmark-harness simplification track as the recent mirror removals instead of opening a new architecture lane:
  - `RBR-0851` already collapsed counted-repeat selected-case-id sidecars onto live bundles;
  - `RBR-0853` already collapsed module-workflow raw keyword-error sidecars onto live fixture categories; and
  - `RBR-0857` already removed the remaining replacement-suite case-id mirrors from the fixture-backed parity owner.
