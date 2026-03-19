# RBR-0706: Convert the module-workflow verbose compile bytes follow-on to real parity

Status: ready
Owner: feature-implementation
Created: 2026-03-19

## Goal
- Convert the exact verbose `bytes` `module.compile()` follow-on that `RBR-0704` published as an honest `unimplemented` outcome into Rust-backed behavior on the existing module-workflow parity surface, without widening into new verbose workflows, multiline-only support, or benchmark catch-up.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The exact published bytes verbose compile row stops raising the scaffold placeholder and instead matches CPython through the public `rebar` API:
  - `rebar.compile(rb"^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $", int(rebar.MULTILINE | rebar.VERBOSE))` returns a compiled `rebar.Pattern`;
  - the compiled metadata matches CPython exactly for this bounded slice: `pattern` stays the same `bytes`, `flags == 72`, `groups == 1`, and `groupindex == {"key": 1}`;
  - repeated calls for that exact bytes pattern/flag pair reuse the cached compiled object just as the existing module-workflow compile surface expects.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path and converts the published bytes follow-on into ordinary parity coverage instead of a `rebar`-only gap:
  - `test_compile_workflows_match_cpython()` no longer special-cases `VERBOSE_BYTES_COMPILE_CASE_ID` as a `NotImplementedError` branch;
  - `test_source_package_verbose_compile_metadata_and_neighbor_gaps_remain_pinned()` no longer expects `rebar.compile(pattern.encode("ascii"), int(VERBOSE_COMPILE_CASE.flags or 0))` to raise, and instead asserts CPython-matching bytes metadata for that exact verbose pair while keeping the adjacent `rebar.compile(pattern, rebar.MULTILINE)` neighbor gap pinned as unsupported; and
  - do not fork another bytes-only parity suite, fixture path, or helper surface for this one compile row.
- Any new compile classification or metadata plumbing lives behind `rebar._rebar`; Python changes stay limited to public-surface marshalling, cache/object plumbing, and native result handling.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1383` total / `1382` passed / `1` `unimplemented` across `114` manifests to `1383` / `1383` / `0`;
  - `module.workflow` moves from `13` total / `12` passed / `1` `unimplemented` to `13` / `13` / `0`; and
  - the existing `module.workflow.bytes` and `module.workflow.compile` suite summaries each move from `5` total / `4` passed / `1` `unimplemented` to `5` / `5` / `0`.
- Verification passes with:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0706-module-workflow-verbose-bytes-parity.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the implementation bounded to the exact bytes verbose compile row published by `RBR-0704`. Do not broaden into additional verbose workflows, multiline-only parsing support, non-verbose bytes compile work, search/match execution on this pattern, or stdlib delegation.
- Reuse the existing `module_workflow_surface.py` fixture and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another bytes-only correctness manifest, another parity suite, or another benchmark family in this run.
- Keep later benchmark catch-up for this same verbose compile family on the existing `benchmarks/workloads/regression_matrix.py` path rather than inventing a second regression manifest.
- Keep this slice Rust-backed, not Python-only.

## Notes
- `RBR-0706` is the next available feature task id in the current checkout; `RBR-0705` is already occupied by the done architecture cleanup task in `ops/tasks/done/`, and `rg -n "RBR-0706" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked` returned no matches during this planning run.
- Queue this directly behind the drained `RBR-0704` feature head so the only live module-workflow correctness gap closes behind `rebar._rebar` before any later regression benchmark catch-up reopens the same verbose compile family.
- 2026-03-19 feature-planning probes confirm this follow-on is concrete from the tracked frontier:
  - `ops/tasks/done/RBR-0704-publish-module-workflow-verbose-bytes-compile-follow-on.md` records that `workflow-compile-bytes-verbose-regression` was intentionally published as an honest `unimplemented` row on the shared module-workflow surface;
  - direct public-API probing in this planning run showed `rebar.native_module_loaded() == True`, but `rebar.compile(rb"^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $", int(rebar.MULTILINE | rebar.VERBOSE))` still raises `NotImplementedError`, while CPython compiles the same bytes pattern with `flags == 72`, `groups == 1`, and `groupindex == {"key": 1}`;
  - `tests/python/test_module_workflow_parity_suite.py` still special-cases `VERBOSE_BYTES_COMPILE_CASE_ID` as a `rebar`-only gap in `test_compile_workflows_match_cpython()` and still expects the same bytes verbose call to raise inside `test_source_package_verbose_compile_metadata_and_neighbor_gaps_remain_pinned()`;
  - `reports/correctness/latest.py` currently reports `1383` total / `1382` passed / `1` `unimplemented` across `114` manifests, and `module.workflow` at `13` total / `12` passed / `1` `unimplemented`; and
  - `benchmarks/workloads/regression_matrix.py` already owns the adjacent `regression-module-compile-verbose-purged` regression anchor for this verbose compile family, so later Python-path benchmark catch-up can stay on the existing manifest path instead of inventing another benchmark surface.
