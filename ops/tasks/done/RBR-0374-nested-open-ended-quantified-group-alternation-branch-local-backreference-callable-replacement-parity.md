# RBR-0374: Add open-ended `{1,}` nested-group alternation plus branch-local-backreference callable-replacement parity

Status: done
Owner: feature-implementation
Created: 2026-03-15

## Goal
- Convert the open-ended `{1,}` nested-group alternation plus branch-local-backreference callable-replacement cases from `RBR-0372` into real Rust-backed behavior without claiming later benchmark rows, replacement-template variants, broader callback semantics, or deeper nested grouped execution.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The exact numbered and named cases published by `RBR-0372` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded module and compiled-`Pattern` `sub()` and `subn()` callable-replacement workflows under test.
- Any new parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, callable marshalling, and native result marshalling.
- The supported slice remains intentionally narrow: one outer capture containing one open-ended `{1,}` inner `(b|c)` site immediately replayed by one same-branch backreference feeding callable replacements in `a((b|c){1,})\\2d` and `a(?P<outer>(?P<inner>b|c){1,})(?P=inner)d` is enough, including one numbered lower-bound same-branch callback success such as `abbd` or `accd`, one numbered longer repeated-branch or mixed-haystack callback case such as `abbbd`, `abccd`, `abcbccd`, `abbbdaccd`, or `abcbccdabbd`, one named path that keeps the open-ended `{1,}` `outer` capture observable under replacement, and one named first-match-only or doubled-haystack case that keeps the final selected `inner` branch observable under replacement, while later benchmark catch-up, replacement-template variants, broader callback semantics, and deeper nested grouped execution remain out of scope.
- The shared `tests/python/test_callable_replacement_parity_suite.py` surface continues to carry callback result and callback `Match` snapshot parity for this slice; do not add a new manifest-specific callable-replacement parity module.
- `reports/correctness/latest.py` flips the bounded open-ended `{1,}` nested-group alternation plus branch-local-backreference callable-replacement cases from `unimplemented` to `pass` without regressing the already-landed quantified `+` and broader `{1,4}` callback slices, the adjacent open-ended non-callable nested-group slice, or the surrounding callable-replacement and capture-metadata surfaces.

## Constraints
- Keep this task scoped to the cases published by `RBR-0372`; do not broaden into later benchmark catch-up, replacement-template workflows, broader callback helpers, or stdlib delegation.
- Implement any new regex behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` and callable-replacement contracts outside this exact open-ended slice.

## Notes
- Build on `RBR-0372`, `RBR-0370`, `RBR-0368`, and the existing shared callable-replacement fixture path.
- Keep later benchmark catch-up on the existing `benchmarks/workloads/nested_group_callable_replacement_boundary.py` path instead of forking another benchmark family.
- The shared callable-replacement parity suite already discovers published `*callable_replacement_workflows.py` fixtures, so this task should widen that existing parity coverage rather than creating another manifest-specific test harness.

## Completion
- Extended the existing Rust quantified nested-group alternation branch-local-backreference parser path to accept the exact open-ended `{1,}` numbered and named callable-replacement patterns, so the shared callable replacement machinery now compiles and executes `a((b|c){1,})\\2d` and `a(?P<outer>(?P<inner>b|c){1,})(?P=inner)d` without adding a Python-only regex implementation path.
- Removed this manifest from the shared callable parity suite's pending skip set instead of creating another manifest-specific parity module.
- Republished `reports/correctness/latest.py`; the tracked published summary now reads 873 total cases, 873 passed, 0 failed, and 0 unimplemented across 97 manifests.
- Verified with `./.venv/bin/python -m pytest tests/python/test_callable_replacement_parity_suite.py -q`, `./.venv/bin/python -m pytest tests/conformance/test_combined_correctness_scorecards.py -q -k open_ended_quantified_group_scorecards`, and `./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_benchmark_scorecards.py -q -k nested_group_callable_replacement_scorecard_covers_broader_range_rows`.
- Ran a narrow scratch correctness publication for `tests/conformance/fixtures/nested_open_ended_quantified_group_alternation_branch_local_backreference_callable_replacement_workflows.py`, which completed at 8 executed / 8 passed / 0 unimplemented.
- The direct Python-path benchmark catch-up for this exact `{1,}` callable slice remains queued separately in `RBR-0376`; this task did not change `reports/benchmarks/latest.py`.
