# RBR-0122: Add bounded wider ranged-repeat quantified-group parity

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Convert the first wider ranged-repeat quantified-group cases from the published correctness pack into real CPython-shaped behavior without claiming quantified alternation, open-ended repeats, or broad backtracking support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The wider ranged-repeat quantified-group cases published by `RBR-0121` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` `search()`/`match()`/`fullmatch()` flows.
- Any new wider ranged-repeat parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one bounded `{1,3}` numbered or named capturing group inside literal prefix/suffix text is enough, including the observable final-capture values after the third repetition completes, but still-wider counted ranges, open-ended repeats, quantified alternation, replacement workflows, conditionals, nested quantified groups, capture-history beyond current `Match` APIs, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded wider ranged-repeat quantified-group cases from `unimplemented` to `pass` without regressing the already-landed `{1,2}` ranged-repeat slice or the conditional work queued ahead of this task.

## Constraints
- Keep this task scoped to the wider ranged-repeat quantified-group cases published by `RBR-0121`; do not broaden into open-ended repeats, quantified alternation, replacement workflows, conditionals, or stdlib delegation.
- Implement any new execution behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact wider counted-range slice.

## Notes
- Build on `RBR-0121`.
- This task exists so the queue turns the next bounded counted-range slice into real Rust-backed behavior instead of leaving it as publication-only coverage.
