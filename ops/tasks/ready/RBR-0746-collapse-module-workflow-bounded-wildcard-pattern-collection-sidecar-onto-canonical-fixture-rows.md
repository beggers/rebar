# RBR-0746: Collapse module-workflow bounded-wildcard pattern-collection sidecar onto canonical fixture rows

Status: ready
Owner: architecture-implementation
Created: 2026-03-20

## Goal
- Remove the detached `BOUNDED_WILDCARD_PATTERN_COLLECTION_CASES` table from `tests/python/test_module_workflow_parity_suite.py` now that the exact same bounded-wildcard bound-`Pattern` collection rows are already published in `tests/conformance/fixtures/module_workflow_surface.py`.
- Make `MODULE_WORKFLOW_BOUNDED_WILDCARD_PATTERN_CASE_IDS`, `PATTERN_CASES`, and `PATTERN_CASES_BY_ID` the sole canonical owners for this published collection pair inside the module-workflow parity owner.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` stops defining or reading `BOUNDED_WILDCARD_PATTERN_COLLECTION_CASES`.
- `tests/python/test_module_workflow_parity_suite.py` stops defining or reading `BoundedWildcardPatternCase`.
- `tests/python/test_module_workflow_parity_suite.py` stops defining or reading `_call_bounded_wildcard_pattern_helper`.
- The now-published bounded-wildcard bound-`Pattern` collection coverage derives directly from the canonical fixture-backed rows instead of from the deleted wildcard-specific sidecar:
  - `test_bounded_wildcard_pattern_collection_helpers_match_cpython` no longer parametrizes over a deleted local collection table.
  - That test consumes the exact published `FixtureCase` rows selected by the existing canonical ids `workflow-pattern-findall-str-bounded-wildcard` and `workflow-pattern-finditer-str-bounded-wildcard`.
  - If a tiny file-local selector/helper is useful, derive it from `PATTERN_CASES`, `PATTERN_CASES_BY_ID`, and `MODULE_WORKFLOW_BOUNDED_WILDCARD_PATTERN_CASE_IDS` instead of introducing another mirrored tuple/list/map block.
- Preserve the current effective published row order and payloads exactly. The canonical fixture-backed collection selection must stay:
  - `workflow-pattern-findall-str-bounded-wildcard`, helper `findall`, pattern `"a.c"`, args `("zabcaxcz", 1, 7)`, flags `0`
  - `workflow-pattern-finditer-str-bounded-wildcard`, helper `finditer`, pattern `"a.c"`, args `("zabcaxcx", 1, 7)`, flags `0`
- Keep the remaining owner-local bounded-wildcard coverage unchanged:
  - do not change `_published_bounded_wildcard_pattern_match_cases()`, `BOUNDED_WILDCARD_MODULE_MATCH_CASES`, `BOUNDED_WILDCARD_MODULE_COLLECTION_CASES`, `test_rebar_bounded_wildcard_unsupported_paths_keep_placeholder_messages`, fake-native-boundary coverage, or direct-test bucket accounting outside this already-published collection pair.
- Keep scope structural only:
  - do not edit `tests/conformance/fixtures/module_workflow_surface.py`, `tests/conformance/test_combined_correctness_scorecards.py`, `reports/correctness/latest.py`, `python/rebar/`, `crates/`, benchmark files, README copy, or tracked project-state prose in this run.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
import tests.python.test_module_workflow_parity_suite as mod

pattern_cases_by_id = {case.case_id: case for case in mod.PATTERN_CASES}

assert tuple(
    (case.case_id, case.helper, mod.case_pattern(case), tuple(case.args), case.flags or 0)
    for case in (
        pattern_cases_by_id[case_id]
        for case_id in (
            "workflow-pattern-findall-str-bounded-wildcard",
            "workflow-pattern-finditer-str-bounded-wildcard",
        )
    )
) == (
    ("workflow-pattern-findall-str-bounded-wildcard", "findall", "a.c", ("zabcaxcz", 1, 7), 0),
    ("workflow-pattern-finditer-str-bounded-wildcard", "finditer", "a.c", ("zabcaxcx", 1, 7), 0),
)

print("ok")
PY`
  - `bash -lc "! rg -n 'BOUNDED_WILDCARD_PATTERN_COLLECTION_CASES|BoundedWildcardPatternCase|_call_bounded_wildcard_pattern_helper' tests/python/test_module_workflow_parity_suite.py"`

## Constraints
- Keep this cleanup structural only. The point is to delete one more duplicated owner-local layer now that the same bounded-wildcard bound-`Pattern` collection rows are published on the canonical module-workflow fixture path, not to reinterpret wildcard behavior or broaden the published frontier.
- Prefer the existing fixture-backed owner path over another shared abstraction layer or another wildcard-specific registry.

## Notes
- `RBR-0746` is the next available task id in the current checkout:
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
print('highest_existing_tail', existing_sorted[-10:])
print('reserved_tail', reserved_sorted[-10:])
for n in range(int(re.search(r'\d+', existing_sorted[-1]).group()), int(re.search(r'\d+', existing_sorted[-1]).group()) + 80):
    rid = f'RBR-{n:04d}'
    if rid not in existing and rid not in reserved:
        print('next_free', rid)
        break
PY` reported the existing tail through `RBR-0745`, no reserved missing tail ids, and `next_free RBR-0746`.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added; and
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`.
- JSON burn-down is complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- This cleanup is newly unblocked by the landed bounded-wildcard publication work on the same owner path:
  - `RBR-0745` published `workflow-pattern-findall-str-bounded-wildcard` and `workflow-pattern-finditer-str-bounded-wildcard` onto `tests/conformance/fixtures/module_workflow_surface.py`; and
  - the exact collection-row probe in Acceptance already passes in the current checkout (`ok`), so the remaining local pattern-collection table is now a redundant owner-local mirror.
- The duplicated owner layer is concrete and bounded in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py` currently passes (`653 passed, 1 skipped in 0.51s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'bounded_wildcard and pattern_collection_helpers'` currently passes (`4 passed, 650 deselected in 0.10s`);
  - the canonical-row probe in Acceptance already passes in the current checkout (`ok`); and
  - the final `rg` absence check in Acceptance currently fails exactly on this cleanup because `BOUNDED_WILDCARD_PATTERN_COLLECTION_CASES`, `BoundedWildcardPatternCase`, and `_call_bounded_wildcard_pattern_helper` still exist.
