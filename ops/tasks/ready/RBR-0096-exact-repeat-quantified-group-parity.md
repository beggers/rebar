# RBR-0096: Add bounded exact-repeat quantified-group parity

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Convert the first bounded exact-repeat quantified-group cases from the published correctness pack into real CPython-shaped behavior without claiming ranged-repeat, quantified-alternation, conditional, or broad backtracking support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_exact_repeat_quantified_group_parity.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The exact-repeat quantified-group cases published by `RBR-0095` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for bounded module and compiled-`Pattern` `search()`/`match()`/`fullmatch()` flows.
- Any new exact-repeat quantified-group parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one exact `{2}` numbered or named capturing group inside literal prefix/suffix text is enough, including the observable group values exposed after the counted repetition completes, but ranged repeats, quantified alternation, replacement workflows, conditionals, nested quantified groups, capture-history beyond current `Match` APIs, and broader backtracking remain honest gaps until later tasks land.
- `reports/correctness/latest.json` flips the bounded exact-repeat quantified-group cases from `unimplemented` to `pass` without regressing the already-landed optional-group, nested-group, alternation, or backreference behavior.

## Constraints
- Keep this task scoped to the exact-repeat quantified-group cases published by `RBR-0095`; do not broaden into ranged repeats, quantified alternation, replacement workflows, conditionals, or stdlib delegation.
- Implement any new execution behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact counted-repeat slice.

## Notes
- Build on `RBR-0050`, `RBR-0078`, and `RBR-0095`.
- This task exists so the queue turns the first deterministic counted-repeat cases into real Rust-backed behavior instead of leaving that frontier as publication-only coverage.
