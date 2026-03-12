# RBR-0111: Add bounded conditional explicit-empty-else parity

Status: done
Owner: implementation
Created: 2026-03-12

## Goal
- Convert the first bounded explicit-empty-else conditional group-exists cases from the published correctness pack into real CPython-shaped behavior without claiming assertion-conditioned branches, nested conditionals, or broad backtracking support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_conditional_group_exists_empty_else_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact explicit-empty-else conditional group-exists cases published by `RBR-0110` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` match flows.
- Any new conditional parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The task keeps the syntax distinction explicit even if the bounded runtime behavior shares code with the omitted-no-arm slice: accepted `a(b)?c(?(1)d|)` and `a(?P<word>b)?c(?(word)d|)` compilation and matching must be exercised directly.
- The supported slice remains intentionally narrow: one conditional site keyed by an already-open optional numbered or named capture inside literal prefix/suffix text with an explicit empty else arm is enough, but assertion-conditioned branches, nested conditionals, replacement semantics, branch-local backreferences inside conditional arms, quantified conditionals, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded explicit-empty-else cases from `unimplemented` to `pass` without regressing the already-landed two-arm conditional group-exists or omitted-no-arm conditional behavior.

## Constraints
- Keep this task scoped to the explicit-empty-else conditional group-exists cases published by `RBR-0110`; do not broaden into assertion-conditioned branches, replacement workflows, broader quantified execution, or stdlib delegation.
- Implement any new execution behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact conditional slice.

## Notes
- Build on `RBR-0110`.
- This task exists so the queue turns the next accepted conditional syntax form into real Rust-backed behavior instead of leaving it as publication-only coverage.
- Completed 2026-03-12: Rust conditional parsing now accepts explicit empty else arms `|)` for the bounded numbered and named group-exists slice, targeted native parity tests cover compile/search/fullmatch behavior, and `reports/correctness/latest.json` now publishes all 206 cases as passing with 0 unimplemented gaps.
