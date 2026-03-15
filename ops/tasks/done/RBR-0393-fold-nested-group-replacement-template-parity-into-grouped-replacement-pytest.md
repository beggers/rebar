# RBR-0393: Fold nested-group replacement-template parity into the grouped replacement pytest module

Status: done
Owner: architecture-implementation
Created: 2026-03-15

## Goal
- Remove `tests/python/test_nested_group_replacement_template_parity.py` as a standalone parity surface by folding its bounded nested-group and quantified nested-group replacement-template coverage into `tests/python/test_grouped_literal_replacement_template.py`, so the grouped replacement frontier no longer keeps these numbered and named nested slices on a second near-duplicate fixture-backed wrapper.

## Deliverables
- `tests/python/test_grouped_literal_replacement_template.py`
- Delete `tests/python/test_nested_group_replacement_template_parity.py`

## Acceptance Criteria
- `tests/python/test_grouped_literal_replacement_template.py` absorbs `tests/conformance/fixtures/nested_group_replacement_workflows.py` and `tests/conformance/fixtures/quantified_nested_group_replacement_workflows.py` through the module's existing `load_fixture_manifest(...)` / `FixtureCase` pytest path instead of leaving those manifests on a separate parity module.
- The grouped replacement pytest module keeps the absorbed nested-group replacement bundles explicit by adding manifest-alignment assertions that cover these two published fixture contracts and no broader nested replacement frontier:
  - manifest id `nested-group-replacement-workflows` with exactly these case ids:
    - `module-sub-template-nested-group-numbered-str`
    - `module-subn-template-nested-group-numbered-str`
    - `pattern-sub-template-nested-group-numbered-str`
    - `pattern-subn-template-nested-group-numbered-str`
    - `module-sub-template-nested-group-named-str`
    - `module-subn-template-nested-group-named-str`
    - `pattern-sub-template-nested-group-named-str`
    - `pattern-subn-template-nested-group-named-str`
  - manifest id `quantified-nested-group-replacement-workflows` with exactly these case ids:
    - `module-sub-template-quantified-nested-group-numbered-lower-bound-str`
    - `module-subn-template-quantified-nested-group-numbered-first-match-only-str`
    - `pattern-sub-template-quantified-nested-group-numbered-repeated-outer-capture-str`
    - `pattern-subn-template-quantified-nested-group-numbered-first-match-only-str`
    - `module-sub-template-quantified-nested-group-named-lower-bound-str`
    - `module-subn-template-quantified-nested-group-named-first-match-only-str`
    - `pattern-sub-template-quantified-nested-group-named-repeated-outer-capture-str`
    - `pattern-subn-template-quantified-nested-group-named-first-match-only-str`
- The absorbed bundles keep their current manifest contracts explicit inside `tests/python/test_grouped_literal_replacement_template.py`:
  - compile patterns `a((b))d` and `a(?P<outer>(?P<inner>b))d` for the bounded nested-group slice
  - compile patterns `a((bc)+)d` and `a(?P<outer>(?P<inner>bc)+)d` for the quantified nested-group slice
  - operation/helper counts of two module `sub()` rows, two module `subn()` rows, two pattern `sub()` rows, and two pattern `subn()` rows for each absorbed fixture
- The absorbed nested-group replacement rows reuse the grouped replacement module's existing shared pytest flow rather than another local bundle/compile wrapper, so this slice now receives:
  - compile metadata parity through the same `regex_backend` path already used by `tests/python/test_grouped_literal_replacement_template.py`
  - direct module `sub()` / `subn()` result parity for the published numbered and named nested-group and quantified nested-group replacement rows
  - direct compiled-`Pattern` `sub()` / `subn()` result parity for the published numbered and named nested-group and quantified nested-group replacement rows
- The consolidation preserves the current bounded no-match supplements from `tests/python/test_nested_group_replacement_template_parity.py` for `a((b))d` and `a(?P<outer>(?P<inner>b))d`: module and compiled-pattern `sub()` keep returning the original `zzadzz` haystack, and `subn()` keeps returning `(zzadzz, 0)`, without leaving those checks in another file-local wrapper.
- The consolidation preserves the existing grouped literal replacement-template, grouped-alternation replacement-template, and grouped single-capture match assertions already anchored in `tests/conformance/fixtures/collection_replacement_workflows.py`, `tests/conformance/fixtures/grouped_alternation_replacement_workflows.py`, and `tests/conformance/fixtures/grouped_match_workflows.py`; do not narrow that current grouped replacement coverage while absorbing the nested slices.
- No new suite, support module, manifest registry, or generated case layer is introduced. Expand the existing grouped replacement pytest module directly.
- After the consolidation lands, `rg --files tests/python | rg 'test_nested_group_replacement_template_parity\\.py$'` returns no matches.
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_grouped_literal_replacement_template.py`.

## Constraints
- Keep this task on the Python parity surface only. Do not change Rust code, `python/rebar/`, correctness fixture contents, benchmark manifests, published reports, README reporting, or tracked state files beyond this task file.
- Keep the nested-group replacement rows on the existing grouped replacement pytest path. Do not create a second grouped-replacement suite and do not broaden this cleanup into open-ended quantified-group replacement, callable replacement, or benchmark catch-up work.
- Reuse the existing helpers already in the repo, especially `load_fixture_manifest(...)`, `FixtureCase`, `compile_with_cpython_parity(...)`, and the backend-parameterized `regex_backend` fixture, instead of adding another fixture loader or file-local parity harness.

## Notes
- Both tracked and live JSON counts are zero in the current checkout (`tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, `git ls-files '*.json' | wc -l = 0`, `rg --files -g '*.json' | wc -l = 0`), so the next architecture priority is deleting duplicate Python parity plumbing rather than another JSON burn-down task.
- `tests/python/test_nested_group_replacement_template_parity.py` was a 288-line standalone fixture-backed wrapper with its own `FixtureBundle` dataclass, fixture loader, compile parity pass, and bounded no-match supplements, even though `tests/python/test_grouped_literal_replacement_template.py` already owned the adjacent grouped replacement-template surface through the same shared pytest information flow.
- Build directly on `RBR-0355` and `RBR-0389`: the nested and quantified nested replacement rows are already fixture-backed, and the next simplification is to delete the extra wrapper rather than keep parallel grouped-replacement parity modules.

## Completion
- Folded the nested and quantified nested replacement-template fixture rows into `tests/python/test_grouped_literal_replacement_template.py`, including exact manifest-alignment assertions, shared compile/result parity coverage, and the preserved bounded nested no-match supplements.
- Deleted `tests/python/test_nested_group_replacement_template_parity.py`.
- Verified with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_grouped_literal_replacement_template.py` and confirmed `rg --files tests/python | rg 'test_nested_group_replacement_template_parity\\.py$'` returns no matches.
