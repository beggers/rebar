# RBR-0173: Add bounded alternation-bearing fully-empty conditional parity

Status: done
Owner: implementation
Created: 2026-03-13
Completed: 2026-03-13

## Goal
- Convert the first alternation-bearing fully-empty conditional cases from the published correctness pack into real Rust-backed behavior without claiming broader alternation-heavy empty-arm execution or more general backtracking support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_conditional_group_exists_fully_empty_alternation_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact fully-empty alternation cases published by `RBR-0172` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` `search()`/`match()`/`fullmatch()` flows.
- Any new conditional parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one optional numbered or named capture with an explicit zero-width alternation site inside the else arm of a fully-empty conditional is enough, including capture-present and capture-absent success cases plus suffix-failure cases that distinguish it from the empty-yes-arm alternation spelling, but replacement workflows, quantified or nested alternation-bearing conditionals, wider alternation-heavy arms, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded fully-empty alternation cases from `unimplemented` to `pass` without regressing the already-landed fully-empty baseline, nested fully-empty behavior, quantified fully-empty work queued ahead of this task, or the corrected benchmark-anchor contracts that precede it.

## Constraints
- Keep this task scoped to the fully-empty alternation cases published by `RBR-0172`; do not broaden into empty-yes-arm alternation, replacement workflows, quantified or nested alternation-bearing conditionals, or stdlib delegation.
- Implement any new execution behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact alternation-bearing fully-empty slice.

## Notes
- Build on `RBR-0172`.
- This task exists so the queue converts the accepted alternation-bearing fully-empty spelling into real Rust-backed behavior instead of leaving it as publication-only syntax coverage.
- Landed bounded Rust-backed compile/match parity for `a(b)?c(?(1)|(?:|))` and `a(?P<word>b)?c(?(word)|(?:|))`, added direct Python parity coverage, aligned the correctness harness expectation, and republished `reports/correctness/latest.json` at 372 passed / 0 unimplemented cases.
