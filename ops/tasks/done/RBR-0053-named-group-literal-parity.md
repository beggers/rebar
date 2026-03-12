# RBR-0053: Add bounded named-group literal metadata parity

Status: done
Owner: implementation
Created: 2026-03-12

## Goal
- Convert the first named-group literal metadata cases from the published correctness pack into real CPython-shaped behavior without claiming broad named-group or backreference support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_named_group_literal_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact named-group literal cases published by `RBR-0052` stop reporting `unimplemented` for bounded metadata observations and instead match CPython through the public `rebar` API for `groupindex`, `group("name")`, `groupdict()`, and `span("name")`.
- Module and compiled-`Pattern` flows both consume Rust-backed named-group metadata rather than ad hoc Python-only regex semantics; Python changes stay limited to wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one simple named-group literal path is enough, but named backreferences, conditional groups, nested named-group interactions, and named replacement-template behavior remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded named-group literal cases from `unimplemented` to `pass` without regressing the already-landed grouped numbered-capture and replacement-template workflow behavior.

## Constraints
- Keep this task scoped to the named-group cases published by `RBR-0052`; do not broaden into general named-group parsing, named backreferences, nested groups, or stdlib delegation.
- Implement any new execution or metadata behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Match`/`Pattern` object contracts outside this exact named-group literal slice.

## Notes
- Build on `RBR-0051`, `RBR-0052`, and the existing Rust-backed compile/match boundary.
- This task exists so the next grouped/named-group scorecard expansion can turn into concrete behavior work immediately instead of becoming another reporting-only dead end.

## Completion
- Landed bounded Rust-backed named-group metadata for the published `(?P<word>abc)` literal path, including compile-time `groupindex` plus `Match.group("word")`, `groupdict()`, `span("word")`, and `lastgroup` parity through module and compiled-pattern flows.
- Added focused Python and Rust coverage for the named-group literal slice and regenerated the combined correctness scorecard; `reports/correctness/latest.json` now reports 89 passes, 0 failures, and 0 unimplemented cases across the default ten-manifest fixture set.
