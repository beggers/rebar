# RBR-0758: Collapse module-workflow published module-helper case-id sidecars onto canonical fixture selectors

Status: done
Owner: architecture-implementation
Created: 2026-03-20
Completed: 2026-03-20

## Goal
- Remove the remaining published module-helper case-id sidecars from `tests/python/test_module_workflow_parity_suite.py`; `PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_CASE_IDS` and `PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASE_IDS` currently just restate rows that are already derivable from the canonical fixture-backed `MODULE_CALL_CASES`.
- Make `MODULE_CALL_CASES`, `PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_CASES`, and `PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES` the sole published owners for those two module-helper slices inside the module-workflow parity owner.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` stops defining or reading these detached case-id sidecars:
  - `PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_CASE_IDS`
  - `PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASE_IDS`
- `PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_CASES` is derived directly from `MODULE_CALL_CASES` via structural fixture selectors instead of from a deleted id tuple:
  - use the existing fixture-backed fields already present on `MODULE_CALL_CASES` rather than introducing a new mirrored registry;
  - the selector must preserve the exact current row order:
    - `workflow-module-search-str-bounded-wildcard-ignorecase`
    - `workflow-module-match-str-bounded-wildcard-miss`
    - `workflow-module-fullmatch-str-bounded-wildcard`
- `PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES` is derived directly from `MODULE_CALL_CASES` via structural fixture selectors instead of from a deleted id tuple:
  - use the existing `use_compiled_pattern` / helper / pattern metadata already present on the fixture-backed rows rather than introducing a new mirrored registry;
  - the selector must preserve the exact current row order:
    - `workflow-module-search-str-compiled-pattern`
    - `workflow-module-match-str-compiled-pattern`
    - `workflow-module-search-str-bounded-wildcard-ignorecase-compiled-pattern`
    - `workflow-module-match-str-bounded-wildcard-compiled-pattern`
    - `workflow-module-fullmatch-str-bounded-wildcard-compiled-pattern`
    - `workflow-module-search-bytes-verbose-regression-compiled-pattern`
    - `workflow-module-fullmatch-bytes-verbose-regression-compiled-pattern`
    - `workflow-module-split-str-compiled-pattern`
    - `workflow-module-findall-bytes-compiled-pattern`
    - `workflow-module-finditer-str-compiled-pattern`
    - `workflow-module-sub-str-compiled-pattern`
    - `workflow-module-subn-bytes-compiled-pattern`
- The published-surface alignment tests stop comparing against the deleted case-id sidecars:
  - `test_module_workflow_surface_publishes_bounded_wildcard_raw_module_helpers_from_direct_cases` keeps verifying the exact published order and direct-case alignment, but it must derive any order check from canonical fixture selectors or inline expected tuples rather than from `PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_CASE_IDS`;
  - `test_module_workflow_surface_publishes_compiled_pattern_module_helpers_from_direct_cases` keeps verifying the exact published order and direct-case alignment, but it must derive any order check from canonical fixture selectors or inline expected tuples rather than from `PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASE_IDS`.
- Keep the remaining owner-local coverage unchanged:
  - do not change `MODULE_CALL_CASES`, `PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_CASES`, `PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES`, `_published_compiled_pattern_module_helper_cases_for_text_model(...)`, `BOUNDED_WILDCARD_MODULE_MATCH_CASES`, `COMPILED_PATTERN_MODULE_HELPER_CASES`, collection/replacement coverage, keyword-argument coverage, fake-native-boundary coverage, public-surface coverage, or direct-test bucket accounting outside this id-sidecar cleanup.
- Keep scope structural only:
  - do not edit `tests/conformance/fixtures/module_workflow_surface.py`, `tests/conformance/test_combined_correctness_scorecards.py`, `reports/correctness/latest.py`, `python/rebar/`, `crates/`, benchmark files, README copy, or tracked project-state prose in this run.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
import tests.python.test_module_workflow_parity_suite as mod

bounded_raw_case_ids = tuple(
    case.case_id
    for case in mod.MODULE_CALL_CASES
    if not case.use_compiled_pattern
    and mod.case_pattern(case) == "a.c"
    and case.helper in {"search", "match", "fullmatch"}
)
compiled_case_ids = tuple(
    case.case_id for case in mod.MODULE_CALL_CASES if case.use_compiled_pattern
)

assert bounded_raw_case_ids == (
    "workflow-module-search-str-bounded-wildcard-ignorecase",
    "workflow-module-match-str-bounded-wildcard-miss",
    "workflow-module-fullmatch-str-bounded-wildcard",
)
assert compiled_case_ids == (
    "workflow-module-search-str-compiled-pattern",
    "workflow-module-match-str-compiled-pattern",
    "workflow-module-search-str-bounded-wildcard-ignorecase-compiled-pattern",
    "workflow-module-match-str-bounded-wildcard-compiled-pattern",
    "workflow-module-fullmatch-str-bounded-wildcard-compiled-pattern",
    "workflow-module-search-bytes-verbose-regression-compiled-pattern",
    "workflow-module-fullmatch-bytes-verbose-regression-compiled-pattern",
    "workflow-module-split-str-compiled-pattern",
    "workflow-module-findall-bytes-compiled-pattern",
    "workflow-module-finditer-str-compiled-pattern",
    "workflow-module-sub-str-compiled-pattern",
    "workflow-module-subn-bytes-compiled-pattern",
)
assert tuple(
    case.case_id for case in mod.PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_CASES
) == bounded_raw_case_ids
assert tuple(
    case.case_id for case in mod.PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES
) == compiled_case_ids
print("ok")
PY`
  - `bash -lc "! rg -n '^PUBLISHED_(BOUNDED_WILDCARD_RAW|COMPILED_PATTERN)_MODULE_HELPER_CASE_IDS =' tests/python/test_module_workflow_parity_suite.py"`

## Constraints
- Keep this cleanup limited to `tests/python/test_module_workflow_parity_suite.py`. Do not use this run to collapse the remaining owner-local direct cases, merge public-surface and module-workflow selectors, or broaden the published correctness frontier.
- Prefer deriving both published slices directly from the existing fixture-backed row attributes over introducing another top-level tuple, id table, or selector registry.

## Notes
- `RBR-0758` is the next available task id in the current checkout:
  - `python3 - <<'PY'
import pathlib, re
existing = set()
for base in ['ops/tasks/ready', 'ops/tasks/in_progress', 'ops/tasks/done', 'ops/tasks/blocked']:
    for path in pathlib.Path(base).glob('RBR-*.md'):
        m = re.match(r'(RBR-\d+[A-Z]?)', path.name)
        if m:
            existing.add(m.group(1))
text = '\n'.join(
    pathlib.Path(p).read_text(encoding='utf-8')
    for p in ['ops/state/backlog.md', 'ops/state/current_status.md']
)
reserved = set(re.findall(r'RBR-\d+[A-Z]?', text)) - existing
existing_sorted = sorted(existing, key=lambda s: (int(re.search(r'\d+', s).group()), s))
reserved_sorted = sorted(reserved, key=lambda s: (int(re.search(r'\d+', s).group()), s))
print('highest_existing_tail', existing_sorted[-15:])
print('reserved_tail', reserved_sorted[-20:])
for n in range(int(re.search(r'\d+', existing_sorted[-1]).group()), int(re.search(r'\d+', existing_sorted[-1]).group()) + 200):
    rid = f'RBR-{n:04d}'
    if rid not in existing and rid not in reserved:
        print('next_free', rid)
        break
PY` reported the existing tail through `RBR-0757`, no reserved missing tail ids, and `next_free RBR-0758`.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added; and
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`.
- JSON burn-down is complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The detached owner layer is concrete and bounded in the current checkout:
  - `rg -n '^PUBLISHED_(BOUNDED_WILDCARD_RAW|COMPILED_PATTERN)_MODULE_HELPER_CASE_IDS =' tests/python/test_module_workflow_parity_suite.py` currently shows exactly the two remaining case-id sidecars in `tests/python/test_module_workflow_parity_suite.py`;
  - the structural-selector probe in Acceptance already passes in the current checkout (`ok`), so the existing fixture-backed row metadata is already sufficient to recover both published slices without those mirrored id tables; and
  - `bash -lc "! rg -n '^PUBLISHED_(BOUNDED_WILDCARD_RAW|COMPILED_PATTERN)_MODULE_HELPER_CASE_IDS =' tests/python/test_module_workflow_parity_suite.py"` currently fails exactly on this cleanup because those two sidecars still exist.
- Baseline verification is green in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py` passed (`657 passed, 1 skipped in 0.51s`);
  - the structural-selector probe from Acceptance passed (`ok`).

## Completion
- 2026-03-20: Removed `PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_CASE_IDS` and `PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASE_IDS` from `tests/python/test_module_workflow_parity_suite.py`.
- Re-derived `PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_CASES` directly from `MODULE_CALL_CASES` with the existing fixture-backed selector fields (`use_compiled_pattern`, `case_pattern(...)`, and `helper`), and re-derived `PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES` directly from the canonical `MODULE_CALL_CASES` rows that already carry `use_compiled_pattern=True`.
- Reworked the two published-surface alignment tests to keep the same exact published order and direct-case alignment checks while asserting against inline expected case-id tuples instead of the deleted sidecars.
- Verification passed with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py` (`657 passed, 1 skipped in 0.71s`), the task-local structural selector probe from Acceptance (`ok`), and `bash -lc "! rg -n '^PUBLISHED_(BOUNDED_WILDCARD_RAW|COMPILED_PATTERN)_MODULE_HELPER_CASE_IDS =' tests/python/test_module_workflow_parity_suite.py"` (passes with no matches).
