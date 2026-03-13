# RBR-0170: Add bounded alternation-heavy empty-yes-arm conditional parity

Status: done
Owner: implementation
Created: 2026-03-13
Completed: 2026-03-13

## Goal
- Convert the first alternation-heavy empty-yes-arm conditional cases from the published correctness pack into real Rust-backed behavior without claiming quantified, replacement-conditioned, or broader backtracking-heavy empty-arm execution.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_conditional_group_exists_empty_yes_else_alternation_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact empty-yes-arm alternation cases published by `RBR-0169` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` `search()`/`match()`/`fullmatch()` flows.
- Any new conditional parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one optional numbered or named capture with a single literal alternation site inside the else arm of an empty-yes-arm conditional is enough, including capture-present haystacks that succeed through the empty yes arm and capture-absent haystacks that take both `(e|f)` branches, but omitted-no-arm or explicit-empty-else variants, replacement workflows, quantified conditionals, nested conditionals, wider alternation-heavy arms, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded empty-yes-arm alternation cases from `unimplemented` to `pass` without regressing the already-landed empty-yes-arm baseline, nested empty-yes-arm behavior, quantified empty-yes-arm behavior, or the broader benchmark-anchor cleanup immediately ahead of this task.

## Constraints
- Keep this task scoped to the empty-yes-arm alternation cases published by `RBR-0169`; do not broaden into omitted-no-arm or explicit-empty-else variants, replacement workflows, quantified or nested alternation-heavy conditionals, or stdlib delegation.
- Implement any new execution behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact alternation-heavy empty-yes-arm slice.

## Notes
- Build on `RBR-0169`.
- This task exists so the queue turns the first broader empty-yes-arm alternation spelling into real Rust-backed behavior instead of leaving it as publication-only syntax coverage.
- Landed bounded Rust-backed compile/match parity for `a(b)?c(?(1)|(e|f))` and `a(?P<word>b)?c(?(word)|(e|f))`, added direct Python parity coverage, and republished `reports/correctness/latest.json` at 364 passed / 0 unimplemented cases.
