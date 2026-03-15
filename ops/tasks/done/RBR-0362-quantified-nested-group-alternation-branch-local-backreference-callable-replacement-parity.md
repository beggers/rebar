# RBR-0362: Add quantified nested-group alternation plus branch-local-backreference callable-replacement parity

Status: done
Owner: feature-implementation
Created: 2026-03-15

## Goal
- Convert the bounded quantified nested-group alternation plus branch-local-backreference callable-replacement cases from `RBR-0360` into real Rust-backed behavior without claiming broader counted-repeat grouped callbacks, replacement-template variants, benchmark rows, or deeper nested grouped execution support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The exact numbered and named cases published by `RBR-0360` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded module and compiled-`Pattern` `sub()` and `subn()` callable-replacement workflows under test.
- Any new parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, callable marshalling, and native result marshalling.
- The supported slice remains intentionally narrow: one outer capture containing one `+`-quantified inner literal alternation site immediately replayed by one same-branch backreference feeding callable replacements in `a((b|c)+)\\2d` and `a(?P<outer>(?P<inner>b|c)+)(?P=inner)d` is enough, including one numbered lower-bound same-branch callback success like `abbd` or `accd`, one numbered repeated-branch or mixed-haystack callback case such as `abbbd`, `abccd`, `acbbd`, `abbbdaccd`, or `abbdacccd`, one named path that keeps both `outer` and the final selected `inner` capture observable under replacement, and one named first-match-only or doubled-haystack callback case that keeps the final inner branch observable, while broader counted repeats like `{1,4}` or `{1,}`, replacement-template variants, broader callback semantics, and deeper nested grouped execution remain out of scope.
- The shared `tests/python/test_callable_replacement_parity_suite.py` surface continues to carry callback result and callback `Match` snapshot parity for this slice; do not add a new manifest-specific callable-replacement parity module.
- `reports/correctness/latest.py` flips the bounded quantified nested-group alternation plus branch-local-backreference callable-replacement cases from `unimplemented` to `pass` without regressing the already-landed quantified nested-group alternation callable-replacement slice, the non-quantified nested-group alternation plus branch-local-backreference callable-replacement slice, or the surrounding callable-replacement and capture-metadata surfaces.

## Constraints
- Keep this task scoped to the cases published by `RBR-0360`; do not broaden into benchmark rows, broader counted repeats like `{1,4}` or `{1,}`, replacement-template workflows, general callback helpers, or stdlib delegation.
- Implement any new regex behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` and callable-replacement contracts outside this exact combined slice.

## Notes
- Build on `RBR-0360`, `RBR-0356`, `RBR-0350`, and `RBR-0332`.
- The shared callable-replacement parity suite already discovers published `*callable_replacement_workflows.py` fixtures, so widen that existing pytest surface instead of creating another manifest-specific harness.
- Keep later benchmark catch-up on the existing `benchmarks/workloads/nested_group_callable_replacement_boundary.py` path; the follow-on should add only the minimal quantified branch-local callback rows needed to publish this exact bounded slice.

## Completion Notes
- Added one native callable-replacement span-discovery path for `a((b|c)+)\\2d` and `a(?P<outer>(?P<inner>b|c)+)(?P=inner)d`, keeping the slice limited to the existing `+`-quantified branch-local-backreference workflows and explicitly rejecting the broader `{1,4}` branch-local callable shape.
- Wired the new span path through `rebar._rebar` and the shared `_native_callable_match_spans()` dispatch, then removed the pending-manifest skip from `tests/python/test_callable_replacement_parity_suite.py` so the published shared callback snapshot suite now executes this manifest directly.
- Republished the tracked combined correctness scorecard in `reports/correctness/latest.py`; the verified tracked summary is `857` total cases, `857` passes, `0` explicit failures, and `0` `unimplemented`, and `collection.replacement.quantified_nested_group_alternation_branch_local_backreference.callable` now reports `8` executed cases with `8` passes and `0` `unimplemented`.
- Verified with `cargo build -p rebar-cpython`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py tests/python/test_quantified_nested_group_alternation_callable_replacement_parity.py tests/python/test_quantified_nested_group_alternation_branch_local_backreference_parity.py tests/python/test_nested_group_alternation_branch_local_backreference_parity.py`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k nested_group_callable_replacement_manifest`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/quantified_nested_group_alternation_branch_local_backreference_callable_replacement_workflows.py --report /tmp/rbr0362-quantified-nested-group-alternation-branch-local-backreference-callable.json`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`.
- Benchmark catch-up for this exact slice remains queued separately in `RBR-0364`; the existing nested-group callable benchmark anchor tests passed, but no new quantified branch-local callable benchmark rows were added in this task.
