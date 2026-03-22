# RBR-0939: Publish the module-workflow module `subn()` keyword-error bytes pair

Status: ready
Owner: feature-implementation
Created: 2026-03-22

## Goal
- Reopen the existing `module-workflow-surface` correctness frontier with the missing raw module-level `subn()` bytes keyword-error pair, publishing the exact duplicate-count and unexpected-keyword rejections that the shared owner path already exercises directly before the later positional-count-plus-extra-keyword follow-on or another owner family widens the queue.

## Pattern Pair
- `re.subn(b"abc", b"x", b"abc", 1, count=1)`
- `re.subn(b"abc", b"x", b"abc", missing=1)`

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by exactly two new raw `module_call` rows:
  - add `workflow-module-subn-duplicate-count-keyword-bytes`;
  - add `workflow-module-subn-unexpected-keyword-bytes`;
  - keep both rows pinned to the exact direct parity anchors already defined in `MODULE_KEYWORD_ERROR_CASES`:
    - `module-subn-duplicate-count-keyword-bytes`: `helper == "subn"`, `args == [b"x", b"abc", 1]`, and `kwargs == {"count": 1}`;
    - `module-subn-unexpected-keyword-bytes`: `helper == "subn"`, `args == [b"x", b"abc"]`, and `kwargs == {"missing": 1}`;
  - keep both rows on the raw module owner path with `pattern == "abc"`, `helper == "subn"`, `text_model == "bytes"`, and `include_pattern_arg == True`;
  - insert `workflow-module-subn-duplicate-count-keyword-bytes` immediately after `workflow-module-subn-count-bool-true-bytes`;
  - insert `workflow-module-subn-unexpected-keyword-bytes` immediately after `workflow-module-subn-duplicate-count-keyword-bytes` and immediately before `workflow-module-split-maxsplit-indexlike-positional-bytes`;
  - categorize the new rows under `["workflow", "subn", "literal", "bytes", ...]` with the appropriate `count` plus `duplicate-keyword` or `unexpected-keyword` tags; and
  - do not widen into `workflow-module-sub-unexpected-keyword-after-positional-count`, `workflow-module-subn-unexpected-keyword-after-positional-count-bytes`, benchmark manifests, or another correctness owner file in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared raw-module keyword-error owner path instead of creating another manifest, another parity suite, or a detached keyword-error table:
  - extend the canonical published `module-keyword-error` slice so it now contains exactly these seven rows in order:
    - `workflow-module-search-duplicate-flags-keyword`
    - `workflow-module-split-duplicate-maxsplit-keyword`
    - `workflow-module-sub-duplicate-count-keyword`
    - `workflow-module-fullmatch-unexpected-keyword`
    - `workflow-module-sub-unexpected-keyword`
    - `workflow-module-subn-duplicate-count-keyword-bytes`
    - `workflow-module-subn-unexpected-keyword-bytes`
  - keep the published `str` subset pinned to the first five rows above and add a new published `bytes` subset with exactly:
    - `workflow-module-subn-duplicate-count-keyword-bytes`
    - `workflow-module-subn-unexpected-keyword-bytes`
  - update the direct-case alignment so those seven published rows map back to the exact direct anchors `module-search-duplicate-flags-keyword`, `module-split-duplicate-maxsplit-keyword`, `module-sub-duplicate-count-keyword`, `module-fullmatch-unexpected-keyword`, `module-sub-unexpected-keyword`, `module-subn-duplicate-count-keyword-bytes`, and `module-subn-unexpected-keyword-bytes` in the same order;
  - move the published raw module keyword-error slice from `5` rows to `7`;
  - keep the slice helper breakdown honest at `search: 1`, `split: 1`, `sub: 2`, `fullmatch: 1`, and `subn: 2`;
  - update the full `module-workflow-surface` bundle expectations from `167` rows to `169`;
  - keep `module.workflow.str` at `95` and move `module.workflow.bytes` from `72` to `74`;
  - move `module.workflow.module_call` from `87` to `89`; and
  - keep `module.workflow.pattern_call` at `68` in this run.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1541` total / `1541` passed / `0` unimplemented across `114` manifests to `1543` / `1543` / `0` across the same `114` manifests;
  - `module.workflow` moves from `167` / `167` / `0` to `169` / `169` / `0`;
  - `module.workflow.str` stays `95` / `95` / `0`;
  - `module.workflow.bytes` moves from `72` / `72` / `0` to `74` / `74` / `0`;
  - `module.workflow.module_call` moves from `87` / `87` / `0` to `89` / `89` / `0`;
  - `module.workflow.pattern_call` stays `68` / `68` / `0`; and
  - at least one of the new raw module `subn()` bytes rows is visible in the tracked scorecard as a representative `module-workflow-surface` module-call case.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module-subn-duplicate-count-keyword-bytes or module-subn-unexpected-keyword-bytes or module_workflow_surface_publishes_module_keyword_error_slice_from_direct_cases'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0939-module-workflow-module-subn-keyword-error-bytes-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or benchmark-side selector logic in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached raw-module keyword publication file.
- Keep the scope pinned to the two raw module `subn()` bytes keyword-error rows above. Leave the later positional-count-plus-unexpected-keyword raw-module follow-on and any Python-path benchmark catch-up for later tasks.

## Notes
- `RBR-0939` is the next available feature task id in the current checkout:
  - `RBR-0937` is the latest done feature task on the adjacent keyword-error frontier;
  - `RBR-0938` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after the drained compiled-pattern positional-count keyword-error catch-up so the raw module keyword-error owner path closes its still-missing `subn()` bytes base pair before the later raw-module positional-count follow-on or another owner family widens the queue.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier while the exact publication rows are still absent:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module-subn-duplicate-count-keyword-bytes or module-subn-unexpected-keyword-bytes'` currently passes in this checkout (`4 passed, 1361 deselected`), so the raw module owner path already exposes the exact bounded bytes pair that this task needs to publish;
  - `rg -n 'workflow-module-subn-duplicate-count-keyword-bytes|workflow-module-subn-unexpected-keyword-bytes' tests/conformance/fixtures/module_workflow_surface.py reports/correctness/latest.py tests/conformance/test_combined_correctness_scorecards.py` returned no matches in this run, so the exact raw module publication rows are still absent;
  - `rg -n 'module-subn-duplicate-count-keyword-warm-bytes|module-subn-unexpected-keyword-purged-bytes' benchmarks/workloads/collection_replacement_boundary.py reports/benchmarks/latest.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` returned no matches in this run, so the matching Python-path benchmark catch-up is also still queued behind this publication step;
  - `reports/correctness/latest.py` currently reports `1541` total / `1541` passed / `0` unimplemented across `114` manifests; and
  - `reports/benchmarks/latest.py` currently reports `889` total / `889` measured / `0` known gaps across `30` manifests, so this run stays on correctness publication instead of skipping ahead to benchmark-only changes.
