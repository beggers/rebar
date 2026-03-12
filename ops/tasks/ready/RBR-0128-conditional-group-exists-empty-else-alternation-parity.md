# RBR-0128: Add bounded alternation-heavy explicit-empty-else conditional parity

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Convert the first alternation-heavy explicit-empty-else conditional cases from the published correctness pack into real CPython-shaped behavior without claiming replacement-conditioned workflows, quantified conditionals, or broad backtracking support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_conditional_group_exists_empty_else_alternation_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact explicit-empty-else alternation cases published by `RBR-0127` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` `search()`/`match()`/`fullmatch()` flows.
- Any new conditional parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one optional numbered or named capture with a single literal alternation site inside the yes-arm of an explicit-empty-else conditional is enough, including capture-present haystacks that select both `(de|df)` branches and capture-absent haystacks that succeed through the empty else branch, but replacement workflows, empty-yes-arm/no-else conditionals with alternation-heavy arms, quantified conditionals, branch-local backreferences inside the conditional arms, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded explicit-empty-else alternation cases from `unimplemented` to `pass` without regressing the already-landed non-alternating explicit-empty-else conditional behavior, fully-empty conditional behavior, or quantified-alternation work queued ahead of this task.

## Constraints
- Keep this task scoped to the explicit-empty-else alternation cases published by `RBR-0127`; do not broaden into replacement workflows, quantified conditionals, wider alternation-heavy conditionals, or stdlib delegation.
- Implement any new execution behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact alternation-heavy conditional slice.

## Notes
- Build on `RBR-0127`.
- This task exists so the queue turns the first bounded backtracking-heavy explicit-empty-else conditional slice into real Rust-backed behavior instead of leaving it as publication-only coverage.
