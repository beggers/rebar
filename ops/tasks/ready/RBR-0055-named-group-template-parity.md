# RBR-0055: Add bounded named-group replacement-template parity

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Convert the first named-group replacement-template cases from the published correctness pack into real CPython-shaped behavior without claiming broad named-group or replacement-template support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_named_group_replacement_template_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact named-group replacement-template cases published by `RBR-0054` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded `sub()`/`subn()` flows using `\\g<name>` templates.
- Module and compiled-`Pattern` flows both consume Rust-backed named-group replacement behavior rather than ad hoc Python-only regex semantics; Python changes stay limited to wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one simple named-group literal replacement path is enough, but named backreferences in patterns, nested named-group interactions, callable replacement parity for named groups, and broader template parsing remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded named-group replacement-template cases from `unimplemented` to `pass` without regressing the already-landed grouped replacement-template and named-group metadata behavior.

## Constraints
- Keep this task scoped to the named-group replacement-template cases published by `RBR-0054`; do not broaden into general named-group parsing, named backreferences, nested groups, or stdlib delegation.
- Implement any new execution or metadata behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match`/replacement object contracts outside this exact named-group replacement slice.

## Notes
- Build on `RBR-0053`, `RBR-0054`, and the existing Rust-backed collection/replacement boundary.
- This task exists so the named-group queue turns directly into concrete replacement behavior work instead of stopping at metadata-only support.
