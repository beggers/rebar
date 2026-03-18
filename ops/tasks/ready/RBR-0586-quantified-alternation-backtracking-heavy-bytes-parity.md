# RBR-0586: Convert the quantified-alternation backtracking-heavy bytes pair to real parity

Status: ready
Owner: feature-implementation
Created: 2026-03-18

## Goal
- Convert the exact bounded `{1,2}` quantified-alternation backtracking-heavy bytes pair published by `RBR-0584` from honest `unimplemented` outcomes into Rust-backed behavior on the existing quantified-alternation parity surface, without widening into benchmark catch-up or another bytes frontier.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_quantified_alternation_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `rebar.compile(rb"a(b|bc){1,2}d")` and `rebar.compile(rb"a(?P<word>b|bc){1,2}d")` no longer raise the scaffold placeholder; compile metadata and visible `word` capture details match CPython through the public `rebar` API.
- The direct bytes follow-on anchor introduced by `RBR-0584` in `tests/python/test_quantified_alternation_parity_suite.py` becomes real parity coverage instead of a `rebar`-only unsupported follow-on:
  - numbered `module.search()` matches CPython for the lower-bound `b`-branch hit `b"zzabdzz"`;
  - numbered compiled `Pattern.fullmatch()` matches CPython for the lower-bound `bc`-branch success `b"abcd"`, the second-repetition successes `b"abbcd"`, `b"abcbd"`, and `b"abcbcd"`, plus the no-match `b"abccd"`;
  - named `module.search()` matches CPython for the lower-bound `bc`-branch hit `b"zzabcdzz"`;
  - named compiled `Pattern.fullmatch()` matches CPython for the second-repetition successes `b"abbd"` and `b"abcbd"`, plus the no-match `b"abccd"`.
- `tests/python/test_quantified_alternation_parity_suite.py` keeps that direct bytes anchor on the existing quantified-alternation suite but drops the current `rebar` unsupported gating for these two patterns; do not fork a second bytes-only suite or fixture path.
- Any new parsing or execution semantics live behind `rebar._rebar`; Python changes stay limited to public-surface marshalling, cache/object plumbing, and native result handling.
- `reports/correctness/latest.py` is regenerated honestly. Building on the publication state expected after `RBR-0584`, the combined report should move from `1212` total / `1200` passed / `12` `unimplemented` across `111` manifests to `1212` / `1212` / `0`, and `match.quantified_alternation_backtracking_heavy` should move from `24` total / `12` passed / `12` `unimplemented` to `24` / `24` / `0` with mixed `str`/`bytes` coverage.
- Verification passes with:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/quantified_alternation_backtracking_heavy_workflows.py --report .rebar/tmp/rbr-0586-quantified-alternation-backtracking-heavy-bytes-parity.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the implementation bounded to the published bytes pair. Do not broaden into benchmark rows, bounded quantified-alternation bytes work, broader-range quantified-alternation bytes work, open-ended quantified-alternation bytes work, nested-branch bytes work, conditional bytes work, branch-local-backreference bytes work, or another bytes family.
- Reuse the existing parity suite and correctness fixture. Do not create another bytes-only correctness manifest, another parity suite, or another benchmark family in this run.
- Keep this slice Rust-backed, not Python-only.

## Notes
- Build on `RBR-0584`.
- 2026-03-18 feature-planning probes confirm this follow-on is concrete from the tracked frontier:
  - `ops/tasks/ready/RBR-0584-quantified-alternation-backtracking-heavy-bytes-pack.md` already pins the exact twelve bytes fixture rows, the direct bytes follow-on surface on `tests/python/test_quantified_alternation_parity_suite.py`, and the post-pack scorecard target for this same numbered and named bytes pair;
  - `tests/python/test_quantified_alternation_parity_suite.py` already carries the matching `str` backtracking-heavy bundle for `a(b|bc){1,2}d` and `a(?P<word>b|bc){1,2}d`, so the bytes parity slice can stay on the existing suite instead of inventing another test path once the pack lands;
  - `benchmarks/workloads/quantified_alternation_boundary.py` already publishes the six adjacent backtracking-heavy `str` benchmark rows for this exact pair, so a later Python-path benchmark catch-up can mirror those rows without another synthesis pass; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this planning run still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`, so the Rust-backed bytes parity work is not already satisfied in the current checkout.
- A later benchmark follow-on should catch the same bytes pair up on the existing quantified-alternation benchmark surface before another quantified-alternation bytes family broadens the frontier.
