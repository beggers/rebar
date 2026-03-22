# RBR-0916: Publish the module-workflow `Pattern.sub()` / `Pattern.subn()` unexpected-keyword pair

Status: done
Owner: feature-implementation
Created: 2026-03-22
Completed: 2026-03-22

## Goal
- Reopen the existing `module-workflow-surface` correctness frontier immediately after `RBR-0914` by publishing the exact direct `Pattern.sub()` / `Pattern.subn()` unexpected-keyword rejection pair on the shared bound-pattern error owner path, while leaving the Python-path benchmark frontier unchanged in this run because the benchmark catch-up should follow the corrected published slice rather than outrun it.

## Pattern Pair
- `re.compile("abc").sub("x", "abc", missing=1)`
- `re.compile(b"abc").subn(b"x", b"abc", missing=1)`

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing direct bound-pattern error owner path instead of creating another fixture file, another parity suite, or a detached keyword-error table:
  - assume `RBR-0914` has already landed the matching runtime parity; if that prerequisite is missing, stop and finish `RBR-0914` first instead of re-implementing the same parity work here;
  - extend the shared direct bound-pattern error publication assertion by exactly two newly published direct cases:
    - `pattern-sub-unexpected-keyword-str`
    - `pattern-subn-unexpected-keyword-bytes`
  - add a focused published direct bound-pattern keyword-error fixture assertion path that maps exactly four published rows:
    - `workflow-pattern-sub-duplicate-count-keyword-str`
    - `workflow-pattern-sub-unexpected-keyword-str`
    - `workflow-pattern-subn-duplicate-count-keyword-bytes`
    - `workflow-pattern-subn-unexpected-keyword-bytes`
  - keep the existing direct bound-pattern keyword-helper subset unchanged at `27` rows, keep the published direct bound-pattern positional `__index__` subset unchanged at `9` rows, and keep the already-published wrong-text-model bound-pattern error cases on the same owner path unchanged in this run;
  - update the full `module-workflow-surface` bundle expectations from `156` rows to `158`, with the text-model split moving from `89` `str` / `67` `bytes` to `90` / `68`;
  - keep `module_call` expectations unchanged at `85` rows;
  - move `pattern_call` expectations from `59` rows to `61`; and
  - move the published `pattern_call` helper breakdown from `sub: 6` / `subn: 6` to `sub: 7` / `subn: 7` without widening into direct `Pattern.split()` duplicate-`maxsplit=` publication or benchmark/report regeneration beyond the correctness report in this run.
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by exactly two new `pattern_call` rows:
  - add `workflow-pattern-sub-unexpected-keyword-str`;
  - add `workflow-pattern-subn-unexpected-keyword-bytes`;
  - keep both rows on the existing direct bound-pattern owner path with no module-level wrapper call, `kwargs == {"missing": 1}`, and the exact direct argument payloads above;
  - insert `workflow-pattern-sub-unexpected-keyword-str` immediately after `workflow-pattern-sub-duplicate-count-keyword-str` and immediately before `workflow-pattern-subn-count-keyword-str`;
  - insert `workflow-pattern-subn-unexpected-keyword-bytes` immediately after `workflow-pattern-subn-duplicate-count-keyword-bytes` and immediately before `workflow-pattern-search-str-pos-indexlike-positional`;
  - categorize the new rows under `["workflow", ..., "literal", ..., "unexpected-keyword"]` with the correct `sub` / `subn` helper tag and `str` / `bytes` text-model tag; and
  - keep the notes explicit that these are the direct bound-pattern unexpected-keyword rejection spellings adjacent to the already published direct replacement keyword rows, not a broader bound-pattern keyword-error dump.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1530` total / `1530` passed / `0` unimplemented across `114` manifests to `1532` / `1532` / `0` across the same `114` manifests;
  - `module.workflow` moves from `156` / `156` / `0` to `158` / `158` / `0`;
  - `module.workflow.str` moves from `89` / `89` / `0` to `90` / `90` / `0`;
  - `module.workflow.bytes` moves from `67` / `67` / `0` to `68` / `68` / `0`;
  - `module.workflow.module_call` stays `85` / `85` / `0`;
  - `module.workflow.pattern_call` moves from `59` / `59` / `0` to `61` / `61` / `0`; and
  - the two new direct bound-pattern unexpected-keyword rows are visible in the tracked scorecard as representative `module-workflow-surface` pattern-call cases.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-sub-unexpected-keyword-str or pattern-subn-unexpected-keyword-bytes or module_workflow_surface_publishes_pattern_keyword_error_slice_from_direct_cases'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0916-module-workflow-pattern-sub-subn-unexpected-keyword-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or benchmark-side selector logic in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached direct bound-pattern keyword-error publication file.
- Keep the scope pinned to the unexpected-keyword pair above. Leave direct `Pattern.split()` duplicate-`maxsplit=` publication and any benchmark catch-up for later tasks.
- Assume `RBR-0914` has already landed the matching runtime parity. If it has not, stop and finish `RBR-0914` first instead of widening this task.

## Notes
- `RBR-0916` is the next available feature task id in the current checkout:
  - `RBR-0914` is already occupied by the latest done feature task on this frontier;
  - `RBR-0915` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0914` on the same shared direct bound-pattern replacement frontier so the exact unexpected-keyword diagnostics reach the tracked correctness surface before Python-path benchmark catch-up or adjacent direct `Pattern.split()` duplicate-`maxsplit=` publication widen the error slice.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier while the exact publication rows are still missing:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-sub-unexpected-keyword-str or pattern-subn-unexpected-keyword-bytes'` is now green because `RBR-0914` already landed the matching direct bound-pattern parity;
  - `rg -n 'workflow-pattern-sub-unexpected-keyword|workflow-pattern-subn-unexpected-keyword' tests/conformance benchmarks/workloads reports tests/benchmarks` returned no matches in this run, so the exact direct bound-pattern publication and benchmark rows are still absent;
  - `reports/correctness/latest.py` currently reports `1530` total / `1530` passed / `0` unimplemented across `114` manifests, with `module.workflow` at `156`, `module.workflow.str` at `89`, `module.workflow.bytes` at `67`, `module.workflow.module_call` at `85`, and `module.workflow.pattern_call` at `59`; and
  - `reports/benchmarks/latest.py` already reports `878` total / `878` measured / `0` known gaps across `30` manifests, so this run stays on the correctness-publication step instead of skipping ahead to another benchmark-only refresh.

## Completion
- Added exactly two `pattern_call` publication rows to `tests/conformance/fixtures/module_workflow_surface.py`: `workflow-pattern-sub-unexpected-keyword-str` and `workflow-pattern-subn-unexpected-keyword-bytes`, in the required positions beside the existing direct bound-pattern replacement keyword-error rows.
- Extended `tests/python/test_module_workflow_parity_suite.py` so the focused direct bound-pattern keyword-error publication selector now maps exactly four rows back to the landed runtime direct cases: the existing duplicate-`count=` pair plus the new unexpected-keyword pair, while keeping the 27-row helper subset and 9-row positional `__index__` subset unchanged.
- Updated the module-workflow bundle expectations in `tests/python/test_module_workflow_parity_suite.py` to `158` total rows with `90` `str`, `68` `bytes`, `61` `pattern_call`, and `sub: 7` / `subn: 7`, leaving `module_call` unchanged at `85`.
- Refreshed `tests/conformance/test_combined_correctness_scorecards.py` representative coverage and republished `reports/correctness/latest.py`; the tracked report file remains in the diff and now reports `1532` total / `1532` passed / `0` unimplemented across `114` manifests, with `module.workflow` at `158`, `module.workflow.str` at `90`, `module.workflow.bytes` at `68`, `module.workflow.module_call` unchanged at `85`, and `module.workflow.pattern_call` at `61`.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-sub-unexpected-keyword-str or pattern-subn-unexpected-keyword-bytes or module_workflow_surface_publishes_pattern_keyword_error_slice_from_direct_cases'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0916-module-workflow-pattern-sub-subn-unexpected-keyword-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`
