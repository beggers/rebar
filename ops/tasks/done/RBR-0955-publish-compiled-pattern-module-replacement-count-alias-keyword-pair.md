# RBR-0955: Publish the compiled-pattern module replacement `count_alias` keyword pair

Status: done
Owner: feature-implementation
Created: 2026-03-22
Completed: 2026-03-22

## Goal
- Reopen the shared `module-workflow-surface` correctness frontier with the adjacent compiled-pattern module-level replacement `count_alias` keyword-name rejection pair, publishing the exact CPython-visible `TypeError` spellings that the current runtime already matches before a later Python-path benchmark catch-up widens the same owner path.

## Pattern Pair
- `re.sub(re.compile("abc"), "x", "abcabc", count_alias=1)`
- `re.subn(re.compile(b"abc"), b"x", b"abcabc", count_alias=1)`

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by exactly two new compiled-pattern raw `module_call` rows:
  - add `workflow-module-sub-count-alias-keyword-str-compiled-pattern`;
  - add `workflow-module-subn-count-alias-keyword-bytes-compiled-pattern`;
  - keep both rows on the compiled-pattern owner path with `use_compiled_pattern == True` and the exact bounded replacement helper calls above;
  - keep `workflow-module-sub-count-alias-keyword-str-compiled-pattern` on the `str` path with `helper == "sub"`, `pattern == "abc"`, `args == ["x", "abcabc"]`, and `kwargs == {"count_alias": 1}`;
  - keep `workflow-module-subn-count-alias-keyword-bytes-compiled-pattern` on the `bytes` path with `helper == "subn"`, `pattern == "abc"`, the existing bytes payload encoding shape for `args == [b"x", b"abcabc"]`, and `kwargs == {"count_alias": 1}`;
  - insert `workflow-module-sub-count-alias-keyword-str-compiled-pattern` immediately after `workflow-module-sub-unexpected-keyword-after-positional-count-str-compiled-pattern`;
  - insert `workflow-module-subn-count-alias-keyword-bytes-compiled-pattern` immediately after `workflow-module-subn-unexpected-keyword-after-positional-count-bytes-compiled-pattern`;
  - categorize the new rows under `["workflow", "<helper>", "literal", ..., "unexpected-keyword", "compiled-pattern"]` with the correct `str` / `bytes` text-model tags; and
  - keep the notes explicit that these are the adjacent compiled-pattern module-level replacement `count_alias` keyword-name rejection spellings on the shared owner path, not a broader compiled-pattern keyword dump.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared compiled-pattern module keyword-error owner path instead of creating another manifest, parity suite, or detached keyword table:
  - extend `COMPILED_PATTERN_MODULE_KEYWORD_ERROR_CASES` with exactly two new direct parity anchors:
    - `compiled-pattern-sub-count-alias-keyword-str` with `helper == "sub"`, `pattern == "abc"`, `args == ("x", "abcabc")`, and `kwargs == {"count_alias": 1}`;
    - `compiled-pattern-subn-count-alias-keyword-bytes` with `helper == "subn"`, `pattern == b"abc"`, `args == (b"x", b"abcabc")`, and `kwargs == {"count_alias": 1}`;
  - update `test_compiled_pattern_module_keyword_frontier_publishes_after_positional_count_cases_on_shared_owner_path(...)` so the published compiled-pattern keyword-error frontier now includes:
    - `workflow-module-sub-count-alias-keyword-str-compiled-pattern` immediately after `workflow-module-sub-unexpected-keyword-after-positional-count-str-compiled-pattern`; and
    - `workflow-module-subn-count-alias-keyword-bytes-compiled-pattern` immediately after `workflow-module-subn-unexpected-keyword-after-positional-count-bytes-compiled-pattern`;
  - keep the shared compiled-pattern owner path explicit and honest by moving the published fixture totals from `60` rows to `62`, the text-model split from `32` `str` / `28` `bytes` to `33` / `29`, and the helper breakdown from `sub: 9` / `subn: 9` to `sub: 10` / `subn: 10` while leaving the other helper totals unchanged;
  - keep the published compiled-pattern fixture ordering otherwise stable and update the matching selected direct-case ordering so the new direct anchors appear immediately after the existing after-positional-count `sub` / `subn` cases; and
  - keep `test_module_workflow_direct_test_buckets_cover_selected_frontier(...)` green on the shared owner path without introducing another case bucket.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1549` total / `1549` passed / `0` unimplemented across `114` manifests to `1551` / `1551` / `0` across the same `114` manifests;
  - `module.workflow` moves from `175` / `175` / `0` to `177` / `177` / `0`;
  - `module.workflow.str` moves from `98` / `98` / `0` to `99` / `99` / `0`;
  - `module.workflow.bytes` moves from `77` / `77` / `0` to `78` / `78` / `0`;
  - `module.workflow.module_call` moves from `95` / `95` / `0` to `97` / `97` / `0`;
  - `module.workflow.pattern_call` stays `68` / `68` / `0`; and
  - at least one of the two new compiled-pattern `count_alias` rows is visible in the tracked scorecard as a representative `module-workflow-surface` module-call case.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'compiled_pattern_module_replacement_unexpected_keyword_names_match_cpython or compiled_pattern_module_keyword_frontier_publishes_after_positional_count_cases_on_shared_owner_path or compiled_pattern_module_keyword_argument_errors_match_cpython'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0955-compiled-pattern-module-replacement-count-alias-keyword-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or benchmark-side selector logic in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached compiled-pattern keyword publication file.
- Keep the scope pinned to the two compiled-pattern replacement `count_alias` rows above. Leave the matching Python-path benchmark catch-up on `benchmarks/workloads/collection_replacement_boundary.py` for a later task.

## Notes
- `RBR-0955` is the next available task id in the current checkout:
  - `RBR-0953` is the latest done feature task on this frontier;
  - `RBR-0954` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after the drained raw module replacement `count_alias` benchmark catch-up because the adjacent compiled-pattern module-helper replacement keyword-name pair already has direct parity coverage on the same owner path but is still absent from the published correctness surface.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier while the exact publication rows are still absent:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'compiled_pattern_module_replacement_unexpected_keyword_names_match_cpython or compiled_pattern_module_keyword_argument_errors_match_cpython'` currently passes (`36 passed`), so the exact bounded compiled-pattern replacement keyword-name parity path is already green in this checkout;
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... re.sub(re.compile("abc"), "x", "abcabc", count_alias=1) ... rebar.sub(rebar.compile("abc"), "x", "abcabc", count_alias=1) ... re.subn(re.compile(b"abc"), b"x", b"abcabc", count_alias=1) ... rebar.subn(rebar.compile(b"abc"), b"x", b"abcabc", count_alias=1) ... PY` shows CPython and `rebar` already agree on the exact bounded `TypeError.args`: `("sub() got an unexpected keyword argument 'count_alias'",)` for the `str` spelling and `("subn() got an unexpected keyword argument 'count_alias'",)` for the `bytes` spelling; and
  - `rg -n 'workflow-module-sub-count-alias-keyword-str-compiled-pattern|workflow-module-subn-count-alias-keyword-bytes-compiled-pattern|compiled-pattern-sub-count-alias-keyword-str|compiled-pattern-subn-count-alias-keyword-bytes|module-sub-count-alias-keyword-purged-str-compiled-pattern|module-subn-count-alias-keyword-purged-bytes-compiled-pattern' tests/conformance/fixtures/module_workflow_surface.py tests/python/test_module_workflow_parity_suite.py reports/correctness/latest.py benchmarks/workloads/collection_replacement_boundary.py reports/benchmarks/latest.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently returns no matches, so both exact compiled-pattern publication ids and their matching benchmark ids are still absent in this checkout.

## Completion
- 2026-03-22: Added `workflow-module-sub-count-alias-keyword-str-compiled-pattern` and `workflow-module-subn-count-alias-keyword-bytes-compiled-pattern` to `tests/conformance/fixtures/module_workflow_surface.py` immediately after the existing compiled-pattern positional-count keyword-error rows, keeping the slice on the shared compiled-pattern module keyword-error owner path with `use_compiled_pattern == True`, the bounded `abcabc` replacement calls, and explicit `count_alias` keyword-name rejection notes.
- Updated `tests/python/test_module_workflow_parity_suite.py` so `COMPILED_PATTERN_MODULE_KEYWORD_ERROR_CASES`, the shared compiled-pattern frontier ordering checks, the selected direct-case ordering, and the published fixture-count assertions all include the two new compiled-pattern replacement `count_alias` anchors without creating another owner path or case bucket. The shared compiled-pattern published fixture counts now read `62` rows with a `33` / `29` str/bytes split and `sub: 10` / `subn: 10`.
- Updated `tests/conformance/test_combined_correctness_scorecards.py` and republished `reports/correctness/latest.py`. The tracked report remains in the diff and now reads `1551` total / `1551` passed / `0` unimplemented across `114` manifests, with `module.workflow` at `177` / `177` / `0`, `module.workflow.str` at `99` / `99` / `0`, `module.workflow.bytes` at `78` / `78` / `0`, `module.workflow.module_call` at `97` / `97` / `0`, and `module.workflow.pattern_call` unchanged at `68` / `68` / `0`. The tracked report now includes both `workflow-module-sub-count-alias-keyword-str-compiled-pattern` and `workflow-module-subn-count-alias-keyword-bytes-compiled-pattern` as passing `module_call` cases on `module-workflow-surface`.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'compiled_pattern_module_replacement_unexpected_keyword_names_match_cpython or compiled_pattern_module_keyword_frontier_publishes_after_positional_count_cases_on_shared_owner_path or compiled_pattern_module_keyword_argument_errors_match_cpython'`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0955-compiled-pattern-module-replacement-count-alias-keyword-pair.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`.
