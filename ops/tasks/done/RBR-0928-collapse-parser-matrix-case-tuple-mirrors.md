# RBR-0928: Collapse parser-matrix case-tuple mirrors

Status: done
Owner: architecture-implementation
Created: 2026-03-22
Completed: 2026-03-22

## Goal
- Remove the remaining detached parser-matrix case-tuple mirrors from `tests/python/test_parser_matrix_parity_suite.py` so the suite derives its compile-metadata, placeholder-search, compile-cache, diagnostic, and no-stdlib-delegation slices directly from the live parser fixture rows it already loads instead of caching second copies of those ordered subsets through explicit case-id lookups.

## Deliverables
- `tests/python/test_parser_matrix_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_parser_matrix_parity_suite.py` no longer defines these detached top-level case-tuple mirrors:
  - `COMPILE_METADATA_CASES`
  - `PLACEHOLDER_SEARCH_CASES`
  - `REPEATED_COMPILE_CACHE_CASES`
  - `DIAGNOSTIC_CASES`
  - `NO_STDLIB_DELEGATION_CASES`
- Replace those mirrors with tiny file-local live selectors over `PARSER_MATRIX_FIXTURE_BUNDLE.cases` and/or `TARGET_CASES`:
  - do not replace the deleted mirrors with another top-level tuple/list/set/map of the same case ids;
  - do not add a new shared helper module, registry table, or cached lookup layer; and
  - keep any replacement helpers local to `tests/python/test_parser_matrix_parity_suite.py`.
- Preserve the current parser-matrix subset surfaces exactly while routing them through live selectors:
  - the compile-metadata surface still resolves, in order, to `str-character-class-ignorecase-success`, `str-possessive-quantifier-success`, `str-atomic-group-success`, `str-fixed-width-lookbehind-success`, `str-parser-stress-compile-proxy-success`, `str-inline-unicode-flag-success`, `bytes-named-backreference-compile-proxy-success`, then `bytes-inline-locale-flag-success`;
  - the placeholder-search surface still resolves, in order, to those same eight rows followed by `str-nested-set-warning`;
  - the repeated-compile-cache surface still resolves, in order, to `str-possessive-quantifier-success`, `str-atomic-group-success`, `str-fixed-width-lookbehind-success`, `str-parser-stress-compile-proxy-success`, `str-inline-unicode-flag-success`, `bytes-named-backreference-compile-proxy-success`, then `bytes-inline-locale-flag-success`;
  - the diagnostic surface still resolves, in order, to `str-invalid-repeat-error`, `str-invalid-inline-flag-position-error`, `str-variable-width-lookbehind-error`, `str-inline-locale-flag-error`, `bytes-inline-unicode-flag-error`, then `bytes-unicode-escape-error`; and
  - the no-stdlib-delegation surface still resolves, in order, to `str-character-class-ignorecase-success`, `str-possessive-quantifier-success`, `str-atomic-group-success`, `str-fixed-width-lookbehind-success`, `str-parser-stress-compile-proxy-success`, `str-variable-width-lookbehind-error`, `str-inline-unicode-flag-success`, `bytes-named-backreference-compile-proxy-success`, then `bytes-inline-locale-flag-success`.
- Keep the live parser-matrix coverage behavior unchanged:
  - the compile-metadata, placeholder-search, compile-cache, diagnostic, conditional-assertion-diagnostic, and no-stdlib-delegation tests still cover the same rows they cover today;
  - `_parser_matrix_direct_test_case_id_buckets()` still exposes the same `warning-cache`, `ignorecase-cache-normalization`, `compile-cache`, and `compile-diagnostics` coverage sets;
  - `NESTED_SET_WARNING_CASE` still points at `str-nested-set-warning`; and
  - `CHARACTER_CLASS_CASE` still points at `str-character-class-ignorecase-success`.
- Keep this cleanup structural only:
  - do not change `KNOWN_UNCOVERED_PARSER_MATRIX_CASE_IDS`, `TARGET_CASES`, `CONDITIONAL_ASSERTION_DIAGNOSTIC_CASES`, fixture manifests, shared parity-support helpers, benchmark/report outputs, or tracked project-state prose; and
  - keep the change limited to `tests/python/test_parser_matrix_parity_suite.py`.
- Verification passes with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_parser_matrix_parity_suite.py`
  - `bash -lc "! rg -n '^(COMPILE_METADATA_CASES|PLACEHOLDER_SEARCH_CASES|REPEATED_COMPILE_CACHE_CASES|DIAGNOSTIC_CASES|NO_STDLIB_DELEGATION_CASES)\\s*=' tests/python/test_parser_matrix_parity_suite.py"`
  - `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from tests.python.test_parser_matrix_parity_suite import PARSER_MATRIX_FIXTURE_BUNDLE

cases = PARSER_MATRIX_FIXTURE_BUNDLE.cases

compile_metadata_live = tuple(
    case.case_id
    for case in cases
    if "valid" in case.categories and "warning" not in case.categories
)
placeholder_search_live = compile_metadata_live + tuple(
    case.case_id
    for case in cases
    if "warning" in case.categories
)
repeated_compile_cache_live = tuple(
    case.case_id
    for case in cases
    if "valid" in case.categories
    and "warning" not in case.categories
    and case.family != "character_classes"
)
diagnostic_live = tuple(
    case.case_id
    for case in cases
    if "invalid" in case.categories
)
no_stdlib_live = tuple(
    case.case_id
    for case in cases
    if ("valid" in case.categories and "warning" not in case.categories)
    or (case.family == "assertions" and "invalid" in case.categories)
)

assert compile_metadata_live == (
    "str-character-class-ignorecase-success",
    "str-possessive-quantifier-success",
    "str-atomic-group-success",
    "str-fixed-width-lookbehind-success",
    "str-parser-stress-compile-proxy-success",
    "str-inline-unicode-flag-success",
    "bytes-named-backreference-compile-proxy-success",
    "bytes-inline-locale-flag-success",
)
assert placeholder_search_live == (
    "str-character-class-ignorecase-success",
    "str-possessive-quantifier-success",
    "str-atomic-group-success",
    "str-fixed-width-lookbehind-success",
    "str-parser-stress-compile-proxy-success",
    "str-inline-unicode-flag-success",
    "bytes-named-backreference-compile-proxy-success",
    "bytes-inline-locale-flag-success",
    "str-nested-set-warning",
)
assert repeated_compile_cache_live == (
    "str-possessive-quantifier-success",
    "str-atomic-group-success",
    "str-fixed-width-lookbehind-success",
    "str-parser-stress-compile-proxy-success",
    "str-inline-unicode-flag-success",
    "bytes-named-backreference-compile-proxy-success",
    "bytes-inline-locale-flag-success",
)
assert diagnostic_live == (
    "str-invalid-repeat-error",
    "str-invalid-inline-flag-position-error",
    "str-variable-width-lookbehind-error",
    "str-inline-locale-flag-error",
    "bytes-inline-unicode-flag-error",
    "bytes-unicode-escape-error",
)
assert no_stdlib_live == (
    "str-character-class-ignorecase-success",
    "str-possessive-quantifier-success",
    "str-atomic-group-success",
    "str-fixed-width-lookbehind-success",
    "str-parser-stress-compile-proxy-success",
    "str-variable-width-lookbehind-error",
    "str-inline-unicode-flag-success",
    "bytes-named-backreference-compile-proxy-success",
    "bytes-inline-locale-flag-success",
)
print("ok", len(compile_metadata_live), len(placeholder_search_live), len(repeated_compile_cache_live), len(diagnostic_live), len(no_stdlib_live))
PY`

## Constraints
- Keep the change limited to `tests/python/test_parser_matrix_parity_suite.py`. Do not edit fixture manifests, shared parity-support helpers, harness modules, reports, README copy, or tracked state files in this run.
- Preserve the parser-matrix subset order and coverage exactly. The point is to delete one more owner-local representation layer, not to reinterpret which parser rows receive compile-metadata, placeholder-search, cache, diagnostic, or no-stdlib-delegation coverage.

## Notes
- `RBR-0928` is the next available architecture task id in the current checkout:
  - `rg -n 'RBR-0928|RBR-0929|RBR-0930|RBR-0931|RBR-0932' ops/state/backlog.md ops/state/current_status.md || true` returned no reserved follow-on ids in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 10` currently ends at `RBR-0927-publish-module-workflow-pattern-collection-replacement-wrong-text-model-trio.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` contains no tracked blocked task file in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The mirror target is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_parser_matrix_parity_suite.py` currently passes (`61 passed, 29 skipped in 0.11s`);
  - `rg -n '^(COMPILE_METADATA_CASES|PLACEHOLDER_SEARCH_CASES|REPEATED_COMPILE_CACHE_CASES|DIAGNOSTIC_CASES|NO_STDLIB_DELEGATION_CASES)\\s*=' tests/python/test_parser_matrix_parity_suite.py` currently finds the remaining mirrors at lines `83`, `96`, `110`, `122`, and `133`; and
  - the task-local live-selector probe in Acceptance currently passes (`ok 8 9 7 6 9`), proving the file's existing parser fixture rows already recover the same ordered subset surfaces without those cached tuple mirrors.

## Completion
- Replaced the parser-matrix case-id lookup table plus the five detached tuple mirrors in `tests/python/test_parser_matrix_parity_suite.py` with file-local live selectors over `PARSER_MATRIX_FIXTURE_BUNDLE.cases`.
- Kept the compile-metadata, placeholder-search, repeated-compile-cache, diagnostic, direct-bucket, warning, ignorecase-cache, and no-stdlib-delegation surfaces wired to the same live parser rows, including the expected diagnostic order from the fixture bundle.
- Verified with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_parser_matrix_parity_suite.py`
  - `bash -lc "! rg -n '^(COMPILE_METADATA_CASES|PLACEHOLDER_SEARCH_CASES|REPEATED_COMPILE_CACHE_CASES|DIAGNOSTIC_CASES|NO_STDLIB_DELEGATION_CASES)\\s*=' tests/python/test_parser_matrix_parity_suite.py"`
  - the acceptance probe from this task (`ok 8 9 7 6 9`)
