## RBR-0822: Publish the module-workflow compiled-pattern split maxsplit bool-false bytes singleton

Status: ready
Owner: feature-implementation
Created: 2026-03-21

## Goal
- Reopen the existing `module-workflow-surface` correctness frontier with the next adjacent compiled-pattern module keyword-call singleton, publishing the exact bytes literal `rebar.split(compiled_pattern, b"abcabc", maxsplit=False)` workflow for the existing `b"abc"` anchor before the unpublished compiled-pattern `sub()`/`subn()` bool-like keyword-call rows, benchmark catch-up, or another owner family reopens the queue.

## Pattern Pair
- `"abc"`
- `b"abc"`

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only one new `module_call` row:
  - add `workflow-module-split-maxsplit-bool-false-bytes-compiled-pattern`;
  - keep the row pinned to the exact direct parity anchor already defined on the shared owner path:
    - `compiled-pattern-split-maxsplit-bool-false-bytes`: `pattern == b"abc"`, `helper == "split"`, `use_compiled_pattern == True`, `args == [b"abcabc"]`, and `kwargs == {"maxsplit": False}`;
  - keep the row on the `bytes` text model with default zero flags; and
  - do not broaden into the unpublished compiled-pattern `sub()`/`subn()` bool-like keyword-call rows, additional compiled-pattern helper rows, benchmark rows, benchmark reports, native-boundary scaffolding, or any new manifest in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another helper-specific manifest, detached selector table, or second compiled-pattern owner path:
  - update the bundle-contract expectations so `module-workflow-surface` now publishes `123` total rows instead of `122`;
  - update the owner-path text-model split from `74` `str` rows and `48` `bytes` rows to `74` `str` rows and `49` `bytes` rows;
  - keep `pattern_call` expectations unchanged at `42` rows with the current helper breakdown;
  - update the shared `module_call` helper breakdown so the owner path now expects `16` `compile` rows, `7` `search` rows, `5` `match` rows, `7` `fullmatch` rows, `10` `split` rows, `2` `findall` rows, `2` `finditer` rows, `10` `sub` rows, `8` `subn` rows, and `2` `escape` rows;
  - extend the published compiled-pattern owner-path assertions so `PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES` now contains fifty rows, inserting `workflow-module-split-maxsplit-bool-false-bytes-compiled-pattern` immediately after `workflow-module-split-maxsplit-indexlike-bytes-compiled-pattern` and immediately before `workflow-module-split-duplicate-maxsplit-keyword-str-compiled-pattern`;
  - extend the compiled-pattern direct-case alignment so the published direct-anchor sequence likewise inserts `compiled-pattern-split-maxsplit-bool-false-bytes` immediately after `compiled-pattern-split-maxsplit-indexlike-bytes` and immediately before `compiled-pattern-split-duplicate-maxsplit-keyword-str`;
  - keep the already published compiled-pattern compile rows, helper rows, helper-error rows, keyword rows, keyword-error rows, bounded-wildcard rows, verbose regression rows, and direct-case buckets unchanged in this run; and
  - do not broaden into the unpublished compiled-pattern `sub()`/`subn()` bool-like keyword-call rows, benchmark manifests, benchmark reports, native-boundary scaffolding, or any new owner path in this run.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1492` total / `1492` passed / `0` `unimplemented` across `114` manifests to `1493` / `1493` / `0` across the same `114` manifests;
  - `module.workflow` moves from `122` / `122` / `0` to `123` / `123` / `0`;
  - `module.workflow.str` stays `74` / `74` / `0`;
  - `module.workflow.bytes` moves from `48` / `48` / `0` to `49` / `49` / `0`;
  - `module.workflow.module_call` moves from `68` / `68` / `0` to `69` / `69` / `0`;
  - `module.workflow.pattern_call` stays `42` / `42` / `0`; and
  - the new bytes literal compiled-pattern `split(..., maxsplit=False)` row is visible in the tracked scorecard as a representative `module-workflow-surface` compiled-pattern module-call case.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'test_compiled_pattern_module_keyword_argument_calls_match_cpython and compiled-pattern-split-maxsplit-bool-false-bytes'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_module_workflow_surface_publishes_compiled_pattern_module_helpers_from_direct_cases tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0822-module-workflow-compiled-pattern-split-maxsplit-bool-false-bytes-singleton.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached compiled-pattern keyword publication file.

## Notes
- `RBR-0822` is the next available task id in the current checkout:
  - `ops/tasks/done/` currently runs through `RBR-0821`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` had no `feature-implementation` task at the start of this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done -maxdepth 1 -type f -printf '%f\n' | rg '^RBR-0822'` returned no matches in this run.
- Queue this directly after `RBR-0820` on the same `module-workflow-surface` owner path. `RBR-0821` is architecture cleanup, so it does not change the feature frontier.
- 2026-03-21 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'test_compiled_pattern_module_keyword_argument_calls_match_cpython and compiled-pattern-split-maxsplit-bool-false-bytes'` passed in this run (`2 passed, 803 deselected`), so the bytes literal compiled-pattern `split(..., maxsplit=False)` behavior is already live on the owner path and this remains a publication-only slice rather than a missing implementation prerequisite;
  - a direct runtime probe in this run showed both CPython and `rebar` return `[b"", b"", b""]` for `split(compile(b"abc"), b"abcabc", maxsplit=False)`, keeping the bounded bytes literal keyword-call target concrete on the live branch;
  - direct publication probes in this run confirmed `workflow-module-split-maxsplit-bool-false-bytes-compiled-pattern` and `compiled-pattern-split-maxsplit-bool-false-bytes` are still absent from `tests/conformance/fixtures/module_workflow_surface.py`, `tests/conformance/test_combined_correctness_scorecards.py`, and `reports/correctness/latest.py`, while the adjacent compiled-pattern split keyword and indexlike rows are already published;
  - the unpublished compiled-pattern `sub()`/`subn()` bool-like keyword-call rows remain out of scope here because `compiled-pattern-split-maxsplit-bool-false-bytes` is the next smaller adjacent singleton already exercised on the shared owner path; and
  - no blocked feature task exists to reopen first.
- `ops/state/backlog.md` and the frontier prose in `ops/state/current_status.md` already honestly say that no ready feature follow-on survives after the likely same-cycle drain, so this one-task refill does not need additional backlog/current-status edits.
