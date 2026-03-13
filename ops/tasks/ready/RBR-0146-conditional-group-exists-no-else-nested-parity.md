# RBR-0146: Add bounded nested omitted-no-arm conditional parity

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Convert the first omitted-no-arm nested-conditional cases from the published correctness pack into real Rust-backed behavior without claiming quantified conditional support or general backtracking coverage.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_conditional_group_exists_no_else_nested_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact omitted-no-arm nested-conditional cases published by `RBR-0145` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` `search()`/`match()`/`fullmatch()` flows.
- Any new conditional parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one optional numbered or named capture with one nested omitted-no-arm conditional site inside the outer yes-arm is enough, including capture-present haystacks that require the nested `d` suffix and capture-absent haystacks that match because the outer no-else arm contributes nothing, but replacement workflows, empty-arm variants, quantified conditionals, alternation inside the nested arms, deeper nesting, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded omitted-no-arm nested-conditional cases from `unimplemented` to `pass` without regressing the already-landed single-site omitted-no-arm conditional behavior, omitted-no-arm conditional replacement slices, or the alternation-heavy omitted-no-arm slice queued immediately ahead of this task.

## Constraints
- Keep this task scoped to the omitted-no-arm nested-conditional cases published by `RBR-0145`; do not broaden into replacement workflows, empty-arm variants, quantified conditionals, deeper nesting, or stdlib delegation.
- Implement any new execution behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact omitted-no-arm nested-conditional slice.

## Notes
- Build on `RBR-0108`, `RBR-0131`, and `RBR-0145`.
- This task exists so the queue converts one exact accepted nested-conditional spelling into real Rust-backed behavior instead of leaving it as publication-only syntax coverage.
