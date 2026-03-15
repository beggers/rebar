# RBR-0383: Fold the remaining systematic capture parity wrapper into the owning fixture suites

Status: ready
Owner: architecture-implementation
Created: 2026-03-15

## Goal
- Delete `tests/python/test_folded_systematic_capture_parity.py` by moving its systematic optional-group and nested explicit-empty-else capture rows onto the family suites that already own those published fixtures, so those rows stop living on a third cross-cutting parity path.

## Deliverables
- `tests/python/test_grouped_capture_parity_suite.py`
- `tests/python/test_conditional_group_exists_nested_parity_suite.py`
- Delete `tests/python/test_folded_systematic_capture_parity.py`

## Acceptance Criteria
- `tests/python/test_grouped_capture_parity_suite.py` absorbs the systematic optional-group compile and workflow coverage currently selected in `tests/python/test_folded_systematic_capture_parity.py` from `tests/conformance/fixtures/optional_group_workflows.py`, while keeping those rows on the suite's existing fixture-backed path instead of another cross-suite loader or private scenario table.
- The grouped-capture suite keeps the absorbed optional-group rows explicit by expanding its manifest-alignment and case-selection assertions to cover the existing optional-group rows plus these exact systematic case ids:
  - `systematic-optional-group-numbered-compile-metadata-str`
  - `systematic-optional-group-numbered-module-search-present-str`
  - `systematic-optional-group-numbered-module-search-absent-str`
  - `systematic-optional-group-numbered-pattern-fullmatch-present-str`
  - `systematic-optional-group-numbered-pattern-fullmatch-absent-str`
  - `systematic-optional-group-named-compile-metadata-str`
  - `systematic-optional-group-named-module-search-present-str`
  - `systematic-optional-group-named-module-search-absent-str`
  - `systematic-optional-group-named-pattern-fullmatch-present-str`
  - `systematic-optional-group-named-pattern-fullmatch-absent-str`
- `tests/python/test_conditional_group_exists_nested_parity_suite.py` absorbs the systematic explicit-empty-else nested compile and workflow coverage currently selected in `tests/python/test_folded_systematic_capture_parity.py` from `tests/conformance/fixtures/conditional_group_exists_empty_else_nested_workflows.py`, and removes the current dedicated-wrapper split for those rows.
- The nested-conditional suite keeps the absorbed explicit-empty-else systematic rows explicit by expanding the existing empty-else fixture bundle to cover the current non-systematic rows plus these exact systematic case ids:
  - `systematic-conditional-group-exists-empty-else-nested-numbered-compile-metadata-str`
  - `systematic-conditional-group-exists-empty-else-nested-numbered-module-search-present-str`
  - `systematic-conditional-group-exists-empty-else-nested-numbered-module-fullmatch-missing-suffix-str`
  - `systematic-conditional-group-exists-empty-else-nested-numbered-pattern-fullmatch-absent-str`
  - `systematic-conditional-group-exists-empty-else-nested-named-compile-metadata-str`
  - `systematic-conditional-group-exists-empty-else-nested-named-module-search-present-str`
  - `systematic-conditional-group-exists-empty-else-nested-named-module-fullmatch-missing-suffix-str`
  - `systematic-conditional-group-exists-empty-else-nested-named-pattern-fullmatch-absent-str`
- The fold preserves the current parity depth from the deleted wrapper for these absorbed rows:
  - repeated `compile()` identity for the active backend where the owning suite already enforces it;
  - compile metadata parity for `.pattern`, `.flags`, `.groups`, and `.groupindex`;
  - match-result parity for `.group(0)`, numbered and named group access, `.groups()`, `.groups(default)`, `.groupdict()`, `.groupdict(default)`, `.span()`, `.start()`, `.end()`, `.string`, `.pos`, `.endpos`, `.lastindex`, and `.lastgroup`; and
  - `None`-result parity for the nested explicit-empty-else missing-suffix rows.
- Reuse the existing loader path in `rebar_harness.correctness`, the shared `regex_backend` pytest parameterization, and existing shared test helpers where practical. If generic helper extraction is needed, extend `tests/python/fixture_parity_support.py` rather than introducing another support module.
- After the fold lands, `rg --files tests/python | rg 'test_folded_systematic_capture_parity\\.py$'` returns no matches.
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py tests/python/test_conditional_group_exists_nested_parity_suite.py`.

## Constraints
- Keep this task on the Python test surface only. Do not change Rust code, `python/rebar/`, correctness fixture contents, benchmark workloads, published reports, or tracked state files beyond this task file.
- Do not broaden grouped-capture or nested-conditional coverage beyond the 18 systematic rows already published in those two fixtures.
- Prefer deleting the cross-cutting wrapper over adding another manifest registry, generated case layer, or bespoke helper module.

## Notes
- `tests/python/test_folded_systematic_capture_parity.py` is still a 202-line cross-cutting parity module whose cases already live in standard published fixtures and are already partially referenced by the owning suites.
- `ops/tasks/done/RBR-0363-consolidate-nested-conditional-group-exists-parity-suite.md` explicitly left these systematic rows on the dedicated wrapper as a follow-on cleanup once the owning nested suite existed.
- Both tracked and live JSON blob counts are zero in the current checkout, so deleting this duplicate parity surface is the next-priority architecture cleanup instead of another JSON burn-down task.
