# RBR-0143: Add bounded alternation-heavy omitted-no-arm conditional parity

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Convert the first omitted-no-arm alternation-heavy conditional cases from the published correctness pack into real Rust-backed behavior without claiming broader conditional composition or general backtracking support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_conditional_group_exists_no_else_alternation_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact omitted-no-arm alternation-heavy conditional cases published by `RBR-0142` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` `search()`/`match()`/`fullmatch()` flows.
- Any new conditional parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one optional numbered or named capture with a single literal alternation site inside the yes-arm of an omitted-no-arm conditional is enough, including capture-present haystacks that select both `(de|df)` branches and capture-absent haystacks that fail because no else arm exists, but replacement workflows, empty-arm variants, quantified conditionals, branch-local backreferences inside the conditional arms, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded omitted-no-arm alternation-heavy cases from `unimplemented` to `pass` without regressing the already-landed omitted-no-arm non-alternating conditional behavior, explicit-empty-else alternation-heavy behavior, or the conditional-replacement slices queued ahead of this task.

## Constraints
- Keep this task scoped to the omitted-no-arm alternation-heavy cases published by `RBR-0142`; do not broaden into replacement workflows, empty-arm variants, quantified conditionals, wider alternation-heavy conditionals, or stdlib delegation.
- Implement any new execution behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact omitted-no-arm alternation-heavy conditional slice.

## Notes
- Build on `RBR-0108`, `RBR-0128`, and `RBR-0142`.
- This task exists so the queue converts the accepted omitted-no-arm alternation-heavy spelling into real Rust-backed behavior instead of leaving it as publication-only syntax coverage.

## Completion Notes
- Completed 2026-03-13.
- Relaxed the bounded conditional parser so the existing Rust matcher now accepts omitted-no-arm yes-arm alternation for `a(b)?c(?(1)(de|df))` and `a(?P<word>b)?c(?(word)(de|df))` without broadening replacement helpers or other conditional shapes.
- Added dedicated Python parity coverage for numbered and named module/compiled-`Pattern` compile, present-branch search, second-arm search, and absent-arm fullmatch behavior.
- Regenerated `reports/correctness/latest.json`; the combined published scorecard now reports 280 passes out of 280 cases with 0 honest `unimplemented` gaps.
