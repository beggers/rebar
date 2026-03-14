# RBR-0338: Add nested broader-range wider-ranged-repeat quantified-group alternation plus branch-local-backreference parity

Status: ready
Owner: feature-implementation
Created: 2026-03-14

## Goal
- Convert the bounded broader `{1,4}` counted-repeat nested-group-alternation-plus-branch-local-backreference cases published by `RBR-0336` into real Rust-backed behavior without widening into open-ended counted repeats, replacement workflows, conditionals, or deeper nested grouped execution.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_quantified_nested_group_alternation_branch_local_backreference_parity.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The exact broader `{1,4}` counted-repeat nested-group-alternation-plus-branch-local-backreference cases published by `RBR-0336` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded compile, `module.search()`, and compiled-`Pattern.fullmatch()` workflows.
- Any new parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one outer capture containing one broader `{1,4}` `(b|c)` site immediately replayed by one same-branch backreference in `a((b|c){1,4})\\2d` and `a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d` is enough, including lower-bound same-branch successes such as `abbd` and `accd`, broader counted-repeat successes such as `abbbd` and `abcbccd`, plus explicit no-match observations such as `abcd`, `abcbcd`, or a fifth-repetition overflow that proves the `{1,4}` envelope stays bounded.
- `reports/correctness/latest.py` flips the newly published broader `{1,4}` counted-repeat nested-group-alternation-plus-branch-local-backreference cases from `unimplemented` to `pass` without regressing the already-landed quantified nested-group-alternation-plus-branch-local-backreference slice, the adjacent broader `{1,4}` nested grouped-alternation slice, or the surrounding nested-group alternation and branch-local-backreference surfaces.

## Constraints
- Keep this task scoped to the cases published by `RBR-0336`; do not broaden into open-ended counted repeats, replacement workflows, conditionals, deeper nested grouped execution, or stdlib delegation.
- Implement any new regex behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact broader `{1,4}` counted-repeat nested-group-alternation-plus-branch-local-backreference slice.
- Prefer extending the existing nested-group alternation branch-local-backreference parity coverage directly instead of adding new custom harness plumbing.

## Notes
- Build on `RBR-0336`, `RBR-0332`, and `RBR-0287`.
- Leave Python-path benchmark catch-up to a follow-on task on `benchmarks/workloads/nested_group_alternation_boundary.py`; do not fork a new benchmark family for this bounded broader `{1,4}` nested branch-local-backreference slice.
