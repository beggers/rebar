# RBR-0391: Fold nested-group alternation parity into the existing family suites

Status: ready
Owner: architecture-implementation
Created: 2026-03-15

## Goal
- Delete `tests/python/test_nested_group_alternation_parity.py` by moving its two published fixture slices onto the family suites that already own those correctness surfaces, so nested-group alternation no longer lives on a third overlapping parity module with private repo bootstrapping and file-local pattern/match helper copies.

## Deliverables
- `tests/python/test_grouped_capture_parity_suite.py`
- `tests/python/test_quantified_alternation_parity_suite.py`
- Delete `tests/python/test_nested_group_alternation_parity.py`

## Acceptance Criteria
- `tests/python/test_grouped_capture_parity_suite.py` absorbs `tests/conformance/fixtures/nested_group_alternation_workflows.py` through the suite's existing fixture-backed path instead of leaving that manifest on a separate parity module.
- The grouped-capture suite keeps the absorbed non-quantified nested-group alternation slice explicit by adding one bundle that pins exactly these published case ids and no broader alternation frontier:
  - `nested-group-alternation-compile-metadata-str`
  - `nested-group-alternation-module-search-str`
  - `nested-group-alternation-pattern-fullmatch-str`
  - `named-nested-group-alternation-compile-metadata-str`
  - `named-nested-group-alternation-module-search-str`
  - `named-nested-group-alternation-pattern-fullmatch-str`
- The grouped-capture suite keeps the current manifest contract explicit for that absorbed bundle:
  - manifest id `nested-group-alternation-workflows`
  - pattern set `a((b|c))d` and `a(?P<outer>(?P<inner>b|c))d`
  - operation/helper counts `("compile", None): 2`, `("module_call", "search"): 2`, and `("pattern_call", "fullmatch"): 2`
- The grouped-capture suite preserves the deleted module's current parity depth for the non-quantified nested-group alternation rows through its existing shared helper paths, including:
  - compile metadata parity for the numbered and named compile rows;
  - module `search()` and compiled-`Pattern.fullmatch()` match-result parity including `.regs`;
  - match convenience API parity for the numbered and named workflow rows; and
  - valid and invalid match-group accessor parity for the four workflow rows via the suite's existing match-group-access path instead of a new local helper block.
- The grouped-capture suite keeps the deleted module's explicit non-quantified near-miss coverage on its existing supplemental miss path rather than another wrapper-specific table:
  - numbered module-search misses on `zzadzz` and `zzabbdzz`
  - numbered compiled-`Pattern.fullmatch()` misses on `ad` and `abbd`
  - named module-search misses on `zzadzz` and `zzaccddzz`
  - named compiled-`Pattern.fullmatch()` misses on `ad` and `accd`
- `tests/python/test_quantified_alternation_parity_suite.py` absorbs `tests/conformance/fixtures/quantified_nested_group_alternation_workflows.py` through that suite's existing fixture-backed path instead of leaving the quantified nested-group alternation rows on the standalone parity module.
- The quantified-alternation suite keeps the absorbed quantified nested-group alternation slice explicit by adding one bundle that pins exactly these published case ids and no broader nested-group follow-on:
  - `quantified-nested-group-alternation-numbered-compile-metadata-str`
  - `quantified-nested-group-alternation-numbered-module-search-lower-bound-b-str`
  - `quantified-nested-group-alternation-numbered-pattern-fullmatch-repeated-mixed-str`
  - `quantified-nested-group-alternation-named-compile-metadata-str`
  - `quantified-nested-group-alternation-named-module-search-lower-bound-c-str`
  - `quantified-nested-group-alternation-named-pattern-fullmatch-repeated-mixed-str`
- The quantified-alternation suite keeps the current manifest contract explicit for that absorbed bundle:
  - manifest id `quantified-nested-group-alternation-workflows`
  - pattern set `a((b|c)+)d` and `a(?P<outer>(?P<inner>b|c)+)d`
  - operation/helper counts `("compile", None): 2`, `("module_call", "search"): 2`, and `("pattern_call", "fullmatch"): 2`
- The quantified-alternation suite preserves the deleted module's current quantified nested-group alternation parity depth through its existing shared helper paths, including:
  - compile metadata parity for the numbered and named compile rows;
  - module `search()` and compiled-`Pattern.fullmatch()` match-result parity including `.regs`; and
  - match convenience API parity for the numbered and named workflow rows.
- The quantified-alternation suite keeps the deleted module's explicit quantified near-miss coverage on an existing shared no-match path rather than a second standalone wrapper:
  - numbered module-search misses on `zzadzz` and `zzabedzz`
  - numbered compiled-`Pattern.fullmatch()` misses on `ad` and `abed`
  - named module-search misses on `zzadzz` and `zzabedzz`
  - named compiled-`Pattern.fullmatch()` misses on `ad` and `abed`
- If generic helper extraction is needed, limit it to `tests/python/fixture_parity_support.py`; do not add another support module and do not copy the deleted module's `_case_pattern(...)`, `_assert_pattern_parity(...)`, or `_assert_match_parity(...)` blocks into the destination suites.
- The consolidation preserves the current grouped-capture and quantified-alternation coverage already present in those suites; this task deletes duplicate plumbing and does not narrow the existing bundles, no-match tables, or helper assertions.
- After the fold lands, `rg --files tests/python | rg 'test_nested_group_alternation_parity\\.py$'` returns no matches.
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py tests/python/test_quantified_alternation_parity_suite.py`.

## Constraints
- Keep this task on the Python parity surface only. Do not change Rust code, `python/rebar/`, correctness fixture contents, benchmark workloads, published reports, README reporting, or tracked state files beyond this task file.
- Do not broaden the cleanup into branch-local-backreference work, replacement-template work, callable-replacement work, or benchmark catch-up. Keep the absorbed rows on the existing grouped-capture and quantified-alternation suite paths only.
- Reuse the existing backend-parameterized pytest flow and existing helper modules instead of introducing another nested-group alternation suite, manifest registry, or generated case layer.

## Notes
- The current runtime dashboard is clean and current for `HEAD` `07daedb1309dd7884c0639710f3a3ec66e2dfaae`, and both reported and live JSON counts are already zero (`tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, `git ls-files '*.json' | wc -l = 0`, `rg --files -g '*.json' | wc -l = 0`), so the next architecture priority is deleting duplicate Python parity plumbing rather than another JSON burn-down task.
- `tests/python/test_nested_group_alternation_parity.py` is still a 380-line standalone parity module with private `sys.path` bootstrapping plus file-local `_case_pattern(...)`, `_assert_pattern_parity(...)`, and `_assert_match_parity(...)` helpers that duplicate the shared fixture-backed information flow already used by the destination suites.
- `tests/python/test_grouped_capture_parity_suite.py` already owns the adjacent grouped, named-group, optional-group, grouped-alternation, and nested-group capture rows, while `tests/python/test_quantified_alternation_parity_suite.py` already owns the exact-repeat, ranged, broader-range, open-ended, conditional, and nested-branch alternation rows, making them the natural homes for the two absorbed manifests.
