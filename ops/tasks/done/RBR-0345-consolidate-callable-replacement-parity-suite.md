# RBR-0345: Consolidate the callable-replacement parity modules into one shared pytest suite

Status: done
Owner: architecture-implementation
Created: 2026-03-14
Completed: 2026-03-14

## Goal
- Replace the three landed callable-replacement parity modules with one backend-parameterized pytest suite so grouped and nested callback parity lives on one Python-path contract instead of repeated fixture loading, compile assertions, module/pattern wrapper tests, and one leftover `unittest` class.

## Deliverables
- `tests/python/test_callable_replacement_parity_suite.py`
- Delete `tests/python/test_nested_group_callable_replacement_parity.py`
- Delete `tests/python/test_grouped_alternation_callable_replacement_parity.py`
- Delete `tests/python/test_quantified_nested_group_callable_replacement_parity.py`

## Acceptance Criteria
- The new suite covers the currently landed numbered and named callable-replacement parity observations now spread across the three superseded modules for:
  - `a((b))d` and `a(?P<outer>(?P<inner>b))d`
  - `a(b|c)d` and `a(?P<word>b|c)d`
  - `a((bc)+)d` and `a(?P<outer>(?P<inner>bc)+)d`
- Case selection is driven from the published correctness fixtures already checked into the repo:
  - `tests/conformance/fixtures/nested_group_callable_replacement_workflows.py`
  - `tests/conformance/fixtures/grouped_alternation_callable_replacement_workflows.py`
  - `tests/conformance/fixtures/quantified_nested_group_callable_replacement_workflows.py`
  The consolidated suite keeps one manifest-alignment assertion per fixture covering the manifest id, published case ids, compile-pattern set, and `operation`/`helper` distribution, so the Python parity surface stays tied to the published correctness surface instead of drifting onto hand-maintained case tables.
- The consolidated suite preserves the current coverage layers for each landed slice:
  - compile metadata parity for `.pattern`, `.flags`, `.groups`, and `.groupindex`
  - direct module and compiled-`Pattern` `sub()` / `subn()` result parity
  - callable `Match` snapshot parity through the existing `assert_callable_replacement_match_parity(...)` helper, including numbered and named group access where those assertions exist today
- Backend parameterization continues to flow through `tests/python/conftest.py` and the shared `regex_backend` fixture, so the consolidated suite uses one central native-availability gate instead of repeated per-file `unittest.skipUnless(...)` decorators or copied backend setup.
- The implementation reuses the existing Python helpers already in the repo, especially `load_fixture_manifest(...)`, `FixtureCase`, and `assert_callable_replacement_match_parity(...)`, rather than introducing another manifest loader, callback helper layer, or generated case format.
- After the consolidation lands, `rg --files tests/python | rg 'test_(nested_group|grouped_alternation|quantified_nested_group)_callable_replacement_parity\\.py$'` returns no matches.
- Keep the current publication-only nested-group alternation callback frontier out of scope: `tests/conformance/fixtures/nested_group_alternation_callable_replacement_workflows.py` and ready task `RBR-0344` are not part of this cleanup, and the new suite must pass against the current checkout without depending on any unlanded Rust-backed behavior.

## Constraints
- Keep this task scoped to the three current callable-replacement parity modules listed above; do not attempt a repo-wide parity-suite migration here.
- Keep the work on the Python test surface only. Do not change Rust code, `python/rebar/` runtime behavior, correctness fixtures, benchmark workloads, or published reports to complete it.
- Use ordinary pytest parameter tables and shared helpers rather than JSON, code generation, or another bespoke harness layer.

## Notes
- The current three modules total 584 lines and already share the same compile/result/callback assertion structure; only the oldest nested-group slice still sits on a standalone `unittest` class with hand-maintained case tuples.
- This is the same simplification pattern already used for the grouped counted-repeat frontiers in `tests/python/test_open_ended_quantified_group_parity_suite.py` and `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`, applied to the callable-replacement frontier that is still split across one legacy singleton and two near-duplicate pytest modules.

## Completion
- Added `tests/python/test_callable_replacement_parity_suite.py`, consolidating the nested-group, grouped-alternation, and quantified-nested-group callable-replacement parity checks onto one backend-parameterized pytest suite.
- Kept manifest alignment explicit per published fixture by asserting each fixture's manifest id, case-id set, compile-pattern set, and operation/helper distribution before reusing the loaded `FixtureCase` rows for compile metadata, module/pattern `sub()` / `subn()` parity, and callback `Match` snapshot parity.
- Deleted `tests/python/test_nested_group_callable_replacement_parity.py`, `tests/python/test_grouped_alternation_callable_replacement_parity.py`, and `tests/python/test_quantified_nested_group_callable_replacement_parity.py`.

## Verification
- `.venv/bin/python -m pytest tests/python/test_callable_replacement_parity_suite.py`
- `git diff --name-status -- tests/python/test_callable_replacement_parity_suite.py tests/python/test_nested_group_callable_replacement_parity.py tests/python/test_grouped_alternation_callable_replacement_parity.py tests/python/test_quantified_nested_group_callable_replacement_parity.py`
- `rg --files tests/python | rg 'test_(nested_group|grouped_alternation|quantified_nested_group)_callable_replacement_parity\\.py$'`
