# RBR-0208: Add bounded quantified branch-local-backreference parity

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Convert the first quantified branch-local-backreference cases from the published correctness pack into real Rust-backed behavior without claiming conditional combinations, replacement semantics, or broader backtracking-heavy grouped execution.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_quantified_branch_local_backreference_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact quantified branch-local-backreference cases published by `RBR-0207` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded module and compiled-`Pattern` workflows under test.
- Any new parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one `+`-quantified inner capture inside one alternation branch followed by one later backreference in `a((b)+|c)\\2d` / `a(?P<outer>(?P<inner>b)+|c)(?P=inner)d` is enough, including the successful `abbd` and `abbbd` paths plus the explicit no-match `c`-branch observations, but conditionals, replacement workflows, callable replacement semantics, nested alternations, wider quantified shapes, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded quantified branch-local-backreference cases from `unimplemented` to `pass` without regressing the already-landed branch-local backreference baseline, the existing quantified-group baseline, or the conditional-plus-branch-local-backreference slice.

## Constraints
- Keep this task scoped to the cases published by `RBR-0207`; do not broaden into conditional combinations, replacement workflows, wider quantified shapes, or stdlib delegation.
- Implement any new regex behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact combined slice.

## Notes
- Build on `RBR-0207`.
- This task exists so the queue turns the first bounded quantified branch-local-backreference workflows into real Rust-backed behavior instead of leaving them as publication-only coverage.
