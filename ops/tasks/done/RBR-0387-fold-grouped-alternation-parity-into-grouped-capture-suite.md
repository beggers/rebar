# RBR-0387: Fold grouped-alternation parity into the grouped-capture suite

Status: done
Owner: architecture-implementation
Created: 2026-03-15

## Goal
- Remove `tests/python/test_grouped_alternation_parity.py` as a standalone parity surface by folding its bounded grouped-alternation coverage into `tests/python/test_grouped_capture_parity_suite.py`, so the top-level grouped-capture family no longer keeps this literal-prefix/suffix alternation slice on an older unittest-only path with private import bootstrapping and file-local parity helpers.

## Deliverables
- `tests/python/test_grouped_capture_parity_suite.py`
- Delete `tests/python/test_grouped_alternation_parity.py`

## Acceptance Criteria
- `tests/python/test_grouped_capture_parity_suite.py` absorbs `tests/conformance/fixtures/grouped_alternation_workflows.py` through the suite's existing fixture-backed path instead of leaving grouped alternation on a separate unittest module.
- The grouped-capture suite keeps the absorbed grouped-alternation fixture explicit by adding one bundle covering exactly these published case ids and no broader alternation frontier:
  - `grouped-alternation-compile-metadata-str`
  - `grouped-alternation-module-search-str`
  - `grouped-alternation-pattern-fullmatch-str`
  - `named-grouped-alternation-compile-metadata-str`
  - `named-grouped-alternation-module-search-str`
  - `named-grouped-alternation-pattern-fullmatch-str`
- The absorbed grouped-alternation bundle keeps the current manifest contract explicit inside `tests/python/test_grouped_capture_parity_suite.py`:
  - manifest id `grouped-alternation-workflows`
  - compile patterns `a(b|c)d` and `a(?P<word>b|c)d`
  - operation/helper counts `("compile", None): 2`, `("module_call", "search"): 2`, and `("pattern_call", "fullmatch"): 2`
- The grouped-capture suite exercises the absorbed grouped-alternation rows through its existing shared pytest flow rather than new file-local assertions, so this slice now receives:
  - compile metadata parity through `compile_with_cpython_parity(...)`
  - match-result parity for the published module and compiled-`Pattern` workflows
  - match convenience parity
  - valid and invalid match-group accessor parity for the numbered and named grouped-alternation workflow rows
- Any grouped-alternation no-match checks that stay after the fold live on `tests/python/test_grouped_capture_parity_suite.py` via the suite's existing supplemental miss path rather than a new helper block or a second wrapper file.
- No new suite, manifest registry, support module, or generated case layer is introduced. Expand the existing grouped-capture suite directly.
- After the consolidation lands, `rg --files tests/python | rg 'test_grouped_alternation_parity\\.py$'` returns no matches.
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py`.

## Constraints
- Keep this task on the Python parity surface only. Do not change Rust code, `python/rebar/`, correctness fixture contents, benchmark manifests, published reports, README reporting, or tracked state files beyond this task file.
- Keep the grouped-alternation rows on the grouped-capture family path. Do not create a separate grouped-alternation suite and do not broaden this cleanup into optional-group alternation, nested-group alternation, replacement-template, callable-replacement, or branch-local-backreference work.
- Reuse the existing backend-parameterized pytest flow and `tests/python/fixture_parity_support.py` helpers instead of adding another abstraction layer.

## Notes
- Both tracked and live JSON counts are zero in the current checkout, so the next architecture priority is deleting duplicate Python parity plumbing rather than another JSON burn-down task.
- `tests/python/test_grouped_alternation_parity.py` is still a 109-line standalone unittest module with local `sys.path` bootstrapping, manual `setUp`/`tearDown` cache purges, and a private match-parity helper for a six-case published fixture slice that already fits the grouped-capture suite's compile/match/access/convenience structure.
- `tests/python/test_grouped_capture_parity_suite.py` already owns the adjacent grouped, named-group, grouped-segment, optional-group, and nested-group capture rows through the shared fixture-backed harness, making it the natural home for this remaining top-level grouped alternation wrapper.

## Completion
- Completed 2026-03-15.
- Folded `grouped_alternation_workflows.py` into `tests/python/test_grouped_capture_parity_suite.py` as one explicit six-case bundle, extended the suite's existing match-group accessor coverage to the numbered and named grouped-alternation search/fullmatch rows, and added grouped-alternation no-match checks through the suite's existing supplemental miss path.
- Deleted `tests/python/test_grouped_alternation_parity.py`.
- Verified with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py` (`260 passed`) and `rg --files tests/python | rg 'test_grouped_alternation_parity\\.py$'` (no matches).
