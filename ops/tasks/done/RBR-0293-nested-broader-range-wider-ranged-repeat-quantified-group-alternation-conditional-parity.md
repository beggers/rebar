# RBR-0293: Add nested broader-range wider-ranged-repeat quantified-group alternation plus conditional parity

Status: done
Owner: feature-implementation
Created: 2026-03-14

## Goal
- Convert the bounded nested broader `{1,4}` grouped-alternation-plus-conditional cases published by `RBR-0291` into real Rust-backed behavior without widening into nested grouped backtracking-heavy flows, replacement workflows, or broader nested grouped execution.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact nested broader-range wider-ranged-repeat grouped-alternation-plus-conditional cases published by `RBR-0291` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded compile, `module.search()`, and compiled-`Pattern.fullmatch()` workflows.
- Any new parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one optional outer capture around the already-landed nested broader `{1,4}` grouped-alternation subpattern plus one later conditional in `a(((bc|de){1,4})d)?(?(1)e|f)` / `a(?P<outer>((bc|de){1,4})d)?(?(outer)e|f)` is enough, including the absent-group `else` path on `af`, lower-bound present-group hits like `abcde` and `adede`, mixed and upper-bound present-group hits like `abcbcdede` and `adedededede`, plus explicit no-match observations like `ae`, a present-group branch that omits the final conditional `e`, or a haystack whose fifth grouped repetition exceeds the bounded `{1,4}` envelope before the later conditional can match.
- The existing backend-parameterized pytest parity suite absorbs this slice instead of reintroducing a standalone frontier-specific parity module.
- `reports/correctness/latest.json` flips the newly published nested grouped-conditional cases from `unimplemented` to `pass` without regressing the already-landed wider-ranged-repeat grouped-alternation, broader `{1,4}` grouped-conditional, or nested grouped-alternation slices.

## Constraints
- Keep this task scoped to the cases published by `RBR-0291`; do not broaden into nested grouped backtracking-heavy flows, replacement workflows, deeper grouped execution, or stdlib delegation.
- Implement any new regex behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact nested grouped-conditional slice.

## Notes
- Build on `RBR-0291`.
- Leave Python-path benchmark catch-up to a follow-on task on `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.json`; do not fork a new benchmark family for this nested grouped-conditional slice.

## Completion Note
- Added a narrow Rust parser and matcher in `crates/rebar-core/src/lib.rs` for `a(((bc|de){1,4})d)?(?(1)e|f)` and `a(?P<outer>((bc|de){1,4})d)?(?(outer)e|f)`, including compile metadata, numbered and named group spans, and `lastindex` parity through the existing generic native compile/match path.
- Extended `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` with numbered and named nested grouped-conditional scenarios so the existing backend-parameterized wider-ranged-repeat parity suite now covers the absent `af` path, lower-bound `abcde`/`adede`, mixed `abcbcdede`, upper-bound `adedededede`, and no-match cases for `ae`, a missing conditional `e`, and a fifth grouped repetition overflow.
- Regenerated `reports/correctness/latest.json`; the combined correctness scorecard now reports 84 manifests, 757 total cases, 757 passes, 0 honest `unimplemented` outcomes, and 0 explicit failures.
- No dedicated `crates/rebar-cpython/src/lib.rs` or `python/rebar/__init__.py` patch was required because `boundary_compile` and `boundary_literal_match` already marshal compile metadata, group spans, and `lastindex` from the generic Rust core paths.
- Verified with `cargo build -p rebar-cpython`, `PYTHONPATH=python ./.venv/bin/python -m pytest tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py -q`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows.py --report .rebar/tmp-rbr-0293-single.json`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.json`, and `PYTHONPATH=python ./.venv/bin/python -m unittest tests.conformance.test_correctness_nested_broader_range_wider_ranged_repeat_quantified_group_alternation_conditional_workflows tests.conformance.test_wider_ranged_repeat_quantified_group_scorecards tests.conformance.test_combined_correctness_scorecards`.
