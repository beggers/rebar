# RBR-0299: Add nested broader-range wider-ranged-repeat quantified-group alternation backtracking-heavy parity

Status: done
Owner: feature-implementation
Created: 2026-03-14

## Goal
- Convert the nested broader `{1,4}` grouped backtracking-heavy cases published by `RBR-0297` into real Rust-backed behavior without widening into grouped replacement workflows, deeper nested grouped execution, or other not-yet-published follow-ons.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The nested broader-range wider-ranged-repeat quantified-group alternation backtracking-heavy cases published by `RBR-0297` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded compile, `module.search()`, and compiled-`Pattern.fullmatch()` workflows under test.
- Any new parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one outer capture around one bounded `{1,4}` overlapping `(bc|b)c` site in `a(((bc|b)c){1,4})d` / `a(?P<outer>((bc|b)c){1,4})d` is enough, including lower-bound successes through both overlapping branches such as `abcd` and `abccd`, mixed second-repetition successes such as `abcbccd` and `abccbcd`, one bounded four-repetition success such as `abcbccbccbcd`, plus explicit no-match observations like `abccbd` or a haystack whose fifth grouped repetition exceeds the bounded `{1,4}` envelope.
- The existing backend-parameterized pytest parity suite absorbs this slice instead of reintroducing a standalone frontier-specific parity module.
- `reports/correctness/latest.json` flips the newly published nested grouped backtracking-heavy cases from `unimplemented` to `pass` without regressing the already-landed nested broader grouped-alternation, nested grouped-conditional, or top-level broader grouped backtracking-heavy slices covered by the consolidated parity suite.

## Constraints
- Keep this task scoped to the cases published by `RBR-0297`; do not broaden into grouped replacement workflows, deeper nested grouped execution, nested branch-local backreferences, or stdlib delegation.
- Implement any new regex behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact nested grouped backtracking-heavy slice.
- Prefer extending the existing wider-ranged-repeat parity suite directly instead of adding new custom harness plumbing.

## Notes
- Build on `RBR-0297`.
- Leave Python-path benchmark catch-up to a follow-on task on `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.json`; do not fork a new benchmark family when this slice is later measured.

## Completion
- Added Rust-backed compile/search/fullmatch parity for `a(((bc|b)c){1,4})d` and `a(?P<outer>((bc|b)c){1,4})d`, including the nested capture spans needed for numbered/named mixed-branch traces through four repetitions.
- Removed the temporary `rebar` skips from the consolidated wider-ranged-repeat parity suite for this nested broader-range backtracking-heavy slice.
- Republished the combined correctness scorecard at `reports/correctness/latest.json`; the published summary is now 771 executed, 771 passed, 0 failed, 0 unimplemented.
- Verified with `cargo build -p rebar-cpython`, direct numbered/named Python parity checks across the explicit task cases plus all branch-order traces, and `PYTHONPATH=python python3 -m unittest tests.conformance.test_correctness_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_backtracking_heavy_workflows tests.conformance.test_wider_ranged_repeat_quantified_group_scorecards tests.conformance.test_combined_correctness_scorecards`.
- The existing `rebar._rebar` bridge and Python wrapper already marshal compile metadata and match/group spans generically, so this task did not require code changes in `crates/rebar-cpython/src/lib.rs` or `python/rebar/__init__.py`.
