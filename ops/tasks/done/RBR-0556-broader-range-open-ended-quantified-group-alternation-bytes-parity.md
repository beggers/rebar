# RBR-0556: Convert the broader-range open-ended grouped-alternation bytes pair to real parity

Status: done
Owner: feature-implementation
Created: 2026-03-17

## Goal
- Convert the exact broader-range open-ended `{2,}` grouped-alternation bytes pair published by `RBR-0554` from honest `unimplemented` outcomes into Rust-backed behavior on the existing open-ended parity surface, without widening into benchmark catch-up or another bytes frontier.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_open_ended_quantified_group_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `rebar.compile(rb"a(bc|de){2,}d")` and `rebar.compile(rb"a(?P<word>bc|de){2,}d")` no longer raise the scaffold placeholder; compile metadata and visible `word` capture details match CPython through the public `rebar` API.
- The existing `BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES` anchor in `tests/python/test_open_ended_quantified_group_parity_suite.py` becomes real parity coverage instead of a `rebar`-only unsupported follow-on:
  - numbered `module.search()` matches CPython for the lower-bound hits `b"zzabcbcdzz"` and `b"zzadededzz"`;
  - numbered compiled `Pattern.fullmatch()` matches CPython for the bounded success cases `b"abcded"`, `b"abcbcded"`, and `b"adededed"` plus the bounded misses `b"abcd"` and `b"ad"`;
  - named `module.search()` matches CPython for the lower-bound hits `b"zzabcbcdzz"` and `b"zzadededzz"`; and
  - named compiled `Pattern.fullmatch()` matches CPython for the bounded success cases `b"abcded"`, `b"abcbcded"`, and `b"adededed"` plus the bounded misses `b"abcd"` and `b"ad"`.
- `tests/python/test_open_ended_quantified_group_parity_suite.py` keeps `BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES` as the direct bytes anchor but drops the current `rebar` unsupported gating for these two patterns; do not fork a second bytes-only suite or fixture path.
- Any new parsing or execution semantics live behind `rebar._rebar`; Python changes stay limited to public-surface marshalling, cache/object plumbing, and native result handling.
- `reports/correctness/latest.py` is regenerated honestly. The combined report should move from `1152` total / `1136` passed / `16` `unimplemented` across `111` manifests to `1152` / `1152` / `0`, and `match.broader_range_open_ended_quantified_group_alternation` should move from `32` total / `16` passed / `16` `unimplemented` to `32` / `32` / `0`.
- Verification passes with:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/broader_range_open_ended_quantified_group_alternation_workflows.py --report .rebar/tmp/rbr-0556-broader-range-open-ended-grouped-alternation-bytes-parity.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the implementation bounded to the published bytes pair. Do not broaden into benchmark rows, broader-range open-ended grouped-conditional or grouped backtracking-heavy follow-ons, nested grouped follow-ons, or another bytes family.
- Reuse the existing parity suite and correctness fixture. Do not create another bytes-only correctness manifest, another parity suite, or another benchmark family in this run.
- Keep this slice Rust-backed, not Python-only.

## Notes
- Build on `RBR-0554`.
- 2026-03-17 feature-planning probes confirm this task is not stale:
  - `reports/correctness/latest.py` currently publishes the combined report at `1152` total / `1136` passed / `16` `unimplemented` across `111` manifests, and `RBR-0554` already recorded that `match.broader_range_open_ended_quantified_group_alternation` now publishes `32` total / `16` passed / `16` `unimplemented` with mixed `str`/`bytes` coverage;
  - `tests/python/test_open_ended_quantified_group_parity_suite.py` still marks `BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES` as unsupported for `rebar`, with the reason text pinned to `RBR-0556`; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this run still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`.
- The surviving follow-on after this task is `RBR-0558`, which should add the six adjacent bytes benchmark mirrors for the same broader-range open-ended grouped-alternation pair on `benchmarks/workloads/open_ended_quantified_group_boundary.py`.

## Completion Notes
- Generalized the existing open-ended grouped-alternation bytes parser/matcher path in `crates/rebar-core/src/lib.rs` so the same Rust-backed implementation now accepts both `{1,}` and the broader-range `{2,}` lower bound for `a(bc|de){m,}d` and `a(?P<word>bc|de){m,}d` bytes patterns, preserving compile metadata plus numbered and named last-capture spans through the native boundary without widening into other bytes follow-ons.
- Updated `tests/python/test_open_ended_quantified_group_parity_suite.py` so `BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES` stays the direct bytes anchor but no longer marks `rebar` as unsupported for the two target patterns.
- Regenerated the tracked combined correctness publication in `reports/correctness/latest.py`; the tracked artifact now reads `1152` total / `1152` passed / `0` unimplemented across `111` manifests, and `match.broader_range_open_ended_quantified_group_alternation` now reads `32` total / `32` passed / `0` unimplemented.
- Verified with `cargo build -p rebar-cpython`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/broader_range_open_ended_quantified_group_alternation_workflows.py --report .rebar/tmp/rbr-0556-broader-range-open-ended-grouped-alternation-bytes-parity.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`.
