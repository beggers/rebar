# RBR-0812: Publish the module-workflow compiled-pattern compile IGNORECASE rejection bytes named-group singleton

Status: done
Owner: feature-implementation
Created: 2026-03-21
Completed: 2026-03-21

## Goal
- Reopen the existing `module-workflow-surface` correctness frontier with the next concrete compiled-pattern compile keyword-error neighbor, publishing the exact explicit `flags=IGNORECASE` `rebar.compile(compiled_pattern, ...)` bytes named-group singleton for the existing `rb"(?P<word>abc)"` anchor before benchmark catch-up, str-side rejection publication, or another owner family reopens the queue.

## Pattern Pair
- `r"(?P<word>abc)"`
- `rb"(?P<word>abc)"`

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another compile-only manifest, detached selector table, or second compiled-pattern owner path:
  - extend `COMPILED_PATTERN_MODULE_KEYWORD_ERROR_CASES` by only one `helper="compile"` direct case:
    - `compiled-pattern-compile-flags-ignorecase-bytes-named-group`: `pattern == rb"(?P<word>abc)"`, `args == ()`, `kwargs == {"flags": int(re.IGNORECASE)}`;
  - keep the new direct case on the existing compiled-pattern module-keyword error path so `test_compiled_pattern_module_keyword_argument_errors_match_cpython` exercises the real module boundary instead of adding a helper-specific test scaffold;
  - keep `COMPILED_PATTERN_COMPILE_CASES` unchanged in this run, relying on the existing `test_compile_rejects_nonzero_flags_for_compiled_patterns_like_cpython` coverage to keep the direct runtime parity anchor live;
  - update the bundle-contract expectations so `module-workflow-surface` now publishes `118` total rows instead of `117`;
  - update the owner-path text-model split so the bundle now expects `72` `str` rows and `46` `bytes` rows;
  - keep `pattern_call` expectations unchanged at `42` rows with the current helper breakdown;
  - update the shared `module_call` helper breakdown so the owner path now expects `13` `compile` rows, `7` `search` rows, `5` `match` rows, `6` `fullmatch` rows, `9` `split` rows, `2` `findall` rows, `2` `finditer` rows, `10` `sub` rows, `8` `subn` rows, and `2` `escape` rows;
  - extend the published compiled-pattern owner-path assertions so `PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES` now contains forty-five rows, inserting `workflow-module-compile-flags-ignorecase-bytes-compiled-pattern-named-group` immediately after `workflow-module-compile-flags-bool-false-bytes-compiled-pattern-named-group` and immediately before `workflow-module-match-bytes-compiled-pattern-on-str-string`;
  - extend the compiled-pattern direct-case alignment so the published direct-anchor sequence likewise inserts `compiled-pattern-compile-flags-ignorecase-bytes-named-group` immediately after `compiled-pattern-compile-flags-bool-false-bytes-named-group` and immediately before `compiled-pattern-match-bytes-on-str-string`;
  - keep the already published literal compiled-pattern compile rows, named-group success rows, zero-flag rows, helper rows, keyword rows, helper-error rows, and default literal compile rows unchanged in this run; and
  - do not broaden into str-side rejection publication, `flags=re.NOFLAG` duplicate publication, benchmark manifests, benchmark reports, native-boundary scaffolding, or any new manifest in this run.
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only one new `module_call` row:
  - add `workflow-module-compile-flags-ignorecase-bytes-compiled-pattern-named-group`;
  - keep the row pinned to the exact direct parity anchor above on the shared owner path: `pattern == rb"(?P<word>abc)"`, `helper == "compile"`, `use_compiled_pattern == True`, no positional `args`, and `kwargs == {"flags": int(re.IGNORECASE)}`;
  - keep the row on the existing `bytes` named-group compiled-pattern path; and
  - keep the categories/notes explicit that this is the compiled-pattern module-level bytes named-group explicit IGNORECASE rejection singleton, not the default, zero-flag, `NOFLAG`, or str-side rejection slice.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1487` total / `1487` passed / `0` `unimplemented` across `114` manifests to `1488` / `1488` / `0` across the same `114` manifests;
  - `module.workflow` moves from `117` / `117` / `0` to `118` / `118` / `0`;
  - `module.workflow.str` stays `72` / `72` / `0`;
  - `module.workflow.bytes` moves from `45` / `45` / `0` to `46` / `46` / `0`;
  - `module.workflow.module_call` moves from `63` / `63` / `0` to `64` / `64` / `0`;
  - `module.workflow.pattern_call` stays `42` / `42` / `0`; and
  - the new bytes named-group IGNORECASE compiled-pattern compile rejection row is visible in the tracked scorecard as a representative `module-workflow-surface` compiled-pattern module-call case.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_compile_rejects_nonzero_flags_for_compiled_patterns_like_cpython tests/python/test_module_workflow_parity_suite.py::test_compiled_pattern_module_keyword_argument_errors_match_cpython tests/python/test_module_workflow_parity_suite.py::test_module_workflow_surface_publishes_compiled_pattern_module_helpers_from_direct_cases`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0812-module-workflow-compiled-pattern-compile-ignorecase-rejection-bytes-named-group-singleton.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached compiled-pattern compile publication file.

## Notes
- `RBR-0812` is the next available task id in the current checkout:
  - `ops/tasks/done/` currently runs through `RBR-0811`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` had no `feature-implementation` task at the start of this run; and
  - a direct repository scan in this run reported `811` as the highest existing `RBR-` id, so `RBR-0812` is the next unused identifier.
- Queue this directly after `RBR-0810` on the same `module-workflow-surface` owner path. `RBR-0811` is cleanup, so it does not change the feature frontier.
- 2026-03-21 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_compile_rejects_nonzero_flags_for_compiled_patterns_like_cpython tests/python/test_module_workflow_parity_suite.py::test_compiled_pattern_module_keyword_argument_errors_match_cpython` passed in this run (`20 passed in 0.08s`), so the bytes named-group IGNORECASE rejection is already live on the owner path and this remains a publication-only slice rather than a missing implementation prerequisite;
  - `test_compile_rejects_nonzero_flags_for_compiled_patterns_like_cpython` already exercises `rb"(?P<word>abc)"` through `COMPILED_PATTERN_COMPILE_CASES`, confirming the direct runtime parity anchor without needing a new Rust-boundary task first;
  - direct publication probes in this run confirmed `compiled-pattern-compile-flags-ignorecase-bytes-named-group` and `workflow-module-compile-flags-ignorecase-bytes-compiled-pattern-named-group` are still absent from `tests/python/test_module_workflow_parity_suite.py`, `tests/conformance/fixtures/module_workflow_surface.py`, `tests/conformance/test_combined_correctness_scorecards.py`, and `reports/correctness/latest.py`;
  - `flags=re.NOFLAG` is still not the next task because the current owner-path keyword signature normalizes `RegexFlag(0)` to the already published integer-zero singleton, while this bytes named-group IGNORECASE rejection remains the next distinct unpublished neighbor on the active boundary;
  - no blocked feature task exists to reopen first; and
  - `ops/state/backlog.md` plus the frontier prose in `ops/state/current_status.md` already honestly say that no ready feature follow-on survives after the likely same-cycle drain, so this one-task refill does not need additional backlog/current-status edits.

## Completion
- Added the single published `module_call` row `workflow-module-compile-flags-ignorecase-bytes-compiled-pattern-named-group` to `tests/conformance/fixtures/module_workflow_surface.py`, added the direct compiled-pattern keyword-error anchor `compiled-pattern-compile-flags-ignorecase-bytes-named-group`, and updated the shared owner-path count/order assertions in `tests/python/test_module_workflow_parity_suite.py`.
- Extended the tracked representative-case list in `tests/conformance/test_combined_correctness_scorecards.py` and republished `reports/correctness/latest.py`; the tracked report now shows `1488` total / `1488` passed / `0` unimplemented overall, with `module.workflow` at `118` / `118`, `module.workflow.str` unchanged at `72` / `72`, `module.workflow.bytes` at `46` / `46`, `module.workflow.module_call` at `64` / `64`, and `module.workflow.pattern_call` unchanged at `42` / `42`.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_compile_rejects_nonzero_flags_for_compiled_patterns_like_cpython tests/python/test_module_workflow_parity_suite.py::test_compiled_pattern_module_keyword_argument_errors_match_cpython tests/python/test_module_workflow_parity_suite.py::test_module_workflow_surface_publishes_compiled_pattern_module_helpers_from_direct_cases` (`23 passed`), `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py` (`808 passed, 1 skipped, 2011 subtests passed`), `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0812-module-workflow-compiled-pattern-compile-ignorecase-rejection-bytes-named-group-singleton.py` (`118/118`), and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py` (`1488/1488`).
