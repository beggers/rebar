# RBR-0550: Convert the open-ended grouped alternation bytes pair to real parity

Status: done
Owner: feature-implementation
Created: 2026-03-17

## Goal
- Convert the exact open-ended `{1,}` grouped alternation bytes pair published by `RBR-0549` from honest `unimplemented` outcomes into Rust-backed behavior on the existing open-ended parity surface, without widening into benchmark catch-up or another bytes frontier.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_open_ended_quantified_group_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `rebar.compile(rb"a(bc|de){1,}d")` and `rebar.compile(rb"a(?P<word>bc|de){1,}d")` no longer raise the scaffold placeholder; compile metadata and visible `word` capture details match CPython through the public `rebar` API.
- The existing `OPEN_ENDED_ALTERNATION_BYTES_CASES` anchor in `tests/python/test_open_ended_quantified_group_parity_suite.py` becomes real parity coverage instead of a `rebar`-only unsupported follow-on:
  - numbered `module.search()` matches CPython for the lower-bound hits `b"zzabcdzz"` and `b"zzadedzz"`;
  - numbered compiled `Pattern.fullmatch()` matches CPython for the bounded success cases `b"abcbcd"`, `b"abcded"`, and `b"abcbcded"` plus the bounded misses `b"ad"` and `b"abed"`;
  - named `module.search()` matches CPython for the lower-bound hits `b"zzabcdzz"` and `b"zzadedzz"`;
  - named compiled `Pattern.fullmatch()` matches CPython for the bounded success cases `b"abcded"`, `b"abcbcded"`, and `b"adededed"` plus the bounded misses `b"ad"` and `b"abed"`.
- `tests/python/test_open_ended_quantified_group_parity_suite.py` keeps `OPEN_ENDED_ALTERNATION_BYTES_CASES` as the direct bytes anchor but drops the current `rebar` unsupported gating for these two patterns; do not fork a second bytes-only suite or fixture path.
- Any new parsing or execution semantics live behind `rebar._rebar`; Python changes stay limited to public-surface marshalling, cache/object plumbing, and native result handling.
- `reports/correctness/latest.py` is regenerated honestly. The combined report should move from `1136` total / `1120` passed / `16` `unimplemented` across `111` manifests to `1136` / `1136` / `0`, and `match.open_ended_quantified_group_alternation` should move from `32` total / `16` passed / `16` `unimplemented` to `32` / `32` / `0`.
- Verification passes with:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/open_ended_quantified_group_alternation_workflows.py --report .rebar/tmp/rbr-0550-open-ended-grouped-alternation-bytes-parity.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the implementation bounded to the published bytes pair. Do not broaden into benchmark rows, broader-range open-ended grouped work, or another bytes family.
- Reuse the existing parity suite and correctness fixture. Do not create another bytes-only correctness manifest, another parity suite, or another benchmark family in this run.
- Keep this slice Rust-backed, not Python-only.

## Notes
- Build on `RBR-0549`.
- 2026-03-17 feature-planning probes confirm this task is not stale:
  - `reports/correctness/latest.py` currently publishes `match.open_ended_quantified_group_alternation` at `32` total / `16` passed / `16` `unimplemented` with `['bytes', 'str']` coverage;
  - `tests/python/test_open_ended_quantified_group_parity_suite.py` still marks `OPEN_ENDED_ALTERNATION_BYTES_CASES` as unsupported for `rebar`;
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this run still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`; and
  - `benchmarks/workloads/open_ended_quantified_group_boundary.py` already publishes the six adjacent measured `str` open-ended grouped-alternation rows for this exact `{1,}` slice, so the surviving benchmark follow-on should reuse that existing Python-path manifest instead of inventing another benchmark family.
- The surviving follow-on after this task is `RBR-0552`, which should add the six adjacent bytes benchmark mirrors for the same open-ended grouped-alternation pair on `benchmarks/workloads/open_ended_quantified_group_boundary.py`.

## Completion Notes
- Landed bounded Rust-backed compile and match support for `rb"a(bc|de){1,}d"` and `rb"a(?P<word>bc|de){1,}d"` in `crates/rebar-core/src/lib.rs`, including bytes compile metadata plus `search()` and `fullmatch()` capture reporting for the exact published `{1,}` grouped-alternation pair.
- Updated `tests/python/test_open_ended_quantified_group_parity_suite.py` to drop the `rebar`-only bytes placeholder gating for `OPEN_ENDED_ALTERNATION_BYTES_CASES` and let the manifest-backed bytes rows run through the normal generic compile/module/pattern parity buckets while keeping the direct bytes anchor in place.
- Republished the tracked combined correctness report in `reports/correctness/latest.py`; the tracked artifact now reads `1136` total / `1136` passed / `0` failed / `0` unimplemented overall, and `match.open_ended_quantified_group_alternation` now reads `32` total / `32` passed / `0` unimplemented with `['bytes', 'str']` coverage.
- Existing native bridge and Python wrapper paths were sufficient once the Rust core recognized this slice, so no slice-specific changes were required in `crates/rebar-cpython/src/lib.rs` or `python/rebar/__init__.py`.
- Verified with `cargo build -p rebar-cpython`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/open_ended_quantified_group_alternation_workflows.py --report .rebar/tmp/rbr-0550-open-ended-grouped-alternation-bytes-parity.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`.
