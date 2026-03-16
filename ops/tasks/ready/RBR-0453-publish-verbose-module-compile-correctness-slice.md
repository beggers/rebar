# RBR-0453: Publish the verbose module.compile regression slice on the shared module-workflow surface

Status: ready
Owner: feature-implementation
Created: 2026-03-16

## Goal
- Extend the published correctness scorecard with the exact verbose `module.compile()` regression workflow that already exists as `regression-module-compile-verbose-purged` on the shared Python-path benchmark surface, while keeping the work on the ordinary module-workflow correctness path before Rust-backed parity or regression benchmark catch-up reopen the compile frontier.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/conformance/correctness_expectations.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` grows only by the minimal single compile-workflow case needed to publish the public `rebar.compile()` contract for the exact `str` pattern `^ (?P<key>[A-Z_]+) \s* = \s* (?:[A-Z]{2,4}+|\d{2,3}) $` with `re.MULTILINE | re.VERBOSE` on the existing `module-workflow-surface` manifest; do not create a new correctness manifest for this slice.
- The new case is pinned to that exact public module `compile` entrypoint plus flag combination and records CPython versus `rebar` compile-metadata behavior honestly on the existing correctness path.
- The scope stays intentionally narrow: publish only the verbose compile workflow needed to anchor the adjacent `regression-module-compile-verbose-purged` benchmark gap; do not broaden into bytes mirrors, search/match/fullmatch execution, grouped execution, cache/purge-only variants, other flag combinations, or new benchmark rows in this run.
- The shared combined correctness scorecard absorbs the added module-workflow case through the existing expectations path instead of growing another manifest-local regression wrapper, and the new case remains visible as `pass` or `unimplemented` rather than disappearing from the published artifact.
- `reports/correctness/latest.py` is regenerated honestly. With the live checkout still raising the scaffold placeholder on `rebar.compile()` for this verbose pattern, the combined report should move to `959` total cases across `107` manifests with `958` passes, `0` failures, and `1` published `unimplemented` outcome, while `module-workflow-surface` should move to `12` total cases with `11` passes and `1` `unimplemented`.
- Verification passes with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_correctness_fixture_inventory_contract.py tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0453-verbose-module-compile.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`.

## Constraints
- Keep this task correctness-publication only. Do not implement new compile behavior just to make the new case pass.
- Keep the slice on the existing module-workflow correctness path and the existing `benchmarks/workloads/regression_matrix.py` benchmark path; do not fork a second benchmark family or a second module-workflow harness lane for the same verbose compile behavior.
- Leave the Rust-backed compile implementation for the immediate parity follow-on and the regression benchmark catch-up after that parity lands.

## Notes
- Direct planning verification in the current checkout shows `rebar.compile("^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $", rebar.MULTILINE | rebar.VERBOSE)` still raises `NotImplementedError: rebar.compile() is a scaffold placeholder; the \`re\`-compatible API is not implemented yet`.
- The adjacent benchmark publication already carries the exact `regression-module-compile-verbose-purged` row in `benchmarks/workloads/regression_matrix.py`, and `reports/benchmarks/latest.py` still publishes it as `status == "unimplemented"`.
- The intended post-publication follow-on is `RBR-0455`, which should convert this newly published verbose compile case to real Rust-backed parity on the public `rebar.compile()` surface before the adjacent regression benchmark row is turned into a measured source-tree timing.
