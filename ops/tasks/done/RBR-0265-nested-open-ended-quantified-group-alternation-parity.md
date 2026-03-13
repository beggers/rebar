# RBR-0265: Add nested open-ended quantified-group alternation parity

Status: done
Owner: feature-implementation
Created: 2026-03-13

## Goal
- Convert the nested open-ended quantified-group alternation cases published by `RBR-0264` from documented gaps into real Rust-backed behavior without widening into broader counted ranges, grouped conditionals, replacement workflows, or deeper grouped execution.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_open_ended_quantified_group_parity_suite.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The nested open-ended quantified-group alternation cases published by `RBR-0264` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded compile, module, and compiled-`Pattern` workflows under test.
- Any new parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one outer capture around one open-ended `(bc|de){1,}` site in `a((bc|de){1,})d` / `a(?P<outer>(bc|de){1,})d` is enough, including lower-bound successes like `abcd` and `aded`, repeated and mixed-branch successes like `abcbcded` and `adededed`, and explicit no-match observations like `ae` or a haystack whose grouped repetition does not satisfy the trailing `d`.
- The existing backend-parameterized pytest parity suite absorbs this slice instead of reintroducing a standalone frontier-specific parity module.
- `reports/correctness/latest.json` flips the nested open-ended quantified-group alternation cases from `unimplemented` to `pass` without regressing the already-landed grouped `{1,}` and `{2,}` alternation, grouped-conditional, and grouped backtracking slices covered by the consolidated parity suite.

## Constraints
- Keep this task scoped to the cases published by `RBR-0264`; do not broaden into broader counted ranges like `{1,4}`, grouped conditionals, replacement workflows, deeper grouped backtracking, or stdlib delegation.
- Implement any new regex behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact nested grouped `{1,}` slice.

## Notes
- Build on `RBR-0264`.
- Keep the later benchmark catch-up for this slice anchored to the existing `pattern-fullmatch-numbered-wider-ranged-repeat-group-open-ended-purged-gap` row in `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.json`; do not fork a new benchmark family for the same bounded nested open-ended grouped-alternation workflows.

## Completion
- Added Rust-backed compile/match support for `a((bc|de){1,})d` and `a(?P<outer>(bc|de){1,})d`, including outer/inner capture spans and CPython-aligned `lastindex`.
- Folded the new numbered/named cases into the consolidated `tests/python/test_open_ended_quantified_group_parity_suite.py`.
- Republished `reports/correctness/latest.json`; the combined scorecard now reports `691` passes, `0` failures, and `0` `unimplemented` cases.
