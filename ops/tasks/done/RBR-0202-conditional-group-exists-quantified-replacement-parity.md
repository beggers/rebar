# RBR-0202: Add bounded quantified two-arm conditional replacement parity

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Convert the first quantified conditional replacement cases from the published correctness pack into real Rust-backed behavior without claiming broader quantified or backtracking-heavy replacement execution.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_conditional_group_exists_quantified_replacement_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact quantified conditional replacement cases published by `RBR-0201` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded `sub()` and `subn()` workflows under test.
- Module and compiled-`Pattern` flows both consume Rust-backed quantified conditional replacement behavior rather than ad hoc Python-only regex semantics; Python changes stay limited to wrapper construction, cache/object plumbing, replacement marshalling, and native result marshalling.
- The supported slice remains intentionally narrow: one exact-repeat `{2}` quantifier over the accepted two-arm conditional `a(b)?c(?(1)d|e){2}` / `a(?P<word>b)?c(?(word)d|e){2}` is enough, but replacement templates that read captures, callable replacement semantics, alternation-heavy repeated arms, nested conditionals inside the repeated site, ranged/open-ended repeats, branch-local backreferences, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded quantified conditional replacement cases from `unimplemented` to `pass` without regressing the already-landed quantified conditional search/fullmatch baseline, the already-landed two-arm conditional replacement baseline, or the existing replacement-helper workflows.

## Constraints
- Keep this task scoped to the quantified conditional replacement cases published by `RBR-0201`; do not broaden into nested quantified conditionals, alternation-heavy repeated arms, replacement-template expansion, callable replacement semantics, ranged/open-ended repeats, or stdlib delegation.
- Any new regex behavior must live behind `rebar._rebar`; `python/rebar/__init__.py` stays limited to export, wrapper, cache, and FFI responsibilities.
- Preserve the current `Pattern`/`Match` contracts outside this exact quantified conditional replacement slice.

## Notes
- Build on `RBR-0201`, `RBR-0149`, and `RBR-0193`.
- This task exists so the queue converts the first quantified conditional replacement workflow into real Rust-backed behavior instead of leaving it as publication-only coverage.

## Completion
- Added a bounded quantified two-arm conditional replacement span collector in `rebar-core` and routed `rebar._rebar` constant `sub()` / `subn()` calls through it, keeping the supported slice pinned to `a(b)?c(?(1)d|e){2}` and `a(?P<word>b)?c(?(word)d|e){2}`.
- Added direct Python parity coverage in `tests/python/test_conditional_group_exists_quantified_replacement_parity.py` and refreshed the quantified-replacement correctness harness expectations for the now fully passing combined scorecard.
- Republished `reports/correctness/latest.json` with the combined 448-case / 60-manifest scorecard now at 448 passes, 0 failures, and 0 honest gaps.
