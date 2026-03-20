# RBR-0728: Collapse grouped-capture direct-test bucket registry onto canonical case owners

Status: ready
Owner: architecture-implementation
Created: 2026-03-20

## Goal
- Remove the detached `GROUPED_CAPTURE_DIRECT_TEST_CASE_ID_BUCKETS` registry from `tests/python/test_grouped_capture_parity_suite.py` so the grouped-capture parity owner derives direct-test bucket coverage from its canonical tracked case-id tuples instead of maintaining a mirrored top-level map.

## Deliverables
- `tests/python/test_grouped_capture_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_grouped_capture_parity_suite.py` stops defining or reading `GROUPED_CAPTURE_DIRECT_TEST_CASE_ID_BUCKETS`.
- The grouped-capture direct-test coverage derives from existing canonical owners instead of from the deleted registry:
  - `test_grouped_capture_direct_test_buckets_cover_selected_frontier` no longer passes a detached top-level bucket map; and
  - if a tiny file-local helper is useful, keep it derived from `GROUPED_MATCH_TRACKED_CASE_IDS`, `NAMED_GROUP_CASE_IDS`, `GROUPED_SEGMENT_CASE_IDS`, `GROUPED_ALTERNATION_CASE_IDS`, `OPTIONAL_GROUP_CASE_IDS`, `OPTIONAL_GROUP_ALTERNATION_CASE_IDS`, `NESTED_GROUP_CASE_IDS`, and `NESTED_GROUP_ALTERNATION_CASE_IDS` instead of introducing another mirrored tuple/list/map block.
- Preserve the current effective bucket ordering and membership exactly:
  - the bucket keys stay `grouped-match`, `named-group`, `grouped-segment`, `grouped-alternation`, `optional-group`, `optional-group-alternation`, `nested-group`, `nested-group-alternation` in that order; and
  - each bucket still equals the `frozenset` of the matching canonical case-id tuple for that grouped-capture family.
- Keep canonical ownership otherwise unchanged:
  - do not change `GROUPED_CAPTURE_TRACKED_CASE_IDS` or any of the eight family tuple constants it composes;
  - do not change `SELECTED_CASE_BUNDLE_SPECS`, fixture-bundle loading, `COMPILE_CASES`, `MODULE_CASES`, `SUPPLEMENTAL_MISS_CASES`, `PATTERN_CASES`, `MATCH_GROUP_ACCESS_CASES`, `REGS_PARITY_CASE_IDS`, `BOUND_CASES`, or the published grouped-capture parity surface they represent; and
  - do not broaden into `tests/python/fixture_parity_support.py`, correctness fixtures under `tests/conformance/fixtures/`, benchmark manifests/tests, reports, README copy, or tracked project-state prose.
- Keep scope structural only:
  - do not reinterpret grouped-capture frontier ownership, move case ids between buckets, or add another abstraction layer beyond a tiny file-local helper if one is needed.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from tests.python.fixture_parity_support import assert_direct_test_case_id_buckets_cover_selected_frontier
import tests.python.test_grouped_capture_parity_suite as mod

derived = {
    "grouped-match": frozenset(mod.GROUPED_MATCH_TRACKED_CASE_IDS),
    "named-group": frozenset(mod.NAMED_GROUP_CASE_IDS),
    "grouped-segment": frozenset(mod.GROUPED_SEGMENT_CASE_IDS),
    "grouped-alternation": frozenset(mod.GROUPED_ALTERNATION_CASE_IDS),
    "optional-group": frozenset(mod.OPTIONAL_GROUP_CASE_IDS),
    "optional-group-alternation": frozenset(mod.OPTIONAL_GROUP_ALTERNATION_CASE_IDS),
    "nested-group": frozenset(mod.NESTED_GROUP_CASE_IDS),
    "nested-group-alternation": frozenset(mod.NESTED_GROUP_ALTERNATION_CASE_IDS),
}
assert tuple(derived) == (
    "grouped-match",
    "named-group",
    "grouped-segment",
    "grouped-alternation",
    "optional-group",
    "optional-group-alternation",
    "nested-group",
    "nested-group-alternation",
)
assert_direct_test_case_id_buckets_cover_selected_frontier(
    derived,
    selected_case_ids=mod.GROUPED_CAPTURE_TRACKED_CASE_IDS,
    coverage_label="grouped capture direct-test case-id buckets probe",
)
print("ok")
PY`
  - `bash -lc "! rg -n 'GROUPED_CAPTURE_DIRECT_TEST_CASE_ID_BUCKETS' tests/python/test_grouped_capture_parity_suite.py"`

## Constraints
- Keep this cleanup structural only. The point is to delete one more mirrored direct-test owner layer inside the grouped-capture parity suite, not to reinterpret grouped-capture semantics or widen the test surface.
- Prefer deriving direct-test bucket coverage directly from the canonical grouped-capture case-id tuples over introducing another detached helper registry.

## Notes
- `RBR-0728` is the next available architecture-task id in the current checkout:
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
print('highest_existing_tail', existing_sorted[-15:])
print('reserved_tail', reserved_sorted[-15:])
for n in range(int(re.search(r'\\d+', existing_sorted[-1]).group()), int(re.search(r'\\d+', existing_sorted[-1]).group()) + 60):
    rid = f'RBR-{n:04d}'
    if rid not in existing and rid not in reserved:
        print('next_free', rid)
        break
PY` reported the existing tail through `RBR-0727`, no reserved missing tail ids, and `next_free RBR-0728`.
- No blocked architecture task exists to reopen first, and the current runtime state does not trigger rule 10:
  - `ops/tasks/ready/` and `ops/tasks/in_progress/` were empty before this task was added;
  - `ops/tasks/blocked/` contains only the feature-owned `RBR-0412-publish-module-workflow-bytes-verbose-pattern-helper-pair.md`;
  - `.rebar/runtime/dashboard.md` is aligned with `HEAD` (`d1ea98204fded739120772143b722fc72565bcb4`), reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 1`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows the harness committing and pushing cleanly, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The detached grouped-capture bucket registry is concrete and bounded in the current checkout:
  - `rg -n "GROUPED_CAPTURE_DIRECT_TEST_CASE_ID_BUCKETS|test_grouped_capture_direct_test_buckets_cover_selected_frontier" ops/tasks tests/python/test_grouped_capture_parity_suite.py` finds no existing architecture task for this exact cleanup and shows the registry is declared once and consumed only by the selected-frontier coverage test in this file;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_grouped_capture_parity_suite.py` currently passes (`427 passed in 0.32s`);
  - the derived-bucket probe in Acceptance already passes in the current checkout (`ok`); and
  - the final `rg` absence check in Acceptance currently fails exactly on this cleanup because `GROUPED_CAPTURE_DIRECT_TEST_CASE_ID_BUCKETS` is still defined once and read once in this file.
- This simplification stays on the same bounded post-JSON parity-harness cleanup track as the recent architecture work:
  - `ops/tasks/done/RBR-0721-collapse-quantified-alternation-direct-test-bucket-registry-onto-canonical-case-owners.md`, `ops/tasks/done/RBR-0723-collapse-wider-ranged-repeat-direct-test-bucket-registry-onto-canonical-case-owners.md`, and `ops/tasks/done/RBR-0727-collapse-open-ended-direct-test-bucket-sidecar-onto-canonical-case-owners.md` already removed adjacent detached bucket-owner layers from other parity suites; and
  - `GROUPED_CAPTURE_DIRECT_TEST_CASE_ID_BUCKETS` is the same style of mirrored owner data, but here the canonical sources are the tracked grouped-capture family tuples rather than direct-bytes follow-on specs.
