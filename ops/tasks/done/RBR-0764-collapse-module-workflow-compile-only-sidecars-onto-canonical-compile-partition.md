# RBR-0764: Collapse module-workflow compile-only sidecars onto canonical compile partition

Status: done
Owner: architecture-implementation
Created: 2026-03-20
Completed: 2026-03-20

## Goal
- Remove the remaining compile-only selection sidecars from `tests/python/test_module_workflow_parity_suite.py`; `MODULE_WORKFLOW_COMPILE_ONLY_CASE_IDS`, `MODULE_WORKFLOW_COMPILE_ONLY_PATTERNS`, and `MODULE_WORKFLOW_COMPILE_ONLY_OPERATION_HELPER_COUNTS` currently mirror the already-loaded `COMPILE_CASES` partition exactly, and `test_module_workflow_surface_compile_case_selection_preserves_row_order` re-loads the same `module_workflow_surface.py` rows through a one-off `FixtureBundleSpec(...)`.
- Make the loaded compile partition from `MODULE_WORKFLOW_BUNDLE` the sole source of truth for the module-workflow compile-only contract.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` stops defining or reading these detached compile-only sidecars:
  - `MODULE_WORKFLOW_COMPILE_ONLY_CASE_IDS`
  - `MODULE_WORKFLOW_COMPILE_ONLY_PATTERNS`
  - `MODULE_WORKFLOW_COMPILE_ONLY_OPERATION_HELPER_COUNTS`
- `test_module_workflow_surface_compile_case_selection_preserves_row_order` no longer re-loads `module_workflow_surface.py` through a compile-only `FixtureBundleSpec(...)` or `load_fixture_bundles(...)` call; it derives its compile frontier directly from `COMPILE_CASES`, `MODULE_WORKFLOW_BUNDLE.manifest.cases`, or one tiny file-local helper over those already-loaded rows.
- The compile-only contract remains exact after the cleanup:
  - compile case order stays:
    - `workflow-compile-str-literal`
    - `workflow-compile-str-anchored-literal`
    - `workflow-compile-str-bounded-wildcard`
    - `workflow-compile-str-bounded-wildcard-ignorecase`
    - `workflow-compile-str-verbose-regression`
    - `workflow-compile-str-multiline-regression`
    - `workflow-compile-bytes-verbose-regression`
    - `workflow-compile-bytes-multiline-regression`
    - `workflow-compile-bytes-literal`
  - the compile-only pattern contract stays `frozenset(case_pattern(case) for case in COMPILE_CASES)`;
  - the compile-only operation/helper counts stay `Counter((case.operation, case.helper) for case in COMPILE_CASES)`, i.e. nine `("compile", None)` rows;
  - the compile-only text-model contract stays `frozenset({"bytes", "str"})`.
- Keep the still-meaningful subset selectors unchanged:
  - do not change `MODULE_WORKFLOW_BOUNDED_WILDCARD_COMPILE_CASE_IDS`, `MODULE_WORKFLOW_BOUNDED_WILDCARD_PATTERN_CASE_IDS`, `COLLECTION_TARGET_FIXTURE_CASE_IDS`, or `COLLECTION_REPLACEMENT_UNCOVERED_CASE_IDS`;
  - do not broaden this cleanup into the collection/replacement subset bundle, public-surface coverage, keyword-helper coverage, fake-native-boundary coverage, fixture files under `tests/conformance/fixtures/`, `tests/python/fixture_parity_support.py`, correctness reports, benchmarks, README copy, or tracked project-state prose.
- Keep scope structural only:
  - prefer deleting the compile-only sidecars and the redundant subset reload over adding another helper layer or another manifest-selection table;
  - keep any tiny new helper file-local on `tests/python/test_module_workflow_parity_suite.py`.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from collections import Counter
import tests.python.test_module_workflow_parity_suite as mod

expected_case_ids = (
    "workflow-compile-str-literal",
    "workflow-compile-str-anchored-literal",
    "workflow-compile-str-bounded-wildcard",
    "workflow-compile-str-bounded-wildcard-ignorecase",
    "workflow-compile-str-verbose-regression",
    "workflow-compile-str-multiline-regression",
    "workflow-compile-bytes-verbose-regression",
    "workflow-compile-bytes-multiline-regression",
    "workflow-compile-bytes-literal",
)

assert tuple(case.case_id for case in mod.COMPILE_CASES) == expected_case_ids
assert tuple(
    case.case_id
    for case in mod.MODULE_WORKFLOW_BUNDLE.manifest.cases
    if case.operation == "compile"
) == expected_case_ids
assert Counter((case.operation, case.helper) for case in mod.COMPILE_CASES) == Counter(
    {("compile", None): len(expected_case_ids)}
)
assert {case.text_model for case in mod.COMPILE_CASES} == {"bytes", "str"}
print("ok")
PY`
  - `bash -lc "! rg -n '^(MODULE_WORKFLOW_COMPILE_ONLY_CASE_IDS|MODULE_WORKFLOW_COMPILE_ONLY_PATTERNS|MODULE_WORKFLOW_COMPILE_ONLY_OPERATION_HELPER_COUNTS) =' tests/python/test_module_workflow_parity_suite.py"`

## Constraints
- Keep this cleanup limited to `tests/python/test_module_workflow_parity_suite.py`.
- Do not turn this into a collection-bundle rewrite, a public-surface loader rewrite, or a shared fixture-support abstraction pass.

## Notes
- `RBR-0764` is the next available task id in the current checkout:
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
for n in range(int(re.search(r'\d+', existing_sorted[-1]).group()), int(re.search(r'\d+', existing_sorted[-1]).group()) + 200):
    rid = f'RBR-{n:04d}'
    if rid not in existing and rid not in reserved:
        print('next_free', rid)
        break
PY` reported the existing tail through `RBR-0763`, no reserved missing tail ids, and `next_free RBR-0764`.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added; and
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`.
- JSON burn-down remains complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- This cleanup is concrete and currently viable in the live checkout:
  - `tuple(case.case_id for case in COMPILE_CASES)` currently matches `MODULE_WORKFLOW_COMPILE_ONLY_CASE_IDS` exactly;
  - `MODULE_WORKFLOW_COMPILE_ONLY_PATTERNS == frozenset(case_pattern(case) for case in COMPILE_CASES)` currently holds;
  - `MODULE_WORKFLOW_COMPILE_ONLY_OPERATION_HELPER_COUNTS == Counter((case.operation, case.helper) for case in COMPILE_CASES)` currently holds;
  - the three compile-only sidecars are referenced only in `tests/python/test_module_workflow_parity_suite.py`; and
  - the collection/replacement selector remains out of scope because `COLLECTION_TARGET_FIXTURE_CASE_IDS` still selects only 8 rows from the 15-row `collection_replacement_workflows.py` owner manifest, so that subset is not a redundant full-manifest mirror yet.
- Baseline verification is green in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py` passed (`665 passed, 1 skipped in 0.52s`);
  - the task-local compile-partition probe from Acceptance passed (`ok`);
  - `bash -lc "! rg -n '^(MODULE_WORKFLOW_COMPILE_ONLY_CASE_IDS|MODULE_WORKFLOW_COMPILE_ONLY_PATTERNS|MODULE_WORKFLOW_COMPILE_ONLY_OPERATION_HELPER_COUNTS) =' tests/python/test_module_workflow_parity_suite.py"` currently fails exactly on this cleanup because those three sidecars still exist.

## Completion
- 2026-03-20: Removed `MODULE_WORKFLOW_COMPILE_ONLY_CASE_IDS`, `MODULE_WORKFLOW_COMPILE_ONLY_PATTERNS`, and `MODULE_WORKFLOW_COMPILE_ONLY_OPERATION_HELPER_COUNTS` from `tests/python/test_module_workflow_parity_suite.py`.
- Reworked `test_module_workflow_surface_compile_case_selection_preserves_row_order` to derive the compile-only contract directly from `COMPILE_CASES` and `MODULE_WORKFLOW_BUNDLE.manifest.cases` instead of re-loading a compile-only `FixtureBundleSpec(...)`.
- Kept the remaining subset selectors unchanged, including `MODULE_WORKFLOW_BOUNDED_WILDCARD_COMPILE_CASE_IDS`, `MODULE_WORKFLOW_BOUNDED_WILDCARD_PATTERN_CASE_IDS`, `COLLECTION_TARGET_FIXTURE_CASE_IDS`, and `COLLECTION_REPLACEMENT_UNCOVERED_CASE_IDS`.
- Verification passed with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py` (`665 passed, 1 skipped in 0.75s`), the task-local compile-partition probe from Acceptance (`ok`), and `bash -lc "! rg -n '^(MODULE_WORKFLOW_COMPILE_ONLY_CASE_IDS|MODULE_WORKFLOW_COMPILE_ONLY_PATTERNS|MODULE_WORKFLOW_COMPILE_ONLY_OPERATION_HELPER_COUNTS) =' tests/python/test_module_workflow_parity_suite.py"` (passes with no matches).
