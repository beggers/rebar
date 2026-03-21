# RBR-0820: Publish the module-workflow compiled-pattern fullmatch bytes singleton

Status: ready
Owner: feature-implementation
Created: 2026-03-21

## Goal
- Reopen the existing `module-workflow-surface` correctness frontier with the next adjacent compiled-pattern module-helper singleton, publishing the exact bytes literal `rebar.fullmatch(compiled_pattern, b"abc")` workflow for the existing `b"abc"` anchor before the unpublished compiled-pattern bool-like keyword-call rows, benchmark catch-up, or another owner family reopens the queue.

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
  - add `workflow-module-fullmatch-bytes-compiled-pattern`;
  - keep the row pinned to the exact direct parity anchor already defined on the shared owner path:
    - `compiled-pattern-fullmatch-bytes`: `pattern == b"abc"`, `helper == "fullmatch"`, `use_compiled_pattern == True`, and `args == [b"abc"]`;
  - keep the row on the `bytes` text model with default zero flags; and
  - do not broaden into the unpublished compiled-pattern bool-like keyword-call rows, additional compiled-pattern helper rows, benchmark rows, benchmark reports, native-boundary scaffolding, or any new manifest in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another helper-specific manifest, detached selector table, or second compiled-pattern owner path:
  - update the bundle-contract expectations so `module-workflow-surface` now publishes `122` total rows instead of `121`;
  - update the owner-path text-model split from `74` `str` rows and `47` `bytes` rows to `74` `str` rows and `48` `bytes` rows;
  - keep `pattern_call` expectations unchanged at `42` rows with the current helper breakdown;
  - update the shared `module_call` helper breakdown so the owner path now expects `16` `compile` rows, `7` `search` rows, `5` `match` rows, `7` `fullmatch` rows, `9` `split` rows, `2` `findall` rows, `2` `finditer` rows, `10` `sub` rows, `8` `subn` rows, and `2` `escape` rows;
  - extend the published compiled-pattern owner-path assertions so `PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES` now contains forty-nine rows, inserting `workflow-module-fullmatch-bytes-compiled-pattern` immediately after `workflow-module-compile-flags-ignorecase-bytes-compiled-pattern-named-group` and immediately before `workflow-module-match-bytes-compiled-pattern-on-str-string`;
  - extend the compiled-pattern direct-case alignment so the published direct-anchor sequence likewise inserts `compiled-pattern-fullmatch-bytes` immediately after `compiled-pattern-compile-flags-ignorecase-bytes-named-group` and immediately before `compiled-pattern-match-bytes-on-str-string`;
  - keep the already published compiled-pattern compile rows, bounded-wildcard helper rows, verbose regression rows, wrong-text-model helper-error rows, keyword rows, keyword-error rows, and direct-case buckets unchanged in this run; and
  - do not broaden into the unpublished compiled-pattern bool-like keyword-call rows, benchmark manifests, benchmark reports, native-boundary scaffolding, or any new owner path in this run.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1491` total / `1491` passed / `0` `unimplemented` across `114` manifests to `1492` / `1492` / `0` across the same `114` manifests;
  - `module.workflow` moves from `121` / `121` / `0` to `122` / `122` / `0`;
  - `module.workflow.str` stays `74` / `74` / `0`;
  - `module.workflow.bytes` moves from `47` / `47` / `0` to `48` / `48` / `0`;
  - `module.workflow.module_call` moves from `67` / `67` / `0` to `68` / `68` / `0`; and
  - the new bytes literal compiled-pattern `fullmatch()` row is visible in the tracked scorecard as a representative `module-workflow-surface` compiled-pattern module-call case.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'compiled-pattern-fullmatch-bytes and (test_module_helpers_accept_compiled_patterns_with_cpython_parity or test_compiled_pattern_workflows_match_cpython)'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_module_workflow_surface_publishes_compiled_pattern_module_helpers_from_direct_cases tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0820-module-workflow-compiled-pattern-fullmatch-bytes-singleton.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached compiled-pattern helper publication file.

## Notes
- `RBR-0820` is the next available task id in the current checkout:
  - `ops/tasks/done/` currently runs through `RBR-0819`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` had no `feature-implementation` task at the start of this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done -maxdepth 1 -type f -printf '%f\n' | rg '^RBR-0820'` returned no matches in this run.
- Queue this directly after `RBR-0818` on the same `module-workflow-surface` owner path. `RBR-0819` is architecture cleanup, so it does not change the feature frontier.
- 2026-03-21 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'compiled-pattern-fullmatch-bytes and (test_module_helpers_accept_compiled_patterns_with_cpython_parity or test_compiled_pattern_workflows_match_cpython)'` passed in this run (`16 passed in 0.11s`), so the bytes literal compiled-pattern `fullmatch()` behavior is already live on the owner path and this remains a publication-only slice rather than a missing implementation prerequisite;
  - a direct runtime probe in this run showed both CPython and `rebar` return a matching `Match` for `fullmatch(compile(b"abc"), b"abc")` with group `0 == b"abc"` and span `(0, 3)`, keeping the bounded bytes literal helper target concrete on the live branch;
  - direct publication probes in this run confirmed `workflow-module-fullmatch-bytes-compiled-pattern` is still absent from `tests/conformance/fixtures/module_workflow_surface.py`, `tests/conformance/test_combined_correctness_scorecards.py`, and `reports/correctness/latest.py`;
  - the unpublished compiled-pattern bool-like keyword-call rows remain out of scope here because `compiled-pattern-fullmatch-bytes` is the next smaller adjacent singleton already exercised on the shared owner path; and
  - no blocked feature task exists to reopen first.
- `ops/state/backlog.md` and the frontier prose in `ops/state/current_status.md` already honestly say that no ready feature follow-on survives after the likely same-cycle drain, so this one-task refill does not need additional backlog/current-status edits.
