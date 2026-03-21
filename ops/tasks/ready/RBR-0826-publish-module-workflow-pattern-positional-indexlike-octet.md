# RBR-0826: Publish the module-workflow `Pattern` positional `__index__` octet

Status: ready
Owner: feature-implementation
Created: 2026-03-21

## Goal
- Reopen the existing `module-workflow-surface` correctness frontier with the next concrete bound-`Pattern` family, publishing the positional `__index__` search/fullmatch/findall/finditer/split/sub/subn octet on the exact `"abc"` / `b"abc"` anchors before benchmark catch-up or another owner family reopens the queue.

## Pattern Pair
- `"abc"`
- `b"abc"`

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only eight new `pattern_call` rows:
  - add `workflow-pattern-search-str-pos-indexlike-positional`;
  - add `workflow-pattern-search-bytes-endpos-indexlike-positional`;
  - add `workflow-pattern-fullmatch-bytes-window-indexlike-positional`;
  - add `workflow-pattern-findall-str-window-indexlike-positional`;
  - add `workflow-pattern-finditer-bytes-window-indexlike-positional`;
  - add `workflow-pattern-split-str-maxsplit-indexlike-positional`;
  - add `workflow-pattern-sub-count-indexlike-positional-bytes`; and
  - add `workflow-pattern-subn-count-indexlike-positional-str`.
- Keep those rows pinned to the exact bound-`Pattern` direct parity anchors already defined on the shared owner path in `PATTERN_POSITIONAL_INDEXLIKE_CALL_CASES`:
  - `pattern-search-pos-indexlike-positional-str`: `helper == "search"`, `pattern == "abc"`, and `args == ["zabcabc", _INDEX_TWO]`;
  - `pattern-search-endpos-indexlike-positional-bytes`: `helper == "search"`, `pattern == b"abc"`, and `args == [b"zabcabc", 0, _INDEX_FOUR]`;
  - `pattern-fullmatch-window-indexlike-positional-bytes`: `helper == "fullmatch"`, `pattern == b"abc"`, and `args == [b"zabc", _INDEX_ONE, _INDEX_FOUR]`;
  - `pattern-findall-window-indexlike-positional-str`: `helper == "findall"`, `pattern == "abc"`, and `args == ["zabcabcabcz", _INDEX_ONE, _INDEX_SEVEN]`;
  - `pattern-finditer-window-indexlike-positional-bytes`: `helper == "finditer"`, `pattern == b"abc"`, and `args == [b"zabcabcabcz", _INDEX_ONE, _INDEX_SEVEN]`;
  - `pattern-split-maxsplit-indexlike-positional-str`: `helper == "split"`, `pattern == "abc"`, and `args == ["zabcabcabc", _INDEX_TWO]`;
  - `pattern-sub-count-indexlike-positional-bytes`: `helper == "sub"`, `pattern == b"abc"`, and `args == [b"x", b"abcabcabc", _INDEX_TWO]`; and
  - `pattern-subn-count-indexlike-positional-str`: `helper == "subn"`, `pattern == "abc"`, and `args == ["x", "abcabcabc", _INDEX_TWO]`.
- Keep the text-model split explicit by landing exactly four new `str` rows and four new `bytes` rows, and do not broaden into bound-`Pattern` bool positional rows, compiled-pattern module helpers, module-call rows, benchmark manifests, benchmark reports, native-boundary scaffolding, or any new manifest in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another positional-only manifest, detached selector table, or second module-workflow owner path:
  - update the bundle-contract expectations so `module-workflow-surface` now publishes `142` total rows instead of `134`;
  - update the owner-path text-model split from `79` `str` rows and `55` `bytes` rows to `83` `str` rows and `59` `bytes` rows;
  - keep `module_call` expectations unchanged at `77` rows;
  - update `pattern_call` expectations from `45` rows to `53` rows;
  - update the shared `pattern_call` helper breakdown so the owner path now expects `16` `search` rows, `4` `match` rows, `11` `fullmatch` rows, `5` `findall` rows, `5` `finditer` rows, `4` `split` rows, `4` `sub` rows, and `4` `subn` rows;
  - extend the published owner-path assertions with exactly this positional octet, keeping the canonical published direct-case alignment anchored to `PATTERN_POSITIONAL_INDEXLIKE_CALL_CASES` on the existing `module-workflow-surface` path instead of inventing another publication bucket; and
  - keep the already published bound-`Pattern` keyword rows, raw module rows, compiled-pattern rows, bounded-wildcard rows, cache/purge rows, and current direct-case buckets unchanged in this run.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1504` total / `1504` passed / `0` `unimplemented` across `114` manifests to `1512` / `1512` / `0` across the same `114` manifests;
  - `module.workflow` moves from `134` / `134` / `0` to `142` / `142` / `0`;
  - `module.workflow.str` moves from `79` / `79` / `0` to `83` / `83` / `0`;
  - `module.workflow.bytes` moves from `55` / `55` / `0` to `59` / `59` / `0`;
  - `module.workflow.module_call` stays `77` / `77` / `0`;
  - `module.workflow.pattern_call` moves from `45` / `45` / `0` to `53` / `53` / `0`; and
  - the eight new positional `__index__` rows are visible in the tracked scorecard as representative `module-workflow-surface` pattern-call cases.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_pattern_positional_indexlike_argument_calls_match_cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'test_module_workflow_surface_publishes_pattern_positional_indexlike_slice_from_direct_cases' tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0826-module-workflow-pattern-positional-indexlike-octet.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached positional-argument publication file.

## Notes
- `RBR-0826` is the next available feature task id in the current checkout:
  - `ops/tasks/ready/` currently holds only the architecture task `RBR-0825`;
  - `ops/tasks/in_progress/` and `ops/tasks/blocked/` have no active `feature-implementation` task; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done -maxdepth 1 -type f -printf '%f\n' | rg '^RBR-082[5-9]|^RBR-083[0-9]'` returned only `RBR-0825` in this run before adding this task.
- Queue this directly after `RBR-0824` on the same `module-workflow-surface` owner path. `RBR-0825` is architecture cleanup, so it does not change the feature frontier.
- 2026-03-21 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_pattern_positional_indexlike_argument_calls_match_cpython` passed in this run (`16 passed in 0.10s`), so the bound-`Pattern` positional `__index__` calls are already live on the owner path and this remains a publication-only slice rather than a missing implementation prerequisite;
  - direct publication probes in this run showed all eight target direct case ids are still absent from `tests/conformance/fixtures/module_workflow_surface.py`, `tests/conformance/test_combined_correctness_scorecards.py`, and `reports/correctness/latest.py`, while the adjacent bound-`Pattern` keyword `__index__` rows are already published;
  - no blocked feature task exists to reopen first; and
  - `ops/state/backlog.md` and the frontier prose in `ops/state/current_status.md` already honestly say that no ready feature follow-on survives after the likely same-cycle drain, so this one-task refill does not need additional backlog/current-status edits.
