# RBR-0152: Add bounded nested explicit-empty-else conditional parity

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Convert the first nested explicit-empty-else conditional cases from the published correctness pack into real Rust-backed behavior without claiming broader nested conditional or backtracking-heavy execution.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_conditional_group_exists_empty_else_nested_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact nested explicit-empty-else conditional cases published by `RBR-0151` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` `search()`/`match()`/`fullmatch()` flows.
- Any new conditional parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one optional numbered or named capture with one nested explicit-empty-else conditional site inside the outer yes-arm is enough, including capture-present haystacks that require the nested `d` suffix and capture-absent haystacks that match because the outer explicit empty else contributes nothing, but replacement workflows, omitted-no-arm or empty-yes-arm nested variants, alternation inside the nested arms, quantified conditionals, deeper nesting, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded nested explicit-empty-else conditional cases from `unimplemented` to `pass` without regressing the already-landed explicit-empty-else baseline, omitted-no-arm nested conditional behavior, or the quantified conditional slice queued immediately ahead of this task.

## Constraints
- Keep this task scoped to the nested explicit-empty-else conditional cases published by `RBR-0151`; do not broaden into replacement workflows, omitted-no-arm or empty-yes-arm nested variants, quantified conditionals, deeper nesting, or stdlib delegation.
- Implement any new execution behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact nested explicit-empty-else conditional slice.

## Notes
- Build on `RBR-0111`, `RBR-0146`, and `RBR-0151`.
- This task exists so the queue converts one exact accepted nested explicit-empty-else spelling into real Rust-backed behavior instead of leaving it as publication-only syntax coverage.
