# RBR-0561: Convert the quantified-alternation open-ended bytes pair to real parity

Status: done
Owner: feature-implementation
Created: 2026-03-17

## Goal
- Convert the exact open-ended `{1,}` quantified-alternation bytes pair published by `RBR-0560` from honest `unimplemented` outcomes into Rust-backed behavior on the existing quantified-alternation parity surface, without widening into benchmark catch-up or another bytes frontier.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_quantified_alternation_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `rebar.compile(rb"a(b|c){1,}d")` and `rebar.compile(rb"a(?P<word>b|c){1,}d")` no longer raise the scaffold placeholder; compile metadata and visible `word` capture details match CPython through the public `rebar` API.
- The `QUANTIFIED_ALTERNATION_OPEN_ENDED_BYTES_CASES` anchor introduced by `RBR-0560` in `tests/python/test_quantified_alternation_parity_suite.py` becomes real parity coverage instead of a `rebar`-only unsupported follow-on:
  - numbered `module.search()` matches CPython for the lower-bound hits `b"zzabdzz"` and `b"zzacdzz"`;
  - numbered compiled `Pattern.fullmatch()` matches CPython for the bounded success cases `b"abcd"`, `b"abccd"`, and `b"abcbcd"` plus the bounded misses `b"ad"` and `b"abed"`;
  - named `module.search()` matches CPython for the lower-bound hits `b"zzabdzz"` and `b"zzacdzz"`; and
  - named compiled `Pattern.fullmatch()` matches CPython for the bounded success cases `b"abcd"`, `b"abccd"`, and `b"abcbcd"` plus the bounded misses `b"ad"` and `b"abed"`.
- `tests/python/test_quantified_alternation_parity_suite.py` keeps `QUANTIFIED_ALTERNATION_OPEN_ENDED_BYTES_CASES` as the direct bytes anchor but drops the current `rebar` unsupported gating for these two patterns; do not fork a second bytes-only suite or fixture path.
- Any new parsing or execution semantics live behind `rebar._rebar`; Python changes stay limited to public-surface marshalling, cache/object plumbing, and native result handling.
- `reports/correctness/latest.py` is regenerated honestly. Building on the publication state expected after `RBR-0560`, the combined report should move from `1168` total / `1152` passed / `16` `unimplemented` across `111` manifests to `1168` / `1168` / `0`, and `match.quantified_alternation_open_ended` should move from `32` total / `16` passed / `16` `unimplemented` to `32` / `32` / `0` with mixed `str`/`bytes` coverage.
- Verification passes with:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/quantified_alternation_open_ended_workflows.py --report .rebar/tmp/rbr-0561-quantified-alternation-open-ended-bytes-parity.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the implementation bounded to the published bytes pair. Do not broaden into benchmark rows, broader-range quantified-alternation bytes work, nested-branch bytes work, conditional bytes work, or another bytes family.
- Reuse the existing parity suite and correctness fixture. Do not create another bytes-only correctness manifest, another parity suite, or another benchmark family in this run.
- Keep this slice Rust-backed, not Python-only.

## Notes
- Build on `RBR-0560`.
- 2026-03-17 feature-planning probes confirm this follow-on is concrete from the tracked frontier:
  - `ops/tasks/ready/RBR-0560-quantified-alternation-open-ended-bytes-pack.md` already pins the exact bytes fixture growth, the direct `QUANTIFIED_ALTERNATION_OPEN_ENDED_BYTES_CASES` follow-on anchor, and the post-pack scorecard target for this same numbered and named bytes pair;
  - `tests/python/test_quantified_alternation_parity_suite.py` already carries the `str` open-ended quantified-alternation bundle for `a(b|c){1,}d` and `a(?P<word>b|c){1,}d`, so the bytes parity slice can stay on the existing suite instead of inventing another test path;
  - `benchmarks/workloads/quantified_alternation_boundary.py` already publishes the six adjacent open-ended `str` benchmark rows for this exact pair, so a later Python-path benchmark catch-up can mirror those rows without another synthesis pass; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this run still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`, so the Rust-backed bytes parity work is not already satisfied in the current checkout.

## Completion
- 2026-03-17: Added Rust-backed compile and bytes match support for `rb"a(b|c){1,}d"` and `rb"a(?P<word>b|c){1,}d"` in `crates/rebar-core/src/lib.rs`; the existing `rebar._rebar` bridge and Python wrapper picked the new support up without additional public-surface logic changes.
- Kept `QUANTIFIED_ALTERNATION_OPEN_ENDED_BYTES_CASES` as the direct bytes anchor and removed the temporary `rebar` unsupported gating instead of forking another suite or manifest path.
- Verified with `cargo build -p rebar-cpython`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/quantified_alternation_open_ended_workflows.py --report .rebar/tmp/rbr-0561-quantified-alternation-open-ended-bytes-parity.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`.
- Published `reports/correctness/latest.py` now records `1168` total / `1168` passed / `0` failed / `0` unimplemented across `111` manifests, and `match.quantified_alternation_open_ended` now records `32` total / `32` passed / `0` failed / `0` unimplemented.
