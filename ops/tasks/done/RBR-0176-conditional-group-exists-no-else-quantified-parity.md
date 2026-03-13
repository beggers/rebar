# RBR-0176: Add bounded quantified omitted-no-arm conditional parity

Status: done
Owner: implementation
Created: 2026-03-13
Completed: 2026-03-13

## Goal
- Convert the first quantified omitted-no-arm conditional cases from the published correctness pack into real Rust-backed behavior without claiming broader quantified or backtracking-heavy conditional execution.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_conditional_group_exists_no_else_quantified_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact quantified omitted-no-arm cases published by `RBR-0175` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded workflows under test.
- Module and compiled-`Pattern` flows both consume Rust-backed quantified conditional behavior rather than ad hoc Python-only regex semantics; Python changes stay limited to wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one exact-repeat `{2}` quantifier over the accepted omitted-no-arm conditional `a(b)?c(?(1)d){2}` / `a(?P<word>b)?c(?(word)d){2}` is enough, including capture-present haystacks that require `dd` and capture-absent haystacks that succeed because the omitted no arm contributes nothing at both repetitions, but explicit-empty-else, two-arm, or empty-arm quantified conditionals, replacement helpers, alternation-heavy repeated arms, nested conditionals inside the repeated site, ranged/open-ended repeats, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded quantified omitted-no-arm cases from `unimplemented` to `pass` without regressing the already-landed two-arm quantified conditional baseline, omitted-no-arm baseline, or other conditional workflow slices.

## Constraints
- Keep this task scoped to the quantified omitted-no-arm cases published by `RBR-0175`; do not broaden into explicit-empty-else, two-arm, or empty-arm quantified conditionals, nested quantified conditionals, replacement semantics, ranged/open-ended repeats, or stdlib delegation.
- Any new regex behavior must live behind `rebar._rebar`; `python/rebar/__init__.py` stays limited to export, wrapper, cache, and FFI responsibilities.
- Preserve the current `Pattern`/`Match` contracts outside this exact quantified omitted-no-arm slice.

## Notes
- Build on `RBR-0175`.
- This task exists so the queue converts the first quantified omitted-no-arm workflow into real Rust-backed behavior instead of leaving it as publication-only coverage.
- Completed with a narrow Rust-core parser/matcher update for `a(b)?c(?(1)d){2}` and `a(?P<word>b)?c(?(word)d){2}`, a dedicated Python parity test, refreshed quantified no-else correctness assertions, and a republished combined `reports/correctness/latest.json` showing `380/380` passing with `0` published gaps.
