# RBR-0066: Add bounded literal-alternation parity

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Convert the first literal-alternation cases from the published correctness pack into real CPython-shaped behavior without claiming general alternation or grouped-branch support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_literal_alternation_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact literal-alternation cases published by `RBR-0065` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` match flows.
- Any new alternation parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one simple top-level literal alternation path is enough, but grouped alternation, nested branches, quantified branches, conditionals, and broader backtracking semantics remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded literal-alternation cases from `unimplemented` to `pass` without regressing the already-landed grouped-capture, named-group, backreference, and grouped-segment workflow behavior.

## Constraints
- Keep this task scoped to the literal-alternation cases published by `RBR-0065`; do not broaden into grouped alternation, nested-group execution, or stdlib delegation.
- Implement any new execution behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact literal-alternation slice.

## Notes
- Build on `RBR-0063`, `RBR-0064`, and `RBR-0065`.
- This task exists so the queue extends from grouped-segment work into the next realistic branch-selection shape instead of stopping at a reporting-only frontier.
