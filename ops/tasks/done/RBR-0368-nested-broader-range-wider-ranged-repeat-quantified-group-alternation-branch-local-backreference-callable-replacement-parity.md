# RBR-0368: Add broader `{1,4}` nested-group alternation plus branch-local-backreference callable-replacement parity

Status: done
Owner: feature-implementation
Created: 2026-03-15
Completed: 2026-03-15

## Goal
- Convert the broader `{1,4}` nested-group alternation plus branch-local-backreference callable-replacement cases from `RBR-0366` into real Rust-backed behavior without claiming open-ended counted-repeat grouped callbacks, replacement-template variants, later benchmark rows, or deeper nested grouped execution support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The exact numbered and named cases published by `RBR-0366` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded module and compiled-`Pattern` `sub()` and `subn()` callable-replacement workflows under test.
- Any new parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, callable marshalling, and native result marshalling.
- The supported slice remains intentionally narrow: one outer capture containing one broader `{1,4}` inner `(b|c)` site immediately replayed by one same-branch backreference feeding callable replacements in `a((b|c){1,4})\\2d` and `a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d` is enough, including one numbered lower-bound same-branch callback success such as `abbd` or `accd`, one numbered broader counted-repeat or mixed-branch callback case such as `abbbd`, `abcbccd`, `abbbdaccd`, or `abcbccdabbd`, one named path that keeps the broader `{1,4}` `outer` capture observable under replacement, and one named first-match-only or doubled-haystack case that keeps the final selected `inner` branch observable under replacement, while open-ended counted repeats like `{1,}`, benchmark rows, replacement-template variants, broader callback semantics, and deeper nested grouped execution remain out of scope.
- The shared `tests/python/test_callable_replacement_parity_suite.py` surface continues to carry callback result and callback `Match` snapshot parity for this slice; do not add a new manifest-specific callable-replacement parity module.
- `reports/correctness/latest.py` flips the bounded broader `{1,4}` nested-group alternation plus branch-local-backreference callable-replacement cases from `unimplemented` to `pass` without regressing the already-landed quantified nested-group alternation plus branch-local-backreference callable-replacement slice, the adjacent broader `{1,4}` nested-group alternation plus branch-local-backreference non-callable slice, or the surrounding callable-replacement and capture-metadata surfaces.

## Constraints
- Keep this task scoped to the cases published by `RBR-0366`; do not broaden into open-ended counted repeats, later benchmark catch-up, replacement-template workflows, or stdlib delegation.
- Implement any new regex behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` and callable-replacement contracts outside this exact broader `{1,4}` combined slice.

## Notes
- Build on `RBR-0366`, `RBR-0362`, `RBR-0356`, and `RBR-0338`.
- Keep later benchmark catch-up on the existing `benchmarks/workloads/nested_group_callable_replacement_boundary.py` path instead of forking another benchmark family.
- The shared callable-replacement parity suite already discovers published `*callable_replacement_workflows.py` fixtures, so this task should widen that existing parity coverage rather than creating another manifest-specific test harness.

## Completion Notes
- Enabled the existing Rust-backed quantified nested-group alternation plus branch-local-backreference callable span collector for bounded `{1,4}` forms by removing the last core-side filter that rejected `max_repeat = Some(4)` after the parser had already accepted `a((b|c){1,4})\\2d` and `a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d`.
- Cleared the stale pending-manifest skip in `tests/python/test_callable_replacement_parity_suite.py`; the shared callable parity suite now executes this broader `{1,4}` manifest directly. No source edits were needed in `crates/rebar-cpython/src/lib.rs` or `python/rebar/__init__.py` because the existing `rebar._rebar` export and `_native_callable_match_spans()` dispatch already routed this slice once the Rust core stopped rejecting it.
- Republished the tracked combined correctness scorecard in `reports/correctness/latest.py`; the verified tracked summary is `865` total cases, `865` passes, `0` explicit failures, and `0` `unimplemented`, and `collection.replacement.nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference.callable` now reports `8` executed cases with `8` passes and `0` `unimplemented`.
- Verified with `cargo build -p rebar-cpython`, `PYTHONPATH=python ./.venv/bin/python -m pytest tests/python/test_callable_replacement_parity_suite.py -q`, `PYTHONPATH=python ./.venv/bin/python -m pytest tests/python/test_branch_local_backreference_parity_suite.py -k broader-range -q`, `PYTHONPATH=python ./.venv/bin/python -m pytest tests/conformance/test_combined_correctness_scorecards.py -k nested_broader_range_wider_ranged_repeat_quantified_group_alternation -q`, `PYTHONPATH=python ./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k nested_group_callable_replacement_manifest -q`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`.
- Later benchmark catch-up for this exact broader `{1,4}` callable slice remains queued separately in `RBR-0370`; the existing nested-group callable benchmark-anchor expectations stayed green, but this task did not add new broader-range callable benchmark rows.
