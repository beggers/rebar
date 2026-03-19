# RBR-0719: Collapse branch-local direct-test bucket sidecar onto canonical case owners

Status: done
Owner: architecture-implementation
Created: 2026-03-19

## Goal
- Remove the detached `BRANCH_LOCAL_BACKREFERENCE_DIRECT_TEST_CASE_ID_BUCKETS` registry from `tests/python/test_branch_local_backreference_parity_suite.py` so the branch-local parity owner derives direct-test bucket coverage from its canonical shared case buckets and direct-bytes follow-on specs instead of maintaining a mirrored top-level map.

## Deliverables
- `tests/python/test_branch_local_backreference_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_branch_local_backreference_parity_suite.py` stops defining or reading `BRANCH_LOCAL_BACKREFERENCE_DIRECT_TEST_CASE_ID_BUCKETS`.
- The branch-local direct-test coverage derives from existing canonical owners instead of from the deleted registry:
  - `test_branch_local_backreference_direct_test_case_id_buckets_cover_selected_frontier` no longer passes a detached top-level bucket map;
  - `test_direct_bytes_follow_on_cases_stay_explicit_with_one_direct_follow_on_anchor` no longer indexes a detached top-level bucket map; and
  - if a tiny file-local helper is useful, keep it derived from `COMPILE_CASES`, `MODULE_CASES`, `PATTERN_CASES`, and `DIRECT_BYTES_FOLLOW_ON_SPECS` instead of introducing another mirrored tuple/list/map block.
- Preserve the current effective bucket ordering and routing exactly:
  - the shared bucket keys stay `shared-compile`, `shared-module`, `shared-pattern` in that order;
  - the bytes-follow-on bucket keys stay exactly `quantified-alternation-branch-local-backreference-bytes-follow-on`, `quantified-nested-group-alternation-branch-local-backreference-bytes-follow-on`, `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-bytes-follow-on`, `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-bytes-follow-on`, `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-bytes-follow-on` in the current `DIRECT_BYTES_FOLLOW_ON_SPECS` order; and
  - each bytes-follow-on bucket still equals the `frozenset` of `case.case_id` values from the corresponding `spec.bundle.cases` where `case.text_model == "bytes"`.
- Keep canonical ownership otherwise unchanged:
  - do not change `DIRECT_BYTES_FOLLOW_ON_SPECS` membership, bundle ordering, bytes follow-on case payloads, expected operation-helper counts, expected module-search or pattern-fullmatch text maps, unsupported-backend expectations, or `DIRECT_BYTES_FOLLOW_ON_CASES`;
  - do not change `COMPILE_CASES`, `MODULE_CASES`, `PATTERN_CASES`, `WORKFLOW_CASES`, `BRANCH_LOCAL_BACKREFERENCE_SELECTED_CASE_IDS`, or the selected published workflow surface they represent; and
  - do not broaden into `MATCH_CONVENIENCE_MANIFEST_IDS`, `MATCH_GROUP_ACCESS_CASE_IDS`, generated quantified parity specs, shared helpers in `tests/python/fixture_parity_support.py`, or fixture modules under `tests/conformance/fixtures/`.
- Keep scope structural only:
  - do not edit `python/rebar_harness/correctness.py`, published reports, benchmarks, README copy, or tracked project-state prose.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
import tests.python.test_branch_local_backreference_parity_suite as mod

assert tuple(
    f"{spec.bundle.expected_manifest_id.removesuffix('-workflows')}-bytes-follow-on"
    for spec in mod.DIRECT_BYTES_FOLLOW_ON_SPECS
) == (
    "quantified-alternation-branch-local-backreference-bytes-follow-on",
    "quantified-nested-group-alternation-branch-local-backreference-bytes-follow-on",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-bytes-follow-on",
    "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-bytes-follow-on",
    "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-bytes-follow-on",
)
print("ok")
PY`
  - `bash -lc "! rg -n 'BRANCH_LOCAL_BACKREFERENCE_DIRECT_TEST_CASE_ID_BUCKETS' tests/python/test_branch_local_backreference_parity_suite.py"`

## Constraints
- Keep this cleanup structural only. The point is to delete one more mirrored bucket-owner layer inside the branch-local direct-bytes follow-on surface, not to reinterpret branch-local backreference behavior, change which bytes cases stay explicit, or broaden the suite beyond the current published slice.
- Prefer deriving direct-test bucket coverage directly from the canonical shared case buckets plus `DIRECT_BYTES_FOLLOW_ON_SPECS` over introducing another detached helper registry.

## Notes
- `RBR-0719` is the next available task id in the current checkout:
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
print('highest_existing_tail', sorted(existing, key=lambda s: (int(re.search(r'\\d+', s).group()), s))[-15:])
print('reserved_tail', sorted(reserved, key=lambda s: (int(re.search(r'\\d+', s).group()), s))[-15:])
for n in range(719, 750):
    rid = f'RBR-{n:04d}'
    if rid not in existing and rid not in reserved:
        print('next_free', rid)
        break
PY` reported the existing tail through `RBR-0718`, no reserved missing tail ids, and `next_free RBR-0719`.
- No blocked architecture task exists to reopen first, and the current runtime state does not trigger rule 10:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - both task workers finished `done` in the latest recorded cycle, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The detached direct-test bucket map is concrete and bounded in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py` currently passes (`561 passed in 0.81s`);
  - `rg -n 'BRANCH_LOCAL_BACKREFERENCE_DIRECT_TEST_CASE_ID_BUCKETS =|BRANCH_LOCAL_BACKREFERENCE_DIRECT_TEST_CASE_ID_BUCKETS\\[|assert_direct_test_case_id_buckets_cover_selected_frontier\\(' tests/python/test_branch_local_backreference_parity_suite.py` currently shows the detached map plus its two call sites only in this file;
  - the final `rg` absence check in Acceptance currently fails exactly on this cleanup because the detached registry and its reads still exist; and
  - the import probe in Acceptance already passes in the current checkout, so it pins the preserved follow-on key order independently of the structural cleanup.
- This simplification matches the current branch-local parity information flow:
  - `COMPILE_CASES`, `MODULE_CASES`, and `PATTERN_CASES` already own the shared direct-test buckets; and
  - `DIRECT_BYTES_FOLLOW_ON_SPECS` already owns the canonical follow-on bundle ordering plus the bytes-case routing needed to derive the five explicit follow-on buckets without a second owner layer.

## Completion Notes
- 2026-03-19: Replaced `BRANCH_LOCAL_BACKREFERENCE_DIRECT_TEST_CASE_ID_BUCKETS` with the file-local `_branch_local_direct_test_case_id_buckets()` helper, derived directly from `COMPILE_CASES`, `MODULE_CASES`, `PATTERN_CASES`, and `DIRECT_BYTES_FOLLOW_ON_SPECS` so the detached registry is gone while bucket routing stays unchanged.
- 2026-03-19: Updated the selected-frontier coverage test and the direct bytes follow-on anchor test to call the derived helper instead of indexing a top-level sidecar map.
- 2026-03-19: Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py` (`561 passed in 0.83s`), the acceptance import-order probe (`ok`), a direct helper probe covering shared-key and bytes-follow-on key order plus bytes-case routing (`ok`), and `bash -lc "! rg -n 'BRANCH_LOCAL_BACKREFERENCE_DIRECT_TEST_CASE_ID_BUCKETS' tests/python/test_branch_local_backreference_parity_suite.py"`.
