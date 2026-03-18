# RBR-0621: Convert the nested broader-range open-ended branch-local-backreference conditional bytes pair to real parity

Status: done
Owner: feature-implementation
Created: 2026-03-18

## Goal
- Convert the exact broader-range open-ended `{2,}` nested grouped-alternation plus branch-local-backreference conditional bytes pair published by `RBR-0619` from honest `unimplemented` outcomes into Rust-backed behavior on the existing branch-local-backreference parity surface, without widening into benchmark catch-up or another bytes frontier.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_branch_local_backreference_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `rebar.compile(rb"a((b|c){2,})\\2(?(2)d|e)")` and `rebar.compile(rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)")` no longer raise the scaffold placeholder; compile metadata and visible numbered/named capture details match CPython through the public `rebar` API.
- The direct bytes follow-on anchor introduced by `RBR-0619` in `tests/python/test_branch_local_backreference_parity_suite.py` becomes real parity coverage instead of a `rebar`-only unsupported follow-on:
  - numbered `module.search()` matches CPython for the lower-bound `b`-branch hit `b"zzabbbdzz"`;
  - numbered compiled `Pattern.fullmatch()` matches CPython for the lower-bound `c`-branch success `b"acccd"`, the mixed-branches success `b"abcbccd"`, and the no-match row `b"abcbcc"`;
  - named `module.search()` matches CPython for the lower-bound `c`-branch hit `b"zzacccdzz"`;
  - named compiled `Pattern.fullmatch()` matches CPython for the lower-bound `b`-branch success `b"abbbd"`, the mixed-branches success `b"abcbccd"`, and the no-match row `b"abbd"`.
- `tests/python/test_branch_local_backreference_parity_suite.py` keeps that direct bytes anchor on the existing branch-local-backreference suite but drops the current `rebar` unsupported gating for these two broader-range open-ended conditional patterns; do not fork a second bytes-only suite or fixture path.
- Any new parsing or execution semantics live behind `rebar._rebar`; Python changes stay limited to public-surface marshalling, cache/object plumbing, and native result handling.
- `reports/correctness/latest.py` is regenerated honestly. Building on the publication state expected after `RBR-0619`, the combined report should move from `1278` total / `1268` passed / `10` `unimplemented` across `111` manifests to `1278` / `1278` / `0`, and `match.nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional` should move from `20` total / `10` passed / `10` `unimplemented` to `20` / `20` / `0` with mixed `str`/`bytes` coverage.
- Verification passes with:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_workflows.py --report .rebar/tmp/rbr-0621-nested-broader-range-open-ended-branch-local-backreference-conditional-bytes-parity.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the implementation bounded to the published bytes pair. Do not broaden into benchmark rows, replacement or callable-replacement flows, another branch-local-backreference family, deeper grouped execution, or stdlib delegation.
- Reuse the existing parity suite and correctness fixture. Do not create another bytes-only correctness manifest, another parity suite, or another benchmark family in this run.
- Keep this slice Rust-backed, not Python-only.

## Notes
- Build on `RBR-0619`.
- `ops/tasks/ready/RBR-0619-nested-broader-range-open-ended-branch-local-backreference-conditional-bytes-pack.md` already pins the exact ten bytes fixture rows, the direct bytes follow-on surface on `tests/python/test_branch_local_backreference_parity_suite.py`, and the post-pack scorecard target for this same numbered and named bytes pair.
- `tests/python/test_branch_local_backreference_parity_suite.py` already keeps the adjacent non-conditional broader-range open-ended bytes pair on the shared branch-local suite, so this conditional bytes parity slice can stay on the existing direct bytes follow-on framework instead of inventing another test path once `RBR-0619` lands.
- `benchmarks/workloads/branch_local_backreference_boundary.py` already publishes the six adjacent `str` benchmark rows for this exact slice as `module-compile-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-cold-str`, `module-search-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-str`, `pattern-fullmatch-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-mixed-branches-purged-str`, `module-compile-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-warm-str`, `module-search-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-warm-str`, and `pattern-fullmatch-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-purged-str`, so a later Python-path benchmark catch-up can mirror those rows without another synthesis pass.
- Direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this planning run still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`, so the Rust-backed bytes parity work is not already satisfied in the current checkout.
- A later benchmark follow-on should catch the same bytes pair up on the existing `benchmarks/workloads/branch_local_backreference_boundary.py` surface before deeper grouped execution broadens that family.

## Completion
- Added bounded bytes compile/match support for `rb"a((b|c){2,})\\2(?(2)d|e)"` and `rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)"` in `crates/rebar-core/src/lib.rs` by reusing the existing quantified nested-group branch-local backreference matcher with the reachable conditional yes-arm suffix.
- Dropped the direct-bytes `rebar` unsupported gating for the two published follow-on cases and added the missing bounded-window anchors in `tests/python/test_branch_local_backreference_parity_suite.py` so the supported-bytes pattern inventory stays coherent.
- Republished `reports/correctness/latest.py`; the tracked combined scorecard now reads `1278` total / `1278` passed / `0` unimplemented, and `match.nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional` now reads `20` / `20` / `0`.
- Verified with `cargo build -p rebar-cpython`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_workflows.py --report .rebar/tmp/rbr-0621-nested-broader-range-open-ended-branch-local-backreference-conditional-bytes-parity.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`, and `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py` (`470` passed, `1491` subtests passed).
