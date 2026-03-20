# RBR-0806: Publish the module-workflow compiled-pattern compile bytes named-group singleton

Status: done
Owner: feature-implementation
Created: 2026-03-20

## Goal
- Reopen the existing `module-workflow-surface` correctness frontier with the next concrete compiled-pattern compile neighbor, publishing the exact bytes named-group `rebar.compile(compiled_pattern)` workflow for the existing `rb"(?P<word>abc)"` anchor before bytes named-group explicit zero-flag spellings, bytes named-group bool-false spellings, nonzero-flag rejection rows, benchmark catch-up, or another owner family reopens the queue.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only one new `module_call` row:
  - add `workflow-module-compile-bytes-compiled-pattern-named-group`;
  - keep the row pinned to the exact direct parity anchor already defined on the shared owner path in `COMPILED_PATTERN_COMPILE_CASES`:
    - `compiled-pattern-compile-bytes-named-group`: `pattern == rb"(?P<word>abc)"`;
  - keep the module-helper routing explicit by setting `helper == "compile"` and `use_compiled_pattern` with no extra `args` or `kwargs`;
  - keep the text-model split explicit by leaving this singleton on `bytes`; and
  - do not broaden into bytes named-group explicit `flags=0` / `flags=False` spellings, nonzero-flag rejection rows, benchmark manifests, benchmark reports, native-boundary scaffolding, or any new manifest in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another compile-only manifest, detached selector table, or second compiled-pattern owner path:
  - update the bundle-contract expectations so `module-workflow-surface` now publishes `115` total rows instead of `114`;
  - keep the owner-path text-model split explicit at `72` `str` rows and `43` `bytes` rows;
  - keep `pattern_call` expectations unchanged at `42` rows with the current helper breakdown;
  - update the shared `module_call` helper breakdown so the owner path now expects `10` `compile` rows, `7` `search` rows, `5` `match` rows, `6` `fullmatch` rows, `9` `split` rows, `2` `findall` rows, `2` `finditer` rows, `10` `sub` rows, `8` `subn` rows, and `2` `escape` rows;
  - extend the published compiled-pattern owner-path assertions so `PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES` now contains forty-two rows, inserting the new fixture id directly after the existing bytes explicit-bool-false compiled-pattern compile row:
    - insert `workflow-module-compile-bytes-compiled-pattern-named-group` immediately after `workflow-module-compile-flags-bool-false-bytes-compiled-pattern` and immediately before `workflow-module-match-bytes-compiled-pattern-on-str-string`;
  - extend the compiled-pattern direct-case alignment so the published direct-anchor sequence likewise inserts:
    - `compiled-pattern-compile-bytes-named-group` immediately after `compiled-pattern-compile-flags-bool-false-bytes` and immediately before `compiled-pattern-match-bytes-on-str-string`;
  - keep the shared compiled-pattern publication contract on the existing direct-case alignment path instead of inventing another compile-publication selector; and
  - keep the already published str named-group compile rows, bytes literal compile rows, helper rows, keyword rows, helper-error rows, and default literal compile rows unchanged in this run.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1484` total / `1484` passed / `0` `unimplemented` across `114` manifests to `1485` / `1485` / `0` across the same `114` manifests;
  - `module.workflow` moves from `114` / `114` / `0` to `115` / `115` / `0`;
  - `module.workflow.str` stays `72` / `72` / `0`;
  - `module.workflow.bytes` moves from `42` / `42` / `0` to `43` / `43` / `0`;
  - `module.workflow.module_call` moves from `60` / `60` / `0` to `61` / `61` / `0`;
  - `module.workflow.pattern_call` stays `42` / `42` / `0`; and
  - the new bytes named-group compiled-pattern compile row is visible in the tracked scorecard as a representative `module-workflow-surface` compiled-pattern module-call case.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_compile_accepts_compiled_patterns_with_zero_flags_like_cpython tests/python/test_module_workflow_parity_suite.py::test_module_workflow_surface_publishes_compiled_pattern_module_helpers_from_direct_cases`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0806-module-workflow-compiled-pattern-compile-bytes-named-group-singleton.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached compiled-pattern compile publication file.

## Notes
- `RBR-0806` is the next available task id in the current checkout:
  - `ops/tasks/done/` currently runs through `RBR-0805`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` had no `feature-implementation` task at the start of this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done -maxdepth 1 -type f -printf '%f\n' | rg '^RBR-0806'` returned no matches in this run.
- Queue this directly after `RBR-0804` on the same `module-workflow-surface` owner path. `RBR-0805` is architecture cleanup, so it does not change the feature frontier.
- 2026-03-20 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `tests/python/test_module_workflow_parity_suite.py` already carries the exact adjacent direct parity anchor `compiled-pattern-compile-bytes-named-group` in `COMPILED_PATTERN_COMPILE_CASES`;
  - a direct runtime probe in this run confirmed both CPython and `rebar` already return the same compiled object for `compile(compiled_pattern)` on the existing `rb"(?P<word>abc)"` anchor, with matching `pattern`, `flags`, `groups`, and `groupindex`;
  - the same runtime probe confirmed `compile(compiled_pattern, flags=0)` and `compile(compiled_pattern, flags=False)` already match CPython for that bytes named-group anchor, so this remains a publication-only slice rather than another missing implementation prerequisite;
  - a companion runtime probe in this run confirmed both CPython and `rebar` still reject `compile(compiled_pattern, IGNORECASE)` for that same bytes named-group anchor with the same `ValueError`, so nonzero-flag rejection publication remains a later step rather than missing runtime behavior;
  - direct publication probes in this run confirmed `workflow-module-compile-bytes-compiled-pattern-named-group` is still absent from `tests/conformance/fixtures/module_workflow_surface.py`, `tests/conformance/test_combined_correctness_scorecards.py`, and `reports/correctness/latest.py`;
  - no blocked feature task exists to reopen first; and
  - `ops/state/backlog.md` plus the frontier prose in `ops/state/current_status.md` already honestly say that no ready feature follow-on survives after the likely same-cycle drain, so this one-task refill does not need additional backlog/current-status edits.

## Completion
- Added the single published `module_call` row `workflow-module-compile-bytes-compiled-pattern-named-group` to `tests/conformance/fixtures/module_workflow_surface.py`, aligned the shared owner-path direct-case order and bundle/count assertions in `tests/python/test_module_workflow_parity_suite.py`, and extended the tracked representative-case list in `tests/conformance/test_combined_correctness_scorecards.py`.
- Republished `reports/correctness/latest.py`; the tracked report now shows `1485` total / `1485` passed / `0` unimplemented overall, with `module.workflow` at `115` / `115`, `module.workflow.str` unchanged at `72` / `72`, `module.workflow.bytes` at `43` / `43`, `module.workflow.module_call` at `61` / `61`, and `module.workflow.pattern_call` unchanged at `42` / `42`.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_compile_accepts_compiled_patterns_with_zero_flags_like_cpython tests/python/test_module_workflow_parity_suite.py::test_module_workflow_surface_publishes_compiled_pattern_module_helpers_from_direct_cases` (`33 passed`), `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py` (`802 passed, 1 skipped, 2008 subtests passed`), `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0806-module-workflow-compiled-pattern-compile-bytes-named-group-singleton.py` (`115/115`), and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py` (`1485/1485`).
