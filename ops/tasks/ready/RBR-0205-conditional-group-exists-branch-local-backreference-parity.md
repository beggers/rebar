# RBR-0205: Add bounded conditional-plus-branch-local-backreference parity

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Convert the first conditional-plus-branch-local-backreference cases from the published correctness pack into real Rust-backed behavior without claiming quantified branches, replacement semantics, or broader backtracking-heavy grouped execution.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_conditional_group_exists_branch_local_backreference_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact conditional-plus-branch-local-backreference cases published by `RBR-0204` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded compile, module, and compiled-`Pattern` workflows under test.
- Any new parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one branch-local alternation site followed by one backreference and one group-exists conditional in `a((b)|c)\\2(?(2)d|e)` / `a(?P<outer>(?P<inner>b)|c)(?P=inner)(?(inner)d|e)` is enough, including the successful `abbd` path and the explicit no-match `c`-branch observations, but quantified branches, replacement workflows, callable replacement semantics, nested conditionals, alternation-heavy follow-ons, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded conditional-plus-branch-local-backreference cases from `unimplemented` to `pass` without regressing the already-landed branch-local backreference baseline, the already-landed conditional group-exists baseline, or the two-arm replacement-conditioned slices.

## Constraints
- Keep this task scoped to the cases published by `RBR-0204`; do not broaden into quantified branches, replacement workflows, nested conditionals, or stdlib delegation.
- Implement any new regex behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact combined slice.

## Notes
- Build on `RBR-0204`.
- This task exists so the queue turns the first bounded conditional-plus-branch-local-backreference workflows into real Rust-backed behavior instead of leaving them as publication-only coverage.
