# RBR-0754: Collapse module-workflow compiled-pattern text-model subset sidecars onto canonical published slice

Status: ready
Owner: architecture-implementation
Created: 2026-03-20

## Goal
- Remove the detached `str` and `bytes` subset tables from `tests/python/test_module_workflow_parity_suite.py` now that the same rows already exist inside the canonical published compiled-pattern module-helper slice.
- Make `PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASE_IDS` and `PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES` the sole published owners for this compiled-pattern module-helper surface inside the module-workflow parity owner.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` stops defining or reading these detached subset sidecars:
  - `PUBLISHED_LITERAL_STR_COMPILED_PATTERN_MODULE_HELPER_CASE_IDS`
  - `PUBLISHED_LITERAL_STR_COMPILED_PATTERN_MODULE_HELPER_CASES`
  - `PUBLISHED_BYTES_COMPILED_PATTERN_MODULE_HELPER_CASE_IDS`
  - `PUBLISHED_BYTES_COMPILED_PATTERN_MODULE_HELPER_CASES`
- `test_module_workflow_surface_publishes_compiled_pattern_module_helpers_from_direct_cases` no longer relies on deleted text-model subset tables just to restate ids that are already present in `PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES`.
- The file may keep a tiny selector/helper if useful, but it must derive the `str` and `bytes` groupings directly from `PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES` rather than introducing another mirrored tuple/list/map block.
- Preserve the exact current published ordering and payloads:
  - the canonical combined published slice stays, in order:
    - `workflow-module-search-str-compiled-pattern`
    - `workflow-module-match-str-compiled-pattern`
    - `workflow-module-search-str-bounded-wildcard-ignorecase-compiled-pattern`
    - `workflow-module-match-str-bounded-wildcard-compiled-pattern`
    - `workflow-module-fullmatch-str-bounded-wildcard-compiled-pattern`
    - `workflow-module-search-bytes-verbose-regression-compiled-pattern`
    - `workflow-module-fullmatch-bytes-verbose-regression-compiled-pattern`
    - `workflow-module-split-str-compiled-pattern`
    - `workflow-module-findall-bytes-compiled-pattern`
  - the `str` subset derivable from that canonical slice stays, in order:
    - `workflow-module-search-str-compiled-pattern`
    - `workflow-module-match-str-compiled-pattern`
    - `workflow-module-search-str-bounded-wildcard-ignorecase-compiled-pattern`
    - `workflow-module-match-str-bounded-wildcard-compiled-pattern`
    - `workflow-module-fullmatch-str-bounded-wildcard-compiled-pattern`
    - `workflow-module-split-str-compiled-pattern`
  - the `bytes` subset derivable from that canonical slice stays, in order:
    - `workflow-module-search-bytes-verbose-regression-compiled-pattern`
    - `workflow-module-fullmatch-bytes-verbose-regression-compiled-pattern`
    - `workflow-module-findall-bytes-compiled-pattern`
- Keep the remaining owner-local coverage unchanged:
  - do not change `PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASE_IDS`, `PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES`, `BOUNDED_WILDCARD_MODULE_MATCH_CASES`, the bounded-wildcard raw module-helper checks, compiled-pattern direct-case alignment, collection-helper coverage, keyword-argument coverage, fake-native-boundary coverage, or direct-test bucket accounting outside this subset-mirror cleanup.
- Keep scope structural only:
  - do not edit `tests/conformance/fixtures/module_workflow_surface.py`, `tests/conformance/test_combined_correctness_scorecards.py`, `reports/correctness/latest.py`, `python/rebar/`, `crates/`, benchmark files, README copy, or tracked project-state prose in this run.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
import tests.python.test_module_workflow_parity_suite as mod

assert tuple(
    case.case_id
    for case in mod.PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES
    if case.text_model == "str"
) == (
    "workflow-module-search-str-compiled-pattern",
    "workflow-module-match-str-compiled-pattern",
    "workflow-module-search-str-bounded-wildcard-ignorecase-compiled-pattern",
    "workflow-module-match-str-bounded-wildcard-compiled-pattern",
    "workflow-module-fullmatch-str-bounded-wildcard-compiled-pattern",
    "workflow-module-split-str-compiled-pattern",
)
assert tuple(
    case.case_id
    for case in mod.PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES
    if case.text_model == "bytes"
) == (
    "workflow-module-search-bytes-verbose-regression-compiled-pattern",
    "workflow-module-fullmatch-bytes-verbose-regression-compiled-pattern",
    "workflow-module-findall-bytes-compiled-pattern",
)
print("ok")
PY`
  - `bash -lc "! rg -n 'PUBLISHED_LITERAL_STR_COMPILED_PATTERN_MODULE_HELPER_CASE_IDS|PUBLISHED_LITERAL_STR_COMPILED_PATTERN_MODULE_HELPER_CASES|PUBLISHED_BYTES_COMPILED_PATTERN_MODULE_HELPER_CASE_IDS|PUBLISHED_BYTES_COMPILED_PATTERN_MODULE_HELPER_CASES' tests/python/test_module_workflow_parity_suite.py"`

## Constraints
- Keep this cleanup limited to `tests/python/test_module_workflow_parity_suite.py`. Do not use this run to collapse the canonical combined compiled-pattern slice itself, rewrite shared helper APIs, or broaden the module-workflow correctness frontier.
- Prefer deriving the text-model subsets from the existing canonical published slice over introducing another registry or another fixture-selection layer.

## Notes
- `RBR-0754` is the next available task id in the current checkout:
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
print('reserved_tail', reserved_sorted[-20:])
for n in range(int(re.search(r'\d+', existing_sorted[-1]).group()), int(re.search(r'\d+', existing_sorted[-1]).group()) + 160):
    rid = f'RBR-{n:04d}'
    if rid not in existing and rid not in reserved:
        print('next_free', rid)
        break
PY` reported the existing tail through `RBR-0753`, no reserved missing tail ids, and `next_free RBR-0754`.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added; and
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`.
- JSON burn-down is complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication is concrete and bounded in the current checkout:
  - `rg -n 'PUBLISHED_LITERAL_STR_COMPILED_PATTERN_MODULE_HELPER_CASE_IDS|PUBLISHED_LITERAL_STR_COMPILED_PATTERN_MODULE_HELPER_CASES|PUBLISHED_BYTES_COMPILED_PATTERN_MODULE_HELPER_CASE_IDS|PUBLISHED_BYTES_COMPILED_PATTERN_MODULE_HELPER_CASES' tests/python/test_module_workflow_parity_suite.py` currently shows only one definition block for each subset sidecar plus their single remaining test reads in `test_module_workflow_surface_publishes_compiled_pattern_module_helpers_from_direct_cases`;
  - the canonical grouped-subset probe in Acceptance already passes in the current checkout (`ok`), so the remaining subset tables are now redundant mirrors of the combined published slice; and
  - `bash -lc "! rg -n 'PUBLISHED_LITERAL_STR_COMPILED_PATTERN_MODULE_HELPER_CASE_IDS|PUBLISHED_LITERAL_STR_COMPILED_PATTERN_MODULE_HELPER_CASES|PUBLISHED_BYTES_COMPILED_PATTERN_MODULE_HELPER_CASE_IDS|PUBLISHED_BYTES_COMPILED_PATTERN_MODULE_HELPER_CASES' tests/python/test_module_workflow_parity_suite.py"` currently fails exactly on this cleanup because those mirrored subset tables still exist.
- Baseline verification is green in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py` passed (`654 passed, 1 skipped in 0.50s`).
