# RBR-0759: Publish the module-workflow compiled-pattern replacement-helper type-mismatch pair

Status: done
Owner: feature-implementation
Created: 2026-03-20

## Goal
- Reopen the `module-workflow-surface` correctness frontier with the adjacent compiled-pattern replacement-helper type-mismatch pair, so the existing owner path catches the bounded CPython-visible `TypeError` behavior for `sub()` and `subn()` on the wrong text model before keyword-argument publication or another owner family reopens the queue.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only two new `module_call` rows:
  - add `workflow-module-sub-str-compiled-pattern-on-bytes-string` and `workflow-module-subn-bytes-compiled-pattern-on-str-string`;
  - keep both rows pinned to the exact adjacent direct parity anchors already defined on the shared owner path in `COMPILED_PATTERN_MODULE_HELPER_ERROR_CASES`:
    - `compiled-pattern-sub-str-on-bytes-string`: `pattern == "abc"`, default zero flags, `helper == "sub"`, `use_compiled_pattern == True`, and `args == ["x", b"zabczz", 1]`;
    - `compiled-pattern-subn-bytes-on-str-string`: `pattern == b"abc"`, default zero flags, `helper == "subn"`, `use_compiled_pattern == True`, and `args == [b"x", "zabczz", 1]`;
  - keep `workflow-module-sub-str-compiled-pattern-on-bytes-string` on the `str` text model and `workflow-module-subn-bytes-compiled-pattern-on-str-string` on the `bytes` text model so the owner-path str/bytes split stays explicit even though both rows raise `TypeError`; and
  - do not broaden into the remaining compiled-pattern `search()` / `match()` / `fullmatch()` / `split()` / `findall()` / `finditer()` type-mismatch rows, module keyword-argument rows, pattern keyword-argument rows, benchmark rows, native-boundary scaffolding, or any new manifest in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another compiled-pattern error manifest or suite:
  - update the bundle-contract expectations, selected case-id inventory, and operation/helper counts so `module-workflow-surface` now publishes `52` total rows instead of `50`;
  - update the shared `module_call` helper breakdown so the owner path now expects `4` `search` rows, `3` `match` rows, `3` `fullmatch` rows, `1` `split` row, `1` `findall` row, `1` `finditer` row, `2` `sub` rows, `2` `subn` rows, and `2` `escape` rows;
  - extend the published compiled-pattern module-helper ownership by exactly two rows so the canonical published slice now includes `workflow-module-sub-str-compiled-pattern-on-bytes-string` and `workflow-module-subn-bytes-compiled-pattern-on-str-string` beside the existing success-path compiled-pattern module helpers;
  - keep the new rows pinned to the exact direct anchors `compiled-pattern-sub-str-on-bytes-string` and `compiled-pattern-subn-bytes-on-str-string` instead of inventing another replacement-helper error table or detached owner path; and
  - keep the published compiled-pattern direct-case alignment honest by updating the canonical selected direct-case sequence, text-model subset assertions, and compiled-pattern helper coverage checks without restoring any mirrored sidecars.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1420` total / `1420` passed / `0` `unimplemented` across `114` manifests to `1422` / `1422` / `0` across the same `114` manifests;
  - `module.workflow` moves from `50` / `50` / `0` to `52` / `52` / `0`;
  - `module.workflow.str` moves from `34` / `34` / `0` to `35` / `35` / `0`;
  - `module.workflow.bytes` moves from `16` / `16` / `0` to `17` / `17` / `0`;
  - `module.workflow.module_call` moves from `17` / `17` / `0` to `19` / `19` / `0`; and
  - both new compiled-pattern replacement-helper mismatch rows are visible in the tracked scorecard as representative `module-workflow-surface` exception cases.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0759-module-workflow-compiled-pattern-replacement-helper-type-mismatch-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached compiled-pattern error publication file.

## Notes
- `RBR-0759` is the next available task id in the current checkout:
  - `ops/tasks/done/` currently runs through `RBR-0758`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` had no newer `feature-implementation` task at the start of this run; and
  - `ops/state/backlog.md` and the frontier prose in `ops/state/current_status.md` already honestly say that no ready feature follow-on currently survives after the likely same-cycle drain, so this refill does not need a tracked state-prose change.
- Queue this directly after `RBR-0757` and `RBR-0758` on the same `module-workflow-surface` owner path so compiled-pattern publication continues through the adjacent replacement-helper mismatch pair before module keyword-argument publication or another owner family reopens the frontier.
- 2026-03-20 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `tests/python/test_module_workflow_parity_suite.py` already carries the exact adjacent direct parity anchors `compiled-pattern-sub-str-on-bytes-string` and `compiled-pattern-subn-bytes-on-str-string` in `COMPILED_PATTERN_MODULE_HELPER_ERROR_CASES`;
  - direct runtime probes in this run confirmed that `rebar.sub(rebar.compile("abc"), "x", b"zabczz", 1)` and `rebar.subn(rebar.compile(b"abc"), b"x", "zabczz", 1)` raise the same `TypeError` payloads as CPython;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'compiled_pattern and (type_mismatch or error or wrong_type or keyword)'` passed in this run (`16 passed, 642 deselected`);
  - `tests/conformance/fixtures/module_workflow_surface.py` currently publishes the compiled-pattern success-path module helpers through `sub()` / `subn()` but not the adjacent wrong-text-model replacement-helper rows, leaving this pair as the next bounded publication on the same owner path; and
  - no blocked feature task exists to reopen first.

## Completion
- Completed 2026-03-20 by publishing `workflow-module-sub-str-compiled-pattern-on-bytes-string` and `workflow-module-subn-bytes-compiled-pattern-on-str-string` on the existing `module-workflow-surface` manifest, keeping both rows pinned to the existing `COMPILED_PATTERN_MODULE_HELPER_ERROR_CASES` anchors on the shared parity owner path.
- Updated `tests/python/test_module_workflow_parity_suite.py` so the canonical fixture inventory now carries `52` module-workflow rows, the `module_call` helper breakdown now expects `2` `sub` rows and `2` `subn` rows, and the compiled-pattern owner-path alignment check maps the published mismatch rows back to `compiled-pattern-sub-str-on-bytes-string` and `compiled-pattern-subn-bytes-on-str-string`.
- Updated the representative `module-workflow-surface` sample set in `tests/conformance/test_combined_correctness_scorecards.py` and republished `reports/correctness/latest.py`; the tracked combined scorecard now reports `1422` total / `1422` passed / `0` unimplemented across `114` manifests, with `module.workflow` at `52`/`52`/`0`, `module.workflow.str` at `35`/`35`/`0`, `module.workflow.bytes` at `17`/`17`/`0`, and `module.workflow.module_call` at `19`/`19`/`0`.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py` (`679 passed, 1 skipped, 1923 subtests passed`), `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0759-module-workflow-compiled-pattern-replacement-helper-type-mismatch-pair.py` (`52` executed / `52` passed), and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py` (`1422` executed / `1422` passed).
