# RBR-0394: Fold literal-alternation parity into the quantified alternation pytest suite

Status: ready
Owner: architecture-implementation
Created: 2026-03-15

## Goal
- Remove `tests/python/test_literal_alternation_parity.py` as a standalone parity surface by folding its bounded literal-alternation coverage into `tests/python/test_quantified_alternation_parity_suite.py`, so the alternation frontier no longer keeps this earliest top-level branch-selection slice on a second legacy `unittest` wrapper.

## Deliverables
- `tests/python/test_quantified_alternation_parity_suite.py`
- Delete `tests/python/test_literal_alternation_parity.py`

## Acceptance Criteria
- `tests/python/test_quantified_alternation_parity_suite.py` absorbs `tests/conformance/fixtures/literal_alternation_workflows.py` through the module's existing fixture-backed pytest path instead of leaving literal alternation on a separate `unittest` module.
- The quantified alternation parity suite keeps the absorbed literal-alternation fixture explicit by adding one manifest-alignment bundle covering exactly this published contract and no broader literal-only frontier:
  - manifest id `literal-alternation-workflows`
  - case ids:
    - `literal-alternation-compile-metadata-str`
    - `literal-alternation-module-search-str`
    - `literal-alternation-pattern-fullmatch-str`
  - compile patterns:
    - `ab|ac`
  - operation/helper counts:
    - `("compile", None): 1`
    - `("module_call", "search"): 1`
    - `("pattern_call", "fullmatch"): 1`
- The absorbed literal-alternation rows reuse the quantified alternation suite's existing shared pytest flow rather than another local helper, so this slice now receives:
  - compile metadata parity through the same `regex_backend` path already used by `tests/python/test_quantified_alternation_parity_suite.py`
  - direct module `search()` parity for the published literal-alternation workflow row
  - direct compiled-`Pattern` `fullmatch()` parity for the published literal-alternation workflow row
  - shared match convenience API parity through the suite's existing `assert_match_convenience_api_parity(...)` path for the module and pattern match cases
- The consolidation preserves the current quantified alternation, exact-repeat grouped alternation, quantified nested-group alternation, backtracking-heavy alternation, broader-range alternation, quantified-alternation-plus-conditional, open-ended alternation, and nested-branch alternation coverage already anchored in `tests/python/test_quantified_alternation_parity_suite.py`; do not silently narrow that existing family coverage while absorbing the literal slice.
- No new suite, support module, manifest registry, or generated case layer is introduced. Expand the existing quantified alternation pytest module directly.
- After the consolidation lands, `rg --files tests/python | rg 'test_literal_alternation_parity\\.py$'` returns no matches.
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py`.

## Constraints
- Keep this task on the Python parity surface only. Do not change Rust code, `python/rebar/`, correctness fixture contents, benchmark manifests, published reports, README reporting, or tracked state files beyond this task file.
- Keep the literal-alternation rows on the existing quantified alternation family path. Do not create a second alternation suite and do not broaden this cleanup into grouped alternation, benchmark catch-up, or new feature work.
- Reuse the existing helpers already in the repo, especially `load_fixture_manifest(...)`, `FixtureCase`, `compile_with_cpython_parity(...)`, `assert_match_parity(...)`, `assert_match_convenience_api_parity(...)`, and the backend-parameterized `regex_backend` fixture, instead of adding another fixture loader or file-local parity harness.

## Notes
- Both tracked and live JSON counts are zero in the current checkout (`tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, `git ls-files '*.json' | wc -l = 0`, `rg --files -g '*.json' | wc -l = 0`), so the next architecture priority is deleting duplicate Python parity plumbing rather than another JSON burn-down task.
- `tests/python/test_literal_alternation_parity.py` is still an 81-line standalone `unittest` module with private `sys.path` bootstrapping, manual `rebar.purge()` setup/teardown, and a file-local match helper that restates the exact three workflows already published in `tests/conformance/fixtures/literal_alternation_workflows.py`.
- `tests/python/test_quantified_alternation_parity_suite.py` already owns the adjacent alternation family through a shared fixture-backed pytest path, making it the natural home for this remaining literal-alternation wrapper.
