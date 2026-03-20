# RBR-0757: Publish the module-workflow compiled-pattern replacement helper pair

Status: ready
Owner: feature-implementation
Created: 2026-03-20

## Goal
- Reopen the `module-workflow-surface` correctness frontier with the remaining compiled-pattern module-level replacement-helper pair, so the existing owner path catches the adjacent `sub()` / `subn()` workflows up on the published correctness surface before another owner family reopens the queue.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only two new `module_call` rows:
  - add `workflow-module-sub-str-compiled-pattern` and `workflow-module-subn-bytes-compiled-pattern`;
  - keep both rows pinned to the exact adjacent direct parity anchors already defined on the shared owner path in `COMPILED_PATTERN_MODULE_HELPER_CASES`:
    - `compiled-pattern-sub-str-count`: `pattern == "abc"`, default zero flags, `helper == "sub"`, `use_compiled_pattern == True`, and `args == ["x", "zabcabc", 1]`;
    - `compiled-pattern-subn-bytes-count`: `pattern == b"abc"`, default zero flags, `helper == "subn"`, `use_compiled_pattern == True`, and `args == [b"x", b"zabcabc", 1]`;
  - keep `workflow-module-sub-str-compiled-pattern` on the `str` text model and `workflow-module-subn-bytes-compiled-pattern` on the `bytes` text model; and
  - do not broaden into the remaining literal-bytes compiled-pattern `fullmatch()` singleton, raw bounded-wildcard collection helpers, compiled-pattern type-error rows, keyword-argument helper coverage, benchmarks, native-boundary scaffolding, or any new manifest in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another compiled-pattern replacement manifest or suite:
  - update the bundle-contract expectations, selected case-id inventory, and operation/helper counts so `module-workflow-surface` now publishes `50` total rows instead of `48`;
  - update the shared `module_call` helper breakdown so the owner path now expects `4` `search` rows, `3` `match` rows, `3` `fullmatch` rows, `1` `split` row, `1` `findall` row, `1` `finditer` row, `1` `sub` row, `1` `subn` row, and `2` `escape` rows;
  - extend the published compiled-pattern module-helper ownership by exactly two rows so the canonical published slice now includes `workflow-module-sub-str-compiled-pattern` and `workflow-module-subn-bytes-compiled-pattern` beside the existing literal, bounded-wildcard, verbose-bytes, and collection-helper compiled-pattern rows;
  - keep the new rows pinned to the exact direct anchors `compiled-pattern-sub-str-count` and `compiled-pattern-subn-bytes-count` instead of inventing another replacement-helper table or detached owner path; and
  - keep the published compiled-pattern direct-case alignment honest by updating the canonical selected direct-case sequence and text-model subset assertions without restoring any mirrored subset sidecars.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1418` total / `1418` passed / `0` `unimplemented` across `114` manifests to `1420` / `1420` / `0` across the same `114` manifests;
  - `module.workflow` moves from `48` / `48` / `0` to `50` / `50` / `0`;
  - `module.workflow.str` moves from `33` / `33` / `0` to `34` / `34` / `0`;
  - `module.workflow.bytes` moves from `15` / `15` / `0` to `16` / `16` / `0`; and
  - `module.workflow.module_call` moves from `15` / `15` / `0` to `17` / `17` / `0`, with both new compiled-pattern replacement rows visible in the tracked scorecard as representative `module-workflow-surface` cases.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0757-module-workflow-compiled-pattern-replacement-helpers.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached compiled-pattern replacement publication file.

## Notes
- `RBR-0757` is the next available task id in the current checkout:
  - `ops/tasks/done/` currently runs through `RBR-0756`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` had no newer `feature-implementation` task at the start of this run; and
  - `ops/state/backlog.md` and `ops/state/current_status.md` do not reserve a newer tail id.
- Queue this directly after `RBR-0755` on the same `module-workflow-surface` owner path so compiled-pattern publication continues through the adjacent replacement helpers before another owner family reopens the frontier.
- 2026-03-20 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `tests/python/test_module_workflow_parity_suite.py` already carries the exact adjacent direct parity anchors `compiled-pattern-sub-str-count` and `compiled-pattern-subn-bytes-count` in `COMPILED_PATTERN_MODULE_HELPER_CASES`;
  - direct runtime probes in this run confirmed that `rebar.sub(rebar.compile("abc"), "x", "zabcabc", 1)` and `rebar.subn(rebar.compile(b"abc"), b"x", b"zabcabc", 1)` match CPython exactly;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'compiled_pattern and (sub or subn or fullmatch)'` passed in this run (`74 passed, 584 deselected`);
  - `tests/conformance/fixtures/module_workflow_surface.py` currently publishes the compiled-pattern literal and bounded-wildcard match helpers, the bytes verbose regression pair, and the compiled-pattern collection helpers, but not the remaining adjacent `sub()` / `subn()` rows, leaving this pair as the next bounded publication on the same owner path; and
  - no blocked feature task exists to reopen first.
- `ops/state/backlog.md` already honestly says that no ready feature follow-on currently survives after the likely same-cycle drain, so this one-task refill does not need a backlog-frontier prose change.
