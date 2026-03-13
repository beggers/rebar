# RBR-0199: Add bounded nested two-arm conditional replacement parity

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Convert the first bounded nested two-arm conditional replacement cases from the published correctness pack into real Rust-backed behavior without claiming quantified replacement-conditioned helpers, branch-local-backreference arms, or deeper nested replacement semantics.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_conditional_group_exists_nested_replacement_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact nested two-arm conditional replacement cases published by `RBR-0198` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded `sub()` and `subn()` flows.
- Module and compiled-`Pattern` flows both consume Rust-backed conditional replacement behavior rather than ad hoc Python-only regex semantics; Python changes stay limited to wrapper construction, cache/object plumbing, replacement marshalling, and native result marshalling.
- The supported slice remains intentionally narrow: one outer two-arm conditional whose yes arm contains one nested two-arm conditional site in `a(b)?c(?(1)(?(1)d|e)|f)` / `a(?P<word>b)?c(?(word)(?(word)d|e)|f)` feeding constant replacement text is enough, including the present workflow where the nested yes arm still requires `d` and the absent workflow where the outer else arm contributes `f`, but replacement templates that read captures, callable replacement semantics, alternation-heavy nested arms, quantified repeats, deeper nesting, branch-local backreferences, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded nested two-arm conditional replacement cases from `unimplemented` to `pass` without regressing the already-landed two-arm conditional replacement slice, the bounded alternation-heavy two-arm conditional replacement slice, or the already-landed nested two-arm search/fullmatch behavior.

## Constraints
- Keep this task scoped to the nested two-arm conditional replacement cases published by `RBR-0198`; do not broaden into replacement-template capture expansion, callable replacement semantics, alternation-heavy nested arms, quantified repeats, deeper nesting, branch-local backreferences, or stdlib delegation.
- Implement any new replacement behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` and replacement object contracts outside this exact conditional-replacement slice.

## Notes
- Build on `RBR-0198`.
- This task exists so the queue converts the smallest remaining nested replacement-conditioned workflow into real Rust-backed behavior instead of leaving it as publication-only coverage.
- Completed 2026-03-13: added a narrow Rust-backed nested conditional replacement span finder for the one-level nested yes-arm slice, wired `rebar._rebar` replacement dispatch through it, added Python/Rust parity coverage, and republished `reports/correctness/latest.json` with the eight nested replacement cases flipped from `unimplemented` to `pass`.
