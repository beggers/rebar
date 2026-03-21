# RBR-0847: Collapse module-workflow published collection case sidecars onto fixture selectors

Status: done
Owner: architecture-implementation
Created: 2026-03-21
Completed: 2026-03-21

## Goal
- Remove the detached published collection module/pattern case tables from `tests/python/test_module_workflow_parity_suite.py` so `PUBLISHED_COLLECTION_FIXTURE_CASES` remains the sole canonical owner for the published collection frontier inside this parity owner.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` stops defining or reading these detached transformed sidecars:
  - `PUBLISHED_COLLECTION_MODULE_CASES`
  - `PUBLISHED_COLLECTION_PATTERN_CASES`
- The affected collection case pools and direct-frontier coverage check derive their published module/pattern slices from `PUBLISHED_COLLECTION_FIXTURE_CASES` through tiny file-local selectors or conversion helpers instead of those mirrored top-level tables:
  - `MODULE_COLLECTION_CASES`
  - `PATTERN_COLLECTION_CASES`
  - `test_literal_collection_direct_test_buckets_cover_selected_frontier`
- Keep the current effective published ordering exactly unchanged while deriving from the fixture-owned frontier:
  - the fixture-derived published module slice still resolves to `module-split-str-leading-trailing`, `module-split-str-no-match`, `module-findall-bytes-repeated`, `module-finditer-str-repeated`, and `module-findall-nonliteral-str`;
  - the fixture-derived published pattern slice still resolves to `pattern-split-bytes-maxsplit`, `pattern-findall-str-no-match`, and `pattern-finditer-bytes-bounded`;
  - the leading `MODULE_COLLECTION_CASES` order still begins with `module-split-str-leading-trailing`, `module-split-str-no-match`, `module-split-str-maxsplit-one`, `module-split-str-negative-maxsplit`, and `module-split-bytes-maxsplit-one`; and
  - the leading `PATTERN_COLLECTION_CASES` order still begins with `pattern-split-bytes-maxsplit`, `pattern-split-str-no-match`, `pattern-split-str-repeated`, `pattern-split-str-maxsplit-one`, `pattern-split-str-negative-maxsplit`, and `pattern-findall-str-no-match`.
- Keep canonical ownership otherwise unchanged:
  - do not change `COLLECTION_REPLACEMENT_BUNDLE`, `PUBLISHED_COLLECTION_FIXTURE_CASES`, `_module_collection_case_from_fixture`, `_pattern_collection_case_from_fixture`, the supplemental collection cases, bounded-wildcard collection cases, or collection/replacement behavior; and
  - do not broaden or shrink the published collection frontier.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py`
  - `bash -lc "! rg -n '^(PUBLISHED_COLLECTION_MODULE_CASES|PUBLISHED_COLLECTION_PATTERN_CASES) =' tests/python/test_module_workflow_parity_suite.py"`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
import tests.python.test_module_workflow_parity_suite as mod

module_cases = tuple(
    mod._module_collection_case_from_fixture(case)
    for case in mod.PUBLISHED_COLLECTION_FIXTURE_CASES
    if case.operation == "module_call"
)
pattern_cases = tuple(
    mod._pattern_collection_case_from_fixture(case)
    for case in mod.PUBLISHED_COLLECTION_FIXTURE_CASES
    if case.operation == "pattern_call"
)
assert tuple(case.case_id for case in module_cases) == (
    "module-split-str-leading-trailing",
    "module-split-str-no-match",
    "module-findall-bytes-repeated",
    "module-finditer-str-repeated",
    "module-findall-nonliteral-str",
)
assert tuple(case.case_id for case in pattern_cases) == (
    "pattern-split-bytes-maxsplit",
    "pattern-findall-str-no-match",
    "pattern-finditer-bytes-bounded",
)
assert tuple(case.case_id for case in mod.MODULE_COLLECTION_CASES[:5]) == (
    "module-split-str-leading-trailing",
    "module-split-str-no-match",
    "module-split-str-maxsplit-one",
    "module-split-str-negative-maxsplit",
    "module-split-bytes-maxsplit-one",
)
assert tuple(case.case_id for case in mod.PATTERN_COLLECTION_CASES[:6]) == (
    "pattern-split-bytes-maxsplit",
    "pattern-split-str-no-match",
    "pattern-split-str-repeated",
    "pattern-split-str-maxsplit-one",
    "pattern-split-str-negative-maxsplit",
    "pattern-findall-str-no-match",
)
print("ok")
PY`

## Constraints
- Keep this cleanup structural only. The point is to delete one more mirrored owner layer inside the module-workflow parity suite, not to reinterpret collection helper semantics, change fixture membership, or reshuffle supplemental direct cases.
- Keep scope limited to `tests/python/test_module_workflow_parity_suite.py`. Do not edit correctness fixtures, benchmark manifests/tests, harness modules, reports, README copy, or tracked project-state prose in this run.

## Notes
- `RBR-0847` is the next available task id in the current checkout:
  - `ops/state/backlog.md` and `ops/state/current_status.md` reserve only the already-filed `RBR-0846`; and
  - no tracked task file under `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, or `ops/tasks/blocked/` already uses `RBR-0847`.
- No blocked architecture task exists to reopen first, and the current queue/runtime state does not trigger rule 10:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete and bounded in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py` currently passes (`1207 passed, 1 skipped in 0.85s`);
  - `rg -n '^(PUBLISHED_COLLECTION_MODULE_CASES|PUBLISHED_COLLECTION_PATTERN_CASES) =' tests/python/test_module_workflow_parity_suite.py` currently shows exactly the two detached transformed-sidecar declarations and no other owner for the same slice;
  - the final `rg` absence check in Acceptance currently fails exactly on this cleanup because those mirrored top-level tables still exist; and
  - the import/order probe in Acceptance already passes (`ok`), showing that `PUBLISHED_COLLECTION_FIXTURE_CASES` plus the existing fixture-to-direct-case converters already carry the published ordering needed to delete the extra sidecar layer without changing behavior.
- This stays on the same bounded post-JSON cleanup track as the recent sidecar removals in neighboring parity owners, but targets a still-live redundancy in the current checkout instead of reopening already-drained files.

## Completion
- 2026-03-21: Removed the mirrored `PUBLISHED_COLLECTION_MODULE_CASES` and `PUBLISHED_COLLECTION_PATTERN_CASES` sidecars from `tests/python/test_module_workflow_parity_suite.py`.
- Added small file-local helper selectors that derive published module and pattern collection slices directly from `PUBLISHED_COLLECTION_FIXTURE_CASES`, preserving the published fixture ordering without introducing another owner layer.
- Rewired `MODULE_COLLECTION_CASES`, `PATTERN_COLLECTION_CASES`, and `test_literal_collection_direct_test_buckets_cover_selected_frontier` to use those fixture-derived selectors while leaving `COLLECTION_REPLACEMENT_BUNDLE`, `PUBLISHED_COLLECTION_FIXTURE_CASES`, `_module_collection_case_from_fixture`, `_pattern_collection_case_from_fixture`, supplemental collection cases, bounded-wildcard collection cases, and collection behavior unchanged.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py` (`1207 passed, 1 skipped in 1.19s`), `bash -lc "! rg -n '^(PUBLISHED_COLLECTION_MODULE_CASES|PUBLISHED_COLLECTION_PATTERN_CASES) =' tests/python/test_module_workflow_parity_suite.py"` (passes with no matches), and the task-local import/order probe from Acceptance (`ok`).
