# RBR-0087: Add bounded nested-group alternation parity

Status: done
Owner: implementation
Created: 2026-03-12
Completed: 2026-03-12

## Goal
- Convert the first nested-group alternation cases from the published correctness pack into real CPython-shaped behavior without claiming broad nested alternation, quantified-branch, or general backtracking semantics.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_nested_group_alternation_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact nested-group alternation cases published by `RBR-0086` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` match flows.
- Any new nested-group alternation parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one outer capturing group containing one inner numbered or named capturing group with one literal alternation site inside literal prefix/suffix text is enough, but multiple alternations, quantified branches, branch-local backreferences, replacement semantics, callable replacement semantics, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded nested-group alternation cases from `unimplemented` to `pass` without regressing the already-landed grouped-alternation workflow, nested-group workflow, or grouped-alternation callable-replacement support.

## Constraints
- Keep this task scoped to the nested-group alternation cases published by `RBR-0086`; do not broaden into quantified branches, branch-local backreferences, replacement workflows, or stdlib delegation.
- Implement any new execution behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact nested-group alternation slice.

## Notes
- Build on `RBR-0078`, `RBR-0075`, and `RBR-0086`.
- This task exists so the queue turns the first combined nested-group and alternation workflows into real Rust-backed behavior instead of leaving them as publication-only coverage.

## Completion Notes
- Added a bounded Rust-core nested-group alternation parser/matcher for `a((b|c))d` and `a(?P<outer>(?P<inner>b|c))d`, including correct compile metadata, capture spans, and CPython-shaped `lastindex`/`lastgroup` behavior through the existing native compile/match boundary.
- Added targeted Python parity coverage for numbered and named nested-group alternation compile/module/pattern flows and refreshed the correctness-harness regression expectations for the new all-pass frontier.
- Republished `reports/correctness/latest.json`; the combined scorecard now reports 158 total cases with 158 passes and 0 `unimplemented` outcomes across the published manifest set.
