# RBR-0063: Add bounded grouped-segment parity

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Convert the first grouped-segment literal cases from the published correctness pack into real CPython-shaped behavior without claiming general grouped-pattern or alternation support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_grouped_segment_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact grouped-segment literal cases published by `RBR-0062` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` match flows.
- Any new grouped-segment parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: literal prefix/suffix text around one capture group is enough, but nested groups, alternation, quantified groups, interleaved backreferences, and broader segmented-regex parsing remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded grouped-segment cases from `unimplemented` to `pass` without regressing the already-landed grouped-capture, named-group, and backreference workflow behavior.

## Constraints
- Keep this task scoped to the grouped-segment cases published by `RBR-0062`; do not broaden into alternation, nested-group execution, or stdlib delegation.
- Implement any new execution behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact grouped-segment slice.

## Notes
- Build on `RBR-0060`, `RBR-0061`, and `RBR-0062`.
- This task exists so the queue extends from bare grouped-reference parity into the next realistic literal-pattern shape instead of stopping at patterns made only of adjacent captures or references.
