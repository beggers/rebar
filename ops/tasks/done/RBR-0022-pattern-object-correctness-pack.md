# RBR-0022: Expand correctness coverage across compiled pattern scaffolds

Status: done
Owner: implementation
Created: 2026-03-11

## Goal
- Extend the correctness harness so the published scorecard can observe the first compiled `Pattern` scaffold returned by `rebar.compile()` and the placeholder behavior attached to that object.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/pattern_object_surface.json`
- `tests/conformance/test_correctness_pattern_object_surface.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The correctness runner can execute a compiled-pattern fixture pack alongside the existing parser, module-helper, and any exported-symbol manifests.
- The new pack covers the narrow observable `Pattern` scaffold contract from `RBR-0019`, including `compile()` return behavior, `Pattern` type identity, early attributes such as `.pattern`, `.flags`, `.groups`, and `.groupindex`, and the loud placeholder contract for first-reached methods like `search`, `match`, and `fullmatch`.
- `reports/correctness/latest.json` reports compiled-pattern cases separately enough that pattern-object progress is distinguishable from module-level helper coverage, and it does not count placeholder `NotImplementedError` paths as compatibility passes.
- A smoke or unit test regenerates the combined correctness report end to end and validates the expanded scorecard structure.

## Constraints
- Do not implement real parser, engine, replacement, or `Match`-object semantics in this task.
- Keep the observable scaffold narrow and honest; the goal is scorecard visibility for the landed placeholder contract, not fabricated compatibility wins.
- Do not reopen private `sre_*` APIs here; stay on the public `Pattern` surface only.

## Notes
- Use `docs/testing/correctness-plan.md` for Layer 2/3 scoring guidance and `docs/spec/drop-in-re-compatibility.md` for the near-term compiled-pattern contract.
- Build on `RBR-0019`; this task should turn the new `Pattern` scaffold into published correctness coverage as soon as the object exists.

## Completion
- Added `pattern_metadata` and `pattern_call` observation modes to the correctness harness so compiled pattern attributes and bound method placeholder behavior can be scored without claiming compatibility wins.
- Added `tests/conformance/fixtures/pattern_object_surface.json` plus an end-to-end conformance test, and regenerated `reports/correctness/latest.json` with a distinct `pattern_object_parity` layer.
- Refreshed stale parser conformance expectations so the tracked correctness suite reflects the already-landed literal scaffold compile passes from `RBR-0019`.
