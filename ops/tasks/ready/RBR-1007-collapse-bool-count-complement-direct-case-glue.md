## RBR-1007: Collapse bool-count complement direct-case glue

Status: ready
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining repeated bool-count complement direct-case glue from `tests/python/test_module_workflow_parity_suite.py` so the three adjacent complement-balance tests run through one smaller file-local contract surface instead of each open-coding the same `count=True` / `count=False` filtering and signature projection shape with only the source case set and projected value changing.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` adds one explicit file-local helper surface, or a strictly smaller equivalent, that centralizes the current bool-count complement filter/projection contract shared by:
  - `test_module_keyword_direct_cases_keep_bool_count_complements_balanced_for_follow_on()`
  - `test_pattern_keyword_direct_cases_keep_bool_count_complements_balanced_for_follow_on()`
  - `test_compiled_pattern_module_keyword_bool_count_direct_cases_cover_complements()`
- Repoint those tests through that shared helper surface instead of leaving each body to open-code:
  - a filter for `_workflow_keyword_kwargs_signature(case.kwargs)` in `{(("count", "bool", False),), (("count", "bool", True),)}`; and
  - a near-identical tuple/set projection over the selected direct cases.
- Preserve the current complement contracts exactly while shrinking the glue:
  - the module complement test still resolves to the ordered four-row tuple:
    - `("module-sub-count-bool-false-str", "sub", "abc", (("count", "bool", False),))`
    - `("module-sub-count-bool-true-str", "sub", "abc", (("count", "bool", True),))`
    - `("module-subn-count-bool-false-bytes", "subn", b"abc", (("count", "bool", False),))`
    - `("module-subn-count-bool-true-bytes", "subn", b"abc", (("count", "bool", True),))`
  - the pattern complement test still proves the filtered `PATTERN_KEYWORD_CALL_CASES` projection matches `PATTERN_KEYWORD_BOOL_COUNT_COMPLEMENT_DIRECT_CASES` exactly, limited to `helper in {"sub", "subn"}`;
  - the compiled-pattern complement test still resolves to the same four-row set keyed by case id, helper, `"str"`/`"bytes"` text-model label, and bool-count signature; and
  - none of the three tests widen into positional-indexlike, owner-path publication, keyword-error, wrong-text-model, or compiled-pattern publication-contract logic.
- Keep the cleanup structural and file-local:
  - keep `_workflow_keyword_kwargs_signature(...)` as the canonical kwargs normalizer unless a strictly smaller local successor preserves the same verification surface;
  - do not edit fixture manifests, harness modules, benchmark files, reports, or tracked state prose; and
  - do not add a shared helper module, registry, or checked-in data representation.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_keyword_direct_cases_keep_bool_count_complements_balanced_for_follow_on or pattern_keyword_direct_cases_keep_bool_count_complements_balanced_for_follow_on or compiled_pattern_module_keyword_bool_count_direct_cases_cover_complements'`

## Constraints
- Keep the cleanup structural and local to `tests/python/test_module_workflow_parity_suite.py`.
- Prefer deleting repeated bool-count complement selection/projection glue over introducing another detached abstraction layer.
- Do not edit fixture manifests, harness modules, benchmark workloads/tests, reports, or README/current-status/backlog prose in this run.

## Notes
- `RBR-1007` is unreserved in the live queue/state files for this run:
  - `rg -n 'RBR-1007|RBR-1008|RBR-1009|RBR-1010' ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked` returned matches only inside prior done-task notes, with no live reservation in ready, in-progress, blocked, or done task filenames.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- The duplication target is concrete in the live checkout:
  - the focused pytest slice in Verification currently passes (`3 passed, 1448 deselected`);
  - `tests/python/test_module_workflow_parity_suite.py` still open-codes the same bool-count complement filter/projection shape in the module test around lines `4762`-`4791`, the pattern test around lines `4909`-`4933`, and the compiled-pattern test around lines `5107`-`5148`; and
  - the cleanup can stay structural and file-local because those three tests differ only in which direct-case collection they filter and which fourth projected field they assert.
