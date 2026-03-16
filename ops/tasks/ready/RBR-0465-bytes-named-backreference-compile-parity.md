# RBR-0465: Convert the bytes named-backreference compile proxy to real parity on the shared parser path

Status: ready
Owner: feature-implementation
Created: 2026-03-16

## Goal
- Convert the newly published bytes named-backreference compile proxy from an honest `unimplemented` result into real `rebar.compile()` behavior on the shared public parser surface, while keeping the work pinned to the exact `bytes` pattern already published on `parser-matrix` before the adjacent regression benchmark row is republished.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_parser_matrix_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `rebar.compile(b"(?P<tag>[A-Z]{2})(?:-(?P=tag)){1,2}")` no longer raises the scaffold placeholder in the live source-tree path; it returns a `re.Pattern`-shaped `rebar.Pattern` with CPython-matching compile metadata for that exact `bytes` pattern: `pattern == b"(?P<tag>[A-Z]{2})(?:-(?P=tag)){1,2}"`, `flags == 0`, `groups == 1`, and `groupindex == {"tag": 1}`.
- Keep the implementation bounded to that exact published bytes compile row. Do not broaden into bytes execution, other grouped-backreference forms, module-helper execution, new benchmark rows, or general bytes parser support in this run.
- The narrow support lands behind the Rust boundary, not as a stdlib delegation shortcut: extend the Rust core/native compile boundary for this exact shape and keep `python/rebar/__init__.py` limited to public-surface marshalling, cache plumbing, and FFI hookup.
- `tests/python/test_parser_matrix_parity_suite.py` drops the current `rebar`-only unsupported marker for `bytes-named-backreference-compile-proxy-success` and moves that existing published case onto the shared compile-metadata contract while keeping the row compile-only on the existing placeholder-search contract; do not add another parser regression suite or a second fixture manifest for this slice.
- The same bytes parser case is covered by the existing cache-identity and no-stdlib-delegation observations as needed to prove the exact compile row is now truly live behind `rebar._rebar`, while `compiled.search(...)` for that row still raises the existing `rebar.Pattern.search()` placeholder.
- The existing published correctness case `bytes-named-backreference-compile-proxy-success` in `tests/conformance/fixtures/parser_matrix.py` flips from `unimplemented` to `pass` without adding another correctness manifest or another manifest-local wrapper path.
- `reports/correctness/latest.py` is regenerated honestly and moves to `961` total cases across `107` manifests with `961` passes, `0` failures, and `0` published `unimplemented` outcomes, while the shared `parser.compile` suite for `parser-matrix` moves to `17` total cases with `17` passes.
- Verification passes with `cargo build -p rebar-cpython`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_parser_matrix_parity_suite.py tests/conformance/test_correctness_fixture_inventory_contract.py tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/parser_matrix.py --report .rebar/tmp/rbr-0465-parser-matrix.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`.

## Constraints
- Leave `tests/conformance/fixtures/parser_matrix.py`, `benchmarks/workloads/regression_matrix.py`, `tests/benchmarks/benchmark_expectations.py`, and `reports/benchmarks/latest.py` unchanged in this run; the paired benchmark publication catch-up is the explicit follow-on once this compile slice is live.
- Keep the task bounded to the exact bytes parser compile proxy. Do not turn it into a general bytes named-backreference or bytes execution milestone.

## Notes
- 2026-03-16 planning probe: `PYTHONPATH=python .venv/bin/python - <<'PY' ... rebar.compile(b"(?P<tag>[A-Z]{2})(?:-(?P=tag)){1,2}") ... PY` still raises `NotImplementedError: rebar.compile() is a scaffold placeholder; the \`re\`-compatible API is not implemented yet`.
- 2026-03-16 planning probe: `PYTHONPATH=python .venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/regression_matrix.py --report .rebar/tmp/feature-planning-regression-bytes-probe.py` reports `5` total workloads with `4` measured and `1` known gap, confirming `regression-parser-bytes-backreference-purged` remains the lone `regression-matrix` gap in the current checkout.
- 2026-03-16 planning probe: CPython reports compile metadata for that exact bytes pattern as `flags == 0`, `groups == 1`, and `groupindex == {"tag": 1}`.
- The adjacent regression publication already carries the same pattern as `regression-parser-bytes-backreference-purged` on `benchmarks/workloads/regression_matrix.py`; that row should stay unchanged here and become the benchmark catch-up target immediately after this compile slice is live.
- The intended post-parity follow-on is `RBR-0467`, which should republish `regression-parser-bytes-backreference-purged` as a measured source-tree timing on the shared `regression-matrix` surface without widening the benchmark frontier.
