# RBR-0712: Convert the module-workflow multiline compile follow-on to real parity

Status: ready
Owner: feature-implementation
Created: 2026-03-19

## Goal
- Convert the exact multiline-only `str` `module.compile()` follow-on that `RBR-0710` published as an honest `unimplemented` outcome into Rust-backed behavior on the existing module-workflow parity surface, without widening into bytes siblings, verbose-neighbor rewrites, execution coverage, or benchmark catch-up.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The exact published multiline compile row stops raising the scaffold placeholder and instead matches CPython through the public `rebar` API:
  - `rebar.compile("^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $", int(rebar.MULTILINE))` returns a compiled `rebar.Pattern`;
  - the compiled metadata matches CPython exactly for this bounded slice: `pattern` stays the same `str`, `flags == 40`, `groups == 1`, and `groupindex == {"key": 1}`;
  - repeated calls for that exact `str` pattern and `MULTILINE` flag pair reuse the cached compiled object just as the existing module-workflow compile surface expects; and
  - do not broaden into `bytes` multiline siblings, search/match execution on this pattern, or any new compile family in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path and converts the published multiline follow-on into ordinary parity coverage instead of a `rebar`-only gap:
  - `test_compile_workflows_match_cpython()` no longer special-cases `MULTILINE_COMPILE_CASE_ID` as a `NotImplementedError` branch;
  - `test_source_package_verbose_compile_metadata_and_neighbor_gaps_remain_pinned()` no longer expects `rebar.compile(multiline_pattern, rebar.MULTILINE)` to raise, and instead asserts CPython-matching multiline metadata plus cached repeat-compile reuse for that exact call while keeping the adjacent verbose `str` and `bytes` regression assertions on the same shared owner path; and
  - do not fork another multiline-only parity suite, fixture path, or helper surface for this one compile row.
- Any new compile classification or metadata plumbing lives behind `rebar._rebar`; Python changes stay limited to public-surface marshalling, cache/object plumbing, and native result handling.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1384` total / `1383` passed / `1` `unimplemented` across `114` manifests to `1384` / `1384` / `0`;
  - `module.workflow` moves from `14` total / `13` passed / `1` `unimplemented` to `14` / `14` / `0`; and
  - `module.workflow.compile` moves from `6` total / `5` passed / `1` `unimplemented` to `6` / `6` / `0`.
- Verification passes with:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0712-module-workflow-multiline-parity.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the implementation bounded to the exact multiline-only compile row already published by `RBR-0710`. Do not broaden into bytes multiline support, verbose-neighbor benchmark work, module execution on this pattern, or stdlib delegation.
- Reuse the existing `module_workflow_surface.py` fixture and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or another benchmark family in this run.
- Keep later benchmark catch-up for this same multiline compile family on the existing `benchmarks/workloads/regression_matrix.py` path rather than inventing a second regression manifest.
- Keep this slice Rust-backed, not Python-only.

## Notes
- `RBR-0712` is the next available feature task id in the current checkout; `RBR-0711` is already occupied by the done architecture cleanup task in `ops/tasks/done/`, and `rg -n "RBR-0712" ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked ops/state/backlog.md ops/state/current_status.md` returned no matches during this planning run.
- Queue this directly behind the drained `RBR-0710` head so the only live module-workflow correctness gap closes behind `rebar._rebar` before any later regression benchmark catch-up reopens the same compile family.
- 2026-03-19 feature-planning probes confirm this follow-on is concrete from the tracked frontier:
  - `ops/tasks/done/RBR-0710-publish-module-workflow-multiline-compile-follow-on.md` records that `workflow-compile-str-multiline-regression` was intentionally published as an honest `unimplemented` row on the shared module-workflow surface;
  - `tests/conformance/fixtures/module_workflow_surface.py` already publishes that exact case on the existing manifest with `pattern == "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $"`, `flags == 8`, and `text_model == "str"`;
  - `tests/python/test_module_workflow_parity_suite.py` still special-cases `MULTILINE_COMPILE_CASE_ID` as a `rebar`-only `NotImplementedError` gap in `test_compile_workflows_match_cpython()` and still expects the same exact call to raise inside `test_source_package_verbose_compile_metadata_and_neighbor_gaps_remain_pinned()`;
  - `reports/correctness/latest.py` currently reports `1384` total / `1383` passed / `1` `unimplemented` across `114` manifests, and the only published gap is `workflow-compile-str-multiline-regression`, with CPython already reporting `flags == 40`, `groups == 1`, and `groupindex == {"key": 1}` for that row; and
  - `benchmarks/workloads/regression_matrix.py` already owns the adjacent verbose module-compile regression rows for this exact pattern family, so any later Python-path benchmark catch-up can stay on the existing regression manifest instead of inventing another benchmark surface.
