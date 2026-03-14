# RBR-0276: Add broader-range wider ranged-repeat quantified-group alternation backtracking-heavy parity

Status: ready
Owner: feature-implementation
Created: 2026-03-14

## Goal
- Convert the broader `{1,4}` wider-ranged-repeat grouped backtracking-heavy cases published by `RBR-0275` into real Rust-backed behavior without widening into open-ended grouped-conditionals, replacement workflows, or broader grouped backtracking execution.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The broader `{1,4}` wider-ranged-repeat grouped backtracking-heavy cases published by `RBR-0275` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded compile, module, and compiled-`Pattern` workflows under test.
- Any new parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one bounded `{1,4}` envelope around one overlapping `(bc|b)c` site in `a((bc|b)c){1,4}d` / `a(?P<word>(bc|b)c){1,4}d` is enough, including lower-bound successes through both overlapping branches like `abcd` and `abccd`, mixed-branch and upper-bound successes like `abcbccd`, `abccbcd`, and one bounded fourth-repetition success, plus explicit no-match observations such as `abccbd` or a haystack whose fifth grouped repetition exceeds the bounded `{1,4}` envelope.
- `reports/correctness/latest.json` flips the broader `{1,4}` grouped backtracking-heavy cases from `unimplemented` to `pass` without regressing the already-landed broader `{1,4}` grouped-alternation and grouped-conditional slices or the earlier `{1,3}` grouped backtracking-heavy slice.
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` remains the single backend-parameterized parity suite for this wider-ranged-repeat grouped frontier; do not reintroduce a frontier-specific singleton parity module.

## Constraints
- Keep this task scoped to the cases published by `RBR-0275`; do not broaden into open-ended grouped-conditionals, replacement workflows, nested grouped conditionals, or stdlib delegation.
- Implement any new regex behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact grouped backtracking-heavy slice.
- Prefer extending the existing wider-ranged-repeat parity suite directly instead of adding new custom harness plumbing.

## Notes
- Build on `RBR-0275`.
- Keep the eventual benchmark catch-up on the existing `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.json` path rather than forking another benchmark family when this broader `{1,4}` grouped backtracking-heavy slice is later measured.
