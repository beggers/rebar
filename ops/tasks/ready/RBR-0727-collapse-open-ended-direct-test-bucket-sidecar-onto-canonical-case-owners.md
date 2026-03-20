# RBR-0727: Collapse open-ended direct-test bucket sidecar onto canonical case owners

Status: ready
Owner: architecture-implementation
Created: 2026-03-20

## Goal
- Remove the detached `OPEN_ENDED_QUANTIFIED_GROUP_DIRECT_TEST_CASE_ID_BUCKETS` registry from `tests/python/test_open_ended_quantified_group_parity_suite.py` so the open-ended parity owner derives direct-test bucket coverage from its canonical shared case buckets plus the existing direct-bytes follow-on surfaces instead of maintaining a mirrored top-level map.

## Deliverables
- `tests/python/test_open_ended_quantified_group_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_open_ended_quantified_group_parity_suite.py` stops defining or reading `OPEN_ENDED_QUANTIFIED_GROUP_DIRECT_TEST_CASE_ID_BUCKETS`.
- The open-ended direct-test coverage derives from existing canonical owners instead of from the deleted registry:
  - `test_open_ended_quantified_group_direct_test_case_id_buckets_cover_selected_frontier` no longer passes a detached top-level bucket map; and
  - if a tiny file-local helper is useful, keep it derived from `COMPILE_CASES`, `MODULE_CASES`, `PATTERN_CASES`, and `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` instead of introducing another mirrored tuple/list/map block.
- Preserve the current effective bucket ordering and routing exactly:
  - the shared bucket keys stay `shared-compile`, `shared-module-search`, `shared-pattern-fullmatch` in that order;
  - the bytes-follow-on bucket keys stay exactly `broader-range-alternation-bytes-follow-on`, `open-ended-backtracking-heavy-bytes-follow-on`, `broader-range-conditional-bytes-follow-on`, `broader-range-backtracking-heavy-bytes-follow-on` in the current `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` order; and
  - each bytes-follow-on bucket still equals the `frozenset` of `case.case_id` values from the corresponding `spec.bundle.cases` where `case.text_model == "bytes"`.
- Keep canonical ownership otherwise unchanged:
  - do not change `OPEN_ENDED_BYTES_CASE_SURFACES` membership, `follow_on_id` values, supplemental bytes-case payloads, expected operation-helper counts, expected module-search or pattern-fullmatch text maps, or `OPEN_ENDED_SUPPLEMENTAL_BYTES_CASES`;
  - do not change `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES`, `COMPILE_CASES`, `MODULE_CASES`, `PATTERN_CASES`, `OPEN_ENDED_QUANTIFIED_GROUP_SELECTED_CASE_IDS`, `OPEN_ENDED_TRACE_BUNDLES`, `OPEN_ENDED_TRACE_CASES`, or the direct parity surface they represent; and
  - do not broaden into `tests/python/fixture_parity_support.py`, correctness fixtures under `tests/conformance/fixtures/`, benchmark manifests/tests, reports, README copy, or tracked project-state prose.
- Keep scope structural only:
  - do not reinterpret which open-ended grouped bytes cases stay explicit, do not move any family between the shared buckets and the direct follow-on path, and do not revisit the generic-bucket routing cleanup from `RBR-0725`.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from tests.python.fixture_parity_support import assert_direct_test_case_id_buckets_cover_selected_frontier
import tests.python.test_open_ended_quantified_group_parity_suite as mod

derived = {
    "shared-compile": frozenset(case.case_id for case in mod.COMPILE_CASES),
    "shared-module-search": frozenset(case.case_id for case in mod.MODULE_CASES),
    "shared-pattern-fullmatch": frozenset(case.case_id for case in mod.PATTERN_CASES),
    **{
        f"{spec.follow_on_id}-bytes-follow-on": frozenset(
            case.case_id for case in spec.bundle.cases if case.text_model == "bytes"
        )
        for spec in mod.DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES
    },
}
assert tuple(derived) == (
    "shared-compile",
    "shared-module-search",
    "shared-pattern-fullmatch",
    "broader-range-alternation-bytes-follow-on",
    "open-ended-backtracking-heavy-bytes-follow-on",
    "broader-range-conditional-bytes-follow-on",
    "broader-range-backtracking-heavy-bytes-follow-on",
)
assert tuple(spec.follow_on_id for spec in mod.DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES) == (
    "broader-range-alternation",
    "open-ended-backtracking-heavy",
    "broader-range-conditional",
    "broader-range-backtracking-heavy",
)
assert_direct_test_case_id_buckets_cover_selected_frontier(
    derived,
    selected_case_ids=mod.OPEN_ENDED_QUANTIFIED_GROUP_SELECTED_CASE_IDS,
    coverage_label="open-ended quantified-group direct-test case-id buckets probe",
)
print("ok")
PY`
  - `bash -lc "! rg -n 'OPEN_ENDED_QUANTIFIED_GROUP_DIRECT_TEST_CASE_ID_BUCKETS' tests/python/test_open_ended_quantified_group_parity_suite.py"`

## Constraints
- Keep this cleanup structural only. The point is to delete one more mirrored direct-test owner layer inside the open-ended parity suite, not to reinterpret the open-ended grouped frontier, change which bytes cases stay explicit, or broaden the suite beyond the current published slice.
- Prefer deriving direct-test bucket coverage directly from the canonical shared buckets plus `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` over introducing another detached helper registry.

## Notes
- `RBR-0727` is the next available architecture-task id in the current checkout:
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
for n in range(int(re.search(r'\\d+', existing_sorted[-1]).group()), int(re.search(r'\\d+', existing_sorted[-1]).group()) + 40):
    rid = f'RBR-{n:04d}'
    if rid not in existing and rid not in reserved:
        print('next_free', rid)
        break
PY` reported the existing tail through `RBR-0726`, no reserved missing tail ids, and `next_free RBR-0727`.
- No blocked architecture task exists to reopen first, and the current runtime state does not trigger rule 10:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added;
  - `.rebar/runtime/dashboard.md` is aligned with `HEAD` (`6d663e583005959e4e435974d4b4e4d4bd3d470b`), reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The detached direct-test bucket registry is concrete and bounded in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py` passes (`3923 passed in 2.78s`);
  - the derived-bucket probe in Acceptance already passes in the current checkout (`ok`);
  - the final `rg` absence check in Acceptance currently fails exactly on this cleanup because `OPEN_ENDED_QUANTIFIED_GROUP_DIRECT_TEST_CASE_ID_BUCKETS` is still defined once and read once in this file; and
  - `rg -n 'OPEN_ENDED_QUANTIFIED_GROUP_DIRECT_TEST_CASE_ID_BUCKETS|DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES|assert_direct_test_case_id_buckets_cover_selected_frontier' tests/python/test_open_ended_quantified_group_parity_suite.py` shows the detached registry is declared once and only fed to the selected-frontier coverage test in this file.
- This simplification stays on the same bounded open-ended parity-harness cleanup track as the most recent architecture work:
  - `ops/tasks/done/RBR-0725-collapse-open-ended-generic-bucket-routing-sidecars-onto-canonical-follow-on-ownership.md` intentionally left `OPEN_ENDED_QUANTIFIED_GROUP_DIRECT_TEST_CASE_ID_BUCKETS` untouched while removing the stale generic-bucket routing sidecars from this same owner file; and
  - `COMPILE_CASES`, `MODULE_CASES`, `PATTERN_CASES`, and `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` already own the shared buckets, bytes-follow-on ordering, and bundle-to-bucket routing needed to derive the seven direct-test buckets without a second owner layer.
