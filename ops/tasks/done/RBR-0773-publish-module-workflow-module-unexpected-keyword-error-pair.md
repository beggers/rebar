# RBR-0773: Publish the module-workflow module unexpected-keyword error pair

Status: done
Owner: feature-implementation
Created: 2026-03-20
Completed: 2026-03-20

## Goal
- Reopen the existing `module-workflow-surface` correctness frontier with the remaining raw module keyword-error pair, publishing the exact unexpected-keyword rejections for `fullmatch(missing=...)` and `sub(missing=...)` before pattern keyword bool/indexlike rows or another owner family reopens the queue.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only two new `module_call` rows:
  - add `workflow-module-fullmatch-unexpected-keyword` and `workflow-module-sub-unexpected-keyword`;
  - keep both rows pinned to the exact direct parity anchors already defined in `MODULE_KEYWORD_ERROR_CASES`:
    - `module-fullmatch-unexpected-keyword`: `helper == "fullmatch"`, `pattern == "abc"`, `args == ["abc"]`, and `kwargs == {"missing": 1}`;
    - `module-sub-unexpected-keyword`: `helper == "sub"`, `pattern == "abc"`, `args == ["x", "abc"]`, and `kwargs == {"missing": 1}`;
  - keep both rows on the `str` text model with `include_pattern_arg == True` so the raw module-call rejection surface stays explicit; and
  - do not broaden into pattern keyword bool/indexlike rows, bytes siblings, benchmarks, native-boundary scaffolding, or any new manifest in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another keyword-only manifest or detached selector table:
  - update the bundle-contract expectations, selected case-id inventory, and operation/helper counts so `module-workflow-surface` now publishes `71` total rows instead of `69`;
  - update the shared text-model split so the owner path now expects `47` `str` rows and `24` `bytes` rows;
  - update the shared `module_call` helper breakdown so the owner path now expects `6` `search` rows, `4` `match` rows, `5` `fullmatch` rows, `4` `split` rows, `1` `findall` row, `1` `finditer` row, `6` `sub` rows, `4` `subn` rows, and `2` `escape` rows;
  - keep the existing duplicate-keyword trio intact and extend the canonical published `module-keyword-error` slice so it now contains exactly these five rows in order:
    - `workflow-module-search-duplicate-flags-keyword`
    - `workflow-module-split-duplicate-maxsplit-keyword`
    - `workflow-module-sub-duplicate-count-keyword`
    - `workflow-module-fullmatch-unexpected-keyword`
    - `workflow-module-sub-unexpected-keyword`
  - add or extend one focused direct-case alignment test so the two new published rows map to `module-fullmatch-unexpected-keyword` and `module-sub-unexpected-keyword` in that same order; and
  - keep the published direct-test bucket coverage honest without restoring mirrored sidecars or inventing another owner path.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1439` total / `1439` passed / `0` `unimplemented` across `114` manifests to `1441` / `1441` / `0` across the same `114` manifests;
  - `module.workflow` moves from `69` / `69` / `0` to `71` / `71` / `0`;
  - `module.workflow.str` moves from `45` / `45` / `0` to `47` / `47` / `0`;
  - `module.workflow.bytes` stays `24` / `24` / `0`;
  - `module.workflow.module_call` moves from `31` / `31` / `0` to `33` / `33` / `0`; and
  - at least one of the new unexpected-keyword rows is visible in the tracked scorecard as a representative `module-workflow-surface` module-call case.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0773-module-workflow-module-unexpected-keyword-error-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached keyword-error publication file.

## Notes
- `RBR-0773` is the next available task id in the current checkout:
  - `ops/tasks/done/` currently runs through `RBR-0772`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` had no `feature-implementation` task at the start of this run; and
  - `ops/state/backlog.md` and the frontier prose in `ops/state/current_status.md` already honestly say that no ready feature follow-on currently survives after the likely same-cycle drain, so this one-task refill does not need a backlog-frontier prose change.
- Queue this directly after `RBR-0771` on the same `module-workflow-surface` owner path so the remaining raw module keyword-error pair lands before pattern keyword publication reopens the frontier.
- 2026-03-20 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `tests/python/test_module_workflow_parity_suite.py` already carries the exact adjacent direct parity anchors `module-fullmatch-unexpected-keyword` and `module-sub-unexpected-keyword` in `MODULE_KEYWORD_ERROR_CASES`;
  - direct publication probes in this run confirmed both `workflow-module-fullmatch-unexpected-keyword` and `workflow-module-sub-unexpected-keyword` are still absent from `tests/conformance/fixtures/module_workflow_surface.py`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_keyword_argument_errors_match_cpython and (module-fullmatch-unexpected-keyword or module-sub-unexpected-keyword)'` passed in this run (`4 passed, 675 deselected`);
  - the current owner path already publishes the adjacent duplicate-keyword trio, leaving this unexpected-keyword pair as the smallest unpublished slice on the same owner file; and
  - no blocked feature task exists to reopen first.

## Completion
- 2026-03-20: Added `workflow-module-fullmatch-unexpected-keyword` and `workflow-module-sub-unexpected-keyword` to `tests/conformance/fixtures/module_workflow_surface.py` as raw `module_call` `str` rows with `include_pattern_arg == True`, preserving the exact `MODULE_KEYWORD_ERROR_CASES` anchors for `fullmatch(missing=...)` and `sub(missing=...)` without widening into pattern keyword rows, bytes siblings, or another manifest.
- Updated `tests/python/test_module_workflow_parity_suite.py` so the shared `module-workflow-surface` owner path now expects `71` published rows, a `47`/`24` `str`/`bytes` split, and `33` published `module_call` rows, while the canonical `module-keyword-error` slice now contains five rows in order: the existing duplicate-keyword trio followed by `workflow-module-fullmatch-unexpected-keyword` and `workflow-module-sub-unexpected-keyword`, mapped back to the matching direct parity anchors in that same order.
- Extended `tests/conformance/test_combined_correctness_scorecards.py` so the tracked scorecard representative case inventory includes the newly published unexpected-keyword slice, then republished `reports/correctness/latest.py`. Reading the tracked artifact shows `1441` total / `1441` passed / `0` unimplemented across `114` manifests, with `module.workflow` at `71/71/0`, `module.workflow.str` at `47/47/0`, `module.workflow.bytes` unchanged at `24/24/0`, and `module.workflow.module_call` at `33/33/0`.
- Verification passed with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0773-module-workflow-module-unexpected-keyword-error-pair.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`.
