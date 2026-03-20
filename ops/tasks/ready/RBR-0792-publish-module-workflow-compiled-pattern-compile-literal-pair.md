# RBR-0792: Publish the module-workflow compiled-pattern compile literal pair

Status: ready
Owner: feature-implementation
Created: 2026-03-20

## Goal
- Reopen the existing `module-workflow-surface` correctness frontier with the next adjacent compiled-pattern compile slice, publishing the exact literal `rebar.compile(compiled_pattern)` acceptance pair for the existing `"abc"` and `b"abc"` anchors before explicit zero-flag spellings, nonzero-flag rejections, named-group compiled-pattern compile cases, benchmark catch-up, or another owner family reopens the queue.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only two new `module_call` rows:
  - add `workflow-module-compile-str-compiled-pattern`;
  - add `workflow-module-compile-bytes-compiled-pattern`;
  - keep both rows pinned to the exact direct parity anchors already defined on the shared owner path in `COMPILED_PATTERN_COMPILE_CASES`:
    - `compiled-pattern-compile-str-literal`: `pattern == "abc"`;
    - `compiled-pattern-compile-bytes-literal`: `pattern == b"abc"`;
  - keep the module-helper routing explicit by setting `helper == "compile"` and `use_compiled_pattern` on both rows with no extra `args` or `kwargs`;
  - keep the text-model split explicit: `workflow-module-compile-str-compiled-pattern` stays on `str` and `workflow-module-compile-bytes-compiled-pattern` stays on `bytes`; and
  - do not broaden into the existing named-group compiled-pattern compile direct case, explicit `NOFLAG` / `0` / `False` spellings, nonzero-flag rejections, benchmark manifests, benchmark reports, native-boundary scaffolding, or any new manifest in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another compile-only manifest, detached selector table, or second compiled-pattern owner path:
  - update the bundle-contract expectations so `module-workflow-surface` now publishes `107` total rows instead of `105`;
  - update the owner-path text-model split so the bundle now expects `67` `str` rows and `40` `bytes` rows;
  - keep `pattern_call` expectations unchanged at `42` rows with the current helper breakdown;
  - update the shared `module_call` helper breakdown so the owner path now expects `2` `compile` rows, `7` `search` rows, `5` `match` rows, `6` `fullmatch` rows, `9` `split` rows, `2` `findall` rows, `2` `finditer` rows, `10` `sub` rows, `8` `subn` rows, and `2` `escape` rows;
  - extend the published compiled-pattern owner-path assertions so `PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES` now contains thirty-four rows, inserting the two new fixture ids directly ahead of the existing compiled-pattern helper block:
    - insert `workflow-module-compile-str-compiled-pattern` immediately before `workflow-module-search-str-compiled-pattern`;
    - insert `workflow-module-compile-bytes-compiled-pattern` immediately before `workflow-module-match-bytes-compiled-pattern-on-str-string`;
  - extend the compiled-pattern direct-case alignment so the published direct-anchor sequence likewise inserts:
    - `compiled-pattern-compile-str-literal` immediately before `compiled-pattern-search-str`;
    - `compiled-pattern-compile-bytes-literal` immediately before `compiled-pattern-match-bytes-on-str-string`;
  - keep the shared compiled-pattern publication contract on the existing direct-case alignment path instead of inventing another compile-publication selector; and
  - keep the already published compiled-pattern helper, keyword, and helper-error rows unchanged in this run.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1475` total / `1475` passed / `0` `unimplemented` across `114` manifests to `1477` / `1477` / `0` across the same `114` manifests;
  - `module.workflow` moves from `105` / `105` / `0` to `107` / `107` / `0`;
  - `module.workflow.str` moves from `66` / `66` / `0` to `67` / `67` / `0`;
  - `module.workflow.bytes` moves from `39` / `39` / `0` to `40` / `40` / `0`;
  - `module.workflow.module_call` moves from `51` / `51` / `0` to `53` / `53` / `0`;
  - `module.workflow.pattern_call` stays `42` / `42` / `0`; and
  - at least one of the new compiled-pattern compile rows is visible in the tracked scorecard as a representative `module-workflow-surface` compiled-pattern module-call case.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_compile_accepts_compiled_patterns_with_zero_flags_like_cpython tests/python/test_module_workflow_parity_suite.py::test_compile_rejects_nonzero_flags_for_compiled_patterns_like_cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0792-module-workflow-compiled-pattern-compile-literal-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached compiled-pattern compile publication file.

## Notes
- `RBR-0792` is the next available task id in the current checkout:
  - `ops/tasks/done/` currently runs through `RBR-0791`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` had no `feature-implementation` task at the start of this run; and
  - `rg -n "RBR-0792|RBR-0793" ops/tasks ops/state/current_status.md ops/state/backlog.md` returned no active reservation for this id in this run.
- Queue this directly after `RBR-0790` on the same `module-workflow-surface` owner path. `RBR-0791` is architecture cleanup, so it does not change the feature frontier.
- 2026-03-20 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `tests/python/test_module_workflow_parity_suite.py` already carries the exact adjacent direct parity anchors `compiled-pattern-compile-str-literal` and `compiled-pattern-compile-bytes-literal` in `COMPILED_PATTERN_COMPILE_CASES`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_compile_accepts_compiled_patterns_with_zero_flags_like_cpython tests/python/test_module_workflow_parity_suite.py::test_compile_rejects_nonzero_flags_for_compiled_patterns_like_cpython` passed in this run (`30 passed in 0.11s`);
  - `python/rebar_harness/correctness.py` already supports `module_call` rows that compile the fixture pattern first and then pass the compiled object through `module_call_args(...)` when `use_compiled_pattern` is true, so this slice does not need new harness plumbing before publication;
  - direct publication probes in this run confirmed `workflow-module-compile-str-compiled-pattern` and `workflow-module-compile-bytes-compiled-pattern` are still absent from `tests/conformance/fixtures/module_workflow_surface.py`, `tests/conformance/test_combined_correctness_scorecards.py`, and `reports/correctness/latest.py`;
  - the current owner path already publishes the adjacent compiled-pattern helper, keyword, and helper-error rows, leaving this default compile literal pair as the smallest unpublished compiled-pattern neighbor on the same owner file;
  - no blocked feature task exists to reopen first; and
  - `ops/state/backlog.md` and the frontier prose in `ops/state/current_status.md` already honestly say that no ready feature follow-on survives after the likely same-cycle drain, so this one-task refill does not need a backlog-frontier prose change.
