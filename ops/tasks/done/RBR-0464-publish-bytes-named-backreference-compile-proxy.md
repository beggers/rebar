# RBR-0464: Publish the bytes named-backreference compile proxy on the shared parser-matrix surface

Status: done
Owner: feature-implementation
Created: 2026-03-16

## Goal
- Extend the published correctness scorecard with the exact bytes parser compile proxy already anchored as `regression-parser-bytes-backreference-purged` on the shared regression benchmark surface, while keeping the work on the ordinary `parser-matrix` correctness path before Rust-backed parity or later benchmark catch-up reopen that bytes backreference frontier.

## Deliverables
- `tests/conformance/fixtures/parser_matrix.py`
- `tests/conformance/correctness_expectations.py`
- `tests/python/test_parser_matrix_parity_suite.py`
- `tests/benchmarks/test_compile_proxy_correctness_anchor_contract.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/parser_matrix.py` grows only by the minimal single compile case needed to publish the exact bytes pattern `b"(?P<tag>[A-Z]{2})(?:-(?P=tag)){1,2}"` on the existing `parser-matrix` manifest; do not create a new correctness manifest for this slice.
- The new case is pinned to that exact public compile path and records CPython versus `rebar` compile behavior honestly on the existing parser-matrix correctness surface.
- The scope stays intentionally narrow: publish only the bytes parser compile proxy needed to anchor `regression-parser-bytes-backreference-purged`; do not broaden into module-helper execution, new benchmark rows, grouped-backreference workflow packs, or another bytes parser stress family in this run.
- `tests/python/test_parser_matrix_parity_suite.py` changes only as needed to keep the new bytes case visible on the shared selected-case frontier while `rebar.compile()` still reports it honestly as unsupported for that exact shape; do not fork a second parser regression suite or bypass the existing selected-case bundle path.
- `tests/benchmarks/test_compile_proxy_correctness_anchor_contract.py` is updated so `regression-parser-bytes-backreference-purged` is no longer treated as an intentionally unanchored compile workload once the matching correctness case exists.
- The shared combined correctness scorecard absorbs the added bytes parser case through the existing expectations path instead of growing another manifest-local wrapper, and the shared `parser-matrix` representative set keeps the bytes anchor visible in the published artifact.
- `reports/correctness/latest.py` is regenerated honestly. With the live checkout still raising the scaffold placeholder on `rebar.compile()` for this exact bytes pattern, the combined report should move to `961` total cases across `107` manifests with `960` passes, `0` failures, and `1` published `unimplemented` outcome, while the shared `parser.compile` suite for `parser-matrix` should move to `17` total cases with `16` passes and `1` `unimplemented`.
- Verification passes with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_compile_proxy_correctness_anchor_contract.py tests/python/test_fixture_parity_support_contract.py tests/python/test_parser_matrix_parity_suite.py`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_correctness_fixture_inventory_contract.py tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/parser_matrix.py --report .rebar/tmp/rbr-0464-bytes-parser-proxy.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`.

## Constraints
- Keep this task correctness-publication only. Do not implement new compile behavior just to make the new case pass.
- Keep the slice on the existing `parser-matrix` correctness path plus the existing `regression_matrix.py` benchmark path; do not fork a second benchmark family or another parser-only harness lane for the same exact compile proxy.
- Leave the Rust-backed compile implementation for the immediate parity follow-on and benchmark publication for the catch-up after that parity lands.

## Notes
- 2026-03-16 planning probe: `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... rebar.compile(b\"(?P<tag>[A-Z]{2})(?:-(?P=tag)){1,2}\") ... PY` still raises `NotImplementedError: rebar.compile() is a scaffold placeholder; the \`re\`-compatible API is not implemented yet`.
- 2026-03-16 planning probe: CPython reports compile metadata for that exact bytes pattern as `flags == 0`, `groups == 1`, and `groupindex == {"tag": 1}`.
- `tests/benchmarks/test_compile_proxy_correctness_anchor_contract.py` currently leaves `regression-parser-bytes-backreference-purged` as the lone known unanchored regression compile row; this task should retire that anchor gap by publishing the matching correctness case, not by changing benchmark workload rows.
- The intended post-publication follow-on is `RBR-0465`, which should convert this exact bytes parser compile proxy to real Rust-backed compile parity on the shared parser path before source-tree regression benchmark catch-up revisits the adjacent purged-cache anchor.

## Completion
- 2026-03-16: Added the single `parser-matrix` bytes compile proxy case for `b"(?P<tag>[A-Z]{2})(?:-(?P=tag)){1,2}"`, kept it on the shared selected-case frontier, and added a direct parser-suite assertion that CPython still reports `flags == 0`, `groups == 1`, and `groupindex == {"tag": 1}` while `rebar.compile()` still raises the scaffold placeholder for that exact bytes pattern.
- 2026-03-16: Updated `tests/benchmarks/test_compile_proxy_correctness_anchor_contract.py` so `regression-parser-bytes-backreference-purged` is now required to stay anchored to a published correctness compile case instead of remaining the lone intentionally unanchored regression row.
- 2026-03-16: Regenerated the temporary parser-only report and the tracked combined publication. The tracked `reports/correctness/latest.py` now records `961` total cases across `107` manifests with `960` passes, `0` failures, and `1` `unimplemented` outcome; the tracked `parser.compile` suite summary is `17` total cases with `16` passes and `1` `unimplemented`, and `bytes-named-backreference-compile-proxy-success` is recorded as `comparison == "unimplemented"` with CPython bytes metadata `{flags: 0, groups: 1, groupindex: {"tag": 1}}`.
- 2026-03-16: Verification passed in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_compile_proxy_correctness_anchor_contract.py tests/python/test_fixture_parity_support_contract.py tests/python/test_parser_matrix_parity_suite.py` (`151 passed, 27 skipped in 0.22s`)
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_correctness_fixture_inventory_contract.py tests/conformance/test_combined_correctness_scorecards.py` (`11 passed, 2217 subtests passed in 24.79s`)
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/parser_matrix.py --report .rebar/tmp/rbr-0464-bytes-parser-proxy.py` (`17` total, `16` passed, `1` unimplemented)
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py` (`961` total, `960` passed, `1` unimplemented)
