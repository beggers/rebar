# RBR-0211: Add bounded optional-group-alternation-plus-branch-local-backreference parity

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Convert the first optional-group-alternation-plus-branch-local-backreference cases from the published correctness pack into real Rust-backed behavior without claiming broader counted-repeat, replacement, or backtracking-heavy grouped execution.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_optional_group_alternation_branch_local_backreference_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact optional-group-alternation-plus-branch-local-backreference cases published by `RBR-0210` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded compile, module, and compiled-`Pattern` workflows under test.
- Any new parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one optional group containing one literal alternation followed by one same-branch backreference in `a((b|c)\\2)?d` / `a(?P<outer>(?P<inner>b|c)(?P=inner))?d` is enough, including absent-group successes, present-branch successes, and the explicit `abd`/`acd` no-match observations, but counted repeats beyond `?`, replacement workflows, conditionals, nested alternations, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded optional-group-alternation-plus-branch-local-backreference cases from `unimplemented` to `pass` without regressing the already-landed optional-group alternation baseline, the already-landed branch-local backreference baseline, or the bounded quantified branch-local-backreference slice.

## Constraints
- Keep this task scoped to the cases published by `RBR-0210`; do not broaden into counted repeats beyond `?`, replacement workflows, conditional combinations, or stdlib delegation.
- Implement any new regex behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact combined slice.

## Notes
- Build on `RBR-0210`.
- This task exists so the queue turns the first bounded optional-group-alternation-plus-branch-local-backreference workflows into real Rust-backed behavior instead of leaving them as publication-only coverage.
- Completed 2026-03-13: added bounded Rust compile/match support for `a((b|c)\\2)?d` and `a(?P<outer>(?P<inner>b|c)(?P=inner))?d`, added focused parity coverage, corrected the task-local conformance expectations to match CPython span offsets, and republished `reports/correctness/latest.json` to 472 passes / 0 unimplemented.
