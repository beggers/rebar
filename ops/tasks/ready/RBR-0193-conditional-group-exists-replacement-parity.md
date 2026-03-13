# RBR-0193: Add bounded two-arm conditional replacement parity

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Convert the first bounded two-arm conditional replacement cases from the published correctness pack into real Rust-backed behavior without claiming alternation-heavy replacement branches, deeper nested conditionals, or general replacement-template support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_conditional_group_exists_replacement_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact two-arm conditional replacement cases published by `RBR-0192` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded `sub()` and `subn()` flows.
- Module and compiled-`Pattern` flows both consume Rust-backed conditional replacement behavior rather than ad hoc Python-only regex semantics; Python changes stay limited to wrapper construction, cache/object plumbing, replacement marshalling, and native result marshalling.
- The supported slice remains intentionally narrow: one two-arm conditional site inside literal prefix/suffix text feeding constant replacement text is enough, but replacement templates that read capture groups, callable replacement semantics, alternation-heavy conditional arms, nested conditionals, quantified conditionals, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded two-arm conditional replacement cases from `unimplemented` to `pass` without regressing the already-landed two-arm conditional search/fullmatch behavior or the already-landed omitted-no-arm, explicit-empty-else, empty-yes-arm, and fully-empty conditional replacement slices.

## Constraints
- Keep this task scoped to the two-arm conditional replacement cases published by `RBR-0192`; do not broaden into alternation-heavy replacement branches, nested conditionals, quantified conditionals, replacement-template capture expansion, callable replacement semantics, or stdlib delegation.
- Implement any new replacement behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` and replacement object contracts outside this exact conditional-replacement slice.

## Notes
- Build on `RBR-0192`.
- This task exists so the queue converts the smallest remaining two-arm conditional replacement workflow into real Rust-backed behavior instead of leaving it as publication-only coverage.
