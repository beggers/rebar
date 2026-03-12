# RBR-0060: Add bounded numbered-backreference parity

Status: done
Owner: implementation
Created: 2026-03-12

## Goal
- Convert the first numbered-backreference literal cases from the published correctness pack into real CPython-shaped behavior without claiming broad backreference or grouped-regex support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_numbered_backreference_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact numbered-backreference literal cases published by `RBR-0059` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` match flows.
- Any new capture and backreference semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one simple numbered-backreference literal path is enough, but nested groups, alternation-driven backreference semantics, conditional groups, and broader backtracking behavior remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded numbered-backreference cases from `unimplemented` to `pass` without regressing the already-landed grouped-capture, named-group, and named-backreference workflow behavior.

## Constraints
- Keep this task scoped to the numbered-backreference cases published by `RBR-0059`; do not broaden into general backreference parsing, nested groups, or stdlib delegation.
- Implement any new execution behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact numbered-backreference slice.

## Notes
- Build on `RBR-0057`, `RBR-0058`, and `RBR-0059`.
- This task exists so the next grouped-reference scorecard expansion can turn into concrete behavior work immediately instead of becoming another reporting-only dead end.

## Completion
- Landed a bounded Rust-backed `(literal)\\1` numbered-backreference slice for `str` compile metadata plus module and compiled-`Pattern` search flows.
- Added direct native-path parity coverage in `tests/python/test_numbered_backreference_parity.py`, updated the numbered-backreference correctness test to expect passes, and republished `reports/correctness/latest.json` at 99 passing cases with 0 unimplemented.
