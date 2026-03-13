# RBR-0157: Add bounded nested empty-yes-arm conditional parity

Status: done
Owner: implementation
Created: 2026-03-13
Completed: 2026-03-13

## Goal
- Convert the first nested empty-yes-arm conditional cases from the published correctness pack into real Rust-backed behavior without claiming broader nested empty-arm or backtracking-heavy execution.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_conditional_group_exists_empty_yes_else_nested_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact nested empty-yes-arm conditional cases published by `RBR-0156` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` `search()`/`match()`/`fullmatch()` flows.
- Any new conditional parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one optional numbered or named capture with one nested conditional site inside the outer else-arm of an empty-yes-arm conditional is enough, including capture-present haystacks that match at zero width through the outer yes-arm, capture-absent haystacks that match because the nested else-arm selects `f`, and capture-absent haystacks that fail because the nested `e` arm is not taken, but replacement workflows, nested fully-empty variants, explicit-empty-else or omitted-no-arm nested follow-ons, quantified conditionals, deeper nesting, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded nested empty-yes-arm conditional cases from `unimplemented` to `pass` without regressing the already-landed empty-yes-arm baseline, the nested explicit-empty-else slice, or the broader conditional frontier.

## Constraints
- Keep this task scoped to the nested empty-yes-arm cases published by `RBR-0156`; do not broaden into replacement workflows, nested fully-empty variants, other nested empty-arm spellings, quantified conditionals, deeper nesting, or stdlib delegation.
- Implement any new execution behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact nested empty-yes-arm slice.

## Notes
- Build on `RBR-0156`.
- This task exists so the queue converts one exact accepted nested empty-yes-arm spelling into real Rust-backed behavior instead of leaving it as publication-only syntax coverage.
- Implemented the bounded outer-empty-yes / nested-else-arm Rust execution path for `a(b)?c(?(1)|(?(1)e|f))` and `a(?P<word>b)?c(?(word)|(?(word)e|f))` only.
- Added Python parity coverage for numbered and named compile/search/fullmatch flows, kept replacement helpers unsupported for this nested shape, and republished `reports/correctness/latest.json` to `330` passes with `0` honest gaps.
