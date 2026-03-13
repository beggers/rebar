# RBR-0179: Add bounded quantified explicit-empty-else conditional parity

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Convert the first quantified explicit-empty-else conditional cases from the published correctness pack into real Rust-backed behavior without claiming broader quantified or backtracking-heavy conditional execution.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_conditional_group_exists_empty_else_quantified_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact quantified explicit-empty-else cases published by `RBR-0178` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded workflows under test.
- Module and compiled-`Pattern` flows both consume Rust-backed quantified conditional behavior rather than ad hoc Python-only regex semantics; Python changes stay limited to wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one exact-repeat `{2}` quantifier over the accepted explicit-empty-else conditional `a(b)?c(?(1)d|){2}` / `a(?P<word>b)?c(?(word)d|){2}` is enough, including capture-present haystacks that require `dd`, capture-absent haystacks that succeed because the explicit empty else contributes zero width at both repetitions, and compile-path parity that preserves the accepted `|)` spelling as a distinct slice, but omitted-no-arm, two-arm, or empty-arm quantified conditionals, replacement helpers, alternation-heavy repeated arms, nested conditionals inside the repeated site, ranged/open-ended repeats, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded quantified explicit-empty-else cases from `unimplemented` to `pass` without regressing the already-landed explicit-empty-else baseline, nested explicit-empty-else behavior, two-arm quantified conditional behavior, or other conditional workflow slices.

## Constraints
- Keep this task scoped to the quantified explicit-empty-else cases published by `RBR-0178`; do not broaden into omitted-no-arm, two-arm, or empty-arm quantified conditionals, nested quantified conditionals, replacement semantics, ranged/open-ended repeats, or stdlib delegation.
- Any new regex behavior must live behind `rebar._rebar`; `python/rebar/__init__.py` stays limited to export, wrapper, cache, and FFI responsibilities.
- Preserve the current `Pattern`/`Match` contracts outside this exact quantified explicit-empty-else slice.

## Notes
- Build on `RBR-0178`.
- This task exists so the queue converts the first quantified explicit-empty-else workflow into real Rust-backed behavior instead of leaving it as publication-only coverage.

## Completion
- Enabled the bounded quantified explicit-empty-else parser gate for `a(b)?c(?(1)d|){2}` and `a(?P<word>b)?c(?(word)d|){2}` so the existing Rust matcher now services compile/search/fullmatch parity for the published slice.
- Added Rust unit coverage, Python parity tests, and refreshed `reports/correctness/latest.json`; the combined scorecard now reports `388/388` passing with `0` unimplemented cases.
