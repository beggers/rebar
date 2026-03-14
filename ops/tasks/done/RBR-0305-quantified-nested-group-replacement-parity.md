# RBR-0305: Add quantified nested-group replacement-template parity

Status: done
Owner: feature-implementation
Created: 2026-03-14

## Goal
- Convert the quantified nested-group replacement-template cases from `RBR-0303` into real CPython-shaped behavior without claiming broader quantified grouped replacement, callable replacement, alternation inside the repeated site, or deeper nested grouped execution support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_quantified_nested_group_replacement_template_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact quantified nested-group replacement-template cases published by `RBR-0303` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded `sub()` and `subn()` flows.
- Module and compiled-`Pattern` flows both consume Rust-backed quantified nested-group replacement behavior rather than ad hoc Python-only regex semantics; Python changes stay limited to wrapper construction, cache/object plumbing, template marshalling, and native result marshalling.
- The supported slice remains intentionally narrow: one outer capturing group containing one `+`-quantified inner numbered or named capturing group inside literal prefix/suffix text feeding numbered or named replacement templates is enough, including lower-bound one-repetition workflows like `abcd`, repeated-inner-capture workflows like `abcbcd`, and one bounded first-match-only workflow on `abcbcdabcbcd`, but callable replacements, alternation inside the repeated site, broader counted-repeat shapes like `{1,4}` or open-ended grouped backtracking-heavy replacement, branch-local backreferences, and deeper nested grouped execution remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded quantified nested-group replacement-template cases from `unimplemented` to `pass` without regressing the already-landed nested-group replacement-template behavior, quantified nested-group match behavior, grouped replacement-template behavior, or named-group replacement-template behavior.

## Constraints
- Keep this task scoped to the quantified nested-group replacement-template cases published by `RBR-0303`; do not broaden into callable replacement semantics, alternation inside the repeated site, broader counted repeats, general template parsing, or stdlib delegation.
- Implement any new execution or template-expansion behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match`/replacement object contracts outside this exact quantified nested-group replacement slice.

## Notes
- Build on `RBR-0303`, `RBR-0081`, and the existing grouped replacement-template support.
- Keep later benchmark catch-up on the existing `benchmarks/workloads/nested_group_replacement_boundary.py` path, which already carries the quantified named `Pattern.subn()` gap row; do not fork another benchmark family when that follow-on is seeded.

## Completion Notes
- Added a narrow Rust-core quantified nested-group parser/compile classification plus template-replacement span collector for `a((bc)+)d` and `a(?P<outer>(?P<inner>bc)+)d`, keeping the support scoped to numbered and named replacement templates on `sub()` and `subn()`.
- Routed the native template replacement boundary through that new span collector without widening callable replacement or general match execution for the same quantified nested-group shape.
- Added direct Python parity coverage in `tests/python/test_quantified_nested_group_replacement_template_parity.py`, updated the quantified nested-group correctness regression to expect eight passes instead of eight `unimplemented` outcomes, and republished `reports/correctness/latest.json`.
- Verified with `cargo build -p rebar-cpython`, `PYTHONPATH=python python3 -m unittest tests.python.test_quantified_nested_group_replacement_template_parity tests.conformance.test_correctness_quantified_nested_group_replacement_workflows tests.conformance.test_combined_correctness_scorecards`, and `PYTHONPATH=python python3 -m rebar_harness.correctness --report reports/correctness/latest.json`.
