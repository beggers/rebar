# RBR-0090: Add bounded branch-local backreference parity

Status: done
Owner: implementation
Created: 2026-03-12
Completed: 2026-03-12

## Goal
- Convert the first bounded branch-local backreference cases from the published correctness pack into real CPython-shaped behavior without claiming quantified-branch, conditional, or broad backtracking support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_branch_local_backreference_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact branch-local backreference cases published by `RBR-0089` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` match flows.
- Any new branch-local backreference parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one alternation site with one branch-local numbered or named capture that is later referenced inside literal prefix/suffix text is enough, but quantified branches, nested alternation beyond the published pack, replacement semantics, callable replacement semantics, conditionals, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded branch-local backreference cases from `unimplemented` to `pass` without regressing the already-landed numbered-backreference, named-backreference, grouped-alternation, or nested-group alternation behavior.

## Constraints
- Keep this task scoped to the branch-local backreference cases published by `RBR-0089`; do not broaden into quantified branches, conditionals, replacement workflows, or stdlib delegation.
- Implement any new execution behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact branch-local backreference slice.

## Notes
- Build on `RBR-0060`, `RBR-0057`, and `RBR-0089`.
- This task exists so the queue turns the first combined alternation-and-backreference workflows into real Rust-backed behavior instead of leaving them as publication-only coverage.

## Completion Notes
- Added Rust-backed compile and match support for the published numbered and named branch-local backreference shapes, preserving CPython group metadata and `lastindex`/`lastgroup` behavior for the matched branch.
- Added Python parity coverage for the six published compile/module/pattern cases and updated the correctness harness expectation test.
- Republished `reports/correctness/latest.json`; the combined scorecard now reports `164` passes and `0` `unimplemented` cases.
