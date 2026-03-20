# RBR-0748: Collapse module-workflow bounded-wildcard raw module-helper direct-case sidecars onto canonical owner cases

Status: done
Owner: architecture-implementation
Created: 2026-03-20
Completed: 2026-03-20

## Goal
- Remove the detached `PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_DIRECT_CASE_IDS` and `PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_DIRECT_CASES` tables from `tests/python/test_module_workflow_parity_suite.py` now that the same bounded-wildcard raw module-helper slice is already published in `tests/conformance/fixtures/module_workflow_surface.py` and still owned locally by `BOUNDED_WILDCARD_MODULE_MATCH_CASES`.
- Make `PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_CASE_IDS`, `PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_CASES`, and `BOUNDED_WILDCARD_MODULE_MATCH_CASES` the sole canonical owners for this published raw module-helper pair inside the module-workflow parity owner.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` stops defining or reading `PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_DIRECT_CASE_IDS`.
- `tests/python/test_module_workflow_parity_suite.py` stops defining or reading `PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_DIRECT_CASES`.
- The published bounded-wildcard raw module-helper alignment derives directly from canonical owner data instead of from the deleted direct-case sidecars:
  - `test_module_workflow_surface_publishes_bounded_wildcard_raw_module_helpers_from_direct_cases` no longer compares fixture rows against a deleted top-level direct-case tuple.
  - That test still compares the exact two published fixture rows in `PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_CASES` against the matching owner-local direct cases selected from `BOUNDED_WILDCARD_MODULE_MATCH_CASES`.
  - If a tiny file-local selector/helper is useful, derive it from `BOUNDED_WILDCARD_MODULE_MATCH_CASES` plus `PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_CASES` rather than introducing another mirrored tuple/list/map block.
- Preserve the current effective ordering and payloads exactly. The canonical alignment must stay:
  - direct cases:
    - `module-search-ignorecase-bounded-hit`, helper `search`, pattern `"a.c"`, string `"ABC"`, flags `2`, `compiled=False`
    - `module-match-bounded-miss`, helper `match`, pattern `"a.c"`, string `"zabc"`, flags `0`, `compiled=False`
  - published fixture rows:
    - `workflow-module-search-str-bounded-wildcard-ignorecase`, helper `search`, pattern `"a.c"`, args `("ABC",)`, flags `2`, `use_compiled_pattern=False`
    - `workflow-module-match-str-bounded-wildcard-miss`, helper `match`, pattern `"a.c"`, args `("zabc",)`, flags `0`, `use_compiled_pattern=False`
- Keep the remaining owner-local bounded-wildcard coverage unchanged:
  - do not change `BOUNDED_WILDCARD_MODULE_MATCH_CASES`, `PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_CASE_IDS`, `PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_CASES`, `BOUNDED_WILDCARD_MODULE_COLLECTION_CASES`, compiled bounded-wildcard coverage, direct-test bucket accounting, fake-native-boundary coverage, or placeholder-path assertions outside this already-published raw module-helper pair.
- Keep scope structural only:
  - do not edit `tests/conformance/fixtures/module_workflow_surface.py`, `tests/conformance/test_combined_correctness_scorecards.py`, `reports/correctness/latest.py`, `python/rebar/`, `crates/`, benchmark files, README copy, or tracked project-state prose in this run.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
import tests.python.test_module_workflow_parity_suite as mod

selected_direct_cases = tuple(
    case
    for case in mod.BOUNDED_WILDCARD_MODULE_MATCH_CASES
    if case.case_id in (
        "module-search-ignorecase-bounded-hit",
        "module-match-bounded-miss",
    )
)

assert tuple(case.case_id for case in selected_direct_cases) == (
    "module-search-ignorecase-bounded-hit",
    "module-match-bounded-miss",
)
assert tuple(case.case_id for case in mod.PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_CASES) == (
    "workflow-module-search-str-bounded-wildcard-ignorecase",
    "workflow-module-match-str-bounded-wildcard-miss",
)
assert tuple(case.helper for case in mod.PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_CASES) == tuple(
    case.helper for case in selected_direct_cases
)
for fixture_case, direct_case in zip(
    mod.PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_CASES,
    selected_direct_cases,
):
    assert fixture_case.use_compiled_pattern is False
    assert fixture_case.text_model == "str"
    assert mod.case_pattern(fixture_case) == direct_case.pattern
    assert tuple(fixture_case.args) == (direct_case.string,)
    assert fixture_case.flags == direct_case.flags
print("ok")
PY`
  - `bash -lc "! rg -n 'PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_DIRECT_CASE_IDS|PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_DIRECT_CASES' tests/python/test_module_workflow_parity_suite.py"`

## Constraints
- Keep this cleanup limited to the module-workflow owner surface inside `tests/python/test_module_workflow_parity_suite.py`. Do not use this run to collapse the compiled-pattern module-helper direct sidecars, rewrite shared helper APIs, or broaden the bounded-wildcard parity frontier.
- Prefer deriving the published raw-module-helper alignment directly from the existing fixture-backed selection plus `BOUNDED_WILDCARD_MODULE_MATCH_CASES` over introducing another helper registry.

## Notes
- `RBR-0748` is the next available task id in the current checkout:
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
PY` reported the existing tail through `RBR-0747`, no reserved missing tail ids, and `next_free RBR-0748`.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added; and
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`.
- JSON burn-down is complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- This cleanup is newly unblocked by the landed bounded-wildcard raw module-helper publication on the same owner path:
  - `RBR-0747` published `workflow-module-search-str-bounded-wildcard-ignorecase` and `workflow-module-match-str-bounded-wildcard-miss` onto `tests/conformance/fixtures/module_workflow_surface.py`; and
  - the direct-vs-fixture probe in Acceptance already passes in the current checkout (`ok`), so the remaining direct-case sidecars are now redundant owner-local mirrors.
- The duplicated owner layer is concrete and bounded in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py` passed (`654 passed, 1 skipped in 0.50s`);
  - the direct-vs-fixture probe in Acceptance already passed in the current checkout (`ok`);
  - `rg -n 'PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_DIRECT_CASE_IDS|PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_DIRECT_CASES' tests/python/test_module_workflow_parity_suite.py` currently shows one declaration block plus the remaining alignment-test reads in this file; and
  - the final `rg` absence check in Acceptance currently fails exactly on this cleanup because those mirrored direct-case sidecars still exist.

## Completion
- 2026-03-20: Removed `PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_DIRECT_CASE_IDS` and `PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_DIRECT_CASES` from `tests/python/test_module_workflow_parity_suite.py`.
- Reworked `test_module_workflow_surface_publishes_bounded_wildcard_raw_module_helpers_from_direct_cases` to select the matching owner-local raw helper cases directly from `BOUNDED_WILDCARD_MODULE_MATCH_CASES` using signatures derived from `PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_CASES`, preserving the existing `search` then `match` alignment and payloads without another mirrored sidecar block.
- Verification passed with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py`, the task-local direct-vs-fixture probe from Acceptance (`ok`), and `bash -lc "! rg -n 'PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_DIRECT_CASE_IDS|PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_DIRECT_CASES' tests/python/test_module_workflow_parity_suite.py"`.
