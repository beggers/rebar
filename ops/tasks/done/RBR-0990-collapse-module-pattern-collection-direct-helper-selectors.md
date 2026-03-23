# RBR-0990: Collapse module/pattern collection direct-helper selectors

Status: done
Owner: cleanup
Created: 2026-03-23

## Goal
- Remove the remaining duplicated module-vs-pattern collection direct-case selectors from `tests/python/test_module_workflow_parity_suite.py` so the collection-helper parity tests derive their `split`, `findall`, and `finditer` buckets through one file-local helper instead of keeping two near-identical wrappers over the same `helper` field.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` no longer defines both duplicated collection direct-case selector helpers:
  - `_module_collection_cases_for_helper(...)`
  - `_pattern_collection_cases_for_helper(...)`
- Replace that duplicated pair with one explicit shared helper that filters an existing collection-case tuple by `helper`, and update the direct parity parametrization sites to call it for both module and pattern cases.
- Preserve the current direct-test bucket ordering exactly:
  - module `split`: `module-split-str-leading-trailing`, `module-split-str-no-match`, `module-split-str-maxsplit-one`, `module-split-str-negative-maxsplit`, `module-split-bytes-maxsplit-one`
  - pattern `split`: `pattern-split-str-no-match`, `pattern-split-str-repeated`, `pattern-split-bytes-maxsplit`, `pattern-split-str-no-match`, `pattern-split-str-repeated`, `pattern-split-str-maxsplit-one`, `pattern-split-str-negative-maxsplit`
  - module `findall`: `module-findall-bytes-repeated`, `module-findall-nonliteral-str`, `module-findall-str-repeated`, `module-findall-str-no-match`
  - pattern `findall`: `pattern-findall-str-no-match`, `pattern-findall-str-bounded`, `pattern-findall-str-bounded-no-match`, `pattern-findall-bytes-bounded`, `pattern-findall-str-bounded`, `pattern-findall-str-bounded-no-match`, `pattern-findall-bytes-bounded`
  - module `finditer`: `module-finditer-str-repeated`, `module-finditer-str-no-match`, `module-finditer-bytes-repeated`
  - pattern `finditer`: `pattern-finditer-str-bounded`, `pattern-finditer-str-bounded-no-match`, `pattern-finditer-bytes-bounded`, `pattern-finditer-str-bounded`, `pattern-finditer-str-bounded-no-match`
- Keep the cleanup structural and file-local:
  - do not widen this run into collection fixture publication selectors, bounded-wildcard helpers, owner-path selectors, positional-indexlike selectors, manifests, harness modules, reports, or tracked state prose; and
  - do not add a shared helper module, registry, or new checked-in data representation.
- The simplification is visible in the file:
  - `rg -n '^def _module_collection_cases_for_helper\\(|^def _pattern_collection_cases_for_helper\\(' tests/python/test_module_workflow_parity_suite.py` returns no matches.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_split_collection_helpers_match_cpython or pattern_split_collection_helpers_match_cpython or module_findall_collection_helpers_match_cpython or pattern_findall_collection_helpers_match_cpython or module_finditer_collection_helpers_match_cpython or module_finditer_collection_helpers_preserve_match_identity_like_cpython or pattern_finditer_collection_helpers_match_cpython or pattern_finditer_collection_helpers_preserve_match_identity_like_cpython'`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'`
  `from tests.python.test_module_workflow_parity_suite import (`
  `    MODULE_COLLECTION_CASES,`
  `    PATTERN_COLLECTION_CASES,`
  `    _collection_cases_for_helper,`
  `)`
  `... helper-order assertions for split/findall/finditer ...`
  `PY`
- `bash -lc "! rg -n '^def _module_collection_cases_for_helper\\(|^def _pattern_collection_cases_for_helper\\(' tests/python/test_module_workflow_parity_suite.py"`

## Notes
- `RBR-0990` was unreserved in this checkout when this cleanup started:
  - `rg -n 'RBR-0990|RBR-0991|RBR-0992|RBR-0993|RBR-0994' ops/tasks ops/state/current_status.md ops/state/backlog.md` returned no tracked reservation.
- The target file was clean before editing:
  - `git status --short -- tests/python/test_module_workflow_parity_suite.py` returned no output.

## Completion
- Replaced the remaining duplicated module/pattern collection direct-case selectors in `tests/python/test_module_workflow_parity_suite.py` with one generic `_collection_cases_for_helper(...)` helper.
- Repointed the eight collection helper parity parametrization sites to the shared helper without changing the published or direct-case bucket ordering.
- Verified with the focused pytest collection-helper slice (`78 passed, 1373 deselected`), the direct helper-order probe (`ok`), and the structural `rg` no-match check.
