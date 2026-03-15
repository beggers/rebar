# RBR-0381: Fold quantified-alternation backtracking-heavy parity into the existing quantified suite

Status: ready
Owner: architecture-implementation
Created: 2026-03-15

## Goal
- Delete the standalone `tests/python/test_quantified_alternation_backtracking_heavy_parity.py` wrapper by moving its published fixture coverage and bounded supplemental trace checks onto `tests/python/test_quantified_alternation_parity_suite.py`, so the quantified-alternation parity frontier lives on one legible fixture-backed pytest path instead of two near-duplicate modules.

## Deliverables
- `tests/python/test_quantified_alternation_parity_suite.py`
- Delete `tests/python/test_quantified_alternation_backtracking_heavy_parity.py`

## Acceptance Criteria
- `tests/python/test_quantified_alternation_parity_suite.py` expands its quantified-alternation fixture inventory to include `tests/conformance/fixtures/quantified_alternation_backtracking_heavy_workflows.py` alongside the six manifests it already owns, rather than leaving that backtracking-heavy slice on a second standalone pytest module.
- The shared suite keeps one manifest-alignment assertion for the added backtracking-heavy fixture that pins:
- manifest id `quantified-alternation-backtracking-heavy-workflows`
- the exact published case-id set from `tests/conformance/fixtures/quantified_alternation_backtracking_heavy_workflows.py`
- pattern set `a(b|bc){1,2}d` and `a(?P<word>b|bc){1,2}d`
- operation/helper counts `("compile", None): 2`, `("module_call", "search"): 2`, and `("pattern_call", "fullmatch"): 8`
- The fold preserves the current published compile and workflow parity depth for this bounded overlapping-branch slice: compile identity plus `.pattern`, `.flags`, `.groups`, and `.groupindex`, then module `search()` and compiled-`Pattern.fullmatch()` result parity for the exact published lower-bound, mixed-order, repeated-branch, and explicit `abccd` no-match rows.
- The fold also preserves the current bounded supplemental coverage that is not represented by ordinary fixture rows, but keeps it local to the shared quantified suite instead of another file:
- exhaustive successful branch-order traces for every one- and two-repetition `b`/`bc` ordering on both numbered and named patterns for both module `search()` and compiled `Pattern.fullmatch()`
- the extra no-match paths for zero repetitions (`ad`) plus the search-wrapped overlap-tail miss, derived only from the fixture-backed compile patterns and the small short/long branch-text map
- Reuse `tests/python/fixture_parity_support.py` and the existing quantified-suite fixture-loading path instead of copying the standalone file’s `_case_pattern`, `_assert_pattern_parity`, `_assert_match_parity`, repo bootstrap, or backend wrapper logic into a second place. If helper extraction is needed, extend `tests/python/fixture_parity_support.py` only with generic support; do not add another dedicated module.
- The refactor preserves the current compile/module/pattern/convenience coverage already present in `tests/python/test_quantified_alternation_parity_suite.py`; this task only adds the backtracking-heavy manifest plus its bounded supplemental cases and deletes the duplicate wrapper.
- After the fold, `rg --files tests/python | rg 'test_quantified_alternation_backtracking_heavy_parity\\.py$'` returns no matches.
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py`.

## Constraints
- Keep this task on the Python parity surface only. Do not change Rust code, `python/rebar/`, correctness fixtures, benchmark manifests, published reports, README reporting, or tracked state files beyond this task file.
- Do not create another quantified-alternation helper layer or a second suite file. The point is to reduce file-level duplication by keeping this family on one existing fixture-backed suite.
- Keep the supplemental branch-trace and miss assertions bounded to the current `{1,2}` overlapping-branch slice; do not broaden into wider counted ranges, open-ended repeats, conditionals, backreferences, or other quantified frontiers.

## Notes
- `tests/python/test_quantified_alternation_parity_suite.py` already owns the rest of the quantified-alternation family, and `tests/python/test_quantified_alternation_backtracking_heavy_parity.py` is the remaining adjacent holdout still carrying another fixture load, compile helper, and match-parity block for the same family shape.
- Build on `RBR-0351`, `RBR-0353`, and `RBR-0369`: the fixture-backed suite already exists, the backtracking-heavy file already reads the published manifest, and the next simplification is to delete the extra wrapper rather than keep parallel quantified-alternation parity paths.
- Both tracked and live JSON blob counts are already zero in the current checkout, so this is the next-priority architecture cleanup: reduce duplicate parity harness structure instead of seeding another JSON-only task.
