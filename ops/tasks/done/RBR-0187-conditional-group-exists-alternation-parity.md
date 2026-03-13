# RBR-0187: Add bounded alternation-heavy two-arm conditional parity

Status: done
Owner: implementation
Created: 2026-03-13
Completed: 2026-03-13

## Goal
- Convert the bounded alternation-heavy two-arm conditional cases from the published correctness pack into real Rust-backed behavior without reopening quantified conditionals, deeper nesting, or a broad backtracking bucket all at once.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `tests/python/test_conditional_group_exists_alternation_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact alternation-heavy two-arm conditional cases published by `RBR-0186` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` search/match/fullmatch flows.
- The bounded workflows for `a(b)?c(?(1)(de|df)|(eg|eh))` and `a(?P<word>b)?c(?(word)(de|df)|(eg|eh))` compile and execute through the Rust boundary without falling back to Python behavior.
- The supported slice remains intentionally narrow: one small literal alternation site in each arm is enough, including capture-present haystacks that select both yes-arm branches and capture-absent haystacks that select both else-arm branches, but replacement workflows, quantified repeats, nested conditionals inside either arm, branch-local backreferences inside the alternations, ranged/open-ended repetition, and broader backtracking-heavy conditional composition remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded alternation-heavy two-arm conditional cases from `unimplemented` to `pass` without regressing the already-landed two-arm baseline, the single-arm alternation-heavy conditional slices, or the bounded nested/quantified conditional workflows.

## Constraints
- Keep this task scoped to the alternation-heavy two-arm cases published by `RBR-0186`; do not broaden into replacement semantics, quantified alternation-heavy conditionals, deeper nesting, open-ended repeats, or stdlib delegation.
- Any new regex behavior must live behind `rebar._rebar`; `python/rebar/__init__.py` stays limited to export, wrapper, cache, and FFI responsibilities.
- Preserve existing `Pattern`/`Match` contracts outside this exact alternation-heavy two-arm slice.

## Notes
- Build on `RBR-0186`.
- This task exists so the queue converts the first broader backtracking-heavy conditional composition slice into real Rust-backed behavior instead of leaving it as publication-only coverage.

## Completion
- Extended the Rust conditional parser and matcher to accept the exact bounded two-arm alternation shape in both numbered and named forms, with CPython-aligned group metadata for the branch-local capture slots (`groups == 3`, yes-arm capture in group `2`, else-arm capture in group `3`).
- Added focused Rust and Python parity coverage for `a(b)?c(?(1)(de|df)|(eg|eh))` and `a(?P<word>b)?c(?(word)(de|df)|(eg|eh))`, including both yes-arm and else-arm branch selections through module and compiled-pattern flows.
- Republished `reports/correctness/latest.json`; the combined published scorecard now reports `406` total cases across `55` manifests with `406` passes and `0` `unimplemented` cases.
