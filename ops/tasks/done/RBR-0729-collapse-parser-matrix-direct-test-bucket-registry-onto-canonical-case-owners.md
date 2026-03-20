# RBR-0729: Collapse parser-matrix direct-test bucket registry onto canonical case owners

Status: done
Owner: architecture-implementation
Created: 2026-03-20
Completed: 2026-03-20

## Goal
- Remove the detached `PARSER_MATRIX_DIRECT_TEST_CASE_ID_BUCKETS` registry from `tests/python/test_parser_matrix_parity_suite.py` so the parser-matrix parity owner derives direct-test bucket coverage from its canonical case owners instead of maintaining a mirrored top-level map.

## Deliverables
- `tests/python/test_parser_matrix_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_parser_matrix_parity_suite.py` stops defining or reading `PARSER_MATRIX_DIRECT_TEST_CASE_ID_BUCKETS`.
- The parser-matrix direct-test coverage derives from existing canonical owners instead of from the deleted registry:
  - `test_parser_matrix_direct_test_buckets_cover_selected_frontier` no longer passes a detached top-level bucket map; and
  - if a tiny file-local helper is useful, keep it derived from `NESTED_SET_WARNING_CASE`, `CHARACTER_CLASS_CASE`, `REPEATED_COMPILE_CACHE_CASES`, and `DIAGNOSTIC_CASES` instead of introducing another mirrored tuple/list/map block.
- Preserve the current effective bucket ordering and membership exactly:
  - the bucket keys stay `warning-cache`, `ignorecase-cache-normalization`, `compile-cache`, `compile-diagnostics` in that order;
  - `warning-cache` still equals `frozenset({NESTED_SET_WARNING_CASE.case_id})`;
  - `ignorecase-cache-normalization` still equals `frozenset({CHARACTER_CLASS_CASE.case_id})`;
  - `compile-cache` still equals `_case_ids(REPEATED_COMPILE_CACHE_CASES)`; and
  - `compile-diagnostics` still equals `_case_ids(DIAGNOSTIC_CASES)`.
- Keep canonical ownership otherwise unchanged:
  - do not change `EXPECTED_CASE_IDS`, `KNOWN_UNCOVERED_PARSER_MATRIX_CASE_IDS`, `SELECTED_CASE_BUNDLE_SPECS`, `PARSER_MATRIX_FIXTURE_BUNDLE`, `TARGET_CASES`, `COMPILE_METADATA_CASES`, `PLACEHOLDER_SEARCH_CASES`, `REPEATED_COMPILE_CACHE_CASES`, `DIAGNOSTIC_CASES`, `NO_STDLIB_DELEGATION_CASES`, or the conditional-assertion diagnostic fixture coverage carried in the same file;
  - do not broaden into `tests/python/fixture_parity_support.py`, correctness fixtures under `tests/conformance/fixtures/`, benchmark manifests/tests, reports, README copy, or tracked project-state prose.
- Keep scope structural only:
  - do not reinterpret parser-matrix frontier ownership, move case ids between buckets, or add another abstraction layer beyond a tiny file-local helper if one is needed.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_parser_matrix_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from tests.python.fixture_parity_support import assert_direct_test_case_id_buckets_cover_selected_frontier
import tests.python.test_parser_matrix_parity_suite as mod

derived = {
    "warning-cache": frozenset({mod.NESTED_SET_WARNING_CASE.case_id}),
    "ignorecase-cache-normalization": frozenset({mod.CHARACTER_CLASS_CASE.case_id}),
    "compile-cache": mod._case_ids(mod.REPEATED_COMPILE_CACHE_CASES),
    "compile-diagnostics": mod._case_ids(mod.DIAGNOSTIC_CASES),
}
assert tuple(derived) == (
    "warning-cache",
    "ignorecase-cache-normalization",
    "compile-cache",
    "compile-diagnostics",
)
assert_direct_test_case_id_buckets_cover_selected_frontier(
    derived,
    selected_case_ids=mod.EXPECTED_CASE_IDS,
    coverage_label="parser matrix direct-test case-id buckets probe",
)
print("ok")
PY`
  - `bash -lc "! rg -n 'PARSER_MATRIX_DIRECT_TEST_CASE_ID_BUCKETS' tests/python/test_parser_matrix_parity_suite.py"`

## Constraints
- Keep this cleanup structural only. The point is to delete one mirrored direct-test owner layer inside the parser-matrix parity suite, not to reinterpret parser semantics or widen the test surface.
- Prefer deriving direct-test bucket coverage directly from the existing parser-matrix case owners over introducing another detached helper registry.

## Notes
- `RBR-0729` is the next available architecture-task id in the current checkout:
  - `python3 - <<'PY'
import pathlib, re
existing = set()
for base in ['ops/tasks/ready', 'ops/tasks/in_progress', 'ops/tasks/done', 'ops/tasks/blocked']:
    for path in pathlib.Path(base).glob('RBR-*.md'):
        m = re.match(r'(RBR-\\d+[A-Z]?)', path.name)
        if m:
            existing.add(m.group(1))
text = '\\n'.join(
    pathlib.Path(p).read_text(encoding='utf-8')
    for p in ['ops/state/backlog.md', 'ops/state/current_status.md']
)
reserved = set(re.findall(r'RBR-\\d+[A-Z]?', text)) - existing
existing_sorted = sorted(existing, key=lambda s: (int(re.search(r'\\d+', s).group()), s))
reserved_sorted = sorted(reserved, key=lambda s: (int(re.search(r'\\d+', s).group()), s))
print('highest_existing_tail', existing_sorted[-10:])
print('reserved_tail', reserved_sorted[-10:])
for n in range(int(re.search(r'\\d+', existing_sorted[-1]).group()), int(re.search(r'\\d+', existing_sorted[-1]).group()) + 80):
    rid = f'RBR-{n:04d}'
    if rid not in existing and rid not in reserved:
        print('next_free', rid)
        break
PY` reported the existing tail through `RBR-0728`, no reserved missing tail ids, and `next_free RBR-0729`.
- No blocked architecture task exists to reopen first, and the current runtime state does not trigger rule 10:
  - `ops/tasks/ready/` and `ops/tasks/in_progress/` were empty before this task was added;
  - `ops/tasks/blocked/` contains only the feature-owned `RBR-0412-publish-module-workflow-bytes-verbose-pattern-helper-pair.md`;
  - `.rebar/runtime/dashboard.md` is aligned with `HEAD` (`f43b30635a5f0b9c1ba4c3baabc88060646f105d`), reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 1`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows the harness committing and pushing cleanly, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The detached parser-matrix bucket registry is concrete and bounded in the current checkout:
  - `rg -n "PARSER_MATRIX_DIRECT_TEST_CASE_ID_BUCKETS|test_parser_matrix_direct_test_buckets_cover_selected_frontier" ops/tasks tests/python/test_parser_matrix_parity_suite.py` finds no existing architecture task for this exact cleanup and shows the registry is declared once and consumed only by the selected-frontier coverage test in this file;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_parser_matrix_parity_suite.py` currently passes (`61 passed, 29 skipped in 0.12s`);
  - the derived-bucket probe in Acceptance already passes in the current checkout (`ok`); and
  - the final `rg` absence check in Acceptance currently fails exactly on this cleanup because `PARSER_MATRIX_DIRECT_TEST_CASE_ID_BUCKETS` is still defined once and read once in this file.
- This simplification stays on the same bounded post-JSON parity-harness cleanup track as the recent architecture work:
  - `ops/tasks/done/RBR-0721-collapse-quantified-alternation-direct-test-bucket-registry-onto-canonical-case-owners.md`, `ops/tasks/done/RBR-0723-collapse-wider-ranged-repeat-direct-test-bucket-registry-onto-canonical-case-owners.md`, `ops/tasks/done/RBR-0727-collapse-open-ended-direct-test-bucket-sidecar-onto-canonical-case-owners.md`, and `ops/tasks/done/RBR-0728-collapse-grouped-capture-direct-test-bucket-registry-onto-canonical-case-owners.md` already removed the same style of detached direct-test bucket owner layer from adjacent parity suites; and
  - `PARSER_MATRIX_DIRECT_TEST_CASE_ID_BUCKETS` is the same style of mirrored owner data, but here the canonical sources are the parser-matrix warning, cache, and diagnostic case owners that already live in this file.
- 2026-03-20 completion:
  - Removed `PARSER_MATRIX_DIRECT_TEST_CASE_ID_BUCKETS` from `tests/python/test_parser_matrix_parity_suite.py`.
  - Added a tiny file-local helper that derives the direct-test bucket map from `NESTED_SET_WARNING_CASE`, `CHARACTER_CLASS_CASE`, `REPEATED_COMPILE_CACHE_CASES`, and `DIAGNOSTIC_CASES`, preserving the existing bucket ordering and membership.
  - Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_parser_matrix_parity_suite.py` (`61 passed, 29 skipped in 0.13s`), the derived-bucket probe from the task (`ok`), and the `rg` absence check for `PARSER_MATRIX_DIRECT_TEST_CASE_ID_BUCKETS` (no matches).
