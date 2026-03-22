# RBR-0915: Collapse the conditional-group-exists match-api case-id mirror

Status: done
Owner: architecture-implementation
Created: 2026-03-22

## Goal
- Remove the detached `MATCH_API_CASE_IDS` tuple from `tests/python/test_conditional_group_exists_parity_suite.py`, so the conditional parity owner derives its `MATCH_API_CASES` subset directly from the live quantified fixture slices it already builds.

## Deliverables
- `tests/python/test_conditional_group_exists_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_conditional_group_exists_parity_suite.py` no longer defines `MATCH_API_CASE_IDS`:
  - delete the top-level tuple instead of replacing it with another detached tuple/list/set/map; and
  - if a helper remains, keep it as one tiny file-local live selector over `QUANTIFIED_MODULE_CASES` and `QUANTIFIED_PATTERN_CASES` rather than another cached case-id mirror.
- `MATCH_API_CASES` is rebuilt from the existing quantified owner data instead of from the deleted case-id tuple:
  - keep the module half sourced from the live `QUANTIFIED_MODULE_CASES` rows whose `manifest_id` is exactly `"conditional-group-exists-quantified-workflows"`;
  - keep the pattern half sourced from the live `QUANTIFIED_PATTERN_CASES` rows whose `manifest_id` is exactly `"conditional-group-exists-quantified-alternation-workflows"`;
  - preserve the current ordered module ids exactly as `conditional-group-exists-quantified-module-search-present-str`, `conditional-group-exists-quantified-module-fullmatch-absent-str`, `named-conditional-group-exists-quantified-module-search-present-str`, then `named-conditional-group-exists-quantified-module-fullmatch-absent-str`; and
  - preserve the current ordered pattern ids exactly as `conditional-group-exists-quantified-alternation-pattern-fullmatch-present-second-arm-str`, `conditional-group-exists-quantified-alternation-pattern-fullmatch-absent-second-arm-str`, `named-conditional-group-exists-quantified-alternation-pattern-fullmatch-present-second-arm-str`, then `named-conditional-group-exists-quantified-alternation-pattern-fullmatch-absent-second-arm-str`.
- Route the current owner-path assertion through the live selector instead of the deleted mirror:
  - `test_match_api_cases_remain_published_quantified_conditional_matches()` still proves the same eight published `str` cases stay selected in the same order; and
  - any other reads of `MATCH_API_CASES` in `tests/python/test_conditional_group_exists_parity_suite.py` continue to observe the same case objects and ordering.
- Keep this cleanup structural only:
  - do not change fixture contents, manifest order, quantified conditional behavior, parity expectations, benchmark/report outputs, or tracked project-state prose; and
  - prefer deleting the mirror over introducing another shared helper module, selector registry, or sidecar contract table.
- Verification passes with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_conditional_group_exists_parity_suite.py`
  - `bash -lc "! rg -n '^MATCH_API_CASE_IDS = \\(' tests/python/test_conditional_group_exists_parity_suite.py"`
  - `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from tests.python.test_conditional_group_exists_parity_suite import QUANTIFIED_MODULE_CASES, QUANTIFIED_PATTERN_CASES
module_ids = tuple(
    case.case_id
    for case in QUANTIFIED_MODULE_CASES
    if case.manifest_id == 'conditional-group-exists-quantified-workflows'
)
pattern_ids = tuple(
    case.case_id
    for case in QUANTIFIED_PATTERN_CASES
    if case.manifest_id == 'conditional-group-exists-quantified-alternation-workflows'
)
assert module_ids == (
    'conditional-group-exists-quantified-module-search-present-str',
    'conditional-group-exists-quantified-module-fullmatch-absent-str',
    'named-conditional-group-exists-quantified-module-search-present-str',
    'named-conditional-group-exists-quantified-module-fullmatch-absent-str',
)
assert pattern_ids == (
    'conditional-group-exists-quantified-alternation-pattern-fullmatch-present-second-arm-str',
    'conditional-group-exists-quantified-alternation-pattern-fullmatch-absent-second-arm-str',
    'named-conditional-group-exists-quantified-alternation-pattern-fullmatch-present-second-arm-str',
    'named-conditional-group-exists-quantified-alternation-pattern-fullmatch-absent-second-arm-str',
)
print('ok')
PY`

## Constraints
- Keep the change limited to the residual `MATCH_API_CASES` case-id mirror in `tests/python/test_conditional_group_exists_parity_suite.py`. Do not widen into conditional behavior changes, fixture rewrites, shared parity-support refactors, benchmark work, or report regeneration in this run.
- Preserve the current published quantified conditional frontier exactly. The point is to delete one owner-local representation layer, not to reinterpret which quantified rows define the match-api surface.

## Notes
- `RBR-0915` is the next available architecture task id in the current checkout:
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 20` currently ends at `RBR-0914-match-pattern-sub-subn-unexpected-keyword-typeerrors.md`; and
  - `rg -n 'RBR-0915|RBR-0916|RBR-0917|RBR-0918|RBR-0919|RBR-0920' ops/state/backlog.md ops/state/current_status.md` returned no reserved follow-on ids in this run.
- There is no blocked architecture task to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The mirror target is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_conditional_group_exists_parity_suite.py` currently passes (`530 passed in 0.45s`);
  - `bash -lc "! rg -n '^MATCH_API_CASE_IDS = \\(' tests/python/test_conditional_group_exists_parity_suite.py"` currently fails exactly on the remaining mirror at line `430`; and
  - the task-local quantified-slice probe in Acceptance currently passes (`ok`), proving the live `QUANTIFIED_MODULE_CASES` and `QUANTIFIED_PATTERN_CASES` paths already recover the same ordered eight-case surface without the handwritten tuple.
- This stays on the same owner-local mirror cleanup path as the recent conditional and grouped-capture work:
  - `RBR-0905` removed the broader `PUBLISHED_CASES` flattening mirror from this same conditional parity owner; and
  - `RBR-0911` removed direct test bucket wrapper mirrors from the grouped-capture owner instead of adding another shared abstraction layer.

## Completion
- Replaced the detached `MATCH_API_CASE_IDS` mirror in `tests/python/test_conditional_group_exists_parity_suite.py` with a tiny `_select_match_api_cases()` helper that rebuilds `MATCH_API_CASES` directly from the live `QUANTIFIED_MODULE_CASES` and `QUANTIFIED_PATTERN_CASES` slices.
- Kept the match-api publication assertion structural-only by checking the live selected case ids inline against the existing ordered eight-case expectation.
- Verified with `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_conditional_group_exists_parity_suite.py`, `bash -lc "! rg -n '^MATCH_API_CASE_IDS = \\(' tests/python/test_conditional_group_exists_parity_suite.py"`, and the task-local quantified-slice probe from Acceptance (`ok`).
