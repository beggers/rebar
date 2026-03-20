# RBR-0735: Collapse module-workflow direct-test bucket registry onto canonical case owners

Status: done
Owner: architecture-implementation
Created: 2026-03-20
Completed: 2026-03-20

## Goal
- Remove the detached `MODULE_WORKFLOW_DIRECT_TEST_CASE_ID_BUCKETS` registry from `tests/python/test_module_workflow_parity_suite.py` so the module-workflow parity owner derives direct-test bucket coverage from its canonical case owners instead of maintaining a mirrored top-level map.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` stops defining or reading `MODULE_WORKFLOW_DIRECT_TEST_CASE_ID_BUCKETS`.
- The module-workflow direct-test coverage derives from existing canonical owners instead of from the deleted registry:
  - `test_module_workflow_direct_test_buckets_cover_selected_frontier` no longer passes a detached top-level bucket map; and
  - because the registry is only consumed once, prefer building the mapping inline at the coverage assertion or via one tiny file-local helper derived directly from `COMPILE_CASES`, `PATTERN_CASES`, `CACHE_CASES`, `PURGE_CASES`, `PUBLISHED_VERBOSE_BYTES_COMPILED_PATTERN_MODULE_HELPER_CASES`, and `ESCAPE_CASES` instead of introducing another mirrored tuple/list/map.
- Preserve the current effective bucket ordering and membership exactly:
  - the bucket keys stay `compile`, `pattern`, `cache`, `purge`, `compiled-module-helper`, and `escape` in that order;
  - `compile` still equals `frozenset(case.case_id for case in COMPILE_CASES)`;
  - `pattern` still equals `frozenset(case.case_id for case in PATTERN_CASES)`;
  - `cache` still equals `frozenset(case.case_id for case in CACHE_CASES)`;
  - `purge` still equals `frozenset(case.case_id for case in PURGE_CASES)`;
  - `compiled-module-helper` still equals `frozenset(case.case_id for case in PUBLISHED_VERBOSE_BYTES_COMPILED_PATTERN_MODULE_HELPER_CASES)`; and
  - `escape` still equals `frozenset(case.case_id for case in ESCAPE_CASES)`.
- Keep canonical ownership otherwise unchanged:
  - do not change `MODULE_WORKFLOW_BUNDLE`, `MODULE_WORKFLOW_EXPECTED_CASE_IDS`, `COMPILE_CASES`, `PATTERN_CASES`, `CACHE_CASES`, `PURGE_CASES`, `PUBLISHED_VERBOSE_BYTES_COMPILED_PATTERN_MODULE_HELPER_CASES`, `ESCAPE_CASES`, the verbose/multiline compile anchors, or the module-workflow direct parity surface they represent;
  - do not change `_public_surface_direct_test_case_id_buckets()`, the inline literal-collection direct-test bucket coverage, the match-behavior direct bucket coverage, or any public-surface, literal-collection, keyword-argument, or supplemental match-behavior expectations elsewhere in this file; and
  - do not broaden into `tests/python/fixture_parity_support.py`, correctness fixtures under `tests/conformance/fixtures/`, benchmark manifests/tests, published reports, README copy, or tracked project-state prose.
- Keep scope structural only:
  - do not reinterpret module-workflow ownership, move case ids between buckets, or widen the direct-test frontier.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from tests.python.fixture_parity_support import assert_direct_test_case_id_buckets_cover_selected_frontier
import tests.python.test_module_workflow_parity_suite as mod

derived = {
    "compile": frozenset(case.case_id for case in mod.COMPILE_CASES),
    "pattern": frozenset(case.case_id for case in mod.PATTERN_CASES),
    "cache": frozenset(case.case_id for case in mod.CACHE_CASES),
    "purge": frozenset(case.case_id for case in mod.PURGE_CASES),
    "compiled-module-helper": frozenset(
        case.case_id
        for case in mod.PUBLISHED_VERBOSE_BYTES_COMPILED_PATTERN_MODULE_HELPER_CASES
    ),
    "escape": frozenset(case.case_id for case in mod.ESCAPE_CASES),
}
assert tuple(derived) == (
    "compile",
    "pattern",
    "cache",
    "purge",
    "compiled-module-helper",
    "escape",
)
assert_direct_test_case_id_buckets_cover_selected_frontier(
    derived,
    selected_case_ids=mod.MODULE_WORKFLOW_EXPECTED_CASE_IDS,
    coverage_label="module workflow direct-test case-id buckets probe",
)
print("ok")
PY`
  - `bash -lc "! rg -n 'MODULE_WORKFLOW_DIRECT_TEST_CASE_ID_BUCKETS' tests/python/test_module_workflow_parity_suite.py"`

## Constraints
- Keep this cleanup limited to the module-workflow owner surface inside `tests/python/test_module_workflow_parity_suite.py`. Do not use this run to rewrite shared helper APIs, absorb other direct-test bucket assertions in the same file, or add another abstraction layer.
- Prefer deriving direct-test bucket coverage directly from the existing module-workflow case owners over introducing another detached helper registry.

## Notes
- `RBR-0735` is the next available architecture-task id in the current checkout:
  - the repo task queues already extend through `RBR-0734`;
  - `ops/state/backlog.md` and `ops/state/current_status.md` do not reserve any missing tail ids beyond that; and
  - the next free id probe returned `RBR-0735`.
- No blocked architecture task exists to reopen first, the live queue is empty, and the runtime state does not trigger rule 10:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty before this task is added; and
  - `.rebar/runtime/dashboard.md` is aligned with `HEAD` (`b71066e0595956e42ece052ca37f7e157133d010`), reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
- JSON burn-down is complete in both tracked and live views:
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The detached module-workflow bucket registry is concrete and bounded in the current checkout:
  - `rg -n 'MODULE_WORKFLOW_DIRECT_TEST_CASE_ID_BUCKETS|test_module_workflow_direct_test_buckets_cover_selected_frontier' tests/python/test_module_workflow_parity_suite.py` shows the registry is declared once and only consumed by the selected-frontier coverage test in this file;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py` currently passes (`586 passed, 1 skipped in 0.45s`);
  - the derived-bucket probe in Acceptance already passes in the current checkout (`ok`); and
  - the final `rg` absence check in Acceptance currently fails exactly on this cleanup because `MODULE_WORKFLOW_DIRECT_TEST_CASE_ID_BUCKETS` is still defined once and read once in this file.
- This simplification stays on the same bounded post-JSON parity-harness cleanup track as `RBR-0732`, but targets the remaining module-workflow owner map that still mirrors canonical case ownership inside the same suite.
- 2026-03-20 completion:
  - Removed `MODULE_WORKFLOW_DIRECT_TEST_CASE_ID_BUCKETS` from `tests/python/test_module_workflow_parity_suite.py`.
  - Added a tiny file-local helper that derives the module-workflow direct-test bucket map from `COMPILE_CASES`, `PATTERN_CASES`, `CACHE_CASES`, `PURGE_CASES`, `PUBLISHED_VERBOSE_BYTES_COMPILED_PATTERN_MODULE_HELPER_CASES`, and `ESCAPE_CASES`, preserving the existing bucket ordering and membership.
  - Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py` (`586 passed, 1 skipped in 0.65s`), the derived-bucket probe from the task (`ok`), and the `rg` absence check for `MODULE_WORKFLOW_DIRECT_TEST_CASE_ID_BUCKETS` (no matches).
