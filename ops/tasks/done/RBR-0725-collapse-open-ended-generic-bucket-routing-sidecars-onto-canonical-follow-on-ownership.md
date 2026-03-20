# RBR-0725: Collapse open-ended generic-bucket routing sidecars onto canonical follow-on ownership

Status: done
Owner: architecture-implementation
Created: 2026-03-20
Completed: 2026-03-20

## Goal
- Remove the duplicated generic-bucket routing metadata from `tests/python/test_open_ended_quantified_group_parity_suite.py` so the open-ended parity owner derives generic-vs-follow-on bytes routing directly from the canonical `follow_on_id` / `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` split instead of maintaining a stale boolean field plus a detached manifest-id sidecar.

## Deliverables
- `tests/python/test_open_ended_quantified_group_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_open_ended_quantified_group_parity_suite.py` stops defining or reading these duplicated routing sidecars:
  - delete the `routes_through_generic_case_buckets` field from `BytesCaseSurfaceSpec`; and
  - delete `OPEN_ENDED_GENERIC_BUCKET_BYTES_CASE_SURFACES`.
- The open-ended bytes-routing assertions derive their generic-vs-follow-on split from canonical ownership instead of from the deleted sidecars:
  - `test_bytes_cases_stay_explicit_with_expected_bundle_coverage` no longer reads `spec.routes_through_generic_case_buckets`;
  - `test_generic_bytes_fixture_rows_run_through_generic_case_buckets` no longer parametrizes over `OPEN_ENDED_GENERIC_BUCKET_BYTES_CASE_SURFACES`; and
  - if a tiny file-local helper is useful, keep it derived from `OPEN_ENDED_BYTES_CASE_SURFACES` plus `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` or `spec.follow_on_id`, rather than introducing another mirrored tuple/list/map block.
- Preserve the current effective routing split exactly:
  - the direct follow-on manifest ids stay exactly `broader-range-open-ended-quantified-group-alternation-workflows`, `open-ended-quantified-group-alternation-backtracking-heavy-workflows`, `broader-range-open-ended-quantified-group-alternation-conditional-workflows`, `broader-range-open-ended-quantified-group-alternation-backtracking-heavy-workflows` in the current `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` order;
  - the generic-bucket manifest ids are derived in `OPEN_ENDED_BYTES_CASE_SURFACES` order and stay exactly `open-ended-quantified-group-alternation-workflows`, `open-ended-quantified-group-alternation-conditional-workflows`, `nested-open-ended-quantified-group-alternation-workflows`; and
  - `test_generic_bytes_fixture_rows_run_through_generic_case_buckets` collects exactly those three manifest ids in that order, matching the live bucket contents instead of the current two-entry sidecar.
- Keep canonical ownership otherwise unchanged:
  - do not change `OPEN_ENDED_BYTES_CASE_SURFACES` membership, ordering, bundle/case pairing, `follow_on_id` values, bytes-case payloads, expected operation-helper counts, published bytes text maps, or `OPEN_ENDED_SUPPLEMENTAL_BYTES_CASES`;
  - do not change `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES`, `COMPILE_CASES`, `MODULE_CASES`, `PATTERN_CASES`, `OPEN_ENDED_QUANTIFIED_GROUP_SELECTED_CASE_IDS`, or the published parity surface they represent; and
  - do not broaden into `tests/python/fixture_parity_support.py`, correctness fixtures under `tests/conformance/fixtures/`, benchmark manifests/tests, reports, README copy, or tracked project-state prose.
- Keep scope structural only:
  - do not reinterpret which open-ended grouped bytes cases stay explicit, do not move any family between the generic buckets and the direct follow-on path, and do not use this run to remove `OPEN_ENDED_QUANTIFIED_GROUP_DIRECT_TEST_CASE_ID_BUCKETS`.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
import tests.python.test_open_ended_quantified_group_parity_suite as mod

direct_manifest_ids = tuple(
    spec.bundle.manifest.manifest_id for spec in mod.DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES
)
generic_manifest_ids = tuple(
    spec.bundle.manifest.manifest_id
    for spec in mod.OPEN_ENDED_BYTES_CASE_SURFACES
    if spec.bundle.manifest.manifest_id not in direct_manifest_ids
)
assert direct_manifest_ids == (
    "broader-range-open-ended-quantified-group-alternation-workflows",
    "open-ended-quantified-group-alternation-backtracking-heavy-workflows",
    "broader-range-open-ended-quantified-group-alternation-conditional-workflows",
    "broader-range-open-ended-quantified-group-alternation-backtracking-heavy-workflows",
)
assert generic_manifest_ids == (
    "open-ended-quantified-group-alternation-workflows",
    "open-ended-quantified-group-alternation-conditional-workflows",
    "nested-open-ended-quantified-group-alternation-workflows",
)
print("ok")
PY`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
import subprocess

collected = subprocess.check_output(
    [
        "./.venv/bin/python",
        "-m",
        "pytest",
        "--collect-only",
        "-q",
        "tests/python/test_open_ended_quantified_group_parity_suite.py",
    ],
    text=True,
).splitlines()
target_lines = [
    line
    for line in collected
    if "test_generic_bytes_fixture_rows_run_through_generic_case_buckets[" in line
]
assert target_lines == [
    "tests/python/test_open_ended_quantified_group_parity_suite.py::"
    "test_generic_bytes_fixture_rows_run_through_generic_case_buckets[open-ended-quantified-group-alternation-workflows]",
    "tests/python/test_open_ended_quantified_group_parity_suite.py::"
    "test_generic_bytes_fixture_rows_run_through_generic_case_buckets[open-ended-quantified-group-alternation-conditional-workflows]",
    "tests/python/test_open_ended_quantified_group_parity_suite.py::"
    "test_generic_bytes_fixture_rows_run_through_generic_case_buckets[nested-open-ended-quantified-group-alternation-workflows]",
], target_lines
print("ok")
PY`
  - `bash -lc "! rg -n 'routes_through_generic_case_buckets|OPEN_ENDED_GENERIC_BUCKET_BYTES_CASE_SURFACES' tests/python/test_open_ended_quantified_group_parity_suite.py"`

## Constraints
- Keep this cleanup structural only. The point is to delete one more mirrored routing-owner layer inside the open-ended parity suite, not to reinterpret the open-ended grouped bytes frontier or change backend behavior.
- Prefer deriving generic-bucket routing directly from `follow_on_id` / `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` over introducing another detached helper registry or another explicit manifest-id tuple.

## Notes
- `RBR-0725` is the next available architecture-task id in the current checkout:
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
PY` reported the existing tail through `RBR-0724`, no reserved missing tail ids, and `next_free RBR-0725`.
- No blocked architecture task exists to reopen first, and the current runtime state does not trigger rule 10:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added;
  - `.rebar/runtime/dashboard.md` is aligned with `HEAD` (`6787178ba04e20e4d1b4785f9693c4ae8b617e55`), reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplicated generic-routing metadata is concrete and bounded in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py` passes (`3922 passed in 2.66s`);
  - the direct/generic manifest probe in Acceptance already passes in the current checkout (`ok`) and shows the canonical generic split includes `nested-open-ended-quantified-group-alternation-workflows`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest --collect-only -q tests/python/test_open_ended_quantified_group_parity_suite.py | rg "test_generic_bytes_fixture_rows_run_through_generic_case_buckets\\["` currently reports only the two sidecar-driven open-ended manifest ids, so the collect-only Acceptance above currently fails exactly on this cleanup; and
  - `bash -lc "! rg -n 'routes_through_generic_case_buckets|OPEN_ENDED_GENERIC_BUCKET_BYTES_CASE_SURFACES' tests/python/test_open_ended_quantified_group_parity_suite.py"` currently fails exactly on this cleanup because the duplicated field, the detached tuple, and their reads still exist.
- This simplification follows the already-landed open-ended architecture direction instead of opening a new lane:
  - `ops/tasks/done/RBR-0608-collapse-open-ended-quantified-group-bytes-routing-and-parity-ladders-onto-one-table.md` already pinned the canonical routing split as three generic-bucket manifests plus four direct follow-on manifests on this owner suite; and
  - the current `OPEN_ENDED_GENERIC_BUCKET_BYTES_CASE_SURFACES` sidecar has drifted below that canonical split by omitting the nested-open-ended manifest even though the live generic buckets still include its bytes rows.
- 2026-03-20 completion:
  - Removed the mirrored `routes_through_generic_case_buckets` field and deleted `OPEN_ENDED_GENERIC_BUCKET_BYTES_CASE_SURFACES` from `tests/python/test_open_ended_quantified_group_parity_suite.py`.
  - Derived the generic-bucket parametrization and routing assertion directly from `follow_on_id` / `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES`, preserving the existing direct follow-on order and restoring the nested open-ended manifest to the generic collect-only surface.
  - Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py` (`3923 passed in 2.72s`), the inline manifest-order probe (`ok`), the collect-only generic-bucket probe (`ok`), and the `rg` absence check for the deleted sidecars (no matches).
