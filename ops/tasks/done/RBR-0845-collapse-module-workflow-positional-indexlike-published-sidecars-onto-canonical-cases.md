# RBR-0845: Collapse module-workflow positional-indexlike published sidecars onto canonical cases

Status: done
Owner: architecture-implementation
Created: 2026-03-21
Completed: 2026-03-21

## Goal
- Remove the detached published positional-indexlike subset tables from `tests/python/test_module_workflow_parity_suite.py` so the canonical module/pattern fixture-case owners and direct-call case owners remain the only sources of truth for this bounded module-workflow slice.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` stops defining or reading these detached published subset tables:
  - `PUBLISHED_MODULE_POSITIONAL_INDEXLIKE_MODULE_HELPER_CASES`
  - `PUBLISHED_PATTERN_POSITIONAL_INDEXLIKE_PATTERN_CASES`
- The affected direct-case alignment tests derive their fixture-row subsets from canonical owner data instead of from those deleted top-level tables:
  - `test_module_workflow_surface_publishes_module_positional_indexlike_slice_from_direct_cases`
  - `test_module_workflow_surface_publishes_pattern_positional_indexlike_slice_from_direct_cases`
- Keep the current effective published ordering and direct-case alignment exactly unchanged while deriving from canonical owners:
  - the module fixture-row slice still resolves to `workflow-module-split-maxsplit-indexlike-positional-bytes`, `workflow-module-sub-count-indexlike-positional-str`, and `workflow-module-subn-count-indexlike-positional-bytes`;
  - the aligned module direct cases still resolve to `module-split-maxsplit-indexlike-positional-bytes`, `module-sub-count-indexlike-positional-str`, and `module-subn-count-indexlike-positional-bytes`;
  - the pattern fixture-row slice still resolves to `workflow-pattern-search-str-pos-indexlike-positional`, `workflow-pattern-search-bytes-endpos-indexlike-positional`, `workflow-pattern-fullmatch-bytes-window-indexlike-positional`, `workflow-pattern-findall-str-window-indexlike-positional`, `workflow-pattern-finditer-bytes-window-indexlike-positional`, `workflow-pattern-split-str-maxsplit-indexlike-positional`, `workflow-pattern-sub-count-indexlike-positional-bytes`, and `workflow-pattern-subn-count-indexlike-positional-str`; and
  - the aligned pattern direct cases still resolve to `pattern-search-pos-indexlike-positional-str`, `pattern-search-endpos-indexlike-positional-bytes`, `pattern-fullmatch-window-indexlike-positional-bytes`, `pattern-findall-window-indexlike-positional-str`, `pattern-finditer-window-indexlike-positional-bytes`, `pattern-split-maxsplit-indexlike-positional-str`, `pattern-sub-count-indexlike-positional-bytes`, and `pattern-subn-count-indexlike-positional-str`.
- Keep canonical ownership otherwise unchanged:
  - do not change `MODULE_CALL_CASES`, `PATTERN_CASES`, `MODULE_POSITIONAL_INDEXLIKE_CALL_CASES`, `PATTERN_POSITIONAL_INDEXLIKE_CALL_CASES`, `PATTERN_DUAL_INDEXLIKE_WINDOW_CASES`, helper coercion utilities, or positional-indexlike behavior; and
  - do not broaden or shrink the published module-workflow frontier.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py`
  - `bash -lc "! rg -n '^(PUBLISHED_MODULE_POSITIONAL_INDEXLIKE_MODULE_HELPER_CASES|PUBLISHED_PATTERN_POSITIONAL_INDEXLIKE_PATTERN_CASES) =' tests/python/test_module_workflow_parity_suite.py"`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
import tests.python.test_module_workflow_parity_suite as mod

module_direct_signatures = {
    (
        case.helper,
        case.args[0],
        mod._workflow_positional_args_signature(tuple(case.args[1:])),
        "bytes" if isinstance(case.args[0], bytes) else "str",
    ): case.case_id
    for case in mod.MODULE_POSITIONAL_INDEXLIKE_CALL_CASES
}
module_fixture_cases = tuple(
    case
    for case in mod.MODULE_CALL_CASES
    if (
        case.helper,
        mod.case_pattern(case),
        mod._workflow_positional_args_signature(tuple(case.args)),
        case.text_model,
    ) in module_direct_signatures
)
assert tuple(case.case_id for case in module_fixture_cases) == (
    "workflow-module-split-maxsplit-indexlike-positional-bytes",
    "workflow-module-sub-count-indexlike-positional-str",
    "workflow-module-subn-count-indexlike-positional-bytes",
)
assert tuple(
    module_direct_signatures[
        (
            case.helper,
            mod.case_pattern(case),
            mod._workflow_positional_args_signature(tuple(case.args)),
            case.text_model,
        )
    ]
    for case in module_fixture_cases
) == (
    "module-split-maxsplit-indexlike-positional-bytes",
    "module-sub-count-indexlike-positional-str",
    "module-subn-count-indexlike-positional-bytes",
)

pattern_direct_signatures = {
    (
        case.helper,
        case.pattern,
        mod._workflow_positional_args_signature(case.args),
        "bytes" if isinstance(case.pattern, bytes) else "str",
    ): case.case_id
    for case in mod.PATTERN_POSITIONAL_INDEXLIKE_CALL_CASES
}
pattern_fixture_cases = tuple(
    case
    for case in mod.PATTERN_CASES
    if case.kwargs == {}
    and (
        case.helper,
        mod.case_pattern(case),
        mod._workflow_positional_args_signature(tuple(case.args)),
        case.text_model,
    ) in pattern_direct_signatures
)
assert tuple(case.case_id for case in pattern_fixture_cases) == (
    "workflow-pattern-search-str-pos-indexlike-positional",
    "workflow-pattern-search-bytes-endpos-indexlike-positional",
    "workflow-pattern-fullmatch-bytes-window-indexlike-positional",
    "workflow-pattern-findall-str-window-indexlike-positional",
    "workflow-pattern-finditer-bytes-window-indexlike-positional",
    "workflow-pattern-split-str-maxsplit-indexlike-positional",
    "workflow-pattern-sub-count-indexlike-positional-bytes",
    "workflow-pattern-subn-count-indexlike-positional-str",
)
assert tuple(
    pattern_direct_signatures[
        (
            case.helper,
            mod.case_pattern(case),
            mod._workflow_positional_args_signature(tuple(case.args)),
            case.text_model,
        )
    ]
    for case in pattern_fixture_cases
) == (
    "pattern-search-pos-indexlike-positional-str",
    "pattern-search-endpos-indexlike-positional-bytes",
    "pattern-fullmatch-window-indexlike-positional-bytes",
    "pattern-findall-window-indexlike-positional-str",
    "pattern-finditer-window-indexlike-positional-bytes",
    "pattern-split-maxsplit-indexlike-positional-str",
    "pattern-sub-count-indexlike-positional-bytes",
    "pattern-subn-count-indexlike-positional-str",
)
print("ok")
PY`

## Constraints
- Keep this cleanup structural only. The point is to delete one more mirrored owner layer inside the module-workflow parity suite, not to reinterpret `__index__` coercion behavior, change helper semantics, move cases between fixture and direct owners, or broaden the suite.
- Keep scope limited to `tests/python/test_module_workflow_parity_suite.py`. Do not edit correctness fixtures, benchmark manifests/tests, harness modules, reports, README copy, or tracked project-state prose in this run.

## Notes
- `RBR-0845` is the next available task id in the current checkout:
  - `ops/state/backlog.md` and `ops/state/current_status.md` reserve only the already-filed `RBR-0844`; and
  - no tracked task file under `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, or `ops/tasks/blocked/` already uses `RBR-0845`.
- No blocked architecture task exists to reopen first, and the current queue/runtime state does not trigger rule 10:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete and bounded in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py` currently passes (`1207 passed, 1 skipped in 0.85s`);
  - `rg -n '^(PUBLISHED_MODULE_POSITIONAL_INDEXLIKE_MODULE_HELPER_CASES|PUBLISHED_PATTERN_POSITIONAL_INDEXLIKE_PATTERN_CASES) =' tests/python/test_module_workflow_parity_suite.py` currently shows exactly the two detached subset-table declarations and no adjacent owner for the same slice;
  - the final `rg` absence check in Acceptance currently fails exactly on this cleanup because those mirrored top-level tables still exist; and
  - the import probe in Acceptance already passes (`ok`), showing that `MODULE_CALL_CASES`, `PATTERN_CASES`, `MODULE_POSITIONAL_INDEXLIKE_CALL_CASES`, and `PATTERN_POSITIONAL_INDEXLIKE_CALL_CASES` already carry the ordering and direct-alignment data needed to delete the extra published-sidecar layer without changing behavior.
- This stays on the same bounded post-JSON cleanup track as the recent sidecar removals in neighboring parity owners, but targets a still-live redundancy in the current checkout instead of reopening already-drained files.

## Completion
- 2026-03-21: Removed the mirrored `PUBLISHED_MODULE_POSITIONAL_INDEXLIKE_MODULE_HELPER_CASES` and `PUBLISHED_PATTERN_POSITIONAL_INDEXLIKE_PATTERN_CASES` sidecars from `tests/python/test_module_workflow_parity_suite.py`.
- Added small file-local selectors that derive the published positional-indexlike module and pattern fixture slices from `MODULE_CALL_CASES` / `PATTERN_CASES` plus `MODULE_POSITIONAL_INDEXLIKE_CALL_CASES` / `PATTERN_POSITIONAL_INDEXLIKE_CALL_CASES`, preserving the existing published ordering and direct-case alignment.
- Rewired `test_module_workflow_surface_publishes_module_positional_indexlike_slice_from_direct_cases`, `test_module_workflow_surface_publishes_pattern_positional_indexlike_slice_from_direct_cases`, and the direct-bucket coverage check to use those derived selectors instead of detached top-level tables.
- Left `MODULE_CALL_CASES`, `PATTERN_CASES`, `MODULE_POSITIONAL_INDEXLIKE_CALL_CASES`, `PATTERN_POSITIONAL_INDEXLIKE_CALL_CASES`, `PATTERN_DUAL_INDEXLIKE_WINDOW_CASES`, coercion helpers, and positional-indexlike behavior unchanged.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py` (`1207 passed, 1 skipped in 1.19s`), `bash -lc "! rg -n '^(PUBLISHED_MODULE_POSITIONAL_INDEXLIKE_MODULE_HELPER_CASES|PUBLISHED_PATTERN_POSITIONAL_INDEXLIKE_PATTERN_CASES) =' tests/python/test_module_workflow_parity_suite.py"` (passes with no matches), and the task-local import/signature probe from Acceptance (`ok`).
