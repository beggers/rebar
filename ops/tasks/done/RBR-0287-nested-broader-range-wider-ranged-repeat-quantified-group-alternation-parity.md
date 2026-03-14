# RBR-0287: Add nested broader-range wider-ranged-repeat quantified-group alternation parity

Status: done
Owner: feature-implementation
Created: 2026-03-14

## Goal
- Convert the nested broader `{1,4}` grouped-alternation cases published by `RBR-0280` from documented gaps into real Rust-backed behavior without widening into nested grouped conditionals, nested grouped backtracking-heavy flows, replacement workflows, or broader nested grouped execution.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The nested broader-range wider-ranged-repeat quantified-group alternation cases published by `RBR-0280` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded compile, module, and compiled-`Pattern` workflows under test.
- Any new parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one outer capture around one broader `{1,4}` `(bc|de)` site in `a((bc|de){1,4})d` / `a(?P<outer>(bc|de){1,4})d` is enough, including lower-bound successes such as `abcd` and `aded`, mixed and upper-bound successes such as `abcbcded` and `adedededed`, plus explicit no-match observations like `ae`, a haystack whose grouped body omits the required trailing `d`, or a haystack whose fifth grouped repetition exceeds the bounded `{1,4}` envelope.
- The existing backend-parameterized pytest parity suite absorbs this slice instead of reintroducing a standalone frontier-specific parity module.
- `reports/correctness/latest.json` flips the nested broader-range grouped-alternation cases from `unimplemented` to `pass` without regressing the already-landed top-level grouped `{1,4}` alternation, grouped-conditional, grouped backtracking-heavy, or nested grouped `{1,}` slices covered by the consolidated parity suite.

## Constraints
- Keep this task scoped to the cases published by `RBR-0280`; do not broaden into nested grouped conditionals, nested grouped backtracking-heavy flows, replacement workflows, broader nested grouped execution, or stdlib delegation.
- Implement any new regex behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact nested grouped `{1,4}` slice.

## Notes
- Build on `RBR-0280`.
- Leave benchmark publication to a follow-on task on `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.json`; do not fork a new benchmark family when that Python-path catch-up is queued.

## Completion Notes
- Added one bounded Rust-backed parser/matcher shape for `a((bc|de){1,4})d` and `a(?P<outer>(bc|de){1,4})d` in `crates/rebar-core/src/lib.rs`, preserving the outer capture span plus the last inner `(bc|de)` capture span so compile metadata, `search()`, and `fullmatch()` now match CPython for the published numbered and named workflows.
- Kept Python-side changes narrow: `python/rebar/__init__.py` now recognizes the same nested broader `{1,4}` patterns in the source-only compile fallback, while the existing `rebar._rebar` boundary paths picked up the new runtime behavior directly from the Rust core without new bespoke bridge plumbing.
- Folded the new numbered and named nested broader `{1,4}` cases into `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` instead of creating a new standalone parity module.
- Republished `reports/correctness/latest.json`; the combined correctness scorecard now reports 743 executed cases, 743 passes, 0 explicit failures, and 0 honest `unimplemented` gaps.
- Verified with `cargo build -p rebar-cpython`, `.rebar/pytest-venv/bin/python -m pytest tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py -q`, `PYTHONPATH=python python3 -m rebar_harness.correctness --report reports/correctness/latest.json`, and `python3 -m unittest tests.conformance.test_correctness_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_workflows -q`.
