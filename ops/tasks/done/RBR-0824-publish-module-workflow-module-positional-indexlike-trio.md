# RBR-0824: Publish the module-workflow module positional `__index__` trio

Status: done
Owner: feature-implementation
Created: 2026-03-21

## Goal
- Reopen the existing `module-workflow-surface` correctness frontier with the next concrete raw module-call family, publishing the positional `__index__` `split()` / `sub()` / `subn()` trio on the exact `"abc"` / `b"abc"` anchors before pattern positional rows, benchmark catch-up, or another owner family reopens the queue.

## Pattern Pair
- `"abc"`
- `b"abc"`

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only three new `module_call` rows:
  - add `workflow-module-split-maxsplit-indexlike-positional-bytes`;
  - add `workflow-module-sub-count-indexlike-positional-str`;
  - add `workflow-module-subn-count-indexlike-positional-bytes`;
  - keep the rows pinned to the exact direct parity anchors already defined on the shared owner path in `MODULE_POSITIONAL_INDEXLIKE_CALL_CASES`:
    - `module-split-maxsplit-indexlike-positional-bytes`: `helper == "split"`, `pattern == b"abc"`, and `args == [b"zabcabcabc", _INDEX_TWO]`;
    - `module-sub-count-indexlike-positional-str`: `helper == "sub"`, `pattern == "abc"`, and `args == ["x", "abcabcabc", _INDEX_TWO]`;
    - `module-subn-count-indexlike-positional-bytes`: `helper == "subn"`, `pattern == b"abc"`, and `args == [b"x", b"abcabcabc", _INDEX_TWO]`;
  - keep the text-model split explicit by landing exactly one new `str` row and two new `bytes` rows; and
  - do not broaden into pattern positional rows, keyword-argument rows, compiled-pattern rows, benchmark manifests, benchmark reports, native-boundary scaffolding, or any new manifest in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another positional-only manifest, detached selector table, or second module-workflow owner path:
  - update the bundle-contract expectations so `module-workflow-surface` now publishes `134` total rows instead of `131`;
  - update the owner-path text-model split from `78` `str` rows and `53` `bytes` rows to `79` `str` rows and `55` `bytes` rows;
  - keep `pattern_call` expectations unchanged at `45` rows;
  - update the shared `module_call` helper breakdown so the owner path now expects `16` `compile` rows, `7` `search` rows, `5` `match` rows, `7` `fullmatch` rows, `12` `split` rows, `2` `findall` rows, `2` `finditer` rows, `13` `sub` rows, `11` `subn` rows, and `2` `escape` rows;
  - extend the published owner-path assertions with exactly this positional trio, keeping the canonical published direct-case alignment anchored to `MODULE_POSITIONAL_INDEXLIKE_CALL_CASES` on the existing `module-workflow-surface` path instead of inventing another publication bucket;
  - keep the already published raw module keyword rows, compiled-pattern rows, bounded-wildcard rows, cache/purge rows, and current direct-case buckets unchanged in this run; and
  - do not broaden into pattern positional rows, compiled-pattern positional work, benchmark manifests, benchmark reports, or any new owner path in this run.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1501` total / `1501` passed / `0` `unimplemented` across `114` manifests to `1504` / `1504` / `0` across the same `114` manifests;
  - `module.workflow` moves from `131` / `131` / `0` to `134` / `134` / `0`;
  - `module.workflow.str` moves from `78` / `78` / `0` to `79` / `79` / `0`;
  - `module.workflow.bytes` moves from `53` / `53` / `0` to `55` / `55` / `0`;
  - `module.workflow.module_call` moves from `74` / `74` / `0` to `77` / `77` / `0`;
  - `module.workflow.pattern_call` stays `45` / `45` / `0`; and
  - the three new positional `__index__` rows are visible in the tracked scorecard as representative `module-workflow-surface` module-call cases.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_module_positional_indexlike_argument_calls_match_cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'test_module_workflow_surface_publishes_module_positional_indexlike_slice_from_direct_cases' tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0824-module-workflow-module-positional-indexlike-trio.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached positional-argument publication file.

## Notes
- `RBR-0824` is the next available task id in the current checkout:
  - `ops/tasks/done/` currently runs through `RBR-0823`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` had no `feature-implementation` task at the start of this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done -maxdepth 1 -type f -printf '%f\n' | rg '^RBR-0824'` returned no matches in this run.
- Queue this directly after `RBR-0822` on the same `module-workflow-surface` owner path. `RBR-0823` is architecture cleanup, so it does not change the feature frontier.
- 2026-03-21 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_module_positional_indexlike_argument_calls_match_cpython` passed in this run (`6 passed in 0.09s`), so the raw module positional `__index__` calls are already live on the owner path and this remains a publication-only slice rather than a missing implementation prerequisite;
  - a direct runtime probe in this run showed both CPython and `rebar` already agree on the exact bounded outputs for the targeted trio:
    - `split(b"abc", b"zabcabcabc", _IndexLike(2)) -> [b"z", b"", b"abc"]`;
    - `sub("abc", "x", "abcabcabc", _IndexLike(2)) -> "xxabc"`;
    - `subn(b"abc", b"x", b"abcabcabc", _IndexLike(2)) -> (b"xxabc", 2)`;
  - direct publication probes in this run confirmed `workflow-module-split-maxsplit-indexlike-positional-bytes`, `workflow-module-sub-count-indexlike-positional-str`, and `workflow-module-subn-count-indexlike-positional-bytes` are still absent from `tests/conformance/fixtures/module_workflow_surface.py`, `tests/conformance/test_combined_correctness_scorecards.py`, and `reports/correctness/latest.py`, while the adjacent keyword-form rows are already published;
  - no blocked feature task exists to reopen first; and
  - `ops/state/backlog.md` and the frontier prose in `ops/state/current_status.md` already honestly say that no ready feature follow-on survives after the likely same-cycle drain, so this one-task refill does not need additional backlog/current-status edits.

## Completion
- 2026-03-21: Added `workflow-module-split-maxsplit-indexlike-positional-bytes`, `workflow-module-sub-count-indexlike-positional-str`, and `workflow-module-subn-count-indexlike-positional-bytes` to the shared `module-workflow-surface` manifest, with `include_pattern_arg` enabled so the correctness harness calls the raw module helpers on the same direct anchors already exercised in `MODULE_POSITIONAL_INDEXLIKE_CALL_CASES`.
- Updated `tests/python/test_module_workflow_parity_suite.py` so the existing owner path now expects `134` published rows, `79` `str` rows, `55` `bytes` rows, `77` `module_call` rows, and the adjusted `split`/`sub`/`subn` helper counts; added the dedicated published-slice assertion and kept the direct-case matching semantic for `__index__` carriers rather than object identity.
- Regenerated `reports/correctness/latest.py`; the tracked publication now reads `1504` total / `1504` passed / `0` unimplemented across `114` manifests, with `module.workflow` at `134/134/0`, `module.workflow.str` at `79/79/0`, `module.workflow.bytes` at `55/55/0`, `module.workflow.module_call` at `77/77/0`, and `module.workflow.pattern_call` unchanged at `45/45/0`. The tracked report contains all three new positional case ids and marks each `pass`.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_module_positional_indexlike_argument_calls_match_cpython` (`6 passed in 0.40s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'test_module_workflow_surface_publishes_module_positional_indexlike_slice_from_direct_cases' tests/conformance/test_combined_correctness_scorecards.py` (`1 passed, 837 deselected in 0.42s`);
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0824-module-workflow-module-positional-indexlike-trio.py` (`134/134`);
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py` (`1504/1504`);
  - and an additional full `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py` sanity pass (`32 passed, 2027 subtests passed in 35.75s`).
