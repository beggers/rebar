# RBR-0105: Add bounded conditional group-exists parity

Status: done
Owner: implementation
Created: 2026-03-12

## Goal
- Convert the first bounded conditional group-exists cases from the published correctness pack into real CPython-shaped behavior without claiming assertion-conditioned branches, nested conditionals, or broad backtracking support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_conditional_group_exists_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact conditional group-exists cases published by `RBR-0104` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` match flows.
- Any new conditional parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one conditional site keyed by an already-open optional numbered or named capture inside literal prefix/suffix text is enough, but assertion-conditioned branches, nested conditionals, replacement semantics, branch-local backreferences inside conditional arms, quantified conditionals, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded conditional group-exists cases from `unimplemented` to `pass` without regressing the already-landed optional-group, grouped-alternation, or branch-local backreference behavior.

## Constraints
- Keep this task scoped to the conditional group-exists cases published by `RBR-0104`; do not broaden into assertion-conditioned branches, replacement workflows, broader quantified execution, or stdlib delegation.
- Implement any new execution behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact conditional slice.

## Notes
- Build on `RBR-0104`.
- This task exists so the queue turns the first conditional group-exists workflows into real Rust-backed behavior instead of leaving them as publication-only coverage.
- Completed 2026-03-12: added narrow Rust-backed numbered/named group-exists conditional compile and match parity for `a(b)?c(?(1)d|e)` and `a(?P<word>b)?c(?(word)d|e)`, added parity coverage, and republished `reports/correctness/latest.json` at 194/194 passing with 0 `unimplemented` cases.
