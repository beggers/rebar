# RBR-0084: Add bounded nested-group callable-replacement parity

Status: done
Owner: implementation
Created: 2026-03-12
Completed: 2026-03-12

## Goal
- Convert the first nested-group callable-replacement cases from the published correctness pack into real CPython-shaped behavior without claiming broad nested-group, alternation-in-nesting, quantified-group, or general callback semantics.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_nested_group_callable_replacement_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact nested-group callable-replacement cases published by `RBR-0083` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded `sub()` and `subn()` flows.
- Module and compiled-`Pattern` flows both consume Rust-backed nested-group callable-replacement behavior rather than ad hoc Python-only regex semantics; Python changes stay limited to wrapper construction, cache/object plumbing, callable marshalling, and native result marshalling.
- The supported slice remains intentionally narrow: one outer capturing group containing one inner numbered or named capturing group inside literal prefix/suffix text feeding a callable replacement that inspects numbered or named capture values is enough, but nested alternation, quantified groups, replacement-template behavior beyond the published pack, broader match-object callback behavior, branch-local backreferences, conditionals, and broader backtracking semantics remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded nested-group callable-replacement cases from `unimplemented` to `pass` without regressing the already-landed nested-group match behavior, nested-group replacement-template behavior, grouped callable replacement support, or grouped-alternation callable-replacement behavior.

## Constraints
- Keep this task scoped to the nested-group callable-replacement cases published by `RBR-0083`; do not broaden into nested alternation, quantified groups, general callback semantics, or stdlib delegation.
- Implement any new execution or callback behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match`/replacement object contracts outside this exact nested-group callable-replacement slice.

## Notes
- Build on `RBR-0078`, `RBR-0081`, and `RBR-0083`.
- This task exists so the queue turns the first nested capture plus callable-replacement workflows into real Rust-backed behavior instead of leaving them as publication-only coverage.
- Completed with a new native nested-capture finditer boundary wired into the existing Python callable-replacement path, a targeted nested-group callable parity test, refreshed correctness-harness expectations, and a republished `reports/correctness/latest.json` scorecard showing 152 passes and 0 unimplemented cases across the published manifest set.
