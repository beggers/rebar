# RBR-0923: Publish the module-workflow `Pattern.split()` keyword-error pair

Status: done
Owner: feature-implementation
Created: 2026-03-22
Completed: 2026-03-22

## Goal
- Reopen the existing `module-workflow-surface` correctness frontier immediately after `RBR-0921` by publishing the exact direct `Pattern.split()` duplicate-`maxsplit=` / unexpected-keyword rejection pair on the shared bound-pattern error owner path, while leaving the Python-path benchmark frontier unchanged in this run because the benchmark catch-up should follow the corrected published slice rather than outrun it.

## Pattern Pair
- `re.compile("abc").split("abcabc", 1, maxsplit=1)`
- `re.compile(b"abc").split(b"abcabc", missing=1)`

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing direct bound-pattern error owner path instead of creating another fixture file, another parity suite, or a detached keyword-error table:
  - assume `RBR-0921` has already landed the matching runtime parity; if that prerequisite is missing, stop and finish `RBR-0921` first instead of re-implementing the same parity work here;
  - extend the shared direct bound-pattern error publication assertion by exactly two newly published direct cases:
    - `pattern-split-duplicate-maxsplit-keyword-str`
    - `pattern-split-unexpected-keyword-bytes`
  - update the focused published direct bound-pattern keyword-error fixture assertion path so it now maps exactly six published rows:
    - `workflow-pattern-split-duplicate-maxsplit-keyword-str`
    - `workflow-pattern-split-unexpected-keyword-bytes`
    - `workflow-pattern-sub-duplicate-count-keyword-str`
    - `workflow-pattern-sub-unexpected-keyword-str`
    - `workflow-pattern-subn-duplicate-count-keyword-bytes`
    - `workflow-pattern-subn-unexpected-keyword-bytes`
  - keep the existing direct bound-pattern keyword-helper subset unchanged at `27` rows, keep the published direct bound-pattern positional `__index__` subset unchanged at `9` rows, and keep the already-published wrong-text-model bound-pattern error cases on the same owner path unchanged in this run;
  - update the full `module-workflow-surface` bundle expectations from `158` rows to `160`, with the text-model split moving from `90` `str` / `68` `bytes` to `91` / `69`;
  - keep `module_call` expectations unchanged at `85` rows;
  - move `pattern_call` expectations from `61` rows to `63`; and
  - move the published `pattern_call` helper breakdown from `split: 4` / `sub: 7` / `subn: 7` to `split: 6` / `sub: 7` / `subn: 7` without widening into direct `Pattern.sub()` / `Pattern.subn()` benchmark work, raw-module helper diagnostics, or benchmark/report regeneration beyond the correctness report in this run.
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by exactly two new `pattern_call` rows:
  - add `workflow-pattern-split-duplicate-maxsplit-keyword-str`;
  - add `workflow-pattern-split-unexpected-keyword-bytes`;
  - keep both rows on the existing direct bound-pattern owner path with no module-level wrapper call, the exact direct argument payloads above, and `kwargs == {"maxsplit": 1}` / `kwargs == {"missing": 1}`;
  - insert `workflow-pattern-split-duplicate-maxsplit-keyword-str` immediately after `workflow-pattern-split-str-maxsplit-bool-true` and immediately before `workflow-pattern-split-unexpected-keyword-bytes`;
  - insert `workflow-pattern-split-unexpected-keyword-bytes` immediately after `workflow-pattern-split-duplicate-maxsplit-keyword-str` and immediately before `workflow-pattern-sub-count-keyword-bytes`;
  - categorize the new rows under `["workflow", ..., "literal", ..., "duplicate-keyword"]` / `["workflow", ..., "literal", ..., "unexpected-keyword"]` with the correct `split` helper tag and `str` / `bytes` text-model tag; and
  - keep the notes explicit that these are the direct bound `Pattern.split()` duplicate-`maxsplit=` and unexpected-keyword rejection spellings adjacent to the already published direct `Pattern.split()` maxsplit carriers and direct replacement keyword-error rows, not a broader bound-pattern keyword-error dump.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1532` total / `1532` passed / `0` unimplemented across `114` manifests to `1534` / `1534` / `0` across the same `114` manifests;
  - `module.workflow` moves from `158` / `158` / `0` to `160` / `160` / `0`;
  - `module.workflow.str` moves from `90` / `90` / `0` to `91` / `91` / `0`;
  - `module.workflow.bytes` moves from `68` / `68` / `0` to `69` / `69` / `0`;
  - `module.workflow.module_call` stays `85` / `85` / `0`;
  - `module.workflow.pattern_call` moves from `61` / `61` / `0` to `63` / `63` / `0`; and
  - the two new direct bound-pattern split keyword-error rows are visible in the tracked scorecard as representative `module-workflow-surface` pattern-call cases.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-split-duplicate-maxsplit-keyword-str or pattern-split-unexpected-keyword-bytes or module_workflow_surface_publishes_pattern_keyword_error_slice_from_direct_cases'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0923-module-workflow-pattern-split-keyword-error-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or benchmark-side selector logic in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached direct bound-pattern keyword-error publication file.
- Keep the scope pinned to the duplicate-`maxsplit=` / unexpected-keyword pair above. Leave direct `Pattern.split()` benchmark catch-up for a later task.
- Assume `RBR-0921` has already landed the matching runtime parity. If it has not, stop and finish `RBR-0921` first instead of widening this task.

## Notes
- `RBR-0923` is the next available feature task id in the current checkout:
  - `RBR-0921` is already occupied by the latest done feature task on this frontier;
  - `RBR-0922` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0921` on the same shared direct bound-pattern collection/replacement frontier so the exact direct `Pattern.split()` keyword-error diagnostics reach the tracked correctness surface before Python-path benchmark catch-up widens the same owner path.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier while the exact publication rows are still missing:
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... re.compile("abc").split("abcabc", 1, maxsplit=1) ... rebar.compile("abc").split("abcabc", 1, maxsplit=1) ... re.compile(b"abc").split(b"abcabc", missing=1) ... rebar.compile(b"abc").split(b"abcabc", missing=1) ... PY` now shows CPython and `rebar` agree on the exact direct `TypeError.args`: `("split() takes at most 2 arguments (3 given)",)` and `("'missing' is an invalid keyword argument for split()",)`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-split-duplicate-maxsplit-keyword-str or pattern-split-unexpected-keyword-bytes'` is green in this checkout, so the direct `Pattern.split()` owner path already exposes the exact bounded error pair that this task needs to publish;
  - `rg -n 'workflow-pattern-split-duplicate-maxsplit-keyword-str|workflow-pattern-split-unexpected-keyword-bytes' tests/conformance benchmarks/workloads reports tests/benchmarks` returned no matches in this run, so the exact direct bound-pattern publication and benchmark rows are still absent; and
  - `reports/correctness/latest.py` currently reports `1532` total / `1532` passed / `0` unimplemented across `114` manifests, with `module.workflow` at `158`, `module.workflow.str` at `90`, `module.workflow.bytes` at `68`, `module.workflow.module_call` at `85`, and `module.workflow.pattern_call` at `61`.

## Completion
- Added `workflow-pattern-split-duplicate-maxsplit-keyword-str` and `workflow-pattern-split-unexpected-keyword-bytes` to `tests/conformance/fixtures/module_workflow_surface.py` on the existing direct bound `Pattern.split()` owner path, in the required order immediately after `workflow-pattern-split-str-maxsplit-bool-true` and before the adjacent `Pattern.sub()` / `Pattern.subn()` keyword rows.
- Updated `tests/python/test_module_workflow_parity_suite.py` so the published bound-pattern keyword-error selector now maps the exact six-row direct slice, while keeping the published bound-pattern keyword-helper subset at `27` rows and the published positional `__index__` subset at `9` rows. The module-workflow bundle assertions now track `160` total rows with `91` `str`, `69` `bytes`, `85` `module_call`, and `63` `pattern_call` rows, and the published `pattern_call` helper breakdown now carries `split: 6`, `sub: 7`, and `subn: 7`.
- Updated `tests/conformance/test_combined_correctness_scorecards.py` to treat the two new `module-workflow-surface` rows as representative pattern-call cases, then regenerated `reports/correctness/latest.py`. The tracked published artifact now reports `1534` total / `1534` passed / `0` unimplemented across `114` manifests, with `module.workflow` at `160`, `module.workflow.str` at `91`, `module.workflow.bytes` at `69`, `module.workflow.module_call` unchanged at `85`, and `module.workflow.pattern_call` at `63`. The tracked report now contains both new case ids.
- Left benchmark manifests, benchmark reports, README text, and implementation files unchanged in this run.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-split-duplicate-maxsplit-keyword-str or pattern-split-unexpected-keyword-bytes or module_workflow_surface_publishes_pattern_keyword_error_slice_from_direct_cases'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0923-module-workflow-pattern-split-keyword-error-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`
