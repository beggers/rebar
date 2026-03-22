# RBR-0892: Publish the module-workflow `Pattern.match()` bytes window `__index__` pair

Status: ready
Owner: feature-implementation
Created: 2026-03-22

## Goal
- Keep the existing `module-workflow-surface` correctness frontier moving once `RBR-0890` drains by publishing the remaining bytes bound-`Pattern.match()` window `__index__` keyword and positional pair on the shared correctness surface, while leaving the Python-path benchmark frontier unchanged in this run.

## Pattern Pair
- `re.compile(b"abc").match(b"zabc", pos=_INDEX_ONE, endpos=_INDEX_FOUR)`
- `re.compile(b"abc").match(b"zabc", _INDEX_ONE, _INDEX_FOUR)`

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by exactly two new `pattern_call` rows:
  - add `workflow-pattern-match-bytes-window-indexlike`;
  - add `workflow-pattern-match-bytes-window-indexlike-positional`;
  - keep both rows pinned to the exact existing direct parity anchors on the shared owner path:
    - `pattern-match-window-indexlike-bytes`: `helper == "match"`, `pattern == b"abc"`, `args == [b"zabc"]`, and `kwargs == {"pos": _INDEX_ONE, "endpos": _INDEX_FOUR}`;
    - `pattern-match-window-indexlike-positional-bytes`: `helper == "match"`, `pattern == b"abc"`, `args == [b"zabc", _INDEX_ONE, _INDEX_FOUR]`, and `kwargs == {}`;
  - keep the slice bytes-only, and do not broaden into the already published `str` `pos=` keyword rows, the already published bytes `fullmatch()` / `finditer()` window `__index__` rows, or benchmark manifest churn in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another pattern-window manifest, detached selector table, or second module-workflow parity path:
  - extend `PUBLISHED_PATTERN_KEYWORD_PATTERN_CASES` by exactly one row, `workflow-pattern-match-bytes-window-indexlike`, inserted immediately after `workflow-pattern-match-str-bool-pos-keyword` and immediately before `workflow-pattern-fullmatch-bytes-window-keyword`;
  - extend `test_module_workflow_surface_publishes_pattern_keyword_helpers_from_direct_cases` so the matching direct-case order inserts `pattern-match-window-indexlike-bytes` immediately after `pattern-match-bool-pos-keyword-str` and immediately before `pattern-fullmatch-window-keyword-bytes`;
  - extend `test_module_workflow_surface_publishes_pattern_positional_indexlike_slice_from_direct_cases` by exactly one row, `workflow-pattern-match-bytes-window-indexlike-positional`, inserted immediately after `workflow-pattern-search-bytes-endpos-indexlike-positional` and immediately before `workflow-pattern-fullmatch-bytes-window-indexlike-positional`;
  - keep `test_pattern_positional_indexlike_direct_cases_remain_balanced_for_follow_on` honest by converting the stale one-row `match()` bytes follow-on into the published fixture-backed positional slice instead of leaving `pattern-match-window-indexlike-positional-bytes` outside the owner-path publication tables;
  - update the shared `module-workflow-surface` bundle expectations from `146` total rows to `148`, with the text-model split moving from `85` `str` / `61` `bytes` to `85` / `63`;
  - keep `module_call` expectations unchanged at `81` rows;
  - update `pattern_call` expectations from `53` rows to `55`;
  - update the shared `pattern_call` helper breakdown so the owner path now expects `16` `search` rows, `6` `match` rows, `11` `fullmatch` rows, `5` `findall` rows, `5` `finditer` rows, `4` `split` rows, `4` `sub` rows, and `4` `subn` rows; and
  - keep the already published compile rows, module-call rows, bound-`Pattern` keyword rows, positional `__index__` rows, and compiled-pattern rows unchanged outside this exact pair.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1520` total / `1520` passed / `0` `unimplemented` across `114` manifests to `1522` / `1522` / `0` across the same `114` manifests;
  - `module.workflow` moves from `146` / `146` / `0` to `148` / `148` / `0`;
  - `module.workflow.str` stays `85` / `85` / `0`;
  - `module.workflow.bytes` moves from `61` / `61` / `0` to `63` / `63` / `0`;
  - `module.workflow.module_call` stays `81` / `81` / `0`;
  - `module.workflow.pattern_call` moves from `53` / `53` / `0` to `55` / `55` / `0`; and
  - the two new bytes `Pattern.match()` window `__index__` rows are visible in the tracked scorecard as representative `module-workflow-surface` pattern-call cases.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-match-window-indexlike-bytes or pattern-match-window-indexlike-positional-bytes'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0892-module-workflow-pattern-match-bytes-window-indexlike-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or source-tree benchmark selector logic in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached pattern-window publication file.
- Keep the Python-path benchmark frontier unchanged here. The adjacent `pattern_boundary.py` benchmark surface already times neighboring keyword and positional window rows, but this run should not widen that benchmark owner path before the correctness publication lands.

## Notes
- `RBR-0892` is the next available feature task id in the current checkout:
  - `RBR-0890` is already occupied by the ready feature task in `ops/tasks/ready/`;
  - `RBR-0891` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0890` on the same `module-workflow-surface` owner path so the remaining bytes bound-`Pattern.match()` window `__index__` spellings publish once the compiled-pattern literal `NOFLAG` compile pair drains.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier while the publication path still lacks the exact pair:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-match-window-indexlike-bytes or pattern-match-window-indexlike-positional-bytes'` passed in this run (`16 passed, 1207 deselected`), so no Rust or Python regex-behavior prerequisite is missing for these two bytes `Pattern.match()` window spellings;
  - a direct runtime probe in this run confirmed CPython and `rebar` already agree on both `rebar.compile(b"abc").match(b"zabc", pos=_INDEX_ONE, endpos=_INDEX_FOUR)` and `rebar.compile(b"abc").match(b"zabc", _INDEX_ONE, _INDEX_FOUR)`, preserving the same `group(0)`, `span()`, `pattern`, and `flags`;
  - direct publication probes in this run confirmed `workflow-pattern-match-bytes-window-indexlike` and `workflow-pattern-match-bytes-window-indexlike-positional` are still absent from `tests/conformance/fixtures/module_workflow_surface.py`, `tests/conformance/test_combined_correctness_scorecards.py`, and the published case inventories in `tests/python/test_module_workflow_parity_suite.py`;
  - `benchmarks/workloads/pattern_boundary.py` and `reports/benchmarks/latest.py` currently publish adjacent pattern-window keyword and positional rows, but no exact bytes `Pattern.match()` window `__index__` keyword or positional workloads; and
  - once `RBR-0890` lands, this bytes pair is the next exact unpublished owner-path neighbor on the shared bound-`Pattern` window surface.
