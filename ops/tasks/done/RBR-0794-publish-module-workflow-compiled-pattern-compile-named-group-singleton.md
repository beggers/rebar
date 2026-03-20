# RBR-0794: Publish the module-workflow compiled-pattern compile named-group singleton

Status: done
Owner: feature-implementation
Created: 2026-03-20

## Goal
- Reopen the existing `module-workflow-surface` correctness frontier with the next concrete compiled-pattern compile neighbor, publishing the exact named-group `rebar.compile(compiled_pattern)` workflow for the existing `r"(?P<word>abc)"` anchor before explicit zero-flag spellings, nonzero-flag rejections, benchmark catch-up, or another owner family reopens the queue.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only one new `module_call` row:
  - add `workflow-module-compile-str-compiled-pattern-named-group`;
  - keep the row pinned to the exact direct parity anchor already defined on the shared owner path in `COMPILED_PATTERN_COMPILE_CASES`:
    - `compiled-pattern-compile-str-named-group`: `pattern == r"(?P<word>abc)"`;
  - keep the module-helper routing explicit by setting `helper == "compile"` and `use_compiled_pattern` with no extra `args` or `kwargs`;
  - keep the text-model split explicit by leaving this singleton on `str`; and
  - do not broaden into explicit `NOFLAG` / `0` / `False` spellings, nonzero-flag rejection rows, bytes named-group variants, benchmark manifests, benchmark reports, native-boundary scaffolding, or any new manifest in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another compile-only manifest, detached selector table, or second compiled-pattern owner path:
  - update the bundle-contract expectations so `module-workflow-surface` now publishes `108` total rows instead of `107`;
  - update the owner-path text-model split so the bundle now expects `68` `str` rows and `40` `bytes` rows;
  - keep `pattern_call` expectations unchanged at `42` rows with the current helper breakdown;
  - update the shared `module_call` helper breakdown so the owner path now expects `3` `compile` rows, `7` `search` rows, `5` `match` rows, `6` `fullmatch` rows, `9` `split` rows, `2` `findall` rows, `2` `finditer` rows, `10` `sub` rows, `8` `subn` rows, and `2` `escape` rows;
  - extend the published compiled-pattern owner-path assertions so `PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES` now contains thirty-five rows, inserting the new fixture id directly after the existing str literal compiled-pattern compile row:
    - insert `workflow-module-compile-str-compiled-pattern-named-group` immediately after `workflow-module-compile-str-compiled-pattern`;
  - extend the compiled-pattern direct-case alignment so the published direct-anchor sequence likewise inserts:
    - `compiled-pattern-compile-str-named-group` immediately after `compiled-pattern-compile-str-literal`;
  - keep the shared compiled-pattern publication contract on the existing direct-case alignment path instead of inventing another compile-publication selector; and
  - keep the already published compiled-pattern helper, keyword, helper-error, and literal compile rows unchanged in this run.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1477` total / `1477` passed / `0` `unimplemented` across `114` manifests to `1478` / `1478` / `0` across the same `114` manifests;
  - `module.workflow` moves from `107` / `107` / `0` to `108` / `108` / `0`;
  - `module.workflow.str` moves from `67` / `67` / `0` to `68` / `68` / `0`;
  - `module.workflow.bytes` stays `40` / `40` / `0`;
  - `module.workflow.module_call` moves from `53` / `53` / `0` to `54` / `54` / `0`;
  - `module.workflow.pattern_call` stays `42` / `42` / `0`; and
  - the new named-group compiled-pattern compile row is visible in the tracked scorecard as a representative `module-workflow-surface` compiled-pattern module-call case.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_compile_accepts_compiled_patterns_with_zero_flags_like_cpython tests/python/test_module_workflow_parity_suite.py::test_compile_rejects_nonzero_flags_for_compiled_patterns_like_cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0794-module-workflow-compiled-pattern-compile-named-group-singleton.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached compiled-pattern compile publication file.

## Notes
- `RBR-0794` is the next available task id in the current checkout:
  - `ops/tasks/done/` currently runs through `RBR-0793`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` had no `feature-implementation` task at the start of this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done -maxdepth 1 -type f -printf '%f\n' | rg '^RBR-0794|^RBR-0795|^RBR-0796'` returned no matches in this run.
- Queue this directly after `RBR-0792` on the same `module-workflow-surface` owner path. `RBR-0793` is architecture cleanup, so it does not change the feature frontier.
- 2026-03-20 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `tests/python/test_module_workflow_parity_suite.py` already carries the exact adjacent direct parity anchor `compiled-pattern-compile-str-named-group` in `COMPILED_PATTERN_COMPILE_CASES`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_compile_accepts_compiled_patterns_with_zero_flags_like_cpython tests/python/test_module_workflow_parity_suite.py::test_compile_rejects_nonzero_flags_for_compiled_patterns_like_cpython` passed in this run (`30 passed in 0.11s`);
  - direct publication probes in this run confirmed `workflow-module-compile-str-compiled-pattern-named-group` is still absent from `tests/conformance/fixtures/module_workflow_surface.py`, `tests/conformance/test_combined_correctness_scorecards.py`, and `reports/correctness/latest.py`;
  - the current owner path already publishes the adjacent literal compiled-pattern compile pair, leaving this named-group singleton as the smallest unpublished compiled-pattern compile neighbor on the same owner file;
  - no blocked feature task exists to reopen first; and
  - `ops/state/backlog.md` and the frontier prose in `ops/state/current_status.md` already honestly say that no ready feature follow-on survives after the likely same-cycle drain, so this one-task refill does not need a backlog-frontier prose change.

## Completion
- Added `workflow-module-compile-str-compiled-pattern-named-group` to `tests/conformance/fixtures/module_workflow_surface.py` directly after the existing str literal compiled-pattern compile row, keeping the shared owner path pinned to `compiled-pattern-compile-str-named-group` with `helper == "compile"` and `use_compiled_pattern == True`.
- Updated the shared owner-path assertions in `tests/python/test_module_workflow_parity_suite.py` so `module-workflow-surface` now publishes `108` rows with a `68`/`40` str/bytes split, `54` `module_call` rows, `3` published `compile` helper rows, and `35` published compiled-pattern module-helper rows, with the direct-anchor alignment inserting `compiled-pattern-compile-str-named-group` immediately after `compiled-pattern-compile-str-literal`.
- Updated `tests/conformance/test_combined_correctness_scorecards.py` and republished `reports/correctness/latest.py`; the tracked scorecard diff includes the report file, the new representative `workflow-module-compile-str-compiled-pattern-named-group` row, and summary totals of `1478` total / `1478` passed / `0` unimplemented across `114` manifests, with `module.workflow` at `108`, `module.workflow.str` at `68`, `module.workflow.bytes` at `40`, `module.workflow.module_call` at `54`, and `module.workflow.pattern_call` unchanged at `42`.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_compile_accepts_compiled_patterns_with_zero_flags_like_cpython tests/python/test_module_workflow_parity_suite.py::test_compile_rejects_nonzero_flags_for_compiled_patterns_like_cpython` (`30 passed in 0.43s`), `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py` (`758 passed, 1 skipped, 1983 subtests passed in 35.71s`), `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0794-module-workflow-compiled-pattern-compile-named-group-singleton.py` (`108/108`), and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py` (`1478/1478`).
