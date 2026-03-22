Status: ready
Owner: architecture-implementation
Created: 2026-03-22

## Goal
- Remove the detached `PARSER_MATRIX_SELECTED_CASE_IDS` and `CONDITIONAL_ASSERTION_DIAGNOSTIC_CASE_IDS` mirrors from `tests/python/test_parser_matrix_parity_suite.py`, so the parser-matrix owner routes bundle construction and frontier assertions through the live case tuples it already defines.

## Deliverables
- `tests/python/test_parser_matrix_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_parser_matrix_parity_suite.py` no longer defines `PARSER_MATRIX_SELECTED_CASE_IDS` or `CONDITIONAL_ASSERTION_DIAGNOSTIC_CASE_IDS`:
  - delete both top-level mirrors instead of replacing them with another detached tuple/list/set/map of the same ids; and
  - if a helper remains, keep it as one tiny file-local ordered selector over `TARGET_CASES` and `CONDITIONAL_ASSERTION_DIAGNOSTIC_CASES` rather than another cached mirror.
- The two selected fixture bundles are rebuilt from the existing live case tuples instead of the deleted id mirrors:
  - `PARSER_MATRIX_FIXTURE_BUNDLE` keeps selecting the current ordered parser rows directly from `TARGET_CASES`;
  - `CONDITIONAL_ASSERTION_DIAGNOSTIC_FIXTURE_BUNDLE` keeps selecting the current ordered assertion-diagnostic rows directly from `CONDITIONAL_ASSERTION_DIAGNOSTIC_CASES`; and
  - preserve the parser-matrix order exactly as `str-character-class-ignorecase-success`, `str-possessive-quantifier-success`, `str-atomic-group-success`, `str-fixed-width-lookbehind-success`, `str-parser-stress-compile-proxy-success`, `str-nested-set-warning`, `str-invalid-repeat-error`, `str-invalid-inline-flag-position-error`, `str-variable-width-lookbehind-error`, `str-inline-unicode-flag-success`, `str-inline-locale-flag-error`, `bytes-named-backreference-compile-proxy-success`, `bytes-inline-unicode-flag-error`, `bytes-inline-locale-flag-success`, then `bytes-unicode-escape-error`.
- The current owner-path assertions now consume the live selectors instead of the deleted mirrors:
  - `test_parser_matrix_parity_suite_stays_aligned_with_published_correctness_fixture()`, `test_parser_matrix_parity_suite_tracks_published_case_frontier()`, and `test_parser_matrix_direct_test_buckets_cover_selected_frontier()` still observe the same fifteen parser rows in the same order;
  - `test_conditional_assertion_diagnostic_fixture_stays_aligned_with_published_correctness_fixture()` still observes the same ordered diagnostic pair, `conditional-group-exists-assertion-positive-lookahead-error-str` then `conditional-group-exists-assertion-negative-lookahead-error-str`; and
  - leave `KNOWN_UNCOVERED_PARSER_MATRIX_CASE_IDS` as the suite's intentional policy boundary for the two baseline literal compile rows in this run.
- Keep this cleanup structural only:
  - do not change fixture contents, parser behavior, warning/error expectations, benchmark/report outputs, or tracked project-state prose; and
  - prefer deleting the mirrors over introducing a shared selector registry or another support module.
- Verification passes with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_parser_matrix_parity_suite.py`
  - `bash -lc "! rg -n '^(PARSER_MATRIX_SELECTED_CASE_IDS|CONDITIONAL_ASSERTION_DIAGNOSTIC_CASE_IDS)\\s*=' tests/python/test_parser_matrix_parity_suite.py"`
  - `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from tests.python.test_parser_matrix_parity_suite import (
    CONDITIONAL_ASSERTION_DIAGNOSTIC_CASES,
    TARGET_CASES,
)

assert tuple(case.case_id for case in TARGET_CASES) == (
    'str-character-class-ignorecase-success',
    'str-possessive-quantifier-success',
    'str-atomic-group-success',
    'str-fixed-width-lookbehind-success',
    'str-parser-stress-compile-proxy-success',
    'str-nested-set-warning',
    'str-invalid-repeat-error',
    'str-invalid-inline-flag-position-error',
    'str-variable-width-lookbehind-error',
    'str-inline-unicode-flag-success',
    'str-inline-locale-flag-error',
    'bytes-named-backreference-compile-proxy-success',
    'bytes-inline-unicode-flag-error',
    'bytes-inline-locale-flag-success',
    'bytes-unicode-escape-error',
)
assert tuple(case.case_id for case in CONDITIONAL_ASSERTION_DIAGNOSTIC_CASES) == (
    'conditional-group-exists-assertion-positive-lookahead-error-str',
    'conditional-group-exists-assertion-negative-lookahead-error-str',
)
print('ok')
PY`

## Constraints
- Keep the change limited to the residual selected-case id mirrors in `tests/python/test_parser_matrix_parity_suite.py`. Do not widen into parser fixture edits, contract-helper refactors, broader parser-matrix policy changes, or report regeneration in this run.
- Preserve the current parser parity frontier exactly. The point is to delete one owner-local representation layer, not to reinterpret which parser rows belong in the suite.

## Notes
- `RBR-0918` is the next available architecture task id in the current checkout:
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 20` currently ends at `RBR-0917-collapse-compiled-pattern-module-boundary-success-manifest-mirror.md`; and
  - `rg -n 'RBR-0918|RBR-0919|RBR-0920|RBR-0921|RBR-0922' ops/state/backlog.md ops/state/current_status.md` returned no reserved follow-on ids in this run.
- There is no blocked architecture task to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The queue/runtime state does not trigger the inherited-dirty or post-task-refresh bottleneck escape hatch in this run:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and no last-cycle anomalies; and
  - the live queue listing is empty in `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/`.
- The mirror target is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_parser_matrix_parity_suite.py` currently passes (`61 passed, 29 skipped in 0.11s`);
  - `rg -n 'PARSER_MATRIX_SELECTED_CASE_IDS|CONDITIONAL_ASSERTION_DIAGNOSTIC_CASE_IDS' tests/python/test_parser_matrix_parity_suite.py` currently finds the remaining mirror definitions and reads at lines `50` and `54`; and
  - the task-local case-order probe in Acceptance currently passes (`ok`), proving the live `TARGET_CASES` and `CONDITIONAL_ASSERTION_DIAGNOSTIC_CASES` tuples already recover the same ordered selected surfaces without the handwritten id mirrors.
