# RBR-0078: Add bounded nested-group parity

Status: done
Owner: implementation
Created: 2026-03-12

## Goal
- Convert the first nested-group cases from the published correctness pack into real CPython-shaped behavior without claiming broad nesting, alternation-in-nesting, quantified-group, or replacement support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_nested_group_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact nested-group cases published by `RBR-0077` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` match flows.
- Any new nested-group parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one outer capturing group containing one inner numbered or named capturing group inside literal prefix/suffix text is enough, but nested alternation, quantified groups, branch-local backreferences, replacement semantics, callable replacement semantics, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded nested-group cases from `unimplemented` to `pass` without regressing the already-landed grouped-capture, named-group, grouped-segment, literal-alternation, or grouped-alternation workflow behavior.

## Constraints
- Keep this task scoped to the nested-group cases published by `RBR-0077`; do not broaden into alternation inside nested groups, quantified groups, replacement workflows, or stdlib delegation.
- Implement any new execution behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact nested-group slice.

## Notes
- Build on `RBR-0077`.
- This task exists so the queue turns the first bounded nesting cases into real Rust-backed behavior instead of leaving them as publication-only coverage.

## Completion
- Landed a bounded Rust-backed nested-capture parser/executor for literal prefix/suffix workflows such as `a((b))d` and `a(?P<outer>(?P<inner>b))d`, including CPython-shaped compile metadata and match capture spans.
- Threaded native `lastindex` through the CPython boundary so nested named groups report the outer group as the last closed capture, matching CPython.
- Added direct Python parity coverage and regenerated `reports/correctness/latest.json`; the combined published scorecard now reports 136 passes, 0 failures, and 0 unimplemented cases across the default fixture set.
