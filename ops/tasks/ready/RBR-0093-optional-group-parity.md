# RBR-0093: Add bounded optional-group parity

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Convert the first bounded optional-group cases from the published correctness pack into real CPython-shaped behavior without claiming counted-repeat, quantified-alternation, conditional, or broad backtracking support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_optional_group_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact optional-group cases published by `RBR-0092` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` `search()`/`match()`/`fullmatch()` flows.
- Any new optional-group parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one optional numbered or named capturing group inside literal prefix/suffix text is enough, including the observable group values when the capture is omitted, but `*`/`+`/`{m,n}` repeats, quantified alternation, replacement workflows, conditionals, nested quantified groups, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded optional-group cases from `unimplemented` to `pass` without regressing the already-landed grouped capture, named-group, nested-group, alternation, or backreference behavior.

## Constraints
- Keep this task scoped to the optional-group cases published by `RBR-0092`; do not broaden into counted repeats, quantified alternation, replacement workflows, conditionals, or stdlib delegation.
- Implement any new execution behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact optional-group slice.

## Notes
- Build on `RBR-0050`, `RBR-0078`, and `RBR-0092`.
- This task exists so the queue turns the first quantified execution cases into real Rust-backed behavior instead of leaving that frontier as publication-only coverage.
