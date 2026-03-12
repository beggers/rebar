# RBR-0043: Add literal-only replacement-template and callable replacement parity

Status: done
Owner: implementation
Created: 2026-03-12

## Goal
- Convert the remaining published `module.sub()` workflow gaps that do not require grouped-pattern support from honest `unimplemented` outcomes into real CPython-shaped behavior for already-supported literal patterns.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_literal_replacement_variants.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- `rebar.sub()` stops returning `NotImplementedError` for the published workflow cases `module-sub-template-str` and `module-sub-callable-str`, and instead matches CPython for those exact literal-pattern cases.
- The new workflow semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object integration, and callable marshalling.
- The replacement-template slice covers the currently published whole-match template form (`\\g<0>x`) for a supported literal `str` pattern without implying grouped-pattern or general backreference-template support.
- The callable-replacement slice invokes the callable with a real `rebar.Match` object from the current literal-only engine and matches CPython for the published constant-return callable case.
- `reports/correctness/latest.json` flips `module-sub-template-str` and `module-sub-callable-str` from `unimplemented` to `pass`, while `module-sub-grouping-template` remains an honest gap until its dedicated follow-on task lands.

## Constraints
- Keep this task scoped to the already-published literal replacement-template and callable-replacement cases; do not broaden into grouped-pattern replacement templates, non-literal parsing, or stdlib delegation.
- Implement the new workflow behavior in Rust, not in ad hoc Python execution helpers.
- Preserve the current literal-only `sub`/`subn`, `Pattern`, and cache behavior outside these exact cases.
- Do not delegate replacement handling to stdlib `re`.

## Notes
- Build on `RBR-0029`, `RBR-0030`, and `RBR-0042A`. This task exists so the remaining published `sub()` workflow gaps are reduced as explicit Rust-backed compatibility work instead of staying indefinitely `unimplemented`.

## Completion
- 2026-03-12: Added bounded whole-match replacement-template support in `rebar-core` and exposed it through a new `rebar._rebar` template-substitution entrypoint, while keeping grouped-template forms honest gaps.
- 2026-03-12: Routed callable replacement parity through Rust-discovered spans plus Python-side callable marshalling so supported literal `sub()` and `subn()` calls now invoke callables with real `rebar.Match` objects and match CPython for the published constant-return case.
- 2026-03-12: Added direct parity coverage in `tests/python/test_literal_replacement_variants.py`, tightened the existing unsupported-template cache-mutation guard, updated the collection/replacement correctness expectations, and republished `reports/correctness/latest.json` to `80` cases with `75` pass / `5` unimplemented (`module-sub-template-str` and `module-sub-callable-str` now pass).
- 2026-03-12: Verification: `cargo test -p rebar-core -p rebar-cpython`; `python3 -m unittest tests.python.test_literal_replacement_helpers tests.python.test_literal_replacement_variants tests.conformance.test_correctness_collection_replacement_workflows`; `PYTHONPATH=python python3 -m rebar_harness.correctness --report reports/correctness/latest.json`.
