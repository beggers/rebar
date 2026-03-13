# RBR-0149: Add bounded quantified-conditional parity

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Convert the first quantified-conditional cases from the published correctness pack into real Rust-backed behavior without claiming broader quantified or backtracking-heavy conditional execution.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_conditional_group_exists_quantified_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact quantified-conditional cases published by `RBR-0148` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded workflows under test.
- Module and compiled-`Pattern` flows both consume Rust-backed quantified-conditional behavior rather than ad hoc Python-only regex semantics; Python changes stay limited to wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one exact-repeat `{2}` quantifier over the accepted two-arm conditional `a(b)?c(?(1)d|e){2}` / `a(?P<word>b)?c(?(word)d|e){2}` is enough, but omitted-no-arm or empty-arm quantified conditionals, replacement helpers, alternation-heavy repeated arms, nested conditionals inside the repeated site, ranged or open-ended repeats, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded quantified-conditional cases from `unimplemented` to `pass` without regressing the already-landed two-arm conditional baseline, exact-repeat quantified-group baseline, or other conditional workflow slices.

## Constraints
- Keep this task scoped to the quantified-conditional cases published by `RBR-0148`; do not broaden into omitted-no-arm or empty-arm quantified conditionals, nested quantified conditionals, replacement semantics, ranged/open-ended repeats, or stdlib delegation.
- Any new regex behavior must live behind `rebar._rebar`; `python/rebar/__init__.py` stays limited to export, wrapper, cache, and FFI responsibilities.
- Preserve the current `Pattern`/`Match` contracts outside this exact quantified-conditional slice.

## Notes
- Build on `RBR-0148`, `RBR-0105`, and `RBR-0096`.
- This task exists so the queue converts the first quantified-conditional workflow into real Rust-backed behavior instead of leaving it as publication-only coverage.
