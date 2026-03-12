# RBR-0117: Add bounded conditional fully-empty parity

Status: done
Owner: implementation
Created: 2026-03-12

## Goal
- Convert the first bounded fully-empty conditional group-exists cases from the published correctness pack into real CPython-shaped behavior without claiming assertion-conditioned branches, nested conditionals, replacement-conditioned workflows, or broad backtracking support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_conditional_group_exists_fully_empty_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact fully-empty conditional group-exists cases published by `RBR-0116` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` match flows.
- Any new conditional parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The task keeps the syntax distinction explicit: accepted `a(b)?c(?(1)|)` and `a(?P<word>b)?c(?(word)|)` compilation and matching must be exercised directly, including zero-width success when the optional capture is present or absent.
- The supported slice remains intentionally narrow: one conditional site keyed by an already-open optional numbered or named capture inside literal prefix/suffix text with fully empty yes and else arms is enough, but assertion-conditioned branches, nested conditionals, replacement semantics, branch-local backreferences inside conditional arms, quantified conditionals, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded fully-empty cases from `unimplemented` to `pass` without regressing the already-landed two-arm, omitted-no-arm, explicit-empty-else, or empty-yes-arm conditional behavior.

## Constraints
- Keep this task scoped to the fully-empty conditional group-exists cases published by `RBR-0116`; do not broaden into assertion-conditioned branches, replacement workflows, broader quantified execution, or stdlib delegation.
- Implement any new execution behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact conditional slice.

## Notes
- Build on `RBR-0116`.
- This task exists so the queue turns the next accepted conditional syntax form into real Rust-backed behavior instead of leaving it as publication-only coverage.

## Completion
- Landed Rust-backed compile and match support for the bounded fully-empty conditional forms `a(b)?c(?(1)|)` and `a(?P<word>b)?c(?(word)|)` by widening the existing conditional parser gate without broadening other conditional syntax.
- Added focused Rust and Python parity tests for numbered and named module/compiled-pattern flows, and republished `reports/correctness/latest.json` with the six fully-empty conditional cases flipped from `unimplemented` to `pass` in the combined 218-case scorecard.
