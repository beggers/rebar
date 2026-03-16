# RBR-0455: Convert the verbose module.compile regression slice to real parity on the public compile path

Status: done
Owner: feature-implementation
Created: 2026-03-16

## Goal
- Convert the newly published verbose `module.compile()` regression slice from an honest `unimplemented` result into real `rebar.compile()` behavior on the public Python-facing path, while keeping the work pinned to the exact `str` verbose regression pattern before the adjacent regression benchmark row is republished.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_module_surface_scaffold.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `rebar.compile("^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $", rebar.MULTILINE | rebar.VERBOSE)` no longer raises the scaffold placeholder in the live source-tree path; it returns a `re.Pattern`-shaped `rebar.Pattern` with CPython-matching compile metadata for that exact `str` pattern: `pattern == "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $"`, `flags == int(rebar.MULTILINE | rebar.VERBOSE | rebar.UNICODE)`, `groups == 1`, and `groupindex == {"key": 1}`.
- The implementation stays bounded to the exact published verbose compile slice: add support only for that exact `str` pattern and flag pair on the public `compile()` path, and do not broaden into bytes mirrors, non-verbose or differently flagged variants, other grouped compile shapes, direct module `search()`/`match()`/`fullmatch()` helper coverage, cache-mode variants, or new benchmark rows.
- The narrow support lands behind the Rust boundary, not as a stdlib delegation shortcut: extend the Rust core/native compile boundary for this exact shape and keep `python/rebar/__init__.py` limited to public-surface marshalling, cache plumbing, and FFI hookup.
- `tests/python/test_module_surface_scaffold.py` grows only by the minimal module-surface assertions needed to lock the verbose compile metadata down on the shared public helper surface and to keep nearby unsupported compile variants loudly unsupported.
- `tests/python/test_module_workflow_parity_suite.py` drops the current `rebar`-only unsupported marker for the verbose compile slice so the existing `VERBOSE_COMPILE_WORKFLOW_CASES` run through the shared compiled-pattern `search()`/`fullmatch()` contract for both backends without adding another fixture bundle or another verbose workflow manifest.
- The existing published correctness case `workflow-compile-str-verbose-regression` in `tests/conformance/fixtures/module_workflow_surface.py` flips from `unimplemented` to `pass` without adding another fixture manifest or another manifest-local wrapper path.
- `reports/correctness/latest.py` is regenerated honestly and moves to `959` total cases across `107` manifests with `959` passes, `0` failures, and `0` `unimplemented`, while the `module-workflow-surface` slice moves to `12` total cases with `12` passes.
- Verification passes with `cargo build -p rebar-cpython`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_surface_scaffold.py tests/python/test_module_workflow_parity_suite.py tests/conformance/test_correctness_fixture_inventory_contract.py tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0455-verbose-module-compile.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`.

## Constraints
- Leave `benchmarks/workloads/regression_matrix.py`, `tests/benchmarks/benchmark_expectations.py`, and `reports/benchmarks/latest.py` unchanged in this run; the adjacent `regression-module-compile-verbose-purged` row is the explicit benchmark catch-up follow-on once this parity slice lands.
- Keep the task bounded to the exact verbose public compile slice. Do not turn it into a general verbose-mode execution or regression-pack expansion milestone.

## Notes
- Before this task, `RBR-0453` published `workflow-compile-str-verbose-regression` on the shared `module-workflow-surface` manifest, and the tracked `reports/correctness/latest.py` artifact still shows it as the lone `comparison == "unimplemented"` case in the combined scorecard.
- The adjacent benchmark publication already carries `regression-module-compile-verbose-purged` on `benchmarks/workloads/regression_matrix.py`, and the tracked `reports/benchmarks/latest.py` artifact still publishes that row as a known gap.
- The intended post-parity follow-on is `RBR-0457`, which should republish that existing regression benchmark row as a measured source-tree timing once this compile slice is live.
- Completed 2026-03-16: landed exact Rust-backed compile plus bound `search()`/`fullmatch()` support for `^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $` with `MULTILINE|VERBOSE` on the shared native compile path, kept nearby bytes/differently-flagged variants unsupported, verified `cargo build -p rebar-cpython`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_surface_scaffold.py tests/python/test_module_workflow_parity_suite.py tests/conformance/test_correctness_fixture_inventory_contract.py tests/conformance/test_combined_correctness_scorecards.py`, generated `.rebar/tmp/rbr-0455-verbose-module-compile.py` with 12/12 passes for `module_workflow_surface`, and republished `reports/correctness/latest.py` to 959 total / 959 pass / 0 fail / 0 unimplemented. Benchmark artifacts remain unchanged for `RBR-0457`.
