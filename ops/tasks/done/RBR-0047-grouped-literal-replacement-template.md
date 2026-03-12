# RBR-0047: Add narrow grouped-literal replacement-template parity

Status: done
Owner: implementation
Created: 2026-03-12

## Goal
- Convert the last published grouping-dependent `module.sub()` workflow gap from an honest `unimplemented` outcome into real CPython-shaped behavior without claiming broad grouped-pattern or backreference support.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_grouped_literal_replacement_template.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- `rebar.sub("(abc)", "\\1x", "abc")` stops returning `NotImplementedError` and instead matches CPython for the published case `module-sub-grouping-template`.
- The implementation only adds the narrow grouped-literal and replacement-template capability needed for that published case; it does not claim general grouping, nested captures, or arbitrary backreference-template support.
- The new workflow semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object integration, and replacement-result marshalling.
- `reports/correctness/latest.json` flips `module-sub-grouping-template` from `unimplemented` to `pass`.
- Any added capture metadata stays compatible with the existing `Pattern`/`Match` scaffolds and does not regress the current literal-only cache behavior.

## Constraints
- Keep this task scoped to the already-published grouped-literal replacement-template case only; do not broaden into general grouped-pattern parsing, capture semantics, or stdlib delegation.
- Implement the new workflow behavior in Rust, not in ad hoc Python execution helpers.
- Preserve the current literal-only helper behavior outside this exact case.
- Do not silently route grouped-template replacement through stdlib `re`.

## Notes
- Build on `RBR-0042A` and `RBR-0043`. This task exists so the last published replacement-template gap is worked off as a bounded Rust-backed follow-on rather than forcing a much broader grouping rewrite.

## Completion
- Completed 2026-03-12.
- Added a bounded Rust-backed grouped-literal compile/search/template-sub slice for a single outer capturing group around a literal body, wired `Pattern`/`Match` capture metadata through the Python surface, added focused grouped-template tests, updated the grouped-template correctness fixture metadata, and republished `reports/correctness/latest.json` at 80 passes / 0 failures / 0 unimplemented.
