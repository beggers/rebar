# RBR-0945: Publish the module-workflow module `split()` unexpected-keyword str/bytes pair

Status: ready
Owner: feature-implementation
Created: 2026-03-22

## Goal
- Reopen the existing `module-workflow-surface` correctness frontier with the adjacent raw module-level `split()` unexpected-keyword str/bytes pair, publishing the exact CPython-visible rejection spellings that the shared owner path already exposes directly before matching Python-path benchmark catch-up or another module-helper family widens the queue.

## Pattern Pair
- `re.split("abc", "abc", missing=1)`
- `re.split(b"abc", b"abc", missing=1)`

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by exactly two new raw `module_call` rows:
  - add `workflow-module-split-unexpected-keyword`;
  - add `workflow-module-split-unexpected-keyword-bytes`;
  - keep both rows pinned to the exact raw module helper calls above with `helper == "split"`, `include_pattern_arg == True`, and `kwargs == {"missing": 1}`;
  - keep `workflow-module-split-unexpected-keyword` on the raw module `str` owner path with `pattern == "abc"` and `args == ["abc"]`;
  - keep `workflow-module-split-unexpected-keyword-bytes` on the raw module `bytes` owner path with `pattern == "abc"` and the existing bytes payload encoding shape for `args == [b"abc"]`;
  - insert `workflow-module-split-unexpected-keyword` immediately after `workflow-module-split-duplicate-maxsplit-keyword`;
  - insert `workflow-module-split-unexpected-keyword-bytes` immediately after `workflow-module-split-unexpected-keyword` and immediately before `workflow-module-sub-duplicate-count-keyword`;
  - categorize the new rows under `["workflow", "split", "literal", ..., "unexpected-keyword"]` with the correct `str` / `bytes` text-model tags; and
  - keep the notes explicit that these are the adjacent raw module-level `split()` unexpected-keyword rejection spellings on the shared module-workflow owner path, not a broader keyword-error dump.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared raw-module keyword-error owner path instead of creating another manifest, another parity suite, or a detached keyword-error table:
  - extend `MODULE_KEYWORD_ERROR_CASES` with exactly two new direct parity anchors:
    - `module-split-unexpected-keyword` with `helper == "split"`, `args == ("abc", "abc")`, and `kwargs == {"missing": 1}`;
    - `module-split-unexpected-keyword-bytes` with `helper == "split"`, `args == (b"abc", b"abc")`, and `kwargs == {"missing": 1}`;
  - extend the canonical published `module-keyword-error` slice so it now contains exactly these eleven rows in order:
    - `workflow-module-search-duplicate-flags-keyword`
    - `workflow-module-split-duplicate-maxsplit-keyword`
    - `workflow-module-split-unexpected-keyword`
    - `workflow-module-split-unexpected-keyword-bytes`
    - `workflow-module-sub-duplicate-count-keyword`
    - `workflow-module-fullmatch-unexpected-keyword`
    - `workflow-module-sub-unexpected-keyword`
    - `workflow-module-sub-unexpected-keyword-after-positional-count`
    - `workflow-module-subn-duplicate-count-keyword-bytes`
    - `workflow-module-subn-unexpected-keyword-bytes`
    - `workflow-module-subn-unexpected-keyword-after-positional-count-bytes`
  - keep the published `str` subset pinned to:
    - `workflow-module-search-duplicate-flags-keyword`
    - `workflow-module-split-duplicate-maxsplit-keyword`
    - `workflow-module-split-unexpected-keyword`
    - `workflow-module-sub-duplicate-count-keyword`
    - `workflow-module-fullmatch-unexpected-keyword`
    - `workflow-module-sub-unexpected-keyword`
    - `workflow-module-sub-unexpected-keyword-after-positional-count`
  - keep the published `bytes` subset pinned to:
    - `workflow-module-split-unexpected-keyword-bytes`
    - `workflow-module-subn-duplicate-count-keyword-bytes`
    - `workflow-module-subn-unexpected-keyword-bytes`
    - `workflow-module-subn-unexpected-keyword-after-positional-count-bytes`
  - update the direct-case alignment so those eleven published rows map back to the exact direct anchors above, plus `module-search-duplicate-flags-keyword`, `module-split-duplicate-maxsplit-keyword`, `module-sub-duplicate-count-keyword`, `module-fullmatch-unexpected-keyword`, `module-sub-unexpected-keyword`, `module-sub-unexpected-keyword-after-positional-count`, `module-subn-duplicate-count-keyword-bytes`, `module-subn-unexpected-keyword-bytes`, and `module-subn-unexpected-keyword-after-positional-count-bytes`, in the same order;
  - move the published raw module keyword-error slice from `9` rows to `11`;
  - move the slice text-model split from `6` `str` / `3` `bytes` to `7` / `4`;
  - keep the slice helper breakdown honest at `search: 1`, `split: 3`, `sub: 3`, `fullmatch: 1`, and `subn: 3`;
  - update the full `module-workflow-surface` bundle expectations from `171` rows to `173`;
  - move `module.workflow.str` from `96` to `97` and `module.workflow.bytes` from `75` to `76`;
  - move `module.workflow.module_call` from `91` to `93`;
  - keep `module.workflow.pattern_call` at `68` in this run; and
  - keep the overall module-call helper counter honest by moving `split` from `12` to `14` while leaving the other helper totals unchanged.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1545` total / `1545` passed / `0` unimplemented across `114` manifests to `1547` / `1547` / `0` across the same `114` manifests;
  - `module.workflow` moves from `171` / `171` / `0` to `173` / `173` / `0`;
  - `module.workflow.str` moves from `96` / `96` / `0` to `97` / `97` / `0`;
  - `module.workflow.bytes` moves from `75` / `75` / `0` to `76` / `76` / `0`;
  - `module.workflow.module_call` moves from `91` / `91` / `0` to `93` / `93` / `0`;
  - `module.workflow.pattern_call` stays `68` / `68` / `0`; and
  - at least one of the two new raw module `split()` unexpected-keyword rows is visible in the tracked scorecard as a representative `module-workflow-surface` module-call case.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module-split-unexpected-keyword or module_workflow_surface_publishes_module_keyword_error_slice_from_direct_cases'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0945-module-workflow-module-split-unexpected-keyword-str-bytes-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or benchmark-side selector logic in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached raw-module keyword publication file.
- Keep the scope pinned to the two raw module `split()` unexpected-keyword rows above. Leave the matching Python-path benchmark catch-up on `benchmarks/workloads/collection_replacement_boundary.py` for a later task.

## Notes
- `RBR-0945` is the next available feature task id in the current checkout:
  - `RBR-0943` is the latest done feature task on this frontier;
  - `RBR-0944` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after the drained raw module positional-count keyword-error catch-up so the same raw module collection/replacement owner path reopens through the adjacent `split()` unexpected-keyword slice before matching benchmark catch-up or another owner family widens the queue.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier while the exact publication rows are still absent:
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... re.split("abc", "abc", missing=1) ... rebar.split("abc", "abc", missing=1) ... re.split(b"abc", b"abc", missing=1) ... rebar.split(b"abc", b"abc", missing=1) ... PY` shows CPython and `rebar` already agree on the exact bounded `TypeError.args`: `("split() got an unexpected keyword argument 'missing'",)` for both the `str` and `bytes` spellings;
  - `rg -n 'workflow-module-split-unexpected-keyword\"|workflow-module-split-unexpected-keyword-bytes\"|module-split-unexpected-keyword-purged-str\"|module-split-unexpected-keyword-purged-bytes\"' tests/conformance/fixtures/module_workflow_surface.py reports/correctness/latest.py tests/conformance/test_combined_correctness_scorecards.py benchmarks/workloads/collection_replacement_boundary.py reports/benchmarks/latest.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently returns no matches, so both exact raw publication ids and their matching raw benchmark ids are still absent in this checkout;
  - `reports/correctness/latest.py` currently reports `1545` total / `1545` passed / `0` unimplemented across `114` manifests, with `module.workflow` at `171`, `module.workflow.str` at `96`, `module.workflow.bytes` at `75`, `module.workflow.module_call` at `91`, and `module.workflow.pattern_call` at `68`; and
  - `reports/benchmarks/latest.py` currently reports `893` total / `893` measured / `0` known gaps across `30` manifests, so this run should stay on correctness publication instead of skipping ahead to benchmark-only changes.
