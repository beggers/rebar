# RBR-0379: Collapse exact and ranged counted-repeat quantified-group parity onto one fixture-backed pytest suite

Status: done
Owner: architecture-implementation
Created: 2026-03-15
Completed: 2026-03-15

## Goal
- Delete the two remaining legacy `unittest` modules for the bounded exact `{2}` and ranged `{1,2}` quantified-group parity slice by replacing them with one backend-parameterized pytest suite that reads the already-published correctness fixtures and reuses the shared counted-repeat parity support.

## Deliverables
- `tests/python/test_counted_repeat_quantified_group_parity_suite.py`
- Delete `tests/python/test_exact_repeat_quantified_group_parity.py`
- Delete `tests/python/test_ranged_repeat_quantified_group_parity.py`

## Acceptance Criteria
- The new suite loads its published cases through `rebar_harness.correctness.load_fixture_manifest(...)` and `FixtureCase` from exactly these existing fixture modules:
- `tests/conformance/fixtures/exact_repeat_quantified_group_workflows.py`
- `tests/conformance/fixtures/ranged_repeat_quantified_group_workflows.py`
- The suite keeps one manifest-alignment assertion per fixture covering the exact published case-id set, manifest id, pattern set, and `Counter((operation, helper))` distribution so the Python parity surface stays tied to the published correctness surface instead of drifting onto hand-maintained scenario tables.
- For `exact_repeat_quantified_group_workflows.py`, the manifest-alignment assertion pins:
- manifest id `exact-repeat-quantified-group-workflows`
- case ids `exact-repeat-numbered-group-compile-metadata-str`, `exact-repeat-numbered-group-module-search-str`, `exact-repeat-numbered-group-pattern-fullmatch-str`, `exact-repeat-named-group-compile-metadata-str`, `exact-repeat-named-group-module-search-str`, and `exact-repeat-named-group-pattern-fullmatch-str`
- pattern set `a(bc){2}d` and `a(?P<word>bc){2}d`
- operation/helper counts `("compile", None): 2`, `("module_call", "search"): 2`, and `("pattern_call", "fullmatch"): 2`
- For `ranged_repeat_quantified_group_workflows.py`, the manifest-alignment assertion pins:
- manifest id `ranged-repeat-quantified-group-workflows`
- case ids `ranged-repeat-numbered-group-compile-metadata-str`, `ranged-repeat-numbered-group-module-search-lower-bound-str`, `ranged-repeat-numbered-group-pattern-fullmatch-upper-bound-str`, `ranged-repeat-named-group-compile-metadata-str`, `ranged-repeat-named-group-module-search-upper-bound-str`, and `ranged-repeat-named-group-pattern-fullmatch-lower-bound-str`
- pattern set `a(bc){1,2}d` and `a(?P<word>bc){1,2}d`
- operation/helper counts `("compile", None): 2`, `("module_call", "search"): 2`, and `("pattern_call", "fullmatch"): 2`
- The refactor preserves the current parity depth for both bounded slices: compile metadata parity plus numbered and named module `search()` and compiled-`Pattern.fullmatch()` match parity for `group`, `groups`, `groupdict`, `span`, `start`, `end`, `lastindex`, and `lastgroup`. If `tests/python/fixture_parity_support.py` provides a broader shared assertion surface, keep that coverage there instead of recreating a smaller file-local helper.
- Reuse `tests/python/conftest.py` and `tests/python/fixture_parity_support.py` instead of keeping file-local repo bootstrap, `setUp()` / `tearDown()` cache purges, `_assert_match_parity(...)`, or `@unittest.skipUnless(...)` native gating.
- Keep this as one backend-parameterized pytest module. Do not split exact and ranged back into separate files, do not add another helper module, and do not change the correctness fixtures themselves.
- After the consolidation lands, `rg --files tests/python | rg 'test_(exact_repeat|ranged_repeat)_quantified_group_parity\.py$'` returns no matches.
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_counted_repeat_quantified_group_parity_suite.py`.

## Constraints
- Keep this task on the Python parity surface only. Do not change Rust code, `python/rebar/`, correctness fixtures, benchmark manifests, published reports, README reporting, or tracked state files beyond this task file.
- Prefer the existing fixture-backed counted-repeat path already established by `tests/python/test_open_ended_quantified_group_parity_suite.py`, `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`, and `tests/python/fixture_parity_support.py` over inventing another parity harness abstraction.
- Preserve readable pytest failure output so the suite, manifest ids, and fixture case ids still identify the bounded exact and ranged counted-repeat rows directly.

## Notes
- `tests/python/test_exact_repeat_quantified_group_parity.py` and `tests/python/test_ranged_repeat_quantified_group_parity.py` are still near-identical legacy holdouts at 138 lines each: both repeat repo bootstrap, native-module gating, cache-purge hooks, compile metadata checks, and the same file-local match-parity helper even though the same six-case frontiers already exist as ordinary Python fixtures.
- Build on `RBR-0371`, which already extracted shared counted-repeat parity support for the fixture-backed pytest path, and keep this cleanup independent of the active feature queue.
- Both tracked and live JSON counts are already zero in the current checkout, so deleting duplicated Python parity plumbing is the next-priority architecture cleanup.

## Completion
- Added `tests/python/test_counted_repeat_quantified_group_parity_suite.py` as one backend-parameterized fixture-backed pytest suite for the bounded exact `{2}` and ranged `{1,2}` counted-repeat quantified-group frontiers.
- Kept one manifest-alignment assertion per published fixture by pinning each manifest id, exact case-id set, pattern set, and `Counter((operation, helper))` distribution before reusing the loaded `FixtureCase` rows for compile metadata, module `search()`, and compiled-`Pattern.fullmatch()` parity.
- Deleted `tests/python/test_exact_repeat_quantified_group_parity.py` and `tests/python/test_ranged_repeat_quantified_group_parity.py`.

## Verification
- `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_counted_repeat_quantified_group_parity_suite.py`
- `git diff --name-status -- tests/python/test_counted_repeat_quantified_group_parity_suite.py tests/python/test_exact_repeat_quantified_group_parity.py tests/python/test_ranged_repeat_quantified_group_parity.py`
- `rg --files tests/python | rg 'test_(exact_repeat|ranged_repeat)_quantified_group_parity\\.py$'`
