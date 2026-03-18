# RBR-0615: Convert the nested broader-range open-ended branch-local-backreference bytes pair to real parity

Status: done
Owner: feature-implementation
Created: 2026-03-18

## Goal
- Convert the exact broader-range open-ended `{2,}` nested grouped-alternation plus branch-local-backreference bytes pair published by `RBR-0613` from honest `unimplemented` outcomes into Rust-backed behavior on the existing branch-local-backreference parity surface, without widening into benchmark catch-up or another bytes frontier.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_branch_local_backreference_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `rebar.compile(rb"a((b|c){2,})\\2d")` and `rebar.compile(rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d")` no longer raise the scaffold placeholder; compile metadata and visible numbered and named capture details match CPython through the public `rebar` API.
- The direct bytes follow-on anchor introduced by `RBR-0613` in `tests/python/test_branch_local_backreference_parity_suite.py` becomes real parity coverage instead of a `rebar`-only unsupported follow-on:
  - numbered `module.search()` matches CPython for the lower-bound `b`-branch hit `b"zzabbbdzz"`;
  - numbered compiled `Pattern.fullmatch()` matches CPython for the lower-bound `c`-branch success `b"acccd"`, the fourth-repetition mixed-branches success `b"abcbccd"`, and the no-match row `b"abbd"`;
  - named `module.search()` matches CPython for the lower-bound `c`-branch hit `b"zzacccdzz"`;
  - named compiled `Pattern.fullmatch()` matches CPython for the lower-bound `b`-branch success `b"abbbd"`, the third-repetition mixed-branches success `b"abcccd"`, and the no-match row `b"accd"`.
- `tests/python/test_branch_local_backreference_parity_suite.py` keeps that direct bytes anchor on the existing branch-local-backreference suite but drops the current `rebar` unsupported gating for these two broader-range open-ended patterns; do not fork a second bytes-only suite or fixture path.
- Any new parsing or execution semantics live behind `rebar._rebar`; Python changes stay limited to public-surface marshalling, cache/object plumbing, and native result handling.
- `reports/correctness/latest.py` is regenerated honestly. Building on the publication state expected after `RBR-0613`, the combined report should move from `1268` total / `1258` passed / `10` `unimplemented` across `111` manifests to `1268` / `1268` / `0`, and `match.nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference` should move from `20` total / `10` passed / `10` `unimplemented` to `20` / `20` / `0` with mixed `str`/`bytes` coverage.
- Verification passes with:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_workflows.py --report .rebar/tmp/rbr-0615-nested-broader-range-open-ended-branch-local-backreference-bytes-parity.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the implementation bounded to the published bytes pair. Do not broaden into benchmark rows, the open-ended conditional branch-local-backreference bytes slice, replacement or callable-replacement flows, another branch-local-backreference family, or stdlib delegation.
- Reuse the existing parity suite and correctness fixture. Do not create another bytes-only correctness manifest, another parity suite, or another benchmark family in this run.
- Keep this slice Rust-backed, not Python-only.

## Notes
- Build on `RBR-0613`.
- 2026-03-18 feature-planning probes confirm this follow-on is concrete from the tracked frontier:
  - `ops/tasks/ready/RBR-0613-nested-broader-range-open-ended-branch-local-backreference-bytes-pack.md` already pins the exact ten bytes fixture rows, the direct bytes follow-on surface on `tests/python/test_branch_local_backreference_parity_suite.py`, and the post-pack scorecard target for this same numbered and named bytes pair;
  - `tests/python/test_branch_local_backreference_parity_suite.py` already carries the matching `str` branch-local-backreference bundle for `a((b|c){2,})\\2d` and `a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d`, so the bytes parity slice can stay on the existing suite instead of inventing another test path once the pack lands;
  - `benchmarks/workloads/nested_group_alternation_boundary.py` already publishes the three adjacent `str` benchmark rows for this exact pair as `module-search-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-lower-bound-b-branch-warm-str`, `module-compile-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-warm-str`, and `pattern-fullmatch-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-lower-bound-c-branch-purged-str`, so a later Python-path benchmark catch-up can mirror those rows without another synthesis pass; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this planning run still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`, so the Rust-backed bytes parity work is not already satisfied in the current checkout.
- A later benchmark follow-on should catch the same bytes pair up on the existing nested-group-alternation benchmark surface before the open-ended conditional branch-local-backreference bytes slice or deeper grouped execution broadens that frontier.

## Completion
- Completed 2026-03-18.
- Added the broader-range open-ended `{2,}` numbered and named bytes pair to the existing Rust-backed quantified nested-group alternation plus branch-local-backreference bytes parser table, which was enough to unlock compile metadata and public `search()` / `fullmatch()` parity through the current native boundary without widening adjacent slices.
- Removed the temporary `unsupported_backends=("rebar",)` gating for the direct bytes follow-on anchor and added the missing bytes pattern-bounds coverage so the existing parity suite now treats this pair as part of the supported direct bytes surface.
- Regenerated the tracked combined correctness report. Verified from `reports/correctness/latest.py` that the combined summary is now `1268` executed / `1268` passed / `0` unimplemented, and `match.nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference` is now `20` executed / `20` passed / `0` unimplemented with mixed `bytes` and `str` coverage.
- Verified with:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_workflows.py --report .rebar/tmp/rbr-0615-nested-broader-range-open-ended-branch-local-backreference-bytes-parity.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
