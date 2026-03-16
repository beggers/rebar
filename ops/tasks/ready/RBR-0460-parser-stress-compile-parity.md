# RBR-0460: Convert the parser-stress compile proxy to real parity on the shared parser path

Status: ready
Owner: feature-implementation
Created: 2026-03-16

## Goal
- Convert the newly published parser-stress compile proxy from an honest `unimplemented` result into real `rebar.compile()` behavior on the shared public parser surface, while keeping the work pinned to the exact `str` pattern already published on `parser-matrix` before the adjacent benchmark rows are republished.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_parser_matrix_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `rebar.compile("(?i:(?P<lemma>[a-z]+))(?:_(?>[a-z]{2,4}+|\\d{2}))?(?:(?<=foo)bar)?(?P=lemma)")` no longer raises the scaffold placeholder in the live source-tree path; it returns a `re.Pattern`-shaped `rebar.Pattern` with CPython-matching compile metadata for that exact `str` pattern: `pattern == "(?i:(?P<lemma>[a-z]+))(?:_(?>[a-z]{2,4}+|\\d{2}))?(?:(?<=foo)bar)?(?P=lemma)"`, `flags == int(rebar.UNICODE)`, `groups == 1`, and `groupindex == {"lemma": 1}`.
- Keep the implementation bounded to that exact published parser-stress compile row. Do not broaden into bytes mirrors, other grouped-backreference forms, module-helper execution, new benchmark rows, or general parser-stress execution support in this run.
- The narrow support lands behind the Rust boundary, not as a stdlib delegation shortcut: extend the Rust core/native compile boundary for this exact shape and keep `python/rebar/__init__.py` limited to public-surface marshalling, cache plumbing, and FFI hookup.
- `tests/python/test_parser_matrix_parity_suite.py` drops the current `rebar`-only unsupported marker for `str-parser-stress-compile-proxy-success` and moves that existing published case onto the shared compile-metadata contract while keeping the row compile-only on the existing placeholder-search contract; do not add another parser regression suite or a second fixture manifest for this slice.
- The same parser-stress case is covered by the existing cache-identity and no-stdlib-delegation observations as needed to prove the exact compile row is now truly live behind `rebar._rebar`, while `compiled.search(...)` for that row still raises the existing `rebar.Pattern.search()` placeholder.
- The existing published correctness case `str-parser-stress-compile-proxy-success` in `tests/conformance/fixtures/parser_matrix.py` flips from `unimplemented` to `pass` without adding another correctness manifest or another manifest-local wrapper path.
- `reports/correctness/latest.py` is regenerated honestly and moves to `960` total cases across `107` manifests with `960` passes, `0` failures, and `0` published `unimplemented` outcomes, while the shared `parser.compile` suite for `parser-matrix` moves to `16` total cases with `16` passes.
- Verification passes with `cargo build -p rebar-cpython`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_parser_matrix_parity_suite.py tests/conformance/test_correctness_fixture_inventory_contract.py tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/parser_matrix.py --report .rebar/tmp/rbr-0460-parser-matrix.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`.

## Constraints
- Leave `tests/conformance/fixtures/parser_matrix.py`, `benchmarks/workloads/compile_matrix.py`, `benchmarks/workloads/regression_matrix.py`, `tests/benchmarks/benchmark_expectations.py`, and `reports/benchmarks/latest.py` unchanged in this run; the paired benchmark publication catch-up is the explicit follow-on once this compile slice is live.
- Keep the task bounded to the exact parser-stress compile proxy. Do not turn it into a general grouped-backreference or parser-execution milestone.

## Notes
- 2026-03-16 planning probe: `PYTHONPATH=python python3 - <<'PY' ... rebar.compile("(?i:(?P<lemma>[a-z]+))(?:_(?>[a-z]{2,4}+|\\d{2}))?(?:(?<=foo)bar)?(?P=lemma)") ... PY` still raises `NotImplementedError: rebar.compile() is a scaffold placeholder; the \`re\`-compatible API is not implemented yet`.
- 2026-03-16 planning probe: CPython reports compile metadata for that exact pattern as `flags == 32`, `groups == 1`, and `groupindex == {"lemma": 1}`.
- The adjacent benchmark publication already carries the same pattern as `compile-parser-stress-cold` on `benchmarks/workloads/compile_matrix.py` and `regression-parser-atomic-lookbehind-cold` on `benchmarks/workloads/regression_matrix.py`; both rows remain explicit source-tree known gaps in the current checkout.
- The intended post-parity follow-on is `RBR-0462`, which should republish those two existing benchmark rows as measured source-tree timings on the shared `compile-matrix` and `regression-matrix` surfaces without widening the benchmark frontier.
