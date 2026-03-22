# RBR-0951: Publish the module-workflow module replacement `count_alias` keyword pair

Status: ready
Owner: feature-implementation
Created: 2026-03-22

## Goal
- Reopen the shared `module-workflow-surface` correctness frontier with the adjacent raw module replacement `count_alias` keyword-name rejection pair, publishing the exact CPython-visible `TypeError` spellings that the current runtime already matches before a later Python-path benchmark catch-up or compiled-pattern sibling widens the queue.

## Pattern Pair
- `re.sub("abc", "x", "abcabc", count_alias=1)`
- `re.subn(b"abc", b"x", b"abcabc", count_alias=1)`

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by exactly two new raw `module_call` rows:
  - add `workflow-module-sub-count-alias-keyword`;
  - add `workflow-module-subn-count-alias-keyword-bytes`;
  - keep both rows pinned to the exact raw module helper calls above with `include_pattern_arg == True`;
  - keep `workflow-module-sub-count-alias-keyword` on the raw module `str` owner path with `helper == "sub"`, `pattern == "abc"`, `args == ["x", "abcabc"]`, and `kwargs == {"count_alias": 1}`;
  - keep `workflow-module-subn-count-alias-keyword-bytes` on the raw module `bytes` owner path with `helper == "subn"`, `pattern == "abc"`, the existing bytes payload encoding shape for `args == [b"x", b"abcabc"]`, and `kwargs == {"count_alias": 1}`;
  - insert `workflow-module-sub-count-alias-keyword` immediately after `workflow-module-sub-unexpected-keyword-after-positional-count`;
  - insert `workflow-module-subn-count-alias-keyword-bytes` immediately after `workflow-module-subn-unexpected-keyword-after-positional-count-bytes`;
  - categorize the new rows under `["workflow", "<helper>", "literal", ..., "unexpected-keyword"]` with the correct `str` / `bytes` text-model tags; and
  - keep the notes explicit that these are the adjacent raw module replacement `count_alias` keyword-name rejection spellings on the shared module-workflow owner path, not a broader replacement-keyword dump.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared raw-module keyword-error owner path instead of creating another manifest, parity suite, or detached keyword-name table:
  - extend `MODULE_KEYWORD_ERROR_CASES` with exactly two new direct parity anchors:
    - `module-sub-count-alias-keyword` with `helper == "sub"`, `args == ("abc", "x", "abcabc")`, and `kwargs == {"count_alias": 1}`;
    - `module-subn-count-alias-keyword-bytes` with `helper == "subn"`, `args == (b"abc", b"x", b"abcabc")`, and `kwargs == {"count_alias": 1}`;
  - extend the canonical published `module-keyword-error` slice so it now contains exactly these thirteen rows in order:
    - `workflow-module-search-duplicate-flags-keyword`
    - `workflow-module-split-duplicate-maxsplit-keyword`
    - `workflow-module-split-unexpected-keyword`
    - `workflow-module-split-unexpected-keyword-bytes`
    - `workflow-module-sub-duplicate-count-keyword`
    - `workflow-module-fullmatch-unexpected-keyword`
    - `workflow-module-sub-unexpected-keyword`
    - `workflow-module-sub-unexpected-keyword-after-positional-count`
    - `workflow-module-sub-count-alias-keyword`
    - `workflow-module-subn-duplicate-count-keyword-bytes`
    - `workflow-module-subn-unexpected-keyword-bytes`
    - `workflow-module-subn-unexpected-keyword-after-positional-count-bytes`
    - `workflow-module-subn-count-alias-keyword-bytes`
  - keep the published `str` subset pinned to:
    - `workflow-module-search-duplicate-flags-keyword`
    - `workflow-module-split-duplicate-maxsplit-keyword`
    - `workflow-module-split-unexpected-keyword`
    - `workflow-module-sub-duplicate-count-keyword`
    - `workflow-module-fullmatch-unexpected-keyword`
    - `workflow-module-sub-unexpected-keyword`
    - `workflow-module-sub-unexpected-keyword-after-positional-count`
    - `workflow-module-sub-count-alias-keyword`
  - keep the published `bytes` subset pinned to:
    - `workflow-module-split-unexpected-keyword-bytes`
    - `workflow-module-subn-duplicate-count-keyword-bytes`
    - `workflow-module-subn-unexpected-keyword-bytes`
    - `workflow-module-subn-unexpected-keyword-after-positional-count-bytes`
    - `workflow-module-subn-count-alias-keyword-bytes`
  - update the direct-case alignment so those thirteen published rows map back to the exact direct anchors above, plus the existing `module-search-duplicate-flags-keyword`, `module-split-duplicate-maxsplit-keyword`, `module-split-unexpected-keyword`, `module-split-unexpected-keyword-bytes`, `module-sub-duplicate-count-keyword`, `module-fullmatch-unexpected-keyword`, `module-sub-unexpected-keyword`, `module-sub-unexpected-keyword-after-positional-count`, `module-subn-duplicate-count-keyword-bytes`, `module-subn-unexpected-keyword-bytes`, and `module-subn-unexpected-keyword-after-positional-count-bytes`, in the same order;
  - move the published raw module keyword-error slice from `11` rows to `13`;
  - move the slice text-model split from `7` `str` / `4` `bytes` to `8` / `5`;
  - keep the slice helper breakdown honest at `search: 1`, `split: 3`, `sub: 4`, `fullmatch: 1`, and `subn: 4`;
  - update the full `module-workflow-surface` bundle expectations from `173` rows to `175`;
  - move `module.workflow.str` from `97` to `98` and `module.workflow.bytes` from `76` to `77`;
  - move `module.workflow.module_call` from `93` to `95`;
  - keep `module.workflow.pattern_call` at `68` in this run; and
  - keep the overall module-call helper counter honest by moving `sub` from `17` to `18` and `subn` from `17` to `18` while leaving the other helper totals unchanged.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1547` total / `1547` passed / `0` unimplemented across `114` manifests to `1549` / `1549` / `0` across the same `114` manifests;
  - `module.workflow` moves from `173` / `173` / `0` to `175` / `175` / `0`;
  - `module.workflow.str` moves from `97` / `97` / `0` to `98` / `98` / `0`;
  - `module.workflow.bytes` moves from `76` / `76` / `0` to `77` / `77` / `0`;
  - `module.workflow.module_call` moves from `93` / `93` / `0` to `95` / `95` / `0`;
  - `module.workflow.pattern_call` stays `68` / `68` / `0`; and
  - at least one of the two new raw module replacement `count_alias` rows is visible in the tracked scorecard as a representative `module-workflow-surface` module-call case.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module-sub-count-alias-keyword or module-subn-count-alias-keyword-bytes or module_replacement_unexpected_keyword_names_match_cpython or module_workflow_surface_publishes_module_keyword_error_slice_from_direct_cases'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0951-module-workflow-module-replacement-count-alias-keyword-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or benchmark-side selector logic in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached raw-module replacement-keyword publication file.
- Keep the scope pinned to the two raw module replacement `count_alias` rows above. Leave the matching Python-path benchmark catch-up on `benchmarks/workloads/collection_replacement_boundary.py` for a later task.

## Notes
- `RBR-0951` is the next available task id in the current checkout:
  - `RBR-0949` is the latest done feature task on the drained pattern-window benchmark frontier;
  - `RBR-0950` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this after the drained pattern-window benchmark catch-up because the adjacent published `Pattern.search(..., endpos=...)` owner path is now fully benchmarked in the current slice, while the next concrete unpublished module-workflow keyword-error pair sits back on the same collection/replacement helper family rather than a new parser or harness lane.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier while the exact publication rows are still absent:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'replacement_unexpected_keyword_names_match_cpython'` currently passes (`36 passed`), so the raw module replacement keyword-name parity path is already green in this checkout;
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... re.sub('abc', 'x', 'abcabc', count_alias=1) ... rebar.sub('abc', 'x', 'abcabc', count_alias=1) ... re.subn(b'abc', b'x', b'abcabc', count_alias=1) ... rebar.subn(b'abc', b'x', b'abcabc', count_alias=1) ... PY` shows CPython and `rebar` already agree on the exact bounded `TypeError.args`: `(\"sub() got an unexpected keyword argument 'count_alias'\",)` for the `str` spelling and `(\"subn() got an unexpected keyword argument 'count_alias'\",)` for the `bytes` spelling; and
  - `rg -n 'workflow-module-sub-count-alias|workflow-module-subn-count-alias|module-sub-count-alias|module-subn-count-alias|count_alias' tests/conformance/fixtures/module_workflow_surface.py reports/correctness/latest.py benchmarks/workloads/collection_replacement_boundary.py reports/benchmarks/latest.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently returns no matches, so both exact publication ids and any matching benchmark ids are still absent in this checkout.
