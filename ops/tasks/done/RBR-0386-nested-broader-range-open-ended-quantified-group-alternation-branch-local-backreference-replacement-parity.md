# RBR-0386: Add broader-range open-ended `{2,}` nested-group alternation plus branch-local-backreference replacement-template parity

Status: done
Owner: feature-implementation
Created: 2026-03-15

## Goal
- Convert the broader-range open-ended `{2,}` nested-group alternation plus branch-local-backreference replacement-template cases published by `RBR-0384` into real CPython-shaped behavior without claiming benchmark catch-up, callable replacement, broader template parsing, or deeper nested grouped execution support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_open_ended_quantified_group_replacement_template_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The exact broader-range open-ended `{2,}` replacement-template cases published by `RBR-0384` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` `sub()` / `subn()` flows using `\\1x`, `\\2x`, `\\g<outer>x`, and `\\g<inner>x`.
- Backend-parameterized Python parity coverage for this slice stays on an ordinary pytest path in `tests/python/test_open_ended_quantified_group_replacement_template_parity_suite.py`, driven directly from the published fixture instead of another file-local scenario table, bespoke manifest layer, or native-only gate.
- Module and compiled-`Pattern` flows both consume Rust-backed broader-range open-ended counted-repeat replacement behavior rather than ad hoc Python-only regex semantics; Python changes stay limited to wrapper construction, cache/object plumbing, template marshalling, and native result marshalling.
- The supported slice remains intentionally narrow: one outer capture around one broader-range open-ended `{2,}` `(b|c)` site immediately replayed by one same-branch backreference feeding numbered or named replacement templates is enough, including one numbered lower-bound same-branch path such as `abbbd` or `acccd`, one numbered mixed-branch or longer-repetition path such as `abcbccd`, `abbbbd`, `accccd`, `abbbdabcbccd`, or `abcbccdabbbd`, one named path that keeps the shifted `{2,}` `outer` capture observable under template replacement, and one named first-match-only or doubled-haystack path that keeps the final selected `inner` branch observable, while benchmark rows, callable replacements, broader template parsing, broader callback semantics, and deeper nested grouped execution remain out of scope.
- `reports/correctness/latest.py` flips the bounded broader-range open-ended `{2,}` replacement-template cases from `unimplemented` to `pass` without regressing the already-landed open-ended `{1,}` replacement-template parity, quantified nested-group replacement-template parity, the adjacent open-ended callable-replacement slice, or other published nested replacement behavior.

## Constraints
- Keep this task scoped to the cases published by `RBR-0384`; do not broaden into benchmark work, callable replacement semantics, general template parsing, or stdlib delegation.
- Implement any new execution or template-expansion behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern` / `Match` / replacement object contracts outside this exact broader-range open-ended `{2,}` nested-group branch-local-backreference replacement slice.
- Reuse ordinary pytest parameterization plus the published fixture-loading path and the existing open-ended replacement parity suite instead of adding JSON manifests, generators, or another manifest-specific harness layer.

## Notes
- Build on `RBR-0384`, `RBR-0380`, `RBR-0378`, and the existing nested-group replacement boundary.
- Keep later benchmark catch-up on the existing `benchmarks/workloads/nested_group_replacement_boundary.py` path; do not fork another benchmark family when that follow-on is seeded.

## Completion
- Extended the Rust nested branch-local backreference parser/matcher to recognize the broader-range open-ended `{2,}` lower bound for `a((b|c){2,})\\2d` and `a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d`, while keeping the replacement-template span path limited to explicit open-ended counted repeats.
- Expanded `tests/python/test_open_ended_quantified_group_replacement_template_parity_suite.py` so the existing ordinary backend-parameterized parity module now covers both the landed `{1,}` fixture and the new `{2,}` published fixture directly from `tests/conformance/fixtures/`.
- Republished `reports/correctness/latest.py`; the tracked combined scorecard is now `889` total cases, `889` passed, `0` failed, and `0` unimplemented, and the `{2,}` replacement manifest now records `8` passes with `0` gaps.
- The existing CPython bridge and Python wrapper marshalling paths were already sufficient once the Rust core recognized and executed the new slice, so no changes were needed in `crates/rebar-cpython/src/lib.rs` or `python/rebar/__init__.py`.

## Verification
- `cargo build -p rebar-cpython`
- `PYTHONPATH=python ./.venv/bin/python -m pytest tests/python/test_open_ended_quantified_group_replacement_template_parity_suite.py -q`
- `PYTHONPATH=python ./.venv/bin/python -m pytest tests/conformance/test_combined_correctness_scorecards.py -k open_ended_quantified_group_scorecards -q`
- `PYTHONPATH=python ./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_benchmark_scorecards.py::SourceTreeBenchmarkScorecardTest::test_nested_group_replacement_scorecard_covers_open_ended_rows tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeCombinedBoundaryBenchmarkSuiteTest::test_nested_group_replacement_manifest_covers_open_ended_branch_local_backreference_slice -q`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`
