# RBR-0356: Add bounded nested-group alternation plus branch-local-backreference callable-replacement parity

Status: ready
Owner: feature-implementation
Created: 2026-03-15

## Goal
- Convert the bounded nested-group alternation plus branch-local-backreference callable-replacement cases from `RBR-0354` into real Rust-backed behavior without claiming quantified branch-local-backreference callbacks, broader counted repeats, replacement-template variants, or deeper nested grouped execution.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The exact numbered and named cases published by `RBR-0354` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded module and compiled-`Pattern` `sub()` and `subn()` callable-replacement workflows under test.
- Any new parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, callable marshalling, and native result marshalling.
- The supported slice remains intentionally narrow: one outer capture containing one inner literal alternation site immediately replayed by one same-branch backreference feeding callable replacements in `a((b|c))\\2d` and `a(?P<outer>(?P<inner>b|c))(?P=inner)d` is enough, including numbered same-branch callback successes such as `abbd` or `accd`, one first-match-only mixed-haystack callback case such as `abbdaccd` or `accdabbd`, one named path that keeps both `outer` and `inner` captures observable under replacement, and one named doubled-haystack or count-limited case that keeps the final selected inner branch observable, while quantified branch-local-backreference callbacks, broader counted repeats like `{1,4}` or `{1,}`, replacement-template variants, broader callback semantics, and deeper nested grouped execution remain out of scope.
- The shared `tests/python/test_callable_replacement_parity_suite.py` surface continues to carry callback match-object parity for this slice; do not add a new task-local callable-replacement parity module.
- `reports/correctness/latest.py` flips the bounded nested-group alternation plus branch-local-backreference callable-replacement cases from `unimplemented` to `pass` without regressing the already-landed nested-group callable-replacement, nested-group alternation callable-replacement, quantified nested-group alternation callable-replacement, or nested-group alternation plus branch-local-backreference slices.

## Constraints
- Keep this task scoped to the cases published by `RBR-0354`; do not broaden into quantified variants, benchmark rows, replacement-template workflows, or stdlib delegation.
- Implement any new regex behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` and callable-replacement contracts outside this exact combined slice.

## Notes
- Build on `RBR-0354`, `RBR-0345`, `RBR-0344`, and `RBR-0326`.
- Keep later benchmark catch-up on the existing `benchmarks/workloads/nested_group_callable_replacement_boundary.py` path instead of forking another benchmark family.
- The shared callable-replacement parity suite already discovers published `*callable_replacement_workflows.py` fixtures, so this task should widen existing parity coverage rather than creating another manifest-specific test harness.
