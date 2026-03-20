# RBR-0740: Publish the module-workflow bounded wildcard compile pair

Status: done
Owner: feature-implementation
Created: 2026-03-20

## Goal
- Reopen the `module-workflow-surface` correctness frontier with the first bounded Rust-backed wildcard compile pair, so the existing owner path stops deepening shim-only compiled-pattern helper publication and instead publishes an already landed `rebar._rebar` slice on the same backend-parameterized Python correctness surface.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only two new `compile` rows:
  - add `workflow-compile-str-bounded-wildcard` and `workflow-compile-str-bounded-wildcard-ignorecase`;
  - keep both rows pinned to the exact direct parity anchors already defined on the shared owner path in `BOUNDED_WILDCARD_COMPILE_CASES`:
    - `bounded-wildcard-compile-default`: `pattern == "a.c"` with default zero flags; and
    - `bounded-wildcard-compile-ignorecase`: `pattern == "a.c"` with `flags == int(re.IGNORECASE)`;
  - keep both rows on the `str` text model; and
  - do not broaden into bounded-wildcard pattern helper rows, unsupported placeholder paths, bytes wildcard work, additional compiled-pattern module-helper publication, or benchmark rows in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another wildcard-specific fixture or suite:
  - update the bundle-contract expectations, selected case-id inventory, compile-only selection, and operation/helper counts so `module-workflow-surface` now publishes `35` total rows instead of `33`;
  - update the shared `compile` breakdown so the owner path now expects `9` compile rows instead of `7`;
  - extend the published pattern set to include `"a.c"` while keeping the existing compile, pattern, cache, purge, compiled-module-helper, and escape buckets on the same owner file; and
  - keep the new rows pinned to the exact direct parity anchors `bounded-wildcard-compile-default` and `bounded-wildcard-compile-ignorecase` from `BOUNDED_WILDCARD_COMPILE_CASES` instead of inventing another compile-case table or another wildcard-specific ownership layer.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1403` total / `1403` passed / `0` `unimplemented` across `114` manifests to `1405` / `1405` / `0` across the same `114` manifests;
  - `module.workflow` moves from `33` / `33` / `0` to `35` / `35` / `0`;
  - `module.workflow.str` moves from `18` / `18` / `0` to `20` / `20` / `0`;
  - `module.workflow.compile` moves from `7` / `7` / `0` to `9` / `9` / `0`; and
  - both new bounded-wildcard compile rows are visible in the tracked scorecard as representative `module-workflow-surface` cases.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0740-module-workflow-bounded-wildcard-compile-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached bounded-wildcard publication file.

## Notes
- `RBR-0740` is the next available task id in the current checkout:
  - `ops/tasks/done/` currently runs through `RBR-0739`;
  - no newer `feature-implementation` task is ready, in progress, or blocked; and
  - older missing ids exist in historical ranges, but none are still named as the live feature frontier in tracked queue/state files.
- Queue this directly after `RBR-0738` as the next feature slice because the current milestone says to seed a Rust-boundary slice rather than deepen the Python shim, and the bounded wildcard compile pair is already landed behind the live `rebar` path on the existing `module-workflow-surface` owner file.
- 2026-03-20 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `tests/python/test_module_workflow_parity_suite.py` already carries the exact direct parity anchors `bounded-wildcard-compile-default` and `bounded-wildcard-compile-ignorecase` in `BOUNDED_WILDCARD_COMPILE_CASES`;
  - direct runtime probes in this run confirmed that `rebar.compile("a.c")` and `rebar.compile("a.c", rebar.IGNORECASE)` match CPython on `.pattern`, `.flags`, `.groups`, and `.groupindex`;
  - `tests/conformance/fixtures/module_workflow_surface.py` currently publishes no `a.c` rows at all, leaving this compile pair as the next bounded Rust-backed publication slice on the same owner path; and
  - no blocked feature task exists to reopen first.

## Completion
- Added `workflow-compile-str-bounded-wildcard` and `workflow-compile-str-bounded-wildcard-ignorecase` to `tests/conformance/fixtures/module_workflow_surface.py` and kept them aligned to the shared `BOUNDED_WILDCARD_COMPILE_CASES` owner-path anchors in `tests/python/test_module_workflow_parity_suite.py`.
- Updated the shared module-workflow fixture inventories and compile-only selection so the owner path now publishes 35 rows total with 9 compile rows, and extended the combined scorecard representative-case list so both bounded-wildcard compile rows are sampled from the tracked report.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0740-module-workflow-bounded-wildcard-compile-pair.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`.
- Tracked `reports/correctness/latest.py` now publishes 1405 total / 1405 passed / 0 unimplemented across 114 manifests; `module.workflow` is 35 / 35 / 0, `module.workflow.str` is 20 / 20 / 0, and `module.workflow.compile` is 9 / 9 / 0.
