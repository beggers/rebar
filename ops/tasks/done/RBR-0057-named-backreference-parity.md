# RBR-0057: Add bounded named-backreference parity

Status: done
Owner: implementation
Created: 2026-03-12
Completed: 2026-03-12

## Goal
- Convert the first named-backreference literal cases from the published correctness pack into real CPython-shaped behavior without claiming broad backreference or grouped-regex support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_named_backreference_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact named-backreference literal cases published by `RBR-0056` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` match flows.
- Any new capture and backreference semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one simple named-backreference literal path is enough, but nested groups, alternation-driven backreference semantics, numbered backreference expansion beyond the published grouped-capture slice, and broader backtracking behavior remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded named-backreference cases from `unimplemented` to `pass` without regressing the already-landed grouped replacement-template and named-group workflow behavior.

## Constraints
- Keep this task scoped to the named-backreference cases published by `RBR-0056`; do not broaden into general backreference parsing, nested groups, or stdlib delegation.
- Implement any new execution behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact named-backreference slice.

## Notes
- Build on `RBR-0055`, `RBR-0056`, and the existing Rust-backed compile/match boundary.
- This task exists so the next grouped-reference scorecard expansion can turn into concrete behavior work immediately instead of becoming another reporting-only dead end.
- Completed with a bounded Rust-core parser/matcher path for `(?P<word>ab)(?P=word)`, plus Python parity coverage and a republished combined correctness report showing `96/96` passing cases and `0` unimplemented cases.
- No additional Python fallback execution path was added; the new behavior stays behind the existing native compile/match boundary as required.
