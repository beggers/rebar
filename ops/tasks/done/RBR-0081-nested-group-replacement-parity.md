# RBR-0081: Add bounded nested-group replacement-template parity

Status: done
Owner: implementation
Created: 2026-03-12

## Goal
- Convert the first nested-group replacement-template cases from the published correctness pack into real CPython-shaped behavior without claiming broad nested-group, alternation-in-nesting, quantified-group, or callable-replacement support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_nested_group_replacement_template_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact nested-group replacement-template cases published by `RBR-0080` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded `sub()` and `subn()` flows.
- Module and compiled-`Pattern` flows both consume Rust-backed nested-group replacement behavior rather than ad hoc Python-only regex semantics; Python changes stay limited to wrapper construction, cache/object plumbing, callable/template marshalling, and native result marshalling.
- The supported slice remains intentionally narrow: one outer capturing group containing one inner numbered or named capturing group inside literal prefix/suffix text feeding a numbered or named replacement template is enough, but nested alternation, quantified groups, callable replacements for nested groups, branch-local backreferences, conditionals, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded nested-group replacement-template cases from `unimplemented` to `pass` without regressing the already-landed nested-group match behavior, grouped replacement-template behavior, named-group replacement-template behavior, or grouped-alternation replacement behavior.

## Constraints
- Keep this task scoped to the nested-group replacement-template cases published by `RBR-0080`; do not broaden into nested alternation, quantified groups, callable replacement semantics, general template parsing, or stdlib delegation.
- Implement any new execution or template-expansion behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match`/replacement object contracts outside this exact nested-group replacement slice.

## Notes
- Build on `RBR-0078`, `RBR-0080`, and any grouped replacement-template support already landed.
- This task exists so the queue turns the first nested capture plus replacement-template workflows into real Rust-backed behavior instead of leaving them as publication-only coverage.

## Completion
- Landed Rust-backed nested-group replacement-template expansion for the published numbered and named outer/inner capture cases by widening bounded template expansion to consume multiple positional and named captures plus a dedicated nested repeated-span discovery path.
- Added `tests/python/test_nested_group_replacement_template_parity.py`, updated the nested-group replacement correctness expectations, and republished `reports/correctness/latest.json` with the combined 144/144 passing scorecard.
- Verified with `cargo test -p rebar-core replacement_template_expands_nested_group_references -- --nocapture`, `cargo test -p rebar-core nested_capture_find_spans_reports_repeated_matches_and_capture_spans -- --nocapture`, `python3 -m unittest tests.python.test_grouped_literal_replacement_template tests.python.test_named_group_replacement_template_parity tests.python.test_nested_group_replacement_template_parity`, and `python3 -m unittest tests.python.test_nested_group_replacement_template_parity tests.conformance.test_correctness_nested_group_replacement_workflows`.
