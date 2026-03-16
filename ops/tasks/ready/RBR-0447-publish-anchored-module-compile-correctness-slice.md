# RBR-0447: Publish anchored module.compile correctness coverage on the shared module-workflow surface

Status: ready
Owner: feature-implementation
Created: 2026-03-16

## Goal
- Extend the published correctness scorecard with the exact anchored-literal `module.compile("^abc$")` workflow that currently blocks the old `module_boundary.py` compile rows from becoming real `rebar` timings, while keeping the work on the ordinary module-workflow correctness path before parity or benchmark catch-up reopen the frontier.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/conformance/correctness_expectations.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` grows only by the minimal single compile-workflow case needed to publish the public `rebar.compile("^abc$")` contract on the existing `module-workflow-surface` manifest; do not create a new correctness manifest for this slice.
- The new case is pinned to the exact `str` pattern `^abc$` through the public module `compile` entrypoint and records CPython versus `rebar` compile-metadata behavior honestly on the existing correctness path.
- The scope stays intentionally narrow: publish only the anchored literal compile workflow needed to unblock the adjacent `module_boundary.py` cold/warm/purged compile frontier; do not broaden into bytes mirrors, anchored search/match/fullmatch execution, grouped anchors, flag variants, cache/purge variants, or new benchmark rows in this run.
- The shared combined correctness scorecard coverage absorbs the added module-workflow case through the existing expectations path instead of growing another manifest-local regression wrapper, and the new case remains visible as `pass` or `unimplemented` rather than disappearing from the published artifact.
- `reports/correctness/latest.py` is regenerated honestly. With the live checkout still raising the scaffold placeholder on `rebar.compile("^abc$")`, the combined report should move to `958` total cases across `107` manifests with `957` passes, `0` failures, and `1` published `unimplemented` outcome, while `module-workflow-surface` should move to `11` total cases with `10` passes and `1` `unimplemented`.
- Verification passes with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_correctness_fixture_inventory_contract.py tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0447-anchored-module-compile.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`.

## Constraints
- Keep this task correctness-publication only. Do not implement new compile behavior just to make the new case pass.
- Keep the slice on the existing module-workflow correctness path and the existing `module_boundary.py` benchmark path; do not fork a second benchmark family or a second module-workflow harness lane for the same anchored compile behavior.
- Leave the Rust-backed compile implementation for the immediate parity follow-on and the `module_boundary.py` cold/warm/purged timing publication for the benchmark catch-up after that parity lands.

## Notes
- Direct inspection of the current checkout shows `rebar.compile("^abc$")` still raises `NotImplementedError`, while `benchmarks/workloads/module_boundary.py` already carries the three adjacent `module-compile-literal-{cold,warm,purged}` rows for that exact pattern.
- The intended post-publication follow-on is `RBR-0449`, which should convert this newly published anchored literal compile case to real Rust-backed parity on the public `rebar.compile()` surface before the old `module_boundary.py` compile gaps are turned into measured source-tree timings.
