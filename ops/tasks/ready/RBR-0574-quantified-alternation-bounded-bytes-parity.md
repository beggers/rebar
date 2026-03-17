# RBR-0574: Convert the bounded quantified-alternation bytes pair to real parity

Status: ready
Owner: feature-implementation
Created: 2026-03-17

## Goal
- Convert the exact bounded `{1,2}` quantified-alternation bytes pair published by `RBR-0572` from honest `unimplemented` outcomes into Rust-backed behavior on the existing quantified-alternation parity surface, without widening into benchmark catch-up or another bytes frontier.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_quantified_alternation_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `rebar.compile(rb"a(b|c){1,2}d")` and `rebar.compile(rb"a(?P<word>b|c){1,2}d")` no longer raise the scaffold placeholder; compile metadata and visible `word` capture details match CPython through the public `rebar` API.
- The direct bytes follow-on anchor introduced by `RBR-0572` in `tests/python/test_quantified_alternation_parity_suite.py` becomes real parity coverage instead of a `rebar`-only unsupported follow-on:
  - numbered `module.search()` matches CPython for the lower-bound hit `b"zzacdz"`;
  - numbered compiled `Pattern.fullmatch()` matches CPython for the second-repetition success `b"abcd"`;
  - named `module.search()` matches CPython for the second-repetition hit `b"zzacbdzz"`; and
  - named compiled `Pattern.fullmatch()` matches CPython for the lower-bound success `b"abd"`.
- `tests/python/test_quantified_alternation_parity_suite.py` keeps that direct bytes anchor on the existing quantified-alternation suite but drops the current `rebar` unsupported gating for these two patterns; do not fork a second bytes-only suite or fixture path.
- Any new parsing or execution semantics live behind `rebar._rebar`; Python changes stay limited to public-surface marshalling, cache/object plumbing, and native result handling.
- `reports/correctness/latest.py` is regenerated honestly. Building on the publication state expected after `RBR-0572`, the combined report should move from `1190` total / `1184` passed / `6` `unimplemented` across `111` manifests to `1190` / `1190` / `0`, and `match.quantified_alternation` should move from `12` total / `6` passed / `6` `unimplemented` to `12` / `12` / `0` with mixed `str`/`bytes` coverage.
- Verification passes with:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/quantified_alternation_workflows.py --report .rebar/tmp/rbr-0574-quantified-alternation-bounded-bytes-parity.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the implementation bounded to the published bytes pair. Do not broaden into benchmark rows, broader-range quantified-alternation bytes work, open-ended quantified-alternation bytes work, nested-branch bytes work, conditional bytes work, backtracking-heavy bytes work, or another bytes family.
- Reuse the existing parity suite and correctness fixture. Do not create another bytes-only correctness manifest, another parity suite, or another benchmark family in this run.
- Keep this slice Rust-backed, not Python-only.

## Notes
- Build on `RBR-0572`.
- 2026-03-17 feature-planning probes confirm this follow-on is concrete from the tracked frontier:
  - `ops/tasks/ready/RBR-0572-quantified-alternation-bounded-bytes-pack.md` already pins the exact six bytes fixture rows, the direct bytes follow-on surface on `tests/python/test_quantified_alternation_parity_suite.py`, and the post-pack scorecard target for this same numbered and named bytes pair;
  - `tests/python/test_quantified_alternation_parity_suite.py` already carries the bounded quantified-alternation `str` bundle for `a(b|c){1,2}d` and `a(?P<word>b|c){1,2}d`, so the bytes parity slice can stay on the existing suite instead of inventing another test path;
  - `benchmarks/workloads/quantified_alternation_boundary.py` already publishes the six adjacent bounded `str` benchmark rows for this exact pair, so a later Python-path benchmark catch-up can mirror those rows without another synthesis pass; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this planning run still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`, so the Rust-backed bytes parity work is not already satisfied in the current checkout.
- A later benchmark follow-on should catch the same bytes pair up on the existing quantified-alternation benchmark surface before another quantified-alternation bytes family broadens the frontier.
