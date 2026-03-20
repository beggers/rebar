# RBR-0802: Publish the module-workflow compiled-pattern compile explicit-int-zero named-group singleton

Status: ready
Owner: feature-implementation
Created: 2026-03-20

## Goal
- Reopen the existing `module-workflow-surface` correctness frontier with the next concrete compiled-pattern compile keyword neighbor, publishing the exact explicit `flags=0` `rebar.compile(compiled_pattern, ...)` named-group singleton for the existing `r"(?P<word>abc)"` anchor before `NOFLAG` duplicate publication, nonzero-flag rejections, benchmark catch-up, or another owner family reopens the queue.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another compile-only manifest, detached selector table, or second compiled-pattern owner path:
  - extend `COMPILED_PATTERN_MODULE_KEYWORD_CALL_CASES` by only one `helper="compile"` direct case:
    - `compiled-pattern-compile-flags-int-zero-str-named-group`: `pattern == r"(?P<word>abc)"`, `args == ()`, `kwargs == {"flags": 0}`;
  - keep the new direct case on the existing compiled-pattern module-keyword path so `test_compiled_pattern_module_keyword_argument_calls_match_cpython` exercises the real module boundary instead of adding a helper-specific test scaffold;
  - update the bundle-contract expectations so `module-workflow-surface` now publishes `114` total rows instead of `113`;
  - update the owner-path text-model split so the bundle now expects `72` `str` rows and `42` `bytes` rows;
  - keep `pattern_call` expectations unchanged at `42` rows with the current helper breakdown;
  - update the shared `module_call` helper breakdown so the owner path now expects `9` `compile` rows, `7` `search` rows, `5` `match` rows, `6` `fullmatch` rows, `9` `split` rows, `2` `findall` rows, `2` `finditer` rows, `10` `sub` rows, `8` `subn` rows, and `2` `escape` rows;
  - extend the published compiled-pattern owner-path assertions so `PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES` now contains forty-one rows, inserting `workflow-module-compile-flags-int-zero-str-compiled-pattern-named-group` immediately after `workflow-module-compile-str-compiled-pattern-named-group` and immediately before `workflow-module-compile-flags-bool-false-str-compiled-pattern-named-group`;
  - extend the compiled-pattern direct-case alignment so the published direct-anchor sequence likewise inserts `compiled-pattern-compile-flags-int-zero-str-named-group` immediately after `compiled-pattern-compile-str-named-group` and immediately before `compiled-pattern-compile-flags-bool-false-str-named-group`;
  - keep the already published literal compiled-pattern compile rows, default named-group compile singleton, explicit bool-false named-group singleton, helper rows, keyword rows, helper-error rows, and default literal compile rows unchanged in this run; and
  - do not broaden into `flags=re.NOFLAG` duplicate publication, bytes named-group variants, nonzero-flag rejection rows, benchmark manifests, benchmark reports, native-boundary scaffolding, or any new manifest in this run.
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only one new `module_call` row:
  - add `workflow-module-compile-flags-int-zero-str-compiled-pattern-named-group`;
  - keep the row pinned to the exact direct parity anchor above on the shared owner path: `pattern == r"(?P<word>abc)"` with `helper == "compile"`, `use_compiled_pattern == True`, no positional `args`, and `kwargs == {"flags": 0}`;
  - keep the row on the existing `str` named-group path; and
  - keep the categories/notes explicit that this is the compiled-pattern module-level named-group explicit integer-zero flag singleton, not the default, bool-false, or `NOFLAG` spelling slice.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1483` total / `1483` passed / `0` `unimplemented` across `114` manifests to `1484` / `1484` / `0` across the same `114` manifests;
  - `module.workflow` moves from `113` / `113` / `0` to `114` / `114` / `0`;
  - `module.workflow.str` moves from `71` / `71` / `0` to `72` / `72` / `0`;
  - `module.workflow.bytes` stays `42` / `42` / `0`;
  - `module.workflow.module_call` moves from `59` / `59` / `0` to `60` / `60` / `0`;
  - `module.workflow.pattern_call` stays `42` / `42` / `0`; and
  - the new named-group explicit-int-zero compiled-pattern compile row is visible in the tracked scorecard as a representative `module-workflow-surface` compiled-pattern module-call case.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_compile_accepts_compiled_patterns_with_zero_flags_like_cpython tests/python/test_module_workflow_parity_suite.py::test_compiled_pattern_module_keyword_argument_calls_match_cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0802-module-workflow-compiled-pattern-compile-int-zero-named-group-singleton.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached compiled-pattern compile publication file.

## Notes
- `RBR-0802` is the next available task id in the current checkout:
  - `ops/tasks/done/` currently runs through `RBR-0801`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` had no `feature-implementation` task at the start of this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done -maxdepth 1 -type f -printf '%f\n' | rg '^RBR-0802|^RBR-0803'` returned no matches in this run.
- Queue this directly after `RBR-0800` on the same `module-workflow-surface` owner path. `RBR-0801` is architecture cleanup, so it does not change the feature frontier.
- 2026-03-20 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_compile_accepts_compiled_patterns_with_zero_flags_like_cpython tests/python/test_module_workflow_parity_suite.py::test_compiled_pattern_module_keyword_argument_calls_match_cpython` passed in this run (`52 passed in 0.12s`);
  - a direct runtime probe in this run confirmed both CPython and `rebar` already return the same compiled object for `compile(compiled_pattern, flags=0)` on the existing `r"(?P<word>abc)"` anchor, so this remains a publication-only slice rather than a missing implementation prerequisite;
  - a companion runtime probe in this run confirmed both CPython and `rebar` still reject `compile(compiled_pattern, IGNORECASE)` for that same named-group anchor with the same `ValueError`, so nonzero-flag rejection work remains a later publication step rather than missing runtime behavior;
  - direct publication probes in this run confirmed `compiled-pattern-compile-flags-int-zero-str-named-group` and `workflow-module-compile-flags-int-zero-str-compiled-pattern-named-group` are still absent from `tests/python/test_module_workflow_parity_suite.py`, `tests/conformance/fixtures/module_workflow_surface.py`, `tests/conformance/test_combined_correctness_scorecards.py`, and `reports/correctness/latest.py`;
  - the shared `_workflow_keyword_kwargs_signature(...)` selector already distinguishes bool-valued keyword payloads from integer and `__index__` carriers on this owner path, so the explicit integer-zero named-group singleton can land without another selector refactor first;
  - `flags=re.NOFLAG` is still not the next task because the current owner-path signature normalizes `RegexFlag(0)` to the same integer-zero keyword signature this task would publish, while this named-group integer-zero singleton remains the next distinct unpublished row on the current boundary;
  - no blocked feature task exists to reopen first; and
  - `ops/state/backlog.md` plus the frontier prose in `ops/state/current_status.md` already honestly say that no ready feature follow-on survives after the likely same-cycle drain, so this one-task refill does not need a backlog-frontier prose change.
