# RBR-0798: Publish the module-workflow compiled-pattern compile explicit-bool-false literal pair

Status: done
Owner: feature-implementation
Created: 2026-03-20

## Goal
- Reopen the existing `module-workflow-surface` correctness frontier with the next concrete compiled-pattern compile keyword neighbor, publishing the exact explicit `flags=False` `rebar.compile(compiled_pattern, ...)` literal pair for the existing `"abc"` and `b"abc"` anchors before named-group bool spellings, nonzero-flag rejections, benchmark catch-up, or another owner family reopens the queue.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another compile-only manifest, detached selector table, or second compiled-pattern owner path:
  - extend `COMPILED_PATTERN_MODULE_KEYWORD_CALL_CASES` by only two `helper="compile"` direct cases:
    - `compiled-pattern-compile-flags-bool-false-str`: `pattern == "abc"`, `args == ()`, `kwargs == {"flags": False}`;
    - `compiled-pattern-compile-flags-bool-false-bytes`: `pattern == b"abc"`, `args == ()`, `kwargs == {"flags": False}`;
  - keep the new direct cases on the existing compiled-pattern module-keyword path so `test_compiled_pattern_module_keyword_argument_calls_match_cpython` exercises the real module boundary instead of adding a new helper-specific test scaffold;
  - update the bundle-contract expectations so `module-workflow-surface` now publishes `112` total rows instead of `110`;
  - update the owner-path text-model split so the bundle now expects `70` `str` rows and `42` `bytes` rows;
  - keep `pattern_call` expectations unchanged at `42` rows with the current helper breakdown;
  - update the shared `module_call` helper breakdown so the owner path now expects `7` `compile` rows, `7` `search` rows, `5` `match` rows, `6` `fullmatch` rows, `9` `split` rows, `2` `findall` rows, `2` `finditer` rows, `10` `sub` rows, `8` `subn` rows, and `2` `escape` rows;
  - extend the published compiled-pattern owner-path assertions so `PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES` now contains thirty-nine rows, inserting:
    - `workflow-module-compile-flags-bool-false-str-compiled-pattern` immediately after `workflow-module-compile-flags-int-zero-str-compiled-pattern`;
    - `workflow-module-compile-flags-bool-false-bytes-compiled-pattern` immediately after `workflow-module-compile-flags-int-zero-bytes-compiled-pattern`;
  - extend the compiled-pattern direct-case alignment so the published direct-anchor sequence likewise inserts:
    - `compiled-pattern-compile-flags-bool-false-str` immediately after `compiled-pattern-compile-flags-int-zero-str`;
    - `compiled-pattern-compile-flags-bool-false-bytes` immediately after `compiled-pattern-compile-flags-int-zero-bytes`;
  - keep the already published default compiled-pattern compile rows, explicit integer-zero rows, named-group compile singleton, helper rows, keyword rows, helper-error rows, and default literal compile rows unchanged in this run; and
  - do not broaden into `flags=re.NOFLAG` duplicate publication rows, named-group `flags=False` rows, nonzero-flag rejection rows, benchmark manifests, benchmark reports, native-boundary scaffolding, or any new manifest in this run.
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only two new `module_call` rows:
  - add `workflow-module-compile-flags-bool-false-str-compiled-pattern`;
  - add `workflow-module-compile-flags-bool-false-bytes-compiled-pattern`;
  - keep both rows pinned to the exact direct parity anchors above on the shared owner path:
    - `pattern == "abc"` with `helper == "compile"`, `use_compiled_pattern == True`, no positional `args`, and `kwargs == {"flags": False}`;
    - `pattern == b"abc"` with `helper == "compile"`, `text_model == "bytes"`, `use_compiled_pattern == True`, no positional `args`, and `kwargs == {"flags": False}`;
  - keep the text-model split explicit by leaving the first row on `str` and the second on `bytes`; and
  - keep the categories/notes explicit that this is the compiled-pattern module-level explicit bool-false flag pair, not the default, integer-zero, or `NOFLAG` spelling slice.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1480` total / `1480` passed / `0` `unimplemented` across `114` manifests to `1482` / `1482` / `0` across the same `114` manifests;
  - `module.workflow` moves from `110` / `110` / `0` to `112` / `112` / `0`;
  - `module.workflow.str` moves from `69` / `69` / `0` to `70` / `70` / `0`;
  - `module.workflow.bytes` moves from `41` / `41` / `0` to `42` / `42` / `0`;
  - `module.workflow.module_call` moves from `56` / `56` / `0` to `58` / `58` / `0`;
  - `module.workflow.pattern_call` stays `42` / `42` / `0`; and
  - at least one of the new explicit-bool-false compiled-pattern compile rows is visible in the tracked scorecard as a representative `module-workflow-surface` compiled-pattern module-call case.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_workflow_keyword_kwargs_signature_distinguishes_bool_int_and_indexlike tests/python/test_module_workflow_parity_suite.py::test_compile_accepts_compiled_patterns_with_zero_flags_like_cpython tests/python/test_module_workflow_parity_suite.py::test_compiled_pattern_module_keyword_argument_calls_match_cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0798-module-workflow-compiled-pattern-compile-bool-false-literal-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached compiled-pattern compile publication file.

## Notes
- `RBR-0798` is the next available task id in the current checkout:
  - `ops/tasks/done/` currently runs through `RBR-0797`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` had no `feature-implementation` task at the start of this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done -maxdepth 1 -type f -printf '%f\n' | rg '^RBR-0798|^RBR-0799'` returned no matches in this run.
- Queue this directly after `RBR-0796` on the same `module-workflow-surface` owner path. `RBR-0797` is architecture cleanup, so it does not change the feature frontier.
- 2026-03-20 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_compile_accepts_compiled_patterns_with_zero_flags_like_cpython tests/python/test_module_workflow_parity_suite.py::test_compile_rejects_nonzero_flags_for_compiled_patterns_like_cpython` passed in this run (`30 passed in 0.11s`);
  - `tests/python/test_module_workflow_parity_suite.py` already carries `_workflow_keyword_kwargs_signature(...)`, and its dedicated coverage proves bool-valued keyword payloads stay distinct from integer and `__index__` carriers on the shared owner path, so the explicit `flags=False` slice can land without another selector abstraction first;
  - direct publication probes in this run confirmed `compiled-pattern-compile-flags-bool-false-str`, `compiled-pattern-compile-flags-bool-false-bytes`, `workflow-module-compile-flags-bool-false-str-compiled-pattern`, and `workflow-module-compile-flags-bool-false-bytes-compiled-pattern` are still absent from `tests/python/test_module_workflow_parity_suite.py`, `tests/conformance/fixtures/module_workflow_surface.py`, `tests/conformance/test_combined_correctness_scorecards.py`, and `reports/correctness/latest.py`;
  - a runtime probe in this run confirmed both CPython and `rebar` already return the same compiled object for `compile(compiled_pattern, False)` on the existing `"abc"` and `b"abc"` anchors, so this remains a publication-only slice rather than a missing implementation prerequisite;
  - `flags=re.NOFLAG` is still not the next task because the current owner-path signature normalizes `RegexFlag(0)` to the same integer-zero keyword signature already published by `RBR-0796`, while `flags=False` remains the next distinct bool-shaped neighbor on the same boundary;
  - no blocked feature task exists to reopen first; and
  - `ops/state/backlog.md` and the frontier prose in `ops/state/current_status.md` already honestly say that no ready feature follow-on survives after the likely same-cycle drain, so this one-task refill does not need a backlog-frontier prose change.

## Completion
- Added `workflow-module-compile-flags-bool-false-str-compiled-pattern` and `workflow-module-compile-flags-bool-false-bytes-compiled-pattern` to `tests/conformance/fixtures/module_workflow_surface.py` directly beside the existing compiled-pattern literal and integer-zero compile rows, keeping the shared owner path pinned to the literal `"abc"` / `b"abc"` anchors with `helper == "compile"`, `use_compiled_pattern == True`, no positional args, and `kwargs == {"flags": False}`.
- Updated `tests/python/test_module_workflow_parity_suite.py` so the shared owner-path contract now expects `112` `module-workflow-surface` rows with a `70`/`42` str/bytes split, `58` `module_call` rows, `7` published `compile` helper rows, and `39` published compiled-pattern module-helper rows; the direct-anchor alignment now inserts `compiled-pattern-compile-flags-bool-false-str` after `compiled-pattern-compile-flags-int-zero-str` and `compiled-pattern-compile-flags-bool-false-bytes` after `compiled-pattern-compile-flags-int-zero-bytes`.
- Updated `tests/conformance/test_combined_correctness_scorecards.py` and republished `reports/correctness/latest.py`; the tracked report diff includes both new representative compiled-pattern compile rows, and the published scorecard now reads `1482` total / `1482` passed / `0` unimplemented across `114` manifests, with `module.workflow` at `112`, `module.workflow.str` at `70`, `module.workflow.bytes` at `42`, `module.workflow.module_call` at `58`, and `module.workflow.pattern_call` unchanged at `42`.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_workflow_keyword_kwargs_signature_distinguishes_bool_int_and_indexlike tests/python/test_module_workflow_parity_suite.py::test_compile_accepts_compiled_patterns_with_zero_flags_like_cpython tests/python/test_module_workflow_parity_suite.py::test_compiled_pattern_module_keyword_argument_calls_match_cpython` (`51 passed in 0.41s`), `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py` (`784 passed, 1 skipped, 1987 subtests passed in 30.99s`), `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0798-module-workflow-compiled-pattern-compile-bool-false-literal-pair.py` (`112/112`), and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py` (`1482/1482`).
