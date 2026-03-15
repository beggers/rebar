# RBR-0402: Add broader-range open-ended `{2,}` nested-group alternation plus branch-local-backreference conditional parity

Status: done
Owner: feature-implementation
Created: 2026-03-15

## Goal
- Convert the broader-range open-ended `{2,}` nested-group alternation plus branch-local-backreference conditional cases published by `RBR-0401` into real Rust-backed behavior without claiming later benchmark rows, replacement semantics, broader lower bounds, or deeper nested grouped execution.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_branch_local_backreference_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The exact numbered and named cases published by `RBR-0401` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded compile, `module.search()`, and compiled-`Pattern.fullmatch()` workflows under test.
- Any new parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to public-surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one outer capture containing one broader-range open-ended `{2,}` inner `(b|c)` site immediately replayed by one same-branch backreference and one later group-exists conditional in `a((b|c){2,})\\2(?(2)d|e)` and `a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)` is enough, including one numbered lower-bound success such as `abbbd` or `acccd`, one numbered mixed-branch success such as `abcbccd`, one numbered no-match such as `abcbcc`, one named lower-bound success that keeps `outer` and `inner` observable, one named mixed-branch success that keeps the final selected branch observable, and one named no-match such as `abbd`, while later benchmark catch-up, replacement workflows, broader lower bounds, and deeper nested grouped execution remain out of scope.
- The shared `tests/python/test_branch_local_backreference_parity_suite.py` surface stops skipping the `rebar` backend for this fixture bundle and continues to cover the new manifest through the existing fixture-backed parity path instead of adding another manifest-specific parity module.
- `reports/correctness/latest.py` flips the bounded broader-range open-ended `{2,}` nested-group alternation plus branch-local-backreference conditional cases from `unimplemented` to `pass` without regressing the already-landed broader-range open-ended `{2,}` plain branch-local-backreference slice, the already-landed bounded conditional-plus-branch-local-backreference slice, or the surrounding shared branch-local parity surface.

## Constraints
- Keep this task scoped to the cases published by `RBR-0401`; do not broaden into later benchmark catch-up, replacement semantics, callable replacements, or stdlib delegation.
- Implement any new regex behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern` and `Match` contracts outside this exact broader-range open-ended `{2,}` nested branch-local-backreference conditional slice.

## Notes
- Build on `RBR-0401`, `RBR-0399`, and the existing shared branch-local-backreference parity suite.
- Keep later benchmark catch-up on the existing `benchmarks/workloads/branch_local_backreference_boundary.py` path instead of forking another benchmark family.
- The shared branch-local parity suite already discovers published `*branch_local_backreference_workflows.py` fixtures, so this task should widen that existing parity coverage rather than creating another manifest-specific test harness.

## Completion
- Added a narrow Rust parser/match path in `crates/rebar-core/src/lib.rs` for the exact broader-range open-ended `{2,}` conditional spelling `a((b|c){2,})\\2(?(2)d|e)` and `a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)`, reusing the existing open-ended nested branch-local-backreference matcher because the conditional yes-arm is the only reachable arm for this bounded slice.
- Removed the temporary `rebar` backend skip from `tests/python/test_branch_local_backreference_parity_suite.py`; no `crates/rebar-cpython/src/lib.rs` or `python/rebar/__init__.py` source changes were required because the existing native compile/match entrypoints already picked up the new core support.
- Verified the shared parity surface with `./.venv/bin/python -m pytest tests/python/test_branch_local_backreference_parity_suite.py -q` (`285 passed`).
- Verified the fixture-local correctness slice with `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_workflows.py --report /tmp/rbr0402-after-fixture.json`, which reported `10` executed cases, `10` passes, `0` failures, and `0` unimplemented cases.
- Republished the tracked combined correctness report in `reports/correctness/latest.py`; the tracked summary is `917` executed cases, `917` passes, `0` failures, and `0` unimplemented cases.
- Verified the branch-local correctness scorecard path with `./.venv/bin/python -m pytest tests/conformance/test_combined_correctness_scorecards.py -k branch_local_backreference -q` (`1 passed`, `8 deselected`, `38` subtests passed).
- The remaining follow-on for this frontier is benchmark catch-up task `RBR-0404` on `benchmarks/workloads/branch_local_backreference_boundary.py`.
