# RBR-0756: Collapse module-workflow collection-helper ladders onto canonical case surfaces

Status: ready
Owner: architecture-implementation
Created: 2026-03-20

## Goal
- Remove the six helper-specific collection case ladders from `tests/python/test_module_workflow_parity_suite.py`; they currently restate the same split/findall/finditer coverage across parallel module-vs-pattern tuples after the suite already has one fixture-backed owner path plus one set of local dataclasses.
- Make one module collection surface and one pattern collection surface the sole owner-local case tables for the non-wildcard collection-helper parity coverage inside the module-workflow suite.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` stops defining or reading these detached helper-specific case ladders:
  - `MODULE_SPLIT_COLLECTION_CASES`
  - `PATTERN_SPLIT_COLLECTION_CASES`
  - `MODULE_FINDALL_COLLECTION_CASES`
  - `PATTERN_FINDALL_COLLECTION_CASES`
  - `MODULE_FINDITER_COLLECTION_CASES`
  - `PATTERN_FINDITER_COLLECTION_CASES`
- The file defines `MODULE_COLLECTION_CASES` and `PATTERN_COLLECTION_CASES` as the canonical owner-local collection surfaces for this non-wildcard split/findall/finditer coverage.
- If a tiny selector/helper is useful, derive helper-specific parametrization directly from `MODULE_COLLECTION_CASES` and `PATTERN_COLLECTION_CASES` instead of reintroducing another mirrored tuple per helper.
- Preserve the exact current helper-specific subsequences and ordering:
  - `MODULE_COLLECTION_CASES` filtered to `helper == "split"` yields, in order:
    - `module-split-str-leading-trailing`
    - `module-split-str-no-match`
    - `module-split-str-maxsplit-one`
    - `module-split-str-negative-maxsplit`
    - `module-split-bytes-maxsplit-one`
  - `PATTERN_COLLECTION_CASES` filtered to `helper == "split"` yields, in order:
    - `pattern-split-bytes-maxsplit`
    - `pattern-split-str-no-match`
    - `pattern-split-str-repeated`
    - `pattern-split-str-maxsplit-one`
    - `pattern-split-str-negative-maxsplit`
  - `MODULE_COLLECTION_CASES` filtered to `helper == "findall"` yields, in order:
    - `module-findall-bytes-repeated`
    - `module-findall-nonliteral-str`
    - `module-findall-str-repeated`
    - `module-findall-str-no-match`
  - `PATTERN_COLLECTION_CASES` filtered to `helper == "findall"` yields, in order:
    - `pattern-findall-str-no-match`
    - `pattern-findall-str-bounded`
    - `pattern-findall-str-bounded-no-match`
    - `pattern-findall-bytes-bounded`
  - `MODULE_COLLECTION_CASES` filtered to `helper == "finditer"` yields, in order:
    - `module-finditer-str-repeated`
    - `module-finditer-str-no-match`
    - `module-finditer-bytes-repeated`
  - `PATTERN_COLLECTION_CASES` filtered to `helper == "finditer"` yields, in order:
    - `pattern-finditer-bytes-bounded`
    - `pattern-finditer-str-bounded`
    - `pattern-finditer-str-bounded-no-match`
- Keep the remaining owner-local coverage unchanged:
  - do not change `COLLECTION_FIXTURE_BUNDLE`, `PUBLISHED_COLLECTION_MODULE_CASES`, `PUBLISHED_COLLECTION_PATTERN_CASES`, `COLLECTION_TARGET_FIXTURE_CASE_IDS`, `COLLECTION_REPLACEMENT_UNCOVERED_CASE_IDS`, `BOUNDED_WILDCARD_MODULE_COLLECTION_CASES`, bounded-wildcard collection tests, literal collection matrix coverage, collection type-error coverage, unsupported-case coverage, replacement coverage, or direct-test bucket accounting outside this ladder cleanup.
- Keep scope structural only:
  - do not edit `tests/conformance/fixtures/collection_replacement_workflows.py`, `tests/conformance/fixtures/module_workflow_surface.py`, `tests/conformance/test_combined_correctness_scorecards.py`, `reports/correctness/latest.py`, `python/rebar/`, `crates/`, benchmark files, README copy, or tracked project-state prose in this run.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
import tests.python.test_module_workflow_parity_suite as mod

assert tuple(case.case_id for case in mod.MODULE_COLLECTION_CASES if case.helper == "split") == (
    "module-split-str-leading-trailing",
    "module-split-str-no-match",
    "module-split-str-maxsplit-one",
    "module-split-str-negative-maxsplit",
    "module-split-bytes-maxsplit-one",
)
assert tuple(case.case_id for case in mod.PATTERN_COLLECTION_CASES if case.helper == "split") == (
    "pattern-split-bytes-maxsplit",
    "pattern-split-str-no-match",
    "pattern-split-str-repeated",
    "pattern-split-str-maxsplit-one",
    "pattern-split-str-negative-maxsplit",
)
assert tuple(case.case_id for case in mod.MODULE_COLLECTION_CASES if case.helper == "findall") == (
    "module-findall-bytes-repeated",
    "module-findall-nonliteral-str",
    "module-findall-str-repeated",
    "module-findall-str-no-match",
)
assert tuple(case.case_id for case in mod.PATTERN_COLLECTION_CASES if case.helper == "findall") == (
    "pattern-findall-str-no-match",
    "pattern-findall-str-bounded",
    "pattern-findall-str-bounded-no-match",
    "pattern-findall-bytes-bounded",
)
assert tuple(case.case_id for case in mod.MODULE_COLLECTION_CASES if case.helper == "finditer") == (
    "module-finditer-str-repeated",
    "module-finditer-str-no-match",
    "module-finditer-bytes-repeated",
)
assert tuple(case.case_id for case in mod.PATTERN_COLLECTION_CASES if case.helper == "finditer") == (
    "pattern-finditer-bytes-bounded",
    "pattern-finditer-str-bounded",
    "pattern-finditer-str-bounded-no-match",
)
print("ok")
PY`
  - `bash -lc "! rg -n '^(MODULE|PATTERN)_(SPLIT|FINDALL|FINDITER)_COLLECTION_CASES =' tests/python/test_module_workflow_parity_suite.py"`

## Constraints
- Keep this cleanup limited to `tests/python/test_module_workflow_parity_suite.py`. Do not use this run to merge collection coverage into another fixture, broaden the published correctness frontier, or rewrite the literal-collection matrix helpers.
- Prefer deleting the six duplicated ladders in favor of two canonical owner-local surfaces over adding another registry layer or another helper-specific table.

## Notes
- `RBR-0756` is the next available task id in the current checkout:
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
PY` reported the existing tail through `RBR-0755`, no reserved missing tail ids, and `next_free RBR-0756`.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added; and
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`.
- JSON burn-down is complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The detached owner layer is concrete and bounded in the current checkout:
  - `rg -n '^(MODULE|PATTERN)_(SPLIT|FINDALL|FINDITER)_COLLECTION_CASES =' tests/python/test_module_workflow_parity_suite.py` currently shows exactly six helper-specific ladder definitions in `tests/python/test_module_workflow_parity_suite.py`;
  - the future acceptance probe already isolates the intended end state and currently fails exactly on this cleanup because `MODULE_COLLECTION_CASES` and `PATTERN_COLLECTION_CASES` do not exist yet; and
  - `bash -lc "! rg -n '^(MODULE|PATTERN)_(SPLIT|FINDALL|FINDITER)_COLLECTION_CASES =' tests/python/test_module_workflow_parity_suite.py"` currently fails exactly on this cleanup because those six ladders are still present.
- Baseline verification is green in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py` passed (`657 passed, 1 skipped in 0.50s`).
