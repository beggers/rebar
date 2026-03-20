# RBR-0723: Collapse wider-ranged-repeat direct-test bucket registry onto canonical case owners

Status: done
Owner: architecture-implementation
Created: 2026-03-20

## Goal
- Remove the detached `WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_DIRECT_TEST_CASE_ID_BUCKETS` registry from `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` so the wider-ranged-repeat parity owner derives direct-test bucket coverage from its canonical shared case buckets plus the existing direct-bytes follow-on specs instead of maintaining a mirrored top-level map.

## Deliverables
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` stops defining or reading `WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_DIRECT_TEST_CASE_ID_BUCKETS`.
- The wider-ranged-repeat direct-test coverage derives from existing canonical owners instead of from the deleted registry:
  - `test_wider_ranged_repeat_quantified_group_direct_test_case_id_buckets_cover_selected_frontier` no longer passes a detached top-level bucket map; and
  - if a tiny file-local helper is useful, keep it derived from `COMPILE_CASES`, `MODULE_CASES`, `PATTERN_CASES`, and `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` instead of introducing another mirrored tuple/list/map block.
- Preserve the current effective bucket ordering and routing exactly:
  - the shared bucket keys stay `shared-compile`, `shared-module-search`, `shared-pattern-fullmatch` in that order;
  - the bytes-follow-on bucket keys stay exactly `broader-range-conditional-bytes-follow-on`, `broader-range-backtracking-heavy-bytes-follow-on`, `nested-broader-range-alternation-bytes-follow-on`, `nested-broader-range-conditional-bytes-follow-on`, `nested-broader-range-backtracking-heavy-bytes-follow-on` in the current `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` order; and
  - each bytes-follow-on bucket still equals the `frozenset` of `case.case_id` values from the corresponding `spec.bundle.cases` where `case.text_model == "bytes"`.
- Keep canonical ownership otherwise unchanged:
  - do not change `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` membership, bundle ordering, `SupplementalCase` payloads, expected operation-helper counts, published module-search/fullmatch text maps, expected per-case payloads, or `DIRECT_BYTES_FOLLOW_ON_CASES`;
  - do not change `FIXTURE_BUNDLES`, `COMPILE_CASES`, `MODULE_CASES`, `PATTERN_CASES`, `WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_SELECTED_CASE_IDS`, `BACKTRACKING_TRACE_CASES`, `PATTERN_BOUNDS_MATCH_CASES`, `PATTERN_BOUNDS_NO_MATCH_CASES`, or the direct parity surface they represent; and
  - do not broaden into `tests/python/fixture_parity_support.py`, correctness fixture modules under `tests/conformance/fixtures/`, `python/rebar_harness/correctness.py`, published reports, benchmarks, README copy, or tracked project-state prose.
- Keep scope structural only:
  - do not reinterpret the broader `{1,4}` grouped frontier, change which bytes follow-on cases stay explicit, or broaden the suite beyond the current published slice.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from tests.python.fixture_parity_support import assert_direct_test_case_id_buckets_cover_selected_frontier
import tests.python.test_wider_ranged_repeat_quantified_group_parity_suite as mod

derived = {
    "shared-compile": frozenset(case.case_id for case in mod.COMPILE_CASES),
    "shared-module-search": frozenset(case.case_id for case in mod.MODULE_CASES),
    "shared-pattern-fullmatch": frozenset(case.case_id for case in mod.PATTERN_CASES),
    **{
        f"{spec.id}-bytes-follow-on": frozenset(
            case.case_id for case in spec.bundle.cases if case.text_model == "bytes"
        )
        for spec in mod.DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES
    },
}
assert tuple(derived) == (
    "shared-compile",
    "shared-module-search",
    "shared-pattern-fullmatch",
    "broader-range-conditional-bytes-follow-on",
    "broader-range-backtracking-heavy-bytes-follow-on",
    "nested-broader-range-alternation-bytes-follow-on",
    "nested-broader-range-conditional-bytes-follow-on",
    "nested-broader-range-backtracking-heavy-bytes-follow-on",
)
assert tuple(spec.id for spec in mod.DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES) == (
    "broader-range-conditional",
    "broader-range-backtracking-heavy",
    "nested-broader-range-alternation",
    "nested-broader-range-conditional",
    "nested-broader-range-backtracking-heavy",
)
assert_direct_test_case_id_buckets_cover_selected_frontier(
    derived,
    selected_case_ids=mod.WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_SELECTED_CASE_IDS,
    coverage_label="wider-ranged-repeat direct-test case-id buckets probe",
)
print("ok")
PY`
  - `bash -lc "! rg -n 'WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_DIRECT_TEST_CASE_ID_BUCKETS' tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py"`

## Constraints
- Prefer deriving direct-test bucket coverage directly from the canonical shared case buckets plus `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` over introducing another detached helper registry.
- Keep this cleanup limited to the wider-ranged-repeat parity owner. Do not use this run to rewrite shared helper APIs, move fixtures between manifests, or add another abstraction layer.

## Notes
- `RBR-0723` is the next available architecture-task id in the current checkout:
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
print('reserved_tail', reserved_sorted[-20:])
for n in range(int(re.search(r'\\d+', existing_sorted[-1]).group()), int(re.search(r'\\d+', existing_sorted[-1]).group()) + 30):
    rid = f'RBR-{n:04d}'
    if rid not in existing and rid not in reserved:
        print('next_free', rid)
        break
PY` reported the existing tail through `RBR-0722`, no reserved missing tail ids, and `next_free RBR-0723`.
- No blocked architecture task exists to reopen first, and the current runtime state does not trigger rule 10:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` is aligned with `HEAD` (`1f2ce342c0f237d76d496397ae3cbb184291692a`), reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The detached direct-test bucket registry is concrete and bounded in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` passes (`1341 passed in 0.97s`);
  - the derived-bucket probe in Acceptance already passes in the current checkout (`ok`);
  - the final `rg` absence check in Acceptance currently fails exactly on this cleanup because `WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_DIRECT_TEST_CASE_ID_BUCKETS` is still defined once and read once in this file; and
  - `rg -n 'WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_DIRECT_TEST_CASE_ID_BUCKETS|DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES|assert_direct_test_case_id_buckets_cover_selected_frontier' tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` shows the detached registry is only declared once and only fed to the selected-frontier coverage test in this file.
- This simplification stays on the same bounded post-JSON parity-harness cleanup track as the most recent architecture work:
  - `ops/tasks/done/RBR-0709-collapse-wider-ranged-repeat-direct-bytes-follow-on-sidecars.md` already retired the mirrored direct-bytes sidecars from this same owner file; and
  - `ops/tasks/done/RBR-0719-collapse-branch-local-direct-test-bucket-sidecar-onto-canonical-case-owners.md` plus `ops/tasks/done/RBR-0721-collapse-quantified-alternation-direct-test-bucket-registry-onto-canonical-case-owners.md` already removed the same style of detached direct-test bucket owner layer from adjacent parity suites.

## Completion Notes
- 2026-03-20: Replaced `WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_DIRECT_TEST_CASE_ID_BUCKETS` with the file-local `_wider_ranged_repeat_direct_test_case_id_buckets()` helper, derived directly from `COMPILE_CASES`, `MODULE_CASES`, `PATTERN_CASES`, and `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` so the detached registry is gone while bucket ordering and bytes-follow-on routing stay unchanged.
- 2026-03-20: Updated `test_wider_ranged_repeat_quantified_group_direct_test_case_id_buckets_cover_selected_frontier` to call the derived helper instead of reading a top-level mirrored bucket map.
- 2026-03-20: Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` (`1341 passed in 0.98s`), the acceptance derived-bucket probe (`ok`), and `bash -lc "! rg -n 'WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_DIRECT_TEST_CASE_ID_BUCKETS' tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py"`.
