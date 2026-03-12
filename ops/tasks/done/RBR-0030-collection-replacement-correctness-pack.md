# RBR-0030: Publish correctness coverage for literal collection and replacement helpers

Status: done
Owner: implementation
Created: 2026-03-12
Completed: 2026-03-12

## Goal
- Extend the correctness harness so the first literal-only `split`/`findall`/`finditer`/`sub`/`subn` behavior reaches the published scorecard immediately after the helper implementations land.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/collection_replacement_workflows.json`
- `tests/conformance/test_correctness_collection_replacement_workflows.py`
- `reports/correctness/latest.json`

## Acceptance Criteria
- The correctness runner can execute a collection/replacement workflow manifest alongside the existing parser, public-API, exported-symbol, pattern-object, match-behavior, and module-workflow manifests.
- The new pack covers tiny literal-only module and `Pattern` flows for `split`, `findall`, `finditer`, `sub`, and `subn`, including representative no-match, repeated-match, leading/trailing split, bounded `maxsplit`, bounded replacement `count`, iterator exhaustion, and CPython-shaped `str`/`bytes` return values where the implementation supports them.
- `reports/correctness/latest.json` distinguishes the new helper-workflow cases from the earlier module-workflow pack, and it keeps unsupported replacement-template, callable-replacement, grouping-dependent, or non-literal paths explicit instead of counting them as passes.
- A smoke or unit test regenerates the combined correctness report end to end and validates the expanded scorecard structure.

## Constraints
- Keep this task on tiny literal-only collection/replacement workflows only; do not broaden into capture-group extraction, replacement-template parsing, or general regex-engine parity.
- Preserve the exact-baseline metadata and the existing multi-manifest scorecard shape rather than inventing a separate reporting branch.
- Do not delegate the helper workflows to stdlib `re`; the scorecard must continue to expose real `rebar` behavior and remaining gaps honestly.

## Notes
- Build on `RBR-0028` and `RBR-0029`; this task exists so the first honest collection/replacement slice becomes visible in the published correctness report immediately instead of living only in unit tests.
- Added `tests/conformance/fixtures/collection_replacement_workflows.json` with 15 collection/replacement workflow cases covering supported literal-only module and `Pattern` flows plus explicit template, callable, grouping-dependent, and non-literal gaps.
- Extended `python/rebar_harness/correctness.py` so the combined harness includes the new manifest by default, materializes `finditer()` results structurally with exhaustion state, and supports stable fixture-only callable replacements for correctness observations.
- Added `tests/conformance/test_correctness_collection_replacement_workflows.py` and regenerated `reports/correctness/latest.json`; the published combined report now covers 69 cases total, including a 15-case `collection-replacement-workflows` pack and 4 honest `unimplemented` helper-gap cases.
