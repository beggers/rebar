# RBR-0326: Add bounded nested-group-alternation-plus-branch-local-backreference parity

Status: ready
Owner: feature-implementation
Created: 2026-03-14

## Goal
- Convert the bounded nested-group-alternation-plus-branch-local-backreference cases from `RBR-0324` into real Rust-backed behavior without claiming quantified nested backreferences, broader counted repeats, replacement semantics, or deeper nested grouped execution.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_nested_group_alternation_branch_local_backreference_parity.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The exact numbered and named cases published by `RBR-0324` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded compile, `module.search()`, and compiled-`Pattern.fullmatch()` workflows under test.
- Any new parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one outer capture containing one inner literal alternation site immediately followed by one same-branch backreference in `a((b|c))\\2d` and `a(?P<outer>(?P<inner>b|c))(?P=inner)d` is enough, including numbered and named successes like `abbd` and `accd`, explicit no-match observations like `abd` or `acd`, and one named path that keeps both outer and inner captures observable, while quantified nested backreferences, broader counted repeats, replacement semantics, conditionals, and deeper nested grouped execution remain out of scope.
- `reports/correctness/latest.py` flips the bounded nested-group-alternation-plus-branch-local-backreference cases from `unimplemented` to `pass` without regressing the already-landed quantified nested-group alternation slice, the existing branch-local-backreference baselines, or the surrounding nested-group capture metadata surfaces.

## Constraints
- Keep this task scoped to the cases published by `RBR-0324`; do not broaden into quantified variants, replacement workflows, conditionals, or stdlib delegation.
- Implement any new regex behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact combined slice.

## Notes
- Build on `RBR-0324`, `RBR-0320`, and the existing bounded branch-local-backreference execution support.
- Keep later benchmark catch-up on the existing `benchmarks/workloads/nested_group_alternation_boundary.py` path, which already carries the `pattern-fullmatch-named-nested-group-branch-local-backreference-purged-gap` anchor.
