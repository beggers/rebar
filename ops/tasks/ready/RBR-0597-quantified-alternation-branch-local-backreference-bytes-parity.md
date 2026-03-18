# RBR-0597: Convert the quantified-alternation branch-local-backreference bytes pair to real parity

Status: ready
Owner: feature-implementation
Created: 2026-03-18

## Goal
- Convert the exact bounded `{1,2}` quantified-alternation branch-local-backreference bytes pair expected after `RBR-0595` from honest `unimplemented` outcomes into Rust-backed behavior on the existing branch-local-backreference parity surface, without widening into benchmark catch-up or another bytes frontier.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_branch_local_backreference_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `rebar.compile(rb"a((b|c)\\2){1,2}d")` and `rebar.compile(rb"a(?P<outer>(?P<inner>b|c)(?P=inner)){1,2}d")` no longer raise the scaffold placeholder; compile metadata and visible numbered and named capture details match CPython through the public `rebar` API.
- The direct bytes follow-on anchor introduced by `RBR-0595` in `tests/python/test_branch_local_backreference_parity_suite.py` becomes real parity coverage instead of a `rebar`-only unsupported follow-on:
  - numbered `module.search()` matches CPython for the lower-bound `b`-branch hit `b"zzabbdzz"`;
  - numbered compiled `Pattern.fullmatch()` matches CPython for the lower-bound `c`-branch success `b"accd"`, the second-repetition `b`-branch success `b"abbbbd"`, and the no-match `b"abcd"`;
  - named `module.search()` matches CPython for the lower-bound `c`-branch hit `b"zzaccdzz"`;
  - named compiled `Pattern.fullmatch()` matches CPython for the second-repetition `c`-branch success `b"accccd"`, the second-repetition mixed-branch success `b"abbccd"`, and the no-match `b"abcd"`.
- `tests/python/test_branch_local_backreference_parity_suite.py` keeps that direct bytes anchor on the existing branch-local-backreference suite but drops the current `rebar` unsupported gating for these two patterns; do not fork a second bytes-only suite or fixture path.
- Any new parsing or execution semantics live behind `rebar._rebar`; Python changes stay limited to public-surface marshalling, cache/object plumbing, and native result handling.
- `reports/correctness/latest.py` is regenerated honestly. Building on the publication state expected after `RBR-0595`, the combined report should move from `1234` total / `1224` passed / `10` `unimplemented` across `111` manifests to `1234` / `1234` / `0`, and `match.quantified_alternation_branch_local_backreference` should move from `20` total / `10` passed / `10` `unimplemented` to `20` / `20` / `0` with mixed `str`/`bytes` coverage.
- Verification passes with:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/quantified_alternation_branch_local_backreference_workflows.py --report .rebar/tmp/rbr-0597-quantified-alternation-branch-local-backreference-bytes-parity.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the implementation bounded to the published bytes pair. Do not broaden into benchmark rows, bounded optional-group-alternation branch-local-backreference bytes work, quantified nested-group branch-local-backreference bytes work, broader-range grouped branch-local-backreference bytes work, open-ended grouped branch-local-backreference bytes work, or another bytes family.
- Reuse the existing parity suite and correctness fixture. Do not create another bytes-only correctness manifest, another parity suite, or another benchmark family in this run.
- Keep this slice Rust-backed, not Python-only.

## Notes
- Build on `RBR-0595`.
- 2026-03-18 feature-planning probes confirm this follow-on is concrete from the tracked frontier:
  - `ops/tasks/ready/RBR-0595-quantified-alternation-branch-local-backreference-bytes-pack.md` already pins the exact ten bytes fixture rows, the direct bytes follow-on surface on `tests/python/test_branch_local_backreference_parity_suite.py`, and the post-pack scorecard target for this same numbered and named bytes pair;
  - `tests/python/test_branch_local_backreference_parity_suite.py` already carries the matching `str` branch-local-backreference bundle for `a((b|c)\\2){1,2}d` and `a(?P<outer>(?P<inner>b|c)(?P=inner)){1,2}d`, so the bytes parity slice can stay on the existing suite instead of inventing another test path once the pack lands;
  - `benchmarks/workloads/quantified_alternation_boundary.py` already publishes the six adjacent `str` benchmark rows for this exact pair as `module-search-numbered-quantified-alternation-branch-backref-cold-str`, `module-compile-numbered-quantified-alternation-branch-backref-cold-str`, `pattern-fullmatch-numbered-quantified-alternation-branch-backref-second-repetition-purged-str`, `module-compile-named-quantified-alternation-branch-backref-warm-str`, `module-search-named-quantified-alternation-branch-backref-lower-bound-c-branch-warm-str`, and `pattern-fullmatch-named-quantified-alternation-branch-backref-second-repetition-purged-str`, so a later Python-path benchmark catch-up can mirror those rows without another synthesis pass; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this planning run still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`, so the Rust-backed bytes parity work is not already satisfied in the current checkout.
- A later benchmark follow-on should catch the same bytes pair up on the existing quantified-alternation benchmark surface before another quantified-alternation branch-local-backreference bytes family broadens the frontier.
