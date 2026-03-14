# RBR-0332: Add quantified nested-group-alternation-plus-branch-local-backreference parity

Status: ready
Owner: feature-implementation
Created: 2026-03-14

## Goal
- Convert the bounded quantified nested-group-alternation-plus-branch-local-backreference cases from `RBR-0330` into real Rust-backed behavior without claiming broader counted repeats, replacement semantics, conditionals, or deeper nested grouped execution.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_quantified_nested_group_alternation_branch_local_backreference_parity.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The exact numbered and named cases published by `RBR-0330` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded compile, `module.search()`, and compiled-`Pattern.fullmatch()` workflows under test.
- Any new parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one outer capture containing one `+`-quantified inner alternation site immediately replayed by one same-branch backreference in `a((b|c)+)\\2d` and `a(?P<outer>(?P<inner>b|c)+)(?P=inner)d` is enough, including lower-bound same-branch successes like `abbd` and `accd`, repeated-branch successes like `abbbd`, `abccd`, or `acbbd`, explicit no-match observations like `abcd` or `acbd`, and one named path that keeps the quantified outer capture plus final inner branch observable under repetition, while broader counted repeats, replacement semantics, conditionals, and deeper nested grouped execution remain out of scope.
- `reports/correctness/latest.py` flips the bounded quantified nested-group-alternation-plus-branch-local-backreference cases from `unimplemented` to `pass` without regressing the already-landed quantified nested-group alternation slice, the existing nested-group-alternation-plus-branch-local-backreference slice, or the surrounding nested-group capture and branch-local-backreference surfaces.

## Constraints
- Keep this task scoped to the cases published by `RBR-0330`; do not broaden into `{1,4}` or `{1,}` counted repeats, replacement workflows, conditional combinations, or stdlib delegation.
- Implement any new regex behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact combined slice.

## Notes
- Build on `RBR-0330`, `RBR-0326`, and `RBR-0208`.
- Keep later benchmark catch-up on the existing `benchmarks/workloads/nested_group_alternation_boundary.py` path instead of forking another benchmark family for the same bounded nested-group alternation frontier.
