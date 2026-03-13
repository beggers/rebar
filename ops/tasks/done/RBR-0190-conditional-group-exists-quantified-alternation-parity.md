# RBR-0190: Add bounded quantified alternation-heavy two-arm conditional parity

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Convert the bounded quantified alternation-heavy two-arm conditional cases from the published correctness pack into real Rust-backed behavior without reopening deeper nesting, replacement-conditioned helpers, or a broad quantified backtracking bucket all at once.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `tests/python/test_conditional_group_exists_quantified_alternation_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact quantified alternation-heavy two-arm conditional cases published by `RBR-0189` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` search/match/fullmatch flows.
- The bounded workflows for `a(b)?c(?(1)(de|df)|(eg|eh)){2}` and `a(?P<word>b)?c(?(word)(de|df)|(eg|eh)){2}` compile and execute through the Rust boundary without falling back to Python behavior.
- The supported slice remains intentionally narrow: one exact-repeat `{2}` quantifier over one small literal alternation site in each conditional arm is enough, including capture-present haystacks that select both repeated yes-arm branches and capture-absent haystacks that select both repeated else-arm branches, but replacement workflows, deeper nested conditionals, ranged/open-ended repeats, branch-local backreferences inside the alternations, and broader quantified backtracking-heavy composition remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded quantified alternation-heavy two-arm conditional cases from `unimplemented` to `pass` without regressing the already-landed two-arm baseline, the bounded quantified-conditional slice, the bounded alternation-heavy two-arm slice, or the single-arm alternation-heavy conditional workflows.

## Constraints
- Keep this task scoped to the quantified alternation-heavy two-arm conditional cases published by `RBR-0189`; do not broaden into replacement semantics, deeper nesting, ranged/open-ended repeats, or stdlib delegation.
- Any new regex behavior must live behind `rebar._rebar`; `python/rebar/__init__.py` stays limited to export, wrapper, cache, and FFI responsibilities.
- Preserve existing `Pattern`/`Match` contracts outside this exact quantified alternation-heavy two-arm slice.

## Notes
- Build on `RBR-0189`.
- This task exists so the queue converts the first quantified follow-on to the reopened two-arm alternation frontier into real Rust-backed behavior instead of leaving it as publication-only coverage.
- Completed 2026-03-13: extended `rebar-core`'s quantified conditional parser and matcher to cover the bounded two-arm alternation `{2}` slice behind `rebar._rebar`, added public parity coverage for numbered and named module/compiled-pattern workflows including mixed repeated branch selections, updated the quantified alternation correctness harness assertions, and republished `reports/correctness/latest.json` at 416 passing cases with 0 honest gaps.
