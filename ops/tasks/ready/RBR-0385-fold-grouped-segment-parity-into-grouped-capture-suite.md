# RBR-0385: Fold grouped-segment parity into the grouped-capture suite

Status: ready
Owner: architecture-implementation
Created: 2026-03-15

## Goal
- Remove `tests/python/test_grouped_segment_parity.py` as a standalone parity surface by folding its bounded grouped-segment coverage into `tests/python/test_grouped_capture_parity_suite.py`, so the grouped-capture family no longer lives across two fixture-backed pytest modules with nearly identical compile, match, accessor, and miss scaffolding.

## Deliverables
- `tests/python/test_grouped_capture_parity_suite.py`
- Delete `tests/python/test_grouped_segment_parity.py`

## Acceptance Criteria
- `tests/python/test_grouped_capture_parity_suite.py` absorbs the grouped-segment manifest from `tests/conformance/fixtures/grouped_segment_workflows.py` instead of leaving that manifest on a separate parity module.
- The grouped-capture suite adds one explicit grouped-segment fixture bundle covering exactly these published case ids and no broader grouped frontier:
  - `grouped-segment-compile-metadata-str`
  - `grouped-segment-module-search-str`
  - `grouped-segment-pattern-fullmatch-str`
  - `named-grouped-segment-compile-metadata-str`
  - `named-grouped-segment-module-search-str`
  - `named-grouped-segment-pattern-fullmatch-str`
- The absorbed grouped-segment bundle keeps the current manifest-level contract explicit inside `tests/python/test_grouped_capture_parity_suite.py`:
  - manifest id `grouped-segment-workflows`
  - compile patterns `a(b)c` and `a(?P<word>b)c`
  - operation/helper counts `("compile", None): 2`, `("module_call", "search"): 2`, and `("pattern_call", "fullmatch"): 2`
- The grouped-capture suite preserves the grouped-segment parity depth currently asserted by `tests/python/test_grouped_segment_parity.py`:
  - compile metadata parity through `compile_with_cpython_parity(...)`
  - match-result parity for the published module and compiled-`Pattern` workflows
  - match convenience parity
  - valid and invalid match-group accessor parity for the numbered and named grouped-segment workflow rows
- The grouped-segment no-match coverage remains explicit after the fold, derived from the absorbed fixture case ids rather than a second standalone suite:
  - module-search misses stay covered for numbered and named grouped-segment rows with `zzz`
  - compiled-`Pattern.fullmatch()` misses stay covered for numbered and named grouped-segment rows with `abcz`
- No new helper module, registry, generated case layer, or duplicate fixture loader is introduced. Expand the existing grouped-capture suite directly.
- After the consolidation lands, `rg --files tests/python | rg 'test_grouped_segment_parity\\.py$'` returns no matches.

## Constraints
- Keep this task on the Python parity surface only. Do not change Rust code, `python/rebar/`, correctness fixtures, benchmark manifests, scorecards, README reporting, or tracked state files.
- Keep the grouped-segment rows on the grouped-capture family path. Do not split them into another family suite and do not broaden this cleanup into optional-group alternation, grouped replacement-template, or branch-local-backreference work.
- Reuse the existing backend-parameterized pytest flow and the existing grouped-capture suite structure instead of adding another abstraction layer.

## Notes
- Both tracked and live JSON counts are zero in the current checkout, so the next architecture priority is deleting duplicate Python parity plumbing rather than another JSON burn-down task.
- `tests/python/test_grouped_segment_parity.py` is still a 299-line singleton that repeats the same fixture bundle structure, compile path, `_match_for_case(...)` shape, accessor assertions, convenience-API checks, and bounded miss helpers that already exist in `tests/python/test_grouped_capture_parity_suite.py`.
- The grouped-capture suite is now the natural owner for this slice: it already carries grouped, named-group, optional-group, and nested-group capture coverage, and grouped-segment is the remaining single-capture literal-prefix/suffix holdout on a separate file.
