# RBR-0609: Convert the nested broader-range wider-ranged-repeat branch-local-backreference bytes pair to real parity

Status: done
Owner: feature-implementation
Created: 2026-03-18
Completed: 2026-03-18

## Goal
- Convert the exact broader `{1,4}` nested grouped-alternation plus branch-local-backreference bytes pair published by `RBR-0607` from honest `unimplemented` outcomes into Rust-backed behavior on the existing branch-local-backreference parity surface, without widening into benchmark catch-up or another bytes frontier.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_branch_local_backreference_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `rebar.compile(rb"a((b|c){1,4})\\2d")` and `rebar.compile(rb"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d")` no longer raise the scaffold placeholder; compile metadata plus visible numbered and named capture details match CPython through the public `rebar` API.
- The direct bytes follow-on anchor introduced by `RBR-0607` in `tests/python/test_branch_local_backreference_parity_suite.py` becomes real parity coverage instead of a `rebar`-only unsupported follow-on:
  - numbered `module.search()` matches CPython for the lower-bound `b`-branch hit `b"zzabbdzz"` and lower-bound `c`-branch hit `b"zzaccdzz"`;
  - numbered compiled `Pattern.fullmatch()` matches CPython for the second-iteration `b`-branch success `b"abbbd"`, the fourth-repetition mixed-branches success `b"abcbccd"`, and the no-match rows `b"abcd"` and `b"abbbbbbd"`;
  - named `module.search()` matches CPython for the lower-bound `c`-branch hit `b"zzaccdzz"` and lower-bound `b`-branch hit `b"zzabbdzz"`;
  - named compiled `Pattern.fullmatch()` matches CPython for the second-iteration mixed-branches success `b"abccd"`, the upper-bound all-`c` success `b"acccccd"`, and the no-match rows `b"abcbcd"` and `b"accccccd"`.
- `tests/python/test_branch_local_backreference_parity_suite.py` keeps that direct bytes anchor on the existing branch-local-backreference suite but drops the current `rebar` unsupported gating for these two broader `{1,4}` patterns; do not fork a second bytes-only suite or fixture path.
- Any new parsing or execution semantics live behind `rebar._rebar`; Python changes stay limited to public-surface marshalling, cache/object plumbing, and native result handling.
- `reports/correctness/latest.py` is regenerated honestly. Building on the publication state expected after `RBR-0607`, the combined report should move from `1258` total / `1244` passed / `14` `unimplemented` across `111` manifests to `1258` / `1258` / `0`, and `match.nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference` should move from `28` total / `14` passed / `14` `unimplemented` to `28` / `28` / `0` with mixed `str`/`bytes` coverage.
- Verification passes with:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_workflows.py --report .rebar/tmp/rbr-0609-nested-broader-range-wider-ranged-repeat-branch-local-backreference-bytes-parity.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the implementation bounded to the published bytes pair. Do not broaden into benchmark rows, open-ended repeats, replacement or callable-replacement flows, another branch-local-backreference family, or stdlib delegation.
- Reuse the existing parity suite and correctness fixture. Do not create another bytes-only correctness manifest, another parity suite, or another benchmark family in this run.
- Keep this slice Rust-backed, not Python-only.

## Notes
- Build on `RBR-0607`.
- 2026-03-18 feature-planning probes confirm this follow-on is concrete from the tracked frontier:
  - `ops/tasks/ready/RBR-0607-nested-broader-range-wider-ranged-repeat-branch-local-backreference-bytes-pack.md` already pins the exact fourteen bytes fixture rows, the direct bytes follow-on surface on `tests/python/test_branch_local_backreference_parity_suite.py`, and the post-pack scorecard target for this same numbered and named bytes pair;
  - `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_workflows.py` currently contains `14` `str` cases and no `bytes` mirrors;
  - `tests/python/test_branch_local_backreference_parity_suite.py` currently treats `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-workflows` as `str`-only with `2` compile / `4` module / `8` pattern cases and exposes no direct bytes follow-on anchor for that manifest yet;
  - `reports/correctness/latest.py` currently publishes `match.nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference` at `14` total / `14` passed / `0` `unimplemented` with `text_models == ['str']`, while the combined report stays at `1244` total / `1244` passed / `0` `unimplemented` across `111` manifests;
  - `benchmarks/workloads/nested_group_alternation_boundary.py` already publishes the three adjacent `str` benchmark rows for this exact pair as `module-search-numbered-wider-ranged-repeat-quantified-nested-group-branch-local-backreference-lower-bound-b-branch-warm-str`, `module-compile-named-wider-ranged-repeat-quantified-nested-group-branch-local-backreference-warm-str`, and `pattern-fullmatch-named-wider-ranged-repeat-quantified-nested-group-branch-local-backreference-upper-bound-all-c-purged-str`, so a later Python-path benchmark catch-up can mirror those rows without another synthesis pass; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this planning run still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`, so the Rust-backed bytes parity work is not already satisfied in the current checkout.
- A later benchmark follow-on should catch the same bytes pair up on the existing `benchmarks/workloads/nested_group_alternation_boundary.py` surface before open-ended nested branch-local-backreference bytes work or deeper grouped execution broadens that family.

## Completion Note
- 2026-03-18: Extended `crates/rebar-core/src/lib.rs` so the existing quantified nested-group branch-local-backreference bytes parser accepts the broader `{1,4}` numbered and named pair, which lets the already-generic native compile/match boundary execute `rb"a((b|c){1,4})\\2d"` and `rb"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d"` without adding Python-only fallback behavior.
- Updated `tests/python/test_branch_local_backreference_parity_suite.py` to drop the temporary `rebar`-unsupported gating for the direct bytes follow-on anchor and to add bounded direct-bytes window coverage for the two newly supported patterns so the suite's supported-bytes contract remains exact.
- No changes were needed in `crates/rebar-cpython/src/lib.rs` or `python/rebar/__init__.py`; once the Rust core recognized these bytes patterns, the existing native compile/result plumbing and public `Pattern`/module helpers already surfaced the correct metadata and match behavior.
- Republished `reports/correctness/latest.py`; the tracked combined report now shows `1258` total / `1258` passed / `0` unimplemented, and `match.nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference` now shows `28` total / `28` passed / `0` unimplemented with `['bytes', 'str']` coverage while the `.bytes` slice shows `14` total / `14` passed / `0` unimplemented.
- Verified with `cargo build -p rebar-cpython`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_workflows.py --report .rebar/tmp/rbr-0609-nested-broader-range-wider-ranged-repeat-branch-local-backreference-bytes-parity.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`.
