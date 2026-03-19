# RBR-0718: Convert the module-workflow multiline bytes compile follow-on to real parity

Status: ready
Owner: feature-implementation
Created: 2026-03-19

## Goal
- Convert the exact multiline-only `bytes` `module.compile()` follow-on that `RBR-0716` published as an honest `unimplemented` outcome into Rust-backed behavior on the existing module-workflow parity surface, without widening into new `str` coverage, verbose-neighbor rewrites, execution coverage, or benchmark catch-up.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The exact published bytes multiline compile row stops raising the scaffold placeholder and instead matches CPython through the public `rebar` API:
  - `rebar.compile(b"^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $", int(rebar.MULTILINE))` returns a compiled `rebar.Pattern`;
  - the compiled metadata matches CPython exactly for this bounded slice: `pattern` stays the same `bytes`, `flags == 8`, `groups == 1`, and `groupindex == {"key": 1}`;
  - repeated calls for that exact `bytes` pattern and `MULTILINE` flag pair reuse the cached compiled object just as the existing module-workflow compile surface expects; and
  - do not broaden into new `str` rows, `bytes` verbose changes, search/match execution on this pattern, or any new compile family in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path and converts the published bytes multiline follow-on into ordinary parity coverage instead of a `rebar`-only gap:
  - `test_compile_workflows_match_cpython()` no longer special-cases `MULTILINE_BYTES_COMPILE_CASE_ID` as a `NotImplementedError` branch;
  - `test_source_package_verbose_compile_metadata_and_neighbor_gaps_remain_pinned()` no longer expects `rebar.compile(bytes_pattern, rebar.MULTILINE)` to raise, and instead asserts CPython-matching bytes multiline metadata plus cached repeat-compile reuse for that exact call while keeping the adjacent verbose `str` and `bytes` regression assertions and the landed `str` multiline assertion on the same shared owner path; and
  - do not fork another bytes-only parity suite, fixture path, or helper surface for this one compile row.
- Any new compile classification or metadata plumbing lives behind `rebar._rebar`; Python changes stay limited to public-surface marshalling, cache/object plumbing, and native result handling.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1385` total / `1384` passed / `1` `unimplemented` across `114` manifests to `1385` / `1385` / `0`;
  - `module.workflow` moves from `15` total / `14` passed / `1` `unimplemented` to `15` / `15` / `0`; and
  - `module.workflow.compile` moves from `7` total / `6` passed / `1` `unimplemented` to `7` / `7` / `0`.
- Verification passes with:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0718-module-workflow-multiline-bytes-parity.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the implementation bounded to the exact bytes multiline compile row already published by `RBR-0716`. Do not broaden into new `str` multiline work, verbose-neighbor benchmark work, module execution on this pattern, or stdlib delegation.
- Reuse the existing `module_workflow_surface.py` fixture and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or another benchmark family in this run.
- Keep later benchmark catch-up for this same bytes multiline compile family on the existing `benchmarks/workloads/regression_matrix.py` path rather than inventing a second regression manifest.
- Keep this slice Rust-backed, not Python-only.

## Notes
- `RBR-0718` is the next available feature task id in the current checkout; `RBR-0717` is already occupied by the done architecture cleanup task in `ops/tasks/done/`, and `rg -n "RBR-0718" ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked ops/state/backlog.md ops/state/current_status.md` returned no matches during this planning run.
- Queue this directly behind the drained `RBR-0716` head so the only live module-workflow correctness gap closes behind `rebar._rebar` before any later regression benchmark catch-up reopens the same compile family.
- 2026-03-19 feature-planning probes confirm this follow-on is concrete from the tracked frontier:
  - `ops/tasks/done/RBR-0716-publish-module-workflow-multiline-bytes-compile-follow-on.md` records that `workflow-compile-bytes-multiline-regression` was intentionally published as an honest `unimplemented` row on the shared module-workflow surface;
  - `tests/conformance/fixtures/module_workflow_surface.py` already publishes that exact case on the existing manifest with `pattern == b"^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $"`, `flags == 8`, and `text_model == "bytes"`;
  - `tests/python/test_module_workflow_parity_suite.py` still special-cases `MULTILINE_BYTES_COMPILE_CASE_ID` as a `rebar`-only `NotImplementedError` gap in `test_compile_workflows_match_cpython()` and still expects the same exact call to raise inside `test_source_package_verbose_compile_metadata_and_neighbor_gaps_remain_pinned()`;
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... rebar.compile(bytes_pattern, rebar.MULTILINE) ... PY` on the current checkout still raises `NotImplementedError` with the scaffold placeholder message, while CPython reports `flags == 8`, `groups == 1`, and `groupindex == {"key": 1}` for that exact bytes pattern; and
  - `reports/correctness/latest.py` currently reports `1385` total / `1384` passed / `1` `unimplemented` across `114` manifests, and the only published gap is `workflow-compile-bytes-multiline-regression`, while any later Python-path benchmark catch-up can stay on the existing `benchmarks/workloads/regression_matrix.py` manifest instead of inventing another benchmark surface.
