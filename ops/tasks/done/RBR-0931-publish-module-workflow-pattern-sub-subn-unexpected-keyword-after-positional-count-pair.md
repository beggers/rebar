# RBR-0931: Publish the module-workflow `Pattern.sub()` / `Pattern.subn()` unexpected-keyword-after-positional-count pair

Status: done
Owner: feature-implementation
Created: 2026-03-22
Completed: 2026-03-22

## Goal
- Reopen the existing `module-workflow-surface` correctness frontier with the adjacent direct bound-`Pattern` `sub()` / `subn()` unexpected-keyword-after-positional-count pair, so the shared collection/replacement owner path publishes the already-landed CPython-visible `TypeError` behavior before Python-path benchmark catch-up or another direct helper family widens the queue.

## Pattern Pair
- `re.compile("abc").sub("x", "abc", 1, missing=1)`
- `re.compile(b"abc").subn(b"x", b"abc", 1, missing=1)`

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing direct bound-pattern error owner path instead of creating another fixture file, another parity suite, or a detached keyword-error table:
  - assume the matching runtime parity is already landed; if either direct case is missing, stop and finish that runtime parity first instead of re-implementing the same behavior here;
  - extend the shared direct bound-pattern error publication assertion by exactly two newly published direct cases:
    - `pattern-sub-unexpected-keyword-after-positional-count-str`
    - `pattern-subn-unexpected-keyword-after-positional-count-bytes`;
  - update the focused published direct bound-pattern keyword-error fixture assertion path so it now maps exactly eight published rows:
    - `workflow-pattern-split-duplicate-maxsplit-keyword-str`
    - `workflow-pattern-split-unexpected-keyword-bytes`
    - `workflow-pattern-sub-duplicate-count-keyword-str`
    - `workflow-pattern-sub-unexpected-keyword-str`
    - `workflow-pattern-sub-unexpected-keyword-after-positional-count-str`
    - `workflow-pattern-subn-duplicate-count-keyword-bytes`
    - `workflow-pattern-subn-unexpected-keyword-bytes`
    - `workflow-pattern-subn-unexpected-keyword-after-positional-count-bytes`;
  - keep the existing direct bound-pattern keyword-helper subset unchanged at `27` rows, keep the published direct bound-pattern positional `__index__` subset unchanged at `9` rows, and keep the already-published wrong-text-model bound-pattern error cases on the same owner path unchanged in this run;
  - update the full `module-workflow-surface` bundle expectations from `163` rows to `165`, with the text-model split moving from `93` `str` / `70` `bytes` to `94` / `71`;
  - keep `module_call` expectations unchanged at `85` rows;
  - move `pattern_call` expectations from `66` rows to `68`; and
  - move the published `pattern_call` helper breakdown from `split: 7` / `sub: 8` / `subn: 8` to `split: 7` / `sub: 9` / `subn: 9` without widening into benchmark/report regeneration beyond the correctness report in this run.
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by exactly two new `pattern_call` rows:
  - add `workflow-pattern-sub-unexpected-keyword-after-positional-count-str`;
  - add `workflow-pattern-subn-unexpected-keyword-after-positional-count-bytes`;
  - keep both rows on the existing direct bound-pattern owner path with no module-level wrapper call, `kwargs == {"missing": 1}`, and the exact direct argument payloads above with the positional count already present;
  - insert `workflow-pattern-sub-unexpected-keyword-after-positional-count-str` immediately after `workflow-pattern-sub-unexpected-keyword-str` and immediately before `workflow-pattern-sub-str-pattern-on-bytes-string`;
  - insert `workflow-pattern-subn-unexpected-keyword-after-positional-count-bytes` immediately after `workflow-pattern-subn-unexpected-keyword-bytes` and immediately before `workflow-pattern-subn-bytes-pattern-on-str-string`;
  - categorize the new rows under `["workflow", ..., "literal", ..., "unexpected-keyword"]` with the correct `sub` / `subn` helper tags and `str` / `bytes` text-model tags; and
  - keep the notes explicit that these are the direct bound `Pattern.sub()` / `Pattern.subn()` unexpected-keyword rejection spellings with a positional count already supplied, adjacent to the already-published replacement keyword rows, not a broader bound-pattern keyword-error dump.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1537` total / `1537` passed / `0` unimplemented across `114` manifests to `1539` / `1539` / `0` across the same `114` manifests;
  - `module.workflow` moves from `163` / `163` / `0` to `165` / `165` / `0`;
  - `module.workflow.str` moves from `93` / `93` / `0` to `94` / `94` / `0`;
  - `module.workflow.bytes` moves from `70` / `70` / `0` to `71` / `71` / `0`;
  - `module.workflow.module_call` stays `85` / `85` / `0`;
  - `module.workflow.pattern_call` moves from `66` / `66` / `0` to `68` / `68` / `0`; and
  - the two new direct bound-pattern positional-count keyword-error rows are visible in the tracked scorecard as representative `module-workflow-surface` pattern-call cases.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-sub-unexpected-keyword-after-positional-count-str or pattern-subn-unexpected-keyword-after-positional-count-bytes or module_workflow_surface_publishes_pattern_keyword_error_slice_from_direct_cases'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0931-module-workflow-pattern-sub-subn-unexpected-keyword-after-positional-count-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or benchmark-side selector logic in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached direct bound-pattern keyword-error publication file.
- Keep the scope pinned to the positional-count-plus-unexpected-keyword pair above. Leave the direct `Pattern.sub()` / `Pattern.subn()` benchmark catch-up for a later task.

## Notes
- `RBR-0931` is the next available feature task id in the current checkout:
  - `RBR-0929` is the latest done feature task on this frontier;
  - `RBR-0930` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0929` / `RBR-0930` on the same shared direct bound-pattern collection/replacement owner path so the exact positional-count unexpected-keyword diagnostics reach the tracked correctness surface before Python-path benchmark catch-up or another helper family widens the queue.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier while the exact publication rows are still missing:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-sub-unexpected-keyword-after-positional-count-str or pattern-subn-unexpected-keyword-after-positional-count-bytes'` currently passes in this checkout (`8 passed, 1356 deselected`), so the direct `Pattern.sub()` / `Pattern.subn()` owner path already exposes the exact bounded error pair that this task needs to publish;
  - `rg -n 'workflow-pattern-sub-unexpected-keyword-after-positional-count-str|workflow-pattern-subn-unexpected-keyword-after-positional-count-bytes' tests/conformance/fixtures/module_workflow_surface.py reports/correctness/latest.py tests/conformance/test_combined_correctness_scorecards.py` returned no matches in this run, so the exact direct bound-pattern publication rows are still absent;
  - `reports/correctness/latest.py` currently reports `1537` total / `1537` passed / `0` unimplemented across `114` manifests, with `module.workflow` at `163`, `module.workflow.str` at `93`, `module.workflow.bytes` at `70`, `module.workflow.module_call` at `85`, and `module.workflow.pattern_call` at `66`; and
  - `reports/benchmarks/latest.py` already reports `885` total / `885` measured / `0` known gaps across `30` manifests, so this run stays on the correctness-publication step instead of skipping ahead to another benchmark-only refresh.

## Completion
- Added `workflow-pattern-sub-unexpected-keyword-after-positional-count-str` and `workflow-pattern-subn-unexpected-keyword-after-positional-count-bytes` to `tests/conformance/fixtures/module_workflow_surface.py` on the existing direct bound `Pattern.sub()` / `Pattern.subn()` owner path, in the required positions immediately after the adjacent unexpected-keyword rows and before the already-published wrong-text-model rows.
- Updated `tests/python/test_module_workflow_parity_suite.py` so the published direct bound-pattern keyword-error selector now maps the exact eight-row slice, while keeping the published bound-pattern keyword-helper subset at `27` rows and the published positional `__index__` subset at `9` rows. The module-workflow bundle assertions now track `165` total rows with `94` `str`, `71` `bytes`, `85` `module_call`, and `68` `pattern_call` rows, and the published `pattern_call` helper breakdown now carries `split: 7`, `sub: 9`, and `subn: 9`.
- Updated `tests/conformance/test_combined_correctness_scorecards.py` to treat the two new `module-workflow-surface` rows as representative pattern-call cases, then regenerated `reports/correctness/latest.py`. The tracked published artifact remains in the diff and now reports `1539` total / `1539` passed / `0` unimplemented across `114` manifests, with `module.workflow` at `165`, `module.workflow.str` at `94`, `module.workflow.bytes` at `71`, `module.workflow.module_call` unchanged at `85`, and `module.workflow.pattern_call` at `68`. The tracked report now contains both new case ids.
- Left benchmark manifests, benchmark reports, README text, and implementation files unchanged in this run.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-sub-unexpected-keyword-after-positional-count-str or pattern-subn-unexpected-keyword-after-positional-count-bytes or module_workflow_surface_publishes_pattern_keyword_error_slice_from_direct_cases'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0931-module-workflow-pattern-sub-subn-unexpected-keyword-after-positional-count-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`
