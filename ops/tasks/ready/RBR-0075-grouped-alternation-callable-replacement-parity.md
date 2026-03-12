# RBR-0075: Add bounded grouped-alternation callable-replacement parity

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Convert the first grouped-alternation callable-replacement cases from the published correctness pack into real CPython-shaped behavior without claiming broad alternation, nested-group, or general callback semantics.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_grouped_alternation_callable_replacement_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact grouped-alternation callable-replacement cases published by `RBR-0074` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded `sub()` and `subn()` flows.
- Module and compiled-`Pattern` flows both consume Rust-backed grouped-alternation callable-replacement behavior rather than ad hoc Python-only regex semantics; Python changes stay limited to wrapper construction, cache/object plumbing, callable marshalling, and native result marshalling.
- The supported slice remains intentionally narrow: one grouped branch-selection site inside literal prefix/suffix text feeding a callable replacement that inspects numbered or named capture values is enough, but nested groups, multiple alternations, broader match-object callback behavior, quantified branches, branch-local backreferences, conditionals, and broader backtracking semantics remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded grouped-alternation callable-replacement cases from `unimplemented` to `pass` without regressing the already-landed grouped-alternation match behavior, grouped-alternation replacement-template behavior, or earlier bounded callable replacement support.

## Constraints
- Keep this task scoped to the grouped-alternation callable-replacement cases published by `RBR-0074`; do not broaden into nested-group execution, quantified branches, general callback semantics, or stdlib delegation.
- Implement any new execution or callback behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match`/replacement object contracts outside this exact grouped-alternation callable-replacement slice.

## Notes
- Build on `RBR-0072`, `RBR-0073`, and `RBR-0074`.
- This task exists so the queue extends from grouped-alternation replacement templates into the first combined alternation-and-callback workflow instead of stopping at a reporting-only frontier.
