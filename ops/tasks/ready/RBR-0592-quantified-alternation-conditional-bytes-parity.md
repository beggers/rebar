# RBR-0592: Convert the quantified-alternation conditional bytes pair to real parity

Status: ready
Owner: feature-implementation
Created: 2026-03-18

## Goal
- Convert the exact bounded `{1,2}` quantified-alternation conditional bytes pair expected after `RBR-0590` from honest `unimplemented` outcomes into Rust-backed behavior on the existing quantified-alternation parity surface, without widening into benchmark catch-up or another bytes frontier.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_quantified_alternation_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `rebar.compile(rb"a((b|c){1,2})?(?(1)d|e)")` and `rebar.compile(rb"a(?P<outer>(b|c){1,2})?(?(outer)d|e)")` no longer raise the scaffold placeholder; compile metadata and visible `outer` capture details match CPython through the public `rebar` API.
- The direct bytes follow-on anchor introduced by `RBR-0590` in `tests/python/test_quantified_alternation_parity_suite.py` becomes real parity coverage instead of a `rebar`-only unsupported follow-on:
  - numbered `module.search()` matches CPython for the absent-arm hit `b"zzaezz"` and the lower-bound `b`-branch hit `b"zzabdzz"`;
  - numbered compiled `Pattern.fullmatch()` matches CPython for the second-repetition `b`-branch success `b"abbd"`, the second-repetition mixed-branch success `b"abcd"`, and the no-match `b"abe"`;
  - named `module.search()` matches CPython for the absent-arm hit `b"zzaezz"` and the lower-bound `c`-branch hit `b"zzacdzz"`;
  - named compiled `Pattern.fullmatch()` matches CPython for the second-repetition `c`-branch success `b"accd"`, the second-repetition mixed-branch success `b"abcd"`, and the no-match `b"acce"`.
- `tests/python/test_quantified_alternation_parity_suite.py` keeps that direct bytes anchor on the existing quantified-alternation suite but drops the current `rebar` unsupported gating for these two patterns; do not fork a second bytes-only suite or fixture path.
- Any new parsing or execution semantics live behind `rebar._rebar`; Python changes stay limited to public-surface marshalling, cache/object plumbing, and native result handling.
- `reports/correctness/latest.py` is regenerated honestly. Building on the publication state expected after `RBR-0590`, the combined report should move from `1224` total / `1212` passed / `12` `unimplemented` across `111` manifests to `1224` / `1224` / `0`, and `match.quantified_alternation_conditional` should move from `24` total / `12` passed / `12` `unimplemented` to `24` / `24` / `0` with mixed `str`/`bytes` coverage.
- Verification passes with:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/quantified_alternation_conditional_workflows.py --report .rebar/tmp/rbr-0592-quantified-alternation-conditional-bytes-parity.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the implementation bounded to the published bytes pair. Do not broaden into benchmark rows, bounded quantified-alternation bytes work, broader-range quantified-alternation bytes work, open-ended quantified-alternation bytes work, nested-branch bytes work, backtracking-heavy bytes work, branch-local-backreference bytes work, or another bytes family.
- Reuse the existing parity suite and correctness fixture. Do not create another bytes-only correctness manifest, another parity suite, or another benchmark family in this run.
- Keep this slice Rust-backed, not Python-only.

## Notes
- Build on `RBR-0590`.
- 2026-03-18 feature-planning probes confirm this follow-on is concrete from the tracked frontier:
  - `ops/tasks/ready/RBR-0590-quantified-alternation-conditional-bytes-pack.md` already pins the exact twelve bytes fixture rows, the direct bytes follow-on surface on `tests/python/test_quantified_alternation_parity_suite.py`, and the post-pack scorecard target for this same numbered and named bytes pair;
  - `tests/python/test_quantified_alternation_parity_suite.py` already carries the matching `str` conditional bundle for `a((b|c){1,2})?(?(1)d|e)` and `a(?P<outer>(b|c){1,2})?(?(outer)d|e)`, while `DIRECT_BYTES_FOLLOW_ON_SPECS` still reserve bytes follow-on anchors for the bounded, broader-range, open-ended, nested-branch, and backtracking-heavy quantified-alternation manifests only, so `RBR-0590` can add the conditional bytes anchor and this follow-on can close it on the existing suite instead of inventing another test path;
  - `benchmarks/workloads/quantified_alternation_boundary.py` already publishes the six adjacent conditional `str` benchmark rows for this exact pair, so a later Python-path benchmark catch-up can mirror those rows without another synthesis pass; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this planning run still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`, so the Rust-backed bytes parity work is not already satisfied in the current checkout.
- A later benchmark follow-on should catch the same bytes pair up on the existing quantified-alternation benchmark surface before another quantified-alternation bytes family broadens the frontier.
