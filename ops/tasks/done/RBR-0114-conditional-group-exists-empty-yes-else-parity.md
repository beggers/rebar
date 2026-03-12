# RBR-0114: Add bounded conditional empty-yes-arm parity

Status: done
Owner: implementation
Created: 2026-03-12

## Goal
- Convert the first bounded empty-yes-arm conditional group-exists cases from the published correctness pack into real CPython-shaped behavior without claiming fully empty conditional arms, assertion-conditioned branches, nested conditionals, or broad backtracking support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_conditional_group_exists_empty_yes_else_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact empty-yes-arm conditional group-exists cases published by `RBR-0113` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` match flows.
- Any new conditional parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The task keeps the syntax and behavior distinction explicit: accepted `a(b)?c(?(1)|e)` and `a(?P<word>b)?c(?(word)|e)` compilation and matching must be exercised directly, including the zero-width yes-arm success when the capture is present.
- The supported slice remains intentionally narrow: one conditional site keyed by an already-open optional numbered or named capture inside literal prefix/suffix text with an explicit empty yes arm is enough, but fully empty `(?(1)|)` / `(?(name)|)` forms, assertion-conditioned branches, nested conditionals, replacement semantics, branch-local backreferences inside conditional arms, quantified conditionals, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded empty-yes-arm cases from `unimplemented` to `pass` without regressing the already-landed two-arm, omitted-no-arm, or explicit-empty-else conditional behavior.

## Constraints
- Keep this task scoped to the empty-yes-arm conditional group-exists cases published by `RBR-0113`; do not broaden into fully empty arm forms, assertion-conditioned branches, replacement workflows, broader quantified execution, or stdlib delegation.
- Implement any new execution behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact conditional slice.

## Notes
- Build on `RBR-0113`.
- This task exists so the queue turns the next accepted conditional runtime form into real Rust-backed behavior instead of leaving it as publication-only coverage.
- Completed 2026-03-12: widened the bounded Rust conditional parser to accept explicit empty-yes-arm plus literal-else forms while preserving the already-landed empty-else slice and still rejecting the fully empty `(?(1)|)` / `(?(name)|)` forms.
- Added Rust and Python parity coverage for numbered and named `a(b)?c(?(1)|e)` / `a(?P<word>b)?c(?(word)|e)` compile, module `search()`, and compiled-pattern `fullmatch()` flows, and republished `reports/correctness/latest.json` at 212/212 passing cases with zero honest gaps in the published slice.
