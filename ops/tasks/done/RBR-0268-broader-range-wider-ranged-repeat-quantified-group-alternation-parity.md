# RBR-0268: Add broader-range wider-ranged-repeat quantified-group alternation parity

Status: done
Owner: feature-implementation
Created: 2026-03-13

## Goal
- Convert the broader `{1,4}` wider-ranged-repeat quantified-group alternation cases published by `RBR-0267` into real Rust-backed behavior without widening into grouped conditionals, grouped backtracking-heavy flows, open-ended repeats, or replacement workflows.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_alternation_broader_range_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The broader-range wider-ranged-repeat quantified-group alternation cases published by `RBR-0267` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded compile, module, and compiled-`Pattern` workflows under test.
- Any new parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one bounded `{1,4}` envelope around one `bc|de` alternation site in `a(bc|de){1,4}d` / `a(?P<word>bc|de){1,4}d` is enough, including lower-bound successes such as `abcd` and `aded`, mixed and upper-bound successes such as `abcbcded`, `adedededed`, and `abcbcdeded`, plus explicit no-match observations like `ad` and fifth-repetition overflow haystacks.
- `reports/correctness/latest.json` flips the ten broader `{1,4}` grouped-alternation cases from `unimplemented` to `pass` without regressing the already-landed `{1,3}` wider-ranged-repeat grouped alternation slice, the grouped `{1,}` slice, or the broader `{2,}` grouped frontier that precedes this task.

## Constraints
- Keep this task scoped to the cases published by `RBR-0267`; do not broaden into grouped conditionals, grouped backtracking-heavy flows, open-ended repeats, replacement workflows, or stdlib delegation.
- Implement any new regex behavior in Rust, not in ad hoc Python helpers.
- Prefer extending the existing Python-path parity surface directly instead of adding new custom harness plumbing.

## Notes
- Build on `RBR-0267`.
- Leave benchmark publication to the follow-on task after parity lands, anchored to the existing `module-search-numbered-wider-ranged-repeat-group-broader-range-cold-gap` row in `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.json`.

## Completion
- 2026-03-13: Extended the existing Rust quantified-alternation parser/executor path to accept the bounded `a(bc|de){1,4}d` / `a(?P<word>bc|de){1,4}d` slice, added focused Rust and Python parity coverage, and republished `reports/correctness/latest.json` so the ten broader `{1,4}` grouped-alternation cases now pass instead of reporting `unimplemented`.
