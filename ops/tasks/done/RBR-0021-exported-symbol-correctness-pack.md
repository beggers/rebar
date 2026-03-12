# RBR-0021: Expand correctness coverage across exported symbols

Status: done
Owner: implementation
Created: 2026-03-11
Completed: 2026-03-12

## Goal
- Extend the correctness harness so the published scorecard can measure exported flags, exceptions, and helper types once the `rebar` import surface grows beyond the first helper scaffold.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/exported_symbol_surface.json`
- `tests/conformance/test_correctness_exported_symbol_surface.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The correctness runner can execute an exported-symbol fixture pack alongside the existing parser and module-helper manifests.
- The new pack covers a bounded set of directly imported `re` symbols such as `RegexFlag`, `error`, `Pattern`, `Match`, and a representative constant subset, recording presence and observable value/type parity against stdlib `re` where that parity is already part of the public API.
- `reports/correctness/latest.json` adds exported-symbol coverage without hiding missing or placeholder symbols; absent names, wrong values, and scaffold-only contracts must remain explicit in the per-case results and scorecard summaries.
- A smoke or unit test regenerates the combined correctness report end to end and validates the expanded scorecard structure.

## Constraints
- Keep this task on import-surface correctness only; do not implement real matching, compiled-pattern behavior, or private `sre_*` compatibility here.
- Do not silently delegate missing symbols to stdlib `re`; the scorecard must continue to expose `rebar` gaps honestly.
- Reuse the exact-baseline metadata and existing multi-manifest scorecard layout rather than inventing a correctness-only schema branch.

## Notes
- Use `docs/spec/drop-in-re-compatibility.md` for which public `re` symbols matter and `docs/testing/correctness-plan.md` for scorecard/layer guidance.
- Build on `RBR-0014` and `RBR-0018`; this task should publish correctness coverage for the landed symbol surface instead of relying only on narrow unit tests.

## Completion Note
- Extended `python/rebar_harness/correctness.py` with `module_attr_value` and `module_attr_metadata` observations and added the exported-symbol manifest to the default correctness run so symbol coverage reaches the published scorecard.
- Added `tests/conformance/fixtures/exported_symbol_surface.json` plus `tests/conformance/test_correctness_exported_symbol_surface.py`, covering `RegexFlag`, `error`, `Pattern`, `Match`, representative flag constants, and the current non-instantiable helper-type guard behavior.
- Regenerated `reports/correctness/latest.json`; the combined report now covers 38 cases across parser, module-surface, match-behavior, and exported-symbol packs, with 12 passes, 5 explicit failures, and 21 honest unimplemented outcomes.
