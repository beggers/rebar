# RBR-0120: Add bounded assertion-conditioned conditional diagnostic parity

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Convert the first bounded assertion-conditioned conditional diagnostic cases from the published correctness pack into real Rust-backed compile diagnostics without claiming broader conditional execution support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_conditional_group_exists_assertion_diagnostic_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact assertion-conditioned conditional cases published by `RBR-0119` stop reporting `unimplemented` and instead match CPython-shaped compile diagnostics through the public `rebar` API.
- Any new conditional parsing or diagnostic behavior lives behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native error marshalling.
- The supported slice remains intentionally narrow: assertion-conditioned forms such as `a(?(?=b)b|c)d` are rejected with the expected diagnostic shape, while accepted empty-arm forms, nested conditionals, replacement-conditioned workflows, quantified conditionals, and broader backtracking remain scoped to their existing tasks.
- `reports/correctness/latest.json` flips the bounded assertion-conditioned diagnostic cases from `unimplemented` to `pass` without regressing the already-landed accepted conditional behavior.

## Constraints
- Keep this task scoped to the assertion-conditioned diagnostic cases published by `RBR-0119`; do not broaden into general conditional expressions, replacement workflows, broader parser cleanup, or stdlib delegation.
- Implement any new diagnostic behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact compile-diagnostic slice.

## Notes
- Build on `RBR-0119`.
- This task exists so the queue turns the next exact conditional diagnostic frontier into real Rust-backed behavior instead of leaving it as publication-only coverage.
