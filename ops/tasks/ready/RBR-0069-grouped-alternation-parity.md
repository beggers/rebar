# RBR-0069: Add bounded grouped-alternation parity

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Convert the first grouped-alternation cases from the published correctness pack into real CPython-shaped behavior without claiming broad alternation, nested-group, or quantified-branch support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_grouped_alternation_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact grouped-alternation cases published by `RBR-0068` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` match flows.
- Any new grouped-alternation parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one grouped branch-selection site inside literal prefix/suffix text is enough, but nested groups, multiple alternations, quantified branches, branch-local backreferences, conditionals, and broader backtracking semantics remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded grouped-alternation cases from `unimplemented` to `pass` without regressing the already-landed grouped-capture, named-group, backreference, grouped-segment, and literal-alternation workflow behavior.

## Constraints
- Keep this task scoped to the grouped-alternation cases published by `RBR-0068`; do not broaden into nested-group execution, quantified branches, or stdlib delegation.
- Implement any new execution behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact grouped-alternation slice.

## Notes
- Build on `RBR-0066`, `RBR-0067`, and `RBR-0068`.
- This task exists so the queue extends from top-level branch selection into the first combined grouping-and-alternation shape instead of stopping at a reporting-only frontier.
