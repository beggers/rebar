# RBR-0344: Add bounded nested-group alternation callable-replacement parity

Status: ready
Owner: feature-implementation
Created: 2026-03-14

## Goal
- Convert the bounded nested-group alternation callable-replacement cases from `RBR-0342` into real Rust-backed behavior without claiming quantified nested alternation callbacks, branch-local-backreference callbacks, broader counted repeats, or deeper nested grouped execution.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_nested_group_alternation_callable_replacement_parity.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The exact numbered and named cases published by `RBR-0342` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded module and compiled-`Pattern` `sub()` and `subn()` callable-replacement workflows under test.
- Any new parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, callable marshalling, and native result marshalling.
- The supported slice remains intentionally narrow: one outer capture containing one inner literal alternation site feeding callable replacements in `a((b|c))d` and `a(?P<outer>(?P<inner>b|c))d` is enough, including a numbered `b`-branch callback path such as `abd`, a mixed-haystack path such as `abdacd` or `acdabd`, a named `c`-branch callback path, and one count-limited or first-match-only case that keeps the outer capture plus final inner branch observable, while quantified nested alternation callbacks, branch-local-backreference callbacks, broader counted repeats, replacement-template variants, broader callback semantics, and deeper nested grouped execution remain out of scope.
- `reports/correctness/latest.py` flips the bounded nested-group alternation callable-replacement cases from `unimplemented` to `pass` without regressing the already-landed nested-group callable-replacement slice, nested-group alternation slice, or the surrounding callable-replacement and capture-metadata surfaces.

## Constraints
- Keep this task scoped to the cases published by `RBR-0342`; do not broaden into quantified variants, branch-local backreferences, replacement-template workflows, deeper nesting, or stdlib delegation.
- Implement any new regex behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` and callable-replacement contracts outside this exact combined slice.

## Notes
- Build on `RBR-0342`, `RBR-0313`, and `RBR-0320`.
- Keep later benchmark catch-up on the existing `benchmarks/workloads/nested_group_callable_replacement_boundary.py` path, which already carries the `module-sub-callable-nested-group-alternation-cold-gap` anchor.
