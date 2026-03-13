# RBR-0271: Add broader-range wider ranged-repeat quantified-group alternation plus conditional parity

Status: ready
Owner: feature-implementation
Created: 2026-03-13

## Goal
- Convert the broader `{1,4}` wider-ranged-repeat quantified-group alternation plus conditional cases published by `RBR-0270` into real Rust-backed behavior without widening into grouped backtracking-heavy flows, open-ended grouped-conditionals, replacement workflows, or broader counted-repeat execution.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_alternation_conditional_broader_range_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The broader `{1,4}` wider-ranged-repeat grouped-alternation-plus-conditional cases published by `RBR-0270` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded compile, module, and compiled-`Pattern` workflows under test.
- Any new parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one optional outer capture around `(bc|de){1,4}` followed by `(?(1)d|e)` / `(?(outer)d|e)` is enough, including absent-group `else` behavior like `ae`, lower-bound present-group hits like `abcd` and `aded`, mixed and upper-bound present-group hits like `abcbcded` and `abcdededed`, plus explicit no-match observations like `ad`, a present-group branch that omits the required trailing `d`, and a haystack whose fifth grouped repetition exceeds the bounded `{1,4}` envelope.
- `reports/correctness/latest.json` flips the fourteen broader `{1,4}` grouped-alternation-plus-conditional cases from `unimplemented` to `pass` without regressing the already-landed broader `{1,4}` grouped-alternation slice, the earlier `{1,3}` grouped-conditional slice, or the open-ended grouped frontiers that precede this task.

## Constraints
- Keep this task scoped to the cases published by `RBR-0270`; do not broaden into grouped backtracking-heavy flows, open-ended grouped-conditionals, replacement workflows, or stdlib delegation.
- Implement any new regex behavior in Rust, not in ad hoc Python helpers.
- Prefer extending the existing Python-path parity surface directly instead of adding new custom harness plumbing.

## Notes
- Build on `RBR-0270`.
- Leave Python-path benchmark catch-up to the follow-on task on the existing `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.json` path instead of forking another benchmark family for this broader `{1,4}` grouped-conditional slice.
