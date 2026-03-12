# RBR-0102: Add bounded optional-group alternation parity

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Convert the first bounded optional-group alternation cases from the published correctness pack into real CPython-shaped behavior without claiming broader quantified alternation, conditional, or broad backtracking support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_optional_group_alternation_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact optional-group alternation cases published by `RBR-0101` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` `search()`/`match()`/`fullmatch()` flows.
- Any new optional-group alternation parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one optional capturing group containing one literal alternation site inside literal prefix/suffix text is enough, including the observable group values when the capture is omitted, but exact or ranged quantified alternation, replacement workflows, branch-local backreferences inside quantified alternation, conditionals, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded optional-group alternation cases from `unimplemented` to `pass` without regressing the already-landed grouped alternation, optional-group, nested-group alternation, or branch-local backreference behavior.

## Constraints
- Keep this task scoped to the optional-group alternation cases published by `RBR-0101`; do not broaden into exact or ranged quantified alternation, replacement workflows, conditionals, or stdlib delegation.
- Implement any new execution behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact optional quantified-alternation slice.

## Notes
- Build on `RBR-0069`, `RBR-0093`, and `RBR-0101`.
- This task exists so the queue turns the first combined optional-quantifier and grouped-alternation workflows into real Rust-backed behavior instead of leaving them as publication-only coverage.
