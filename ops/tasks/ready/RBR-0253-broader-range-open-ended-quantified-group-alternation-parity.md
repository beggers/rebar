# RBR-0253: Add broader-range open-ended quantified-group alternation parity

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Convert the first broader-range open-ended quantified-group alternation cases from the published correctness pack into real Rust-backed behavior without claiming broader grouped-conditionals, replacement workflows, or deeper grouped backtracking support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_broader_range_open_ended_quantified_group_alternation_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The broader-range open-ended quantified-group alternation cases published by `RBR-0252` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded compile, module, and compiled-`Pattern` workflows under test.
- Any new parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one open-ended `{2,}` envelope around one `bc|de` alternation site in `a(bc|de){2,}d` / `a(?P<word>bc|de){2,}d` is enough, including lower-bound successes, mixed-branch successes, one bounded fourth-repetition success, and explicit no-match observations like `abcd`, but broader grouped-conditionals, replacement workflows, and deeper grouped backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the broader-range open-ended quantified-group alternation cases from `unimplemented` to `pass` without regressing the already-landed open-ended grouped alternation slice or the grouped-conditional and grouped backtracking-heavy trios queued ahead of this task.

## Constraints
- Keep this task scoped to the cases published by `RBR-0252`; do not broaden into broader grouped-conditionals, replacement workflows, deeper grouped backtracking, or stdlib delegation.
- Implement any new regex behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact counted-repeat slice.

## Notes
- Build on `RBR-0252`.
- This task exists so the queue turns one exact broader-range open-ended grouped-alternation frontier into real Rust-backed behavior instead of leaving it as publication-only coverage.
