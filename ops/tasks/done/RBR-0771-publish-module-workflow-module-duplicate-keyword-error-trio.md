# RBR-0771: Publish the module-workflow module duplicate-keyword error trio

Status: done
Owner: feature-implementation
Created: 2026-03-20
Completed: 2026-03-20

## Goal
- Reopen the existing `module-workflow-surface` correctness frontier with the first raw module keyword-argument error slice, publishing the duplicate positional-plus-keyword rejection trio for the exact `search(flags=)`, `split(maxsplit=)`, and `sub(count=)` anchors already carried by the shared owner path before unexpected-keyword rows, pattern keyword bool/indexlike rows, or another owner family reopens the queue.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only three new `module_call` rows:
  - add `workflow-module-search-duplicate-flags-keyword`;
  - add `workflow-module-split-duplicate-maxsplit-keyword`;
  - add `workflow-module-sub-duplicate-count-keyword`;
  - keep the rows pinned to the exact direct parity anchors already defined in `MODULE_KEYWORD_ERROR_CASES`:
    - `module-search-duplicate-flags-keyword`: `helper == "search"`, `pattern == "abc"`, `args == ["abc", 0]`, and `kwargs == {"flags": 0}`;
    - `module-split-duplicate-maxsplit-keyword`: `helper == "split"`, `pattern == "abc"`, `args == ["abc", 1]`, and `kwargs == {"maxsplit": 1}`;
    - `module-sub-duplicate-count-keyword`: `helper == "sub"`, `pattern == "abc"`, `args == ["x", "abc", 1]`, and `kwargs == {"count": 1}`;
  - keep all three rows on the `str` text model so the duplicate-keyword rejection slice stays explicit without widening into bytes siblings; and
  - do not broaden into `module-fullmatch-unexpected-keyword`, `module-sub-unexpected-keyword`, pattern keyword bool/indexlike rows, benchmarks, native-boundary scaffolding, or any new manifest in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another keyword-only manifest or detached selector table:
  - update the bundle-contract expectations, selected case-id inventory, and operation/helper counts so `module-workflow-surface` now publishes `69` total rows instead of `66`;
  - update the shared text-model split so the owner path now expects `45` `str` rows and `24` `bytes` rows;
  - update the shared `module_call` helper breakdown so the owner path now expects `6` `search` rows, `4` `match` rows, `4` `fullmatch` rows, `4` `split` rows, `1` `findall` row, `1` `finditer` row, `5` `sub` rows, `4` `subn` rows, and `2` `escape` rows;
  - keep the published module keyword helper slice pinned to the existing nine success rows and add a separate canonical published module-keyword-error slice for exactly the three new duplicate-keyword rows;
  - add or extend one focused direct-case alignment test so the published duplicate-keyword error slice is derived from `MODULE_KEYWORD_ERROR_CASES` in this exact order:
    - `workflow-module-search-duplicate-flags-keyword` -> `module-search-duplicate-flags-keyword`
    - `workflow-module-split-duplicate-maxsplit-keyword` -> `module-split-duplicate-maxsplit-keyword`
    - `workflow-module-sub-duplicate-count-keyword` -> `module-sub-duplicate-count-keyword`
  - update the direct-test bucket coverage so the selected frontier stays fully covered after the three new published rows land, without folding the error rows into the existing success-only `module-keyword-helper` bucket; and
  - keep the published direct-case alignment honest without restoring mirrored sidecars or inventing another owner path.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1436` total / `1436` passed / `0` `unimplemented` across `114` manifests to `1439` / `1439` / `0` across the same `114` manifests;
  - `module.workflow` moves from `66` / `66` / `0` to `69` / `69` / `0`;
  - `module.workflow.str` moves from `42` / `42` / `0` to `45` / `45` / `0`;
  - `module.workflow.bytes` stays `24` / `24` / `0`;
  - `module.workflow.module_call` moves from `28` / `28` / `0` to `31` / `31` / `0`; and
  - at least one of the new duplicate-keyword rows is visible in the tracked scorecard as a representative `module-workflow-surface` module-call case.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0771-module-workflow-module-duplicate-keyword-error-trio.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached keyword-error publication file.

## Notes
- `RBR-0771` is the next available task id in the current checkout:
  - `ops/tasks/done/` currently runs through `RBR-0770`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` had no newer `feature-implementation` task at the start of this run; and
  - `ops/state/backlog.md` and the frontier prose in `ops/state/current_status.md` already honestly say that no ready feature follow-on currently survives after the likely same-cycle drain, so this one-task refill does not need a backlog-frontier prose change.
- Queue this directly after `RBR-0769` on the same `module-workflow-surface` owner path so the first raw module keyword error slice lands before unexpected-keyword rows or pattern keyword publication reopens the frontier.
- 2026-03-20 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `tests/python/test_module_workflow_parity_suite.py` already carries the exact adjacent direct parity anchors `module-search-duplicate-flags-keyword`, `module-split-duplicate-maxsplit-keyword`, and `module-sub-duplicate-count-keyword` in `MODULE_KEYWORD_ERROR_CASES`;
  - direct publication probes in this run confirmed all three `workflow-module-*duplicate-*keyword` rows are still absent from `tests/conformance/fixtures/module_workflow_surface.py`, `tests/conformance/test_combined_correctness_scorecards.py`, and `reports/correctness/latest.py`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_keyword_argument_errors_match_cpython'` passed in this run (`10 passed, 668 deselected`);
  - the current owner path already publishes the adjacent nine successful module keyword rows, leaving duplicate-keyword rejection as the smallest unpublished slice on the same owner file; and
  - no blocked feature task exists to reopen first.

## Completion
- 2026-03-20: Added the three `workflow-module-*duplicate-*keyword` `module_call` rows to `tests/conformance/fixtures/module_workflow_surface.py`, kept them on the shared `module-workflow-surface` owner manifest as `str` cases, and wired them through the existing correctness path with a bounded `include_pattern_arg` fixture flag in `python/rebar_harness/correctness.py` so the published harness can exercise the raw module duplicate-keyword call shape without disturbing older module-call rows.
- Updated `tests/python/test_module_workflow_parity_suite.py` to keep the existing nine-row `module-keyword-helper` success slice intact, add a separate three-row `module-keyword-error` slice derived from `MODULE_KEYWORD_ERROR_CASES`, and raise the owner-path expectations to `69` total rows with a `45`/`24` `str`/`bytes` split and `31` published `module_call` rows.
- Extended `tests/conformance/test_combined_correctness_scorecards.py` so `module-workflow-surface` representative cases now include the duplicate-keyword slice, and republished `reports/correctness/latest.py` to `1439` total / `1439` passed / `0` unimplemented across `114` manifests; `module.workflow` is now `69/69/0`, `module.workflow.str` `45/45/0`, `module.workflow.bytes` `24/24/0`, and `module.workflow.module_call` `31/31/0`.
- Verification passed with `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0771-module-workflow-module-duplicate-keyword-error-trio.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`, and `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`.
