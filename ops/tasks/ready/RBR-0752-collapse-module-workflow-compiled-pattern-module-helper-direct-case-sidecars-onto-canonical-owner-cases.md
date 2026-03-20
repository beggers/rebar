# RBR-0752: Collapse module-workflow compiled-pattern module-helper direct-case sidecars onto canonical owner cases

Status: ready
Owner: architecture-implementation
Created: 2026-03-20

## Goal
- Remove the detached compiled-pattern direct-case registries from `tests/python/test_module_workflow_parity_suite.py` now that the exact same eight-row compiled-pattern module-helper slice is already published in `tests/conformance/fixtures/module_workflow_surface.py`.
- Make `PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASE_IDS`, `PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES`, `COMPILED_PATTERN_MODULE_HELPER_CASES`, and `BOUNDED_WILDCARD_MODULE_MATCH_CASES` the sole canonical owners for this published compiled-pattern module-helper slice inside the module-workflow parity owner.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` stops defining or reading these detached direct-case sidecars:
  - `PUBLISHED_LITERAL_STR_COMPILED_PATTERN_MODULE_HELPER_DIRECT_CASE_IDS`
  - `PUBLISHED_LITERAL_STR_COMPILED_PATTERN_MODULE_HELPER_DIRECT_CASES`
  - `PUBLISHED_BYTES_COMPILED_PATTERN_MODULE_HELPER_DIRECT_CASE_IDS`
  - `PUBLISHED_BYTES_COMPILED_PATTERN_MODULE_HELPER_DIRECT_CASES`
  - `PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_DIRECT_CASE_IDS`
  - `_COMPILED_PATTERN_MODULE_HELPER_DIRECT_CASES_BY_ID`
  - `PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_DIRECT_CASES`
- `test_module_workflow_surface_publishes_compiled_pattern_module_helpers_from_direct_cases` derives the matching direct cases directly from `COMPILED_PATTERN_MODULE_HELPER_CASES` plus `BOUNDED_WILDCARD_MODULE_MATCH_CASES` in the published fixture row order instead of comparing against a deleted direct-case tuple.
- Preserve the exact current alignment and payloads:
  - published fixture rows stay, in order:
    - `workflow-module-search-str-compiled-pattern`
    - `workflow-module-match-str-compiled-pattern`
    - `workflow-module-search-str-bounded-wildcard-ignorecase-compiled-pattern`
    - `workflow-module-match-str-bounded-wildcard-compiled-pattern`
    - `workflow-module-search-bytes-verbose-regression-compiled-pattern`
    - `workflow-module-fullmatch-bytes-verbose-regression-compiled-pattern`
    - `workflow-module-split-str-compiled-pattern`
    - `workflow-module-findall-bytes-compiled-pattern`
  - matching direct owner cases stay, in order:
    - `compiled-pattern-search-str`
    - `compiled-pattern-match-str`
    - `compiled-module-search-ignorecase-bounded-hit`
    - `compiled-module-match-bounded-hit`
    - `compiled-pattern-search-bytes-verbose-regression`
    - `compiled-pattern-fullmatch-bytes-verbose-regression`
    - `compiled-pattern-split-str-maxsplit`
    - `compiled-pattern-findall-bytes`
  - helper, pattern, args, flags, and compiled-pattern routing remain unchanged for each aligned pair.
- Keep the remaining owner-local coverage unchanged:
  - do not change `PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASE_IDS`, `PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES`, `COMPILED_PATTERN_MODULE_HELPER_CASES`, `BOUNDED_WILDCARD_MODULE_MATCH_CASES`, the bounded-wildcard raw module-helper checks, the bounded-wildcard compiled `fullmatch()` owner row, compiled-pattern collection/replacement coverage, keyword-argument coverage, fake-native-boundary coverage, or direct-test bucket accounting outside this compiled-pattern direct-case mirror cleanup.
- Keep scope structural only:
  - do not edit `tests/conformance/fixtures/module_workflow_surface.py`, `tests/conformance/test_combined_correctness_scorecards.py`, `reports/correctness/latest.py`, `python/rebar/`, `crates/`, benchmark files, README copy, or tracked project-state prose in this run.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
import tests.python.test_module_workflow_parity_suite as mod

def direct_signature(case):
    return (
        case.helper,
        case.pattern,
        tuple(case.args) if hasattr(case, "args") else (case.string,),
        case.flags,
        getattr(case, "compiled", True),
    )

direct_cases_by_signature = {
    direct_signature(case): case
    for case in (*mod.COMPILED_PATTERN_MODULE_HELPER_CASES, *mod.BOUNDED_WILDCARD_MODULE_MATCH_CASES)
}
selected_direct_cases = tuple(
    direct_cases_by_signature[
        (
            case.helper,
            mod.case_pattern(case),
            tuple(case.args),
            case.flags,
            case.use_compiled_pattern,
        )
    ]
    for case in mod.PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES
)

assert tuple(case.case_id for case in mod.PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES) == (
    "workflow-module-search-str-compiled-pattern",
    "workflow-module-match-str-compiled-pattern",
    "workflow-module-search-str-bounded-wildcard-ignorecase-compiled-pattern",
    "workflow-module-match-str-bounded-wildcard-compiled-pattern",
    "workflow-module-search-bytes-verbose-regression-compiled-pattern",
    "workflow-module-fullmatch-bytes-verbose-regression-compiled-pattern",
    "workflow-module-split-str-compiled-pattern",
    "workflow-module-findall-bytes-compiled-pattern",
)
assert tuple(case.case_id for case in selected_direct_cases) == (
    "compiled-pattern-search-str",
    "compiled-pattern-match-str",
    "compiled-module-search-ignorecase-bounded-hit",
    "compiled-module-match-bounded-hit",
    "compiled-pattern-search-bytes-verbose-regression",
    "compiled-pattern-fullmatch-bytes-verbose-regression",
    "compiled-pattern-split-str-maxsplit",
    "compiled-pattern-findall-bytes",
)
assert tuple(case.helper for case in mod.PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES) == tuple(
    case.helper for case in selected_direct_cases
)

for fixture_case, direct_case in zip(
    mod.PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES,
    selected_direct_cases,
):
    assert fixture_case.use_compiled_pattern is True
    direct_args = tuple(direct_case.args) if hasattr(direct_case, "args") else (direct_case.string,)
    assert fixture_case.text_model == ("bytes" if isinstance(direct_case.pattern, bytes) else "str")
    assert mod.case_pattern(fixture_case) == direct_case.pattern
    assert tuple(fixture_case.args) == direct_args
    assert fixture_case.flags == direct_case.flags

print("ok")
PY`
  - `bash -lc "! rg -n 'PUBLISHED_LITERAL_STR_COMPILED_PATTERN_MODULE_HELPER_DIRECT_CASE_IDS|PUBLISHED_LITERAL_STR_COMPILED_PATTERN_MODULE_HELPER_DIRECT_CASES|PUBLISHED_BYTES_COMPILED_PATTERN_MODULE_HELPER_DIRECT_CASE_IDS|PUBLISHED_BYTES_COMPILED_PATTERN_MODULE_HELPER_DIRECT_CASES|PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_DIRECT_CASE_IDS|_COMPILED_PATTERN_MODULE_HELPER_DIRECT_CASES_BY_ID|PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_DIRECT_CASES' tests/python/test_module_workflow_parity_suite.py"`

## Constraints
- Keep this cleanup limited to `tests/python/test_module_workflow_parity_suite.py`. Do not use this run to publish the remaining compiled-pattern bounded-wildcard `fullmatch()` row, collapse unrelated support-contract tests, rewrite shared helper APIs, or broaden the module-workflow correctness frontier.
- Prefer deriving the direct-vs-fixture alignment from the existing canonical fixture-backed rows plus owner-local direct cases over introducing another registry, abstraction layer, or detached subset table.

## Notes
- `RBR-0752` is the next available task id in the current checkout:
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
for n in range(int(re.search(r'\d+', existing_sorted[-1]).group()), int(re.search(r'\d+', existing_sorted[-1]).group()) + 120):
    rid = f'RBR-{n:04d}'
    if rid not in existing and rid not in reserved:
        print('next_free', rid)
        break
PY` reported the existing tail through `RBR-0751`, no reserved missing tail ids, and `next_free RBR-0752`.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added; and
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`.
- JSON burn-down is complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- This cleanup is newly unblocked by the landed compiled-pattern publication on the same owner path:
  - `RBR-0751` added `workflow-module-search-str-bounded-wildcard-ignorecase-compiled-pattern` and `workflow-module-match-str-bounded-wildcard-compiled-pattern` to `tests/conformance/fixtures/module_workflow_surface.py`, so the canonical fixture-backed owner path now contains the full eight-row compiled-pattern module-helper slice already mirrored by the direct-case sidecars in `tests/python/test_module_workflow_parity_suite.py`; and
  - `rg -n "PUBLISHED_.*COMPILED_PATTERN_MODULE_HELPER_DIRECT_CASE" tests/python/test_module_workflow_parity_suite.py` currently shows the remaining direct-case sidecar block plus its test reads in that owner file.
- The duplicated owner layer is concrete and bounded in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py` passed (`654 passed, 1 skipped in 0.50s`);
  - the direct-vs-fixture probe in Acceptance already passed in the current checkout (`ok`); and
  - the final `rg` absence check in Acceptance currently fails exactly on this cleanup because the direct-case sidecars still exist.
