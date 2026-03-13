# RBR-0196: Add bounded alternation-heavy two-arm conditional replacement parity

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Convert the first bounded alternation-heavy two-arm conditional replacement cases from the published correctness pack into real Rust-backed behavior without claiming quantified replacement-conditioned helpers, nested replacement-conditioned flows, or general replacement-template support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_conditional_group_exists_alternation_replacement_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact alternation-heavy two-arm conditional replacement cases published by `RBR-0195` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded `sub()` and `subn()` flows.
- Module and compiled-`Pattern` flows both consume Rust-backed conditional replacement behavior rather than ad hoc Python-only regex semantics; Python changes stay limited to wrapper construction, cache/object plumbing, replacement marshalling, and native result marshalling.
- The supported slice remains intentionally narrow: one small literal alternation site in each arm of `a(b)?c(?(1)(de|df)|(eg|eh))` / `a(?P<word>b)?c(?(word)(de|df)|(eg|eh))` feeding constant replacement text is enough, including capture-present workflows that exercise both yes-arm branches and capture-absent workflows that exercise both else-arm branches, but replacement templates that read captures, callable replacement semantics, quantified repeats, nested conditionals, branch-local backreferences inside the alternations, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded alternation-heavy two-arm conditional replacement cases from `unimplemented` to `pass` without regressing the already-landed two-arm conditional replacement slice, the bounded alternation-heavy two-arm search/fullmatch slice, or the already-landed omitted-no-arm, explicit-empty-else, empty-yes-arm, and fully-empty conditional replacement slices.

## Constraints
- Keep this task scoped to the alternation-heavy two-arm conditional replacement cases published by `RBR-0195`; do not broaden into replacement-template capture expansion, callable replacement semantics, quantified repeats, nested conditionals, branch-local backreferences inside the alternations, or stdlib delegation.
- Implement any new replacement behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` and replacement object contracts outside this exact conditional-replacement slice.

## Notes
- Build on `RBR-0195`.
- This task exists so the queue converts the smallest remaining alternation-heavy replacement-conditioned workflow into real Rust-backed behavior instead of leaving it as publication-only coverage.
