# RBR-0810: Publish the module-workflow compiled-pattern compile explicit-bool-false bytes named-group singleton

Status: done
Owner: feature-implementation
Created: 2026-03-21
Completed: 2026-03-21

## Goal
- Reopen the existing `module-workflow-surface` correctness frontier with the next concrete compiled-pattern compile keyword neighbor, publishing the exact explicit `flags=False` `rebar.compile(compiled_pattern, ...)` bytes named-group singleton for the existing `rb"(?P<word>abc)"` anchor before any `flags=re.NOFLAG` duplicate publication, nonzero-flag rejection rows, benchmark catch-up, or another owner family reopens the queue.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another compile-only manifest, detached selector table, or second compiled-pattern owner path:
  - extend `COMPILED_PATTERN_MODULE_KEYWORD_CALL_CASES` by only one `helper="compile"` direct case:
    - `compiled-pattern-compile-flags-bool-false-bytes-named-group`: `pattern == rb"(?P<word>abc)"`, `args == ()`, `kwargs == {"flags": False}`;
  - keep the new direct case on the existing compiled-pattern module-keyword path so `test_compiled_pattern_module_keyword_argument_calls_match_cpython` exercises the real module boundary instead of adding a helper-specific test scaffold;
  - update the bundle-contract expectations so `module-workflow-surface` now publishes `117` total rows instead of `116`;
  - update the owner-path text-model split so the bundle now expects `72` `str` rows and `45` `bytes` rows;
  - keep `pattern_call` expectations unchanged at `42` rows with the current helper breakdown;
  - update the shared `module_call` helper breakdown so the owner path now expects `12` `compile` rows, `7` `search` rows, `5` `match` rows, `6` `fullmatch` rows, `9` `split` rows, `2` `findall` rows, `2` `finditer` rows, `10` `sub` rows, `8` `subn` rows, and `2` `escape` rows;
  - extend the published compiled-pattern owner-path assertions so `PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES` now contains forty-four rows, inserting `workflow-module-compile-flags-bool-false-bytes-compiled-pattern-named-group` immediately after `workflow-module-compile-flags-int-zero-bytes-compiled-pattern-named-group` and immediately before `workflow-module-match-bytes-compiled-pattern-on-str-string`;
  - extend the compiled-pattern direct-case alignment so the published direct-anchor sequence likewise inserts `compiled-pattern-compile-flags-bool-false-bytes-named-group` immediately after `compiled-pattern-compile-flags-int-zero-bytes-named-group` and immediately before `compiled-pattern-match-bytes-on-str-string`;
  - keep the already published literal compiled-pattern compile rows, default named-group compile singletons, explicit integer-zero rows, helper rows, keyword rows, helper-error rows, and default literal compile rows unchanged in this run; and
  - do not broaden into `flags=re.NOFLAG` duplicate publication, nonzero-flag rejection rows, benchmark manifests, benchmark reports, native-boundary scaffolding, or any new manifest in this run.
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only one new `module_call` row:
  - add `workflow-module-compile-flags-bool-false-bytes-compiled-pattern-named-group`;
  - keep the row pinned to the exact direct parity anchor above on the shared owner path: `pattern == rb"(?P<word>abc)"` with `helper == "compile"`, `use_compiled_pattern == True`, no positional `args`, and `kwargs == {"flags": False}`;
  - keep the row on the existing `bytes` named-group path; and
  - keep the categories/notes explicit that this is the compiled-pattern module-level bytes named-group explicit bool-false flag singleton, not the default, integer-zero, `NOFLAG`, or nonzero-flag rejection slice.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1486` total / `1486` passed / `0` `unimplemented` across `114` manifests to `1487` / `1487` / `0` across the same `114` manifests;
  - `module.workflow` moves from `116` / `116` / `0` to `117` / `117` / `0`;
  - `module.workflow.str` stays `72` / `72` / `0`;
  - `module.workflow.bytes` moves from `44` / `44` / `0` to `45` / `45` / `0`;
  - `module.workflow.module_call` moves from `62` / `62` / `0` to `63` / `63` / `0`;
  - `module.workflow.pattern_call` stays `42` / `42` / `0`; and
  - the new bytes named-group explicit-bool-false compiled-pattern compile row is visible in the tracked scorecard as a representative `module-workflow-surface` compiled-pattern module-call case.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_compile_accepts_compiled_patterns_with_zero_flags_like_cpython tests/python/test_module_workflow_parity_suite.py::test_compiled_pattern_module_keyword_argument_calls_match_cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0810-module-workflow-compiled-pattern-compile-bool-false-bytes-named-group-singleton.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached compiled-pattern compile publication file.

## Notes
- `RBR-0810` is the next available task id in the current checkout:
  - `ops/tasks/done/` currently runs through `RBR-0809`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` had no `feature-implementation` task at the start of this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done -maxdepth 1 -type f -printf '%f\n' | rg '^RBR-0810'` returned no matches in this run.
- Queue this directly after `RBR-0808` on the same `module-workflow-surface` owner path. `RBR-0809` is architecture cleanup, so it does not change the feature frontier.
- 2026-03-21 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `tests/python/test_module_workflow_parity_suite.py` still exercises the runtime behavior for `rb"(?P<word>abc)"` through `test_compile_accepts_compiled_patterns_with_zero_flags_like_cpython`, because `COMPILED_PATTERN_COMPILE_CASES` already includes `compiled-pattern-compile-bytes-named-group` and `COMPILED_PATTERN_ZERO_FLAG_MODES` already covers the explicit bool-false spelling;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_compile_accepts_compiled_patterns_with_zero_flags_like_cpython tests/python/test_module_workflow_parity_suite.py::test_compile_rejects_nonzero_flags_for_compiled_patterns_like_cpython` passed in this run (`40 passed in 0.11s`), so the bytes named-group explicit-bool-false workflow remains a publication-only slice rather than a missing implementation prerequisite;
  - direct publication probes in this run confirmed `compiled-pattern-compile-flags-bool-false-bytes-named-group` and `workflow-module-compile-flags-bool-false-bytes-compiled-pattern-named-group` are still absent from `tests/python/test_module_workflow_parity_suite.py`, `tests/conformance/fixtures/module_workflow_surface.py`, `tests/conformance/test_combined_correctness_scorecards.py`, and `reports/correctness/latest.py`;
  - the shared `_workflow_keyword_kwargs_signature(...)` selector already distinguishes bool-valued keyword payloads from integer-zero payloads on this owner path, so the bytes named-group explicit bool-false singleton can land without another selector refactor first;
  - `flags=re.NOFLAG` is still not the next task because the current owner-path signature normalizes `RegexFlag(0)` to the same integer-zero keyword signature that is already published, while this bytes named-group bool-false singleton remains the next distinct unpublished row on the current boundary;
  - no blocked feature task exists to reopen first; and
  - `ops/state/backlog.md` plus the frontier prose in `ops/state/current_status.md` already honestly say that no ready feature follow-on survives after the likely same-cycle drain, so this one-task refill does not need additional backlog/current-status edits.

## Completion
- Added the single published `module_call` row `workflow-module-compile-flags-bool-false-bytes-compiled-pattern-named-group` to `tests/conformance/fixtures/module_workflow_surface.py`, aligned the shared owner-path direct-case order and bundle/count assertions in `tests/python/test_module_workflow_parity_suite.py`, and extended the tracked representative-case list in `tests/conformance/test_combined_correctness_scorecards.py`.
- Republished `reports/correctness/latest.py`; the tracked report now shows `1487` total / `1487` passed / `0` unimplemented overall, with `module.workflow` at `117` / `117`, `module.workflow.str` unchanged at `72` / `72`, `module.workflow.bytes` at `45` / `45`, `module.workflow.module_call` at `63` / `63`, and `module.workflow.pattern_call` unchanged at `42` / `42`.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_compile_accepts_compiled_patterns_with_zero_flags_like_cpython tests/python/test_module_workflow_parity_suite.py::test_compiled_pattern_module_keyword_argument_calls_match_cpython` (`66 passed`), `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py` (`806 passed, 1 skipped, 2010 subtests passed`), `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0810-module-workflow-compiled-pattern-compile-bool-false-bytes-named-group-singleton.py` (`117/117`), and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py` (`1487/1487`).
