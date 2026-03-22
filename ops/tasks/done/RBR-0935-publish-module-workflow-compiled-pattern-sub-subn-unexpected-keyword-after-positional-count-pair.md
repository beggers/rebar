# RBR-0935: Publish the module-workflow compiled-pattern `sub()` / `subn()` unexpected-keyword-after-positional-count pair

Status: done
Owner: feature-implementation
Created: 2026-03-22
Completed: 2026-03-22

## Goal
- Reopen the existing `module-workflow-surface` correctness frontier with the adjacent compiled-pattern-first-argument `sub()` / `subn()` unexpected-keyword-after-positional-count pair, so the shared module-helper owner path publishes the already-landed CPython-visible `TypeError` behavior before Python-path benchmark catch-up or another compiled-pattern keyword family widens the queue.

## Pattern Pair
- `re.sub(re.compile("abc"), "x", "abc", 1, missing=1)`
- `re.subn(re.compile(b"abc"), b"x", b"abc", 1, missing=1)`

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by exactly two new compiled-pattern `module_call` rows:
  - add `workflow-module-sub-unexpected-keyword-after-positional-count-str-compiled-pattern`;
  - add `workflow-module-subn-unexpected-keyword-after-positional-count-bytes-compiled-pattern`;
  - keep both rows on the existing compiled-pattern module-helper owner path with `use_compiled_pattern == True`, the exact positional argument payloads above, and `kwargs == {"missing": 1}`;
  - insert `workflow-module-sub-unexpected-keyword-after-positional-count-str-compiled-pattern` immediately after `workflow-module-sub-unexpected-keyword-str-compiled-pattern` and immediately before `workflow-module-sub-str-compiled-pattern-on-bytes-string`;
  - insert `workflow-module-subn-unexpected-keyword-after-positional-count-bytes-compiled-pattern` immediately after `workflow-module-subn-unexpected-keyword-bytes-compiled-pattern` and immediately before `workflow-module-subn-bytes-compiled-pattern-on-str-string`;
  - categorize the new rows under `["workflow", ..., "unexpected-keyword", "compiled-pattern"]` with the correct `sub` / `subn` helper tags and `str` / `bytes` text-model tags; and
  - keep the notes explicit that these are the compiled-pattern module-level `sub()` / `subn()` unexpected-keyword rejection spellings with a positional count already supplied, adjacent to the already-published compiled-pattern keyword rows, not a broader module-helper keyword dump.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing compiled-pattern module-helper publication owner path instead of creating another manifest, another parity suite, or a detached compiled-pattern keyword-error table:
  - extend the published compiled-pattern module-helper fixture assertion path so the str sequence now includes `workflow-module-sub-unexpected-keyword-after-positional-count-str-compiled-pattern` immediately after `workflow-module-sub-unexpected-keyword-str-compiled-pattern`, and the bytes sequence now includes `workflow-module-subn-unexpected-keyword-after-positional-count-bytes-compiled-pattern` immediately after `workflow-module-subn-unexpected-keyword-bytes-compiled-pattern`;
  - keep the already-published compiled-pattern `split()` duplicate/unexpected rows, wrong-text-model rows, and non-error keyword carriers unchanged in this run;
  - move the published compiled-pattern module-helper fixture total from `58` rows to `60`;
  - move the compiled-pattern text-model split from `31` `str` / `27` `bytes` to `32` / `28`;
  - keep the compiled-pattern helper counts unchanged except for moving `sub` from `8` to `9` and `subn` from `8` to `9`;
  - update the full `module-workflow-surface` bundle expectations from `165` rows to `167`;
  - move `module.workflow.str` from `94` to `95` and `module.workflow.bytes` from `71` to `72`;
  - move `module.workflow.module_call` from `85` to `87`; and
  - keep `module.workflow.pattern_call` at `68` in this run.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1539` total / `1539` passed / `0` unimplemented across `114` manifests to `1541` / `1541` / `0` across the same `114` manifests;
  - `module.workflow` moves from `165` / `165` / `0` to `167` / `167` / `0`;
  - `module.workflow.str` moves from `94` / `94` / `0` to `95` / `95` / `0`;
  - `module.workflow.bytes` moves from `71` / `71` / `0` to `72` / `72` / `0`;
  - `module.workflow.module_call` moves from `85` / `85` / `0` to `87` / `87` / `0`;
  - `module.workflow.pattern_call` stays `68` / `68` / `0`; and
  - the two new compiled-pattern module-helper positional-count keyword-error rows are visible in the tracked scorecard as representative `module-workflow-surface` module-call cases.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'compiled-pattern-sub-unexpected-keyword-after-positional-count-str or compiled-pattern-subn-unexpected-keyword-after-positional-count-bytes or module_workflow_surface_publishes_compiled_pattern_module_helpers_from_direct_cases'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0935-module-workflow-compiled-pattern-sub-subn-unexpected-keyword-after-positional-count-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or benchmark-side selector logic in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached compiled-pattern module-helper keyword publication file.
- Keep the scope pinned to the positional-count-plus-unexpected-keyword pair above. Leave Python-path benchmark catch-up for these two compiled-pattern module-helper rows for a later task.

## Notes
- `RBR-0935` is the next available feature task id in the current checkout:
  - `RBR-0933` is the latest done feature task on this frontier;
  - `RBR-0934` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0933` / `RBR-0934` on the same shared `module-workflow-surface` frontier so the adjacent compiled-pattern module-helper positional-count keyword-error pair reaches the tracked correctness surface before Python-path benchmark catch-up or another compiled-pattern keyword family widens the queue.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier while the exact publication rows are still missing:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'compiled-pattern-sub-unexpected-keyword-after-positional-count-str or compiled-pattern-subn-unexpected-keyword-after-positional-count-bytes'` currently passes in this checkout (`4 passed, 1361 deselected`), so the compiled-pattern module-helper owner path already exposes the exact bounded error pair that this task needs to publish;
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... re.sub(re.compile("abc"), "x", "abc", 1, missing=1) ... rebar.sub(rebar.compile("abc"), "x", "abc", 1, missing=1) ... re.subn(re.compile(b"abc"), b"x", b"abc", 1, missing=1) ... rebar.subn(rebar.compile(b"abc"), b"x", b"abc", 1, missing=1) ... PY` shows CPython and `rebar` already agree on the exact bounded `TypeError.args`: `("sub() takes at most 3 arguments (4 given)",)` and `("subn() takes at most 3 arguments (4 given)",)`;
  - `rg -n 'workflow-module-sub-unexpected-keyword-after-positional-count-str-compiled-pattern|workflow-module-subn-unexpected-keyword-after-positional-count-bytes-compiled-pattern' tests/conformance/fixtures/module_workflow_surface.py reports/correctness/latest.py` returned no matches in this run, so the exact compiled-pattern publication rows are still absent; and
  - `reports/correctness/latest.py` currently reports `1539` total / `1539` passed / `0` unimplemented across `114` manifests, while `reports/benchmarks/latest.py` already reports `887` total / `887` measured / `0` known gaps across `30` manifests, so this run stays on correctness publication instead of skipping ahead to benchmark-only changes.

## Completion
- Added `workflow-module-sub-unexpected-keyword-after-positional-count-str-compiled-pattern` and `workflow-module-subn-unexpected-keyword-after-positional-count-bytes-compiled-pattern` to `tests/conformance/fixtures/module_workflow_surface.py` on the existing compiled-pattern module-helper owner path, in the required positions immediately after the adjacent unexpected-keyword rows and before the already-published wrong-text-model rows.
- Updated `tests/python/test_module_workflow_parity_suite.py` so the shared compiled-pattern module-helper publication assertions now include both new rows, the stale direct-only frontier guard now asserts these positional-count cases are published on the shared owner path, and the bundle/helper totals now track `167` module-workflow rows overall with `95` `str`, `72` `bytes`, `87` `module_call`, `68` `pattern_call`, plus compiled-pattern helper subtotals of `60` rows with `32` `str`, `28` `bytes`, `sub: 9`, and `subn: 9`.
- Updated `tests/conformance/test_combined_correctness_scorecards.py` so the two new `module-workflow-surface` rows are treated as representative module-call cases, then regenerated `reports/correctness/latest.py`. The tracked published artifact remains in the diff and now reports `1541` total / `1541` passed / `0` unimplemented across `114` manifests, with `module.workflow` at `167`, `module.workflow.str` at `95`, `module.workflow.bytes` at `72`, `module.workflow.module_call` at `87`, and `module.workflow.pattern_call` unchanged at `68`. The tracked report now contains both new case ids.
- Left benchmark manifests, benchmark reports, README text, and implementation files unchanged in this run.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'compiled-pattern-sub-unexpected-keyword-after-positional-count-str or compiled-pattern-subn-unexpected-keyword-after-positional-count-bytes or module_workflow_surface_publishes_compiled_pattern_module_helpers_from_direct_cases'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0935-module-workflow-compiled-pattern-sub-subn-unexpected-keyword-after-positional-count-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py`
