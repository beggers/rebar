# RBR-0459: Publish the parser-stress compile proxy on the shared parser-matrix surface

Status: ready
Owner: feature-implementation
Created: 2026-03-16

## Goal
- Extend the published correctness scorecard with the exact parser-stress compile proxy already anchored as `compile-parser-stress-cold` and `regression-parser-atomic-lookbehind-cold` on the shared benchmark surface, while keeping the work on the ordinary `parser-matrix` correctness path before Rust-backed parity or later benchmark catch-up reopen that heavier parser frontier.

## Deliverables
- `tests/conformance/fixtures/parser_matrix.py`
- `tests/conformance/correctness_expectations.py`
- `tests/python/test_parser_matrix_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/parser_matrix.py` grows only by the minimal single compile case needed to publish the exact `str` parser-stress pattern `(?i:(?P<lemma>[a-z]+))(?:_(?>[a-z]{2,4}+|\\d{2}))?(?:(?<=foo)bar)?(?P=lemma)` on the existing `parser-matrix` manifest; do not create a new correctness manifest for this slice.
- The new case is pinned to that exact public compile path and records CPython versus `rebar` compile behavior honestly on the existing parser-matrix correctness surface.
- The scope stays intentionally narrow: publish only the parser-stress compile proxy needed to anchor the adjacent `compile-parser-stress-cold` and `regression-parser-atomic-lookbehind-cold` benchmark gaps; do not broaden into bytes mirrors, module-helper execution, grouped-backreference workflow packs, or new benchmark rows in this run.
- `tests/python/test_parser_matrix_parity_suite.py` changes only as needed to keep the new published parser-stress case visible on the shared selected-case frontier while `rebar.compile()` still reports it honestly as unsupported for that exact shape; do not fork a second parser regression suite or bypass the existing selected-case bundle path.
- The shared combined correctness scorecard absorbs the added parser case through the existing expectations path instead of growing another manifest-local wrapper, and the new case remains visible as `pass` or `unimplemented` rather than disappearing from the published artifact.
- `reports/correctness/latest.py` is regenerated honestly. With the live checkout still raising the scaffold placeholder on `rebar.compile()` for this exact parser-stress pattern, the combined report should move to `960` total cases across `107` manifests with `959` passes, `0` failures, and `1` published `unimplemented` outcome, while the shared `parser.compile` suite for `parser-matrix` should move to `16` total cases with `15` passes and `1` `unimplemented`.
- Verification passes with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_parser_matrix_parity_suite.py`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_correctness_fixture_inventory_contract.py tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/parser_matrix.py --report .rebar/tmp/rbr-0459-parser-stress.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`.

## Constraints
- Keep this task correctness-publication only. Do not implement new compile behavior just to make the new case pass.
- Keep the slice on the existing `parser-matrix` correctness path plus the existing `compile_matrix.py` and `regression_matrix.py` benchmark paths; do not fork a second benchmark family or another parser-only harness lane for the same exact compile proxy.
- Leave the Rust-backed compile implementation for the immediate parity follow-on and benchmark publication for the catch-up after that parity lands.

## Notes
- 2026-03-16 planning probe: `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... rebar.compile("(?i:(?P<lemma>[a-z]+))(?:_(?>[a-z]{2,4}+|\\d{2}))?(?:(?<=foo)bar)?(?P=lemma)") ... PY` still raises `NotImplementedError: rebar.compile() is a scaffold placeholder; the \`re\`-compatible API is not implemented yet`.
- 2026-03-16 planning probe: `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/compile_matrix.py --report .rebar/tmp/feature-planning-compile-matrix-probe.py` still reports `6` total workloads with `5` measured and `1` known gap, confirming `compile-parser-stress-cold` remains the lone `compile-matrix` gap in the current checkout.
- The adjacent regression publication already carries the exact same pattern as `regression-parser-atomic-lookbehind-cold`, and `reports/benchmarks/latest.py` still publishes that row as a known gap on the shared `regression-matrix` surface.
- The intended post-publication follow-on is `RBR-0460`, which should convert this exact parser-stress compile proxy to real Rust-backed compile parity on the shared parser path before Python-path benchmark catch-up revisits the adjacent compile anchors.
