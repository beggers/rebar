# RBR-0959: Publish the bound Pattern replacement `count_alias` keyword pair

Status: ready
Owner: feature-implementation
Created: 2026-03-22

## Goal
- Reopen the shared `module-workflow-surface` correctness frontier with the adjacent bound `Pattern.sub()` / `Pattern.subn()` `count_alias` keyword-name rejection pair, publishing the exact CPython-visible `TypeError` spellings that the current runtime already matches before a later Python-path benchmark catch-up widens the same collection/replacement owner path.

## Pattern Pair
- `re.compile("abc").sub("x", "abcabc", count_alias=1)`
- `re.compile(b"abc").subn(b"x", b"abcabc", count_alias=1)`

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by exactly two new bound-pattern `pattern_call` rows:
  - add `workflow-pattern-sub-count-alias-keyword-str`;
  - add `workflow-pattern-subn-count-alias-keyword-bytes`;
  - keep `workflow-pattern-sub-count-alias-keyword-str` on the `str` path with `helper == "sub"`, `pattern == "abc"`, `args == ["x", "abcabc"]`, and `kwargs == {"count_alias": 1}`;
  - keep `workflow-pattern-subn-count-alias-keyword-bytes` on the `bytes` path with `helper == "subn"`, `pattern == "abc"`, the existing bytes payload encoding shape for `args == [b"x", b"abcabc"]`, and `kwargs == {"count_alias": 1}`;
  - insert `workflow-pattern-sub-count-alias-keyword-str` immediately after `workflow-pattern-sub-unexpected-keyword-after-positional-count-str`;
  - insert `workflow-pattern-subn-count-alias-keyword-bytes` immediately after `workflow-pattern-subn-unexpected-keyword-after-positional-count-bytes`;
  - categorize the two new rows under the existing bound-pattern replacement keyword-error path with `["workflow", "<helper>", "literal", "<text-model>", "unexpected-keyword"]`; and
  - keep the notes explicit that these are the adjacent bound `Pattern.sub()` / `Pattern.subn()` `count_alias` keyword-name rejection spellings on the shared owner path, not a broader pattern-helper keyword dump.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared bound-pattern keyword-error owner path instead of creating another manifest, parity suite, or detached keyword table:
  - extend `test_module_workflow_surface_publishes_pattern_keyword_error_slice_from_direct_cases(...)` so its selected direct anchors now include:
    - `pattern-sub-count-alias-keyword-str` immediately after `pattern-sub-unexpected-keyword-after-positional-count-str`; and
    - `pattern-subn-count-alias-keyword-bytes` immediately after `pattern-subn-unexpected-keyword-after-positional-count-bytes`;
  - keep the published bound-pattern keyword-error slice ordering otherwise stable while moving that slice from `8` rows to `10`;
  - keep the text-model split for that slice explicit at `5` `str` / `5` `bytes`;
  - keep the helper breakdown for that slice explicit at `split: 2`, `sub: 4`, and `subn: 4`;
  - keep the selected direct-case ordering aligned with the published fixture ordering so the new `count_alias` anchors sit immediately after the existing after-positional-count `sub` / `subn` cases; and
  - keep the broader pattern-call owner path honest by moving the published `PATTERN_CASES` total from `68` rows to `70`, with helper totals moving from `sub: 9` / `subn: 9` to `sub: 10` / `subn: 10` while leaving the other helper totals unchanged.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1551` total / `1551` passed / `0` unimplemented across `114` manifests to `1553` / `1553` / `0` across the same `114` manifests;
  - `module.workflow` moves from `177` / `177` / `0` to `179` / `179` / `0`;
  - `module.workflow.str` moves from `99` / `99` / `0` to `100` / `100` / `0`;
  - `module.workflow.bytes` moves from `78` / `78` / `0` to `79` / `79` / `0`;
  - `module.workflow.pattern_call` moves from `68` / `68` / `0` to `70` / `70` / `0`;
  - `module.workflow.module_call` stays `97` / `97` / `0`; and
  - at least one of the two new bound-pattern `count_alias` rows is visible in the tracked scorecard as a representative `module-workflow-surface` pattern-call case.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern_replacement_unexpected_keyword_names_match_cpython or module_workflow_surface_publishes_pattern_keyword_error_slice_from_direct_cases'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0959-pattern-replacement-count-alias-keyword-pair.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or benchmark-side selector logic in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached pattern-helper keyword publication file.
- Keep the scope pinned to the two bound Pattern replacement `count_alias` rows above. Leave the matching Python-path benchmark catch-up on `benchmarks/workloads/collection_replacement_boundary.py` for a later task.

## Notes
- `RBR-0959` is the next available task id in the current checkout:
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 8` currently ends at `RBR-0958-collapse-compiled-pattern-helper-keyword-contract-test-siblings.md`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` contains only `.gitkeep`.
- Queue this directly after `RBR-0957` / `RBR-0958` on the same shared `module-workflow-surface` / `collection-replacement-boundary` frontier so the remaining adjacent replacement `count_alias` rejection pair on the bound Pattern owner path publishes before a later Python-path benchmark catch-up or another replacement-keyword family widens the queue.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern_replacement_unexpected_keyword_names_match_cpython or module_workflow_surface_publishes_pattern_keyword_error_slice_from_direct_cases'` currently passes (`13 passed`), so the exact bounded owner-path parity is already green in this checkout;
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... re.compile('abc').sub('x', 'abcabc', count_alias=1) ... rebar.compile('abc').sub('x', 'abcabc', count_alias=1) ... re.compile(b'abc').subn(b'x', b'abcabc', count_alias=1) ... rebar.compile(b'abc').subn(b'x', b'abcabc', count_alias=1) ... PY` shows CPython and `rebar` already agree on the exact bounded `TypeError.args`: `("'count_alias' is an invalid keyword argument for sub()",)` for the `str` spelling and `("'count_alias' is an invalid keyword argument for subn()",)` for the `bytes` spelling;
  - `PYTHONPATH=python:. ./.venv/bin/python - <<'PY' ... _pattern_helper_collection_replacement_keyword_error_workload(...) synthetic count_alias probes ... run_internal_workload_probe(...) ... PY` returns `status == "measured"` for both adapters on both synthetic workload shapes, so the later `collection_replacement_boundary.py` benchmark catch-up is already concrete in this checkout; and
  - `rg -n 'workflow-pattern-sub-count-alias-keyword-str|workflow-pattern-subn-count-alias-keyword-bytes|pattern-sub-count-alias-keyword-warm-str|pattern-subn-count-alias-keyword-warm-bytes' tests/conformance/fixtures/module_workflow_surface.py reports/correctness/latest.py benchmarks/workloads/collection_replacement_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/benchmarks/latest.py` currently returns no matches, so both exact publication ids and their matching benchmark ids are still absent in this checkout.
