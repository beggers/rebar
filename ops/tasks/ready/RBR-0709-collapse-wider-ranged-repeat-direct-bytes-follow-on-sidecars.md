# RBR-0709: Collapse wider-ranged-repeat direct-bytes follow-on sidecars onto canonical spec records

Status: ready
Owner: architecture-implementation
Created: 2026-03-19

## Goal
- Remove the detached `DIRECT_BYTES_FOLLOW_ON_SPECS`, `DIRECT_BYTES_FOLLOW_ON_SPEC_IDS`, and `DIRECT_BYTES_FOLLOW_ON_BUNDLES` registries from `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` so `DirectBytesFollowOnSpec` and `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` become the single canonical owner of direct-bytes follow-on ids, bundle ordering, and supplemental-case routing inside the wider-ranged-repeat parity owner.

## Deliverables
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` stops defining these detached direct-bytes follow-on sidecars:
  - delete `DIRECT_BYTES_FOLLOW_ON_SPECS`;
  - delete `DIRECT_BYTES_FOLLOW_ON_SPEC_IDS`; and
  - delete `DIRECT_BYTES_FOLLOW_ON_BUNDLES`.
- The direct-bytes follow-on consumers derive their parametrization, ids, and bundle routing directly from `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` instead of the deleted registries:
  - `COMPILE_CASES, MODULE_CASES, PATTERN_CASES = partition_direct_bytes_follow_on_case_buckets(...)` no longer reads `DIRECT_BYTES_FOLLOW_ON_BUNDLES`;
  - `WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_DIRECT_TEST_CASE_ID_BUCKETS` no longer zips `DIRECT_BYTES_FOLLOW_ON_SPEC_IDS` with `DIRECT_BYTES_FOLLOW_ON_BUNDLES`;
  - `test_direct_bytes_follow_on_manifests_exclude_only_bytes_rows_from_generic_case_buckets` no longer parametrizes over `DIRECT_BYTES_FOLLOW_ON_SPECS` or `DIRECT_BYTES_FOLLOW_ON_SPEC_IDS`; and
  - `test_direct_bytes_follow_on_cases_stay_explicit_with_one_direct_follow_on_anchor` no longer uses `DIRECT_BYTES_FOLLOW_ON_SPEC_IDS` for pytest ids.
- Preserve the current effective ordering and naming exactly:
  - the short direct-bytes follow-on ids stay exactly `broader-range-conditional`, `broader-range-backtracking-heavy`, `nested-broader-range-alternation`, `nested-broader-range-conditional`, `nested-broader-range-backtracking-heavy` in that order;
  - the direct-test bucket keys ending in `-bytes-follow-on` stay exactly `broader-range-conditional-bytes-follow-on`, `broader-range-backtracking-heavy-bytes-follow-on`, `nested-broader-range-alternation-bytes-follow-on`, `nested-broader-range-conditional-bytes-follow-on`, `nested-broader-range-backtracking-heavy-bytes-follow-on` in that order; and
  - `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` keeps the same bundle/supplemental-case pairing and manifest order as today: `broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-workflows`, `broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-workflows`, `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-workflows`, `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-workflows`, `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-workflows`.
- Keep canonical ownership unchanged:
  - do not change `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` membership, `SupplementalCase` payloads, expected operation-helper counts, published module-search/fullmatch text maps, expected per-case payloads, or `DIRECT_BYTES_FOLLOW_ON_CASES`;
  - do not change `FIXTURE_BUNDLES`, `WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_SELECTED_CASE_IDS`, `WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_DIRECT_TEST_CASE_ID_BUCKETS` coverage, `BACKTRACKING_TRACE_CASES`, `PATTERN_BOUNDS_MATCH_CASES`, or the direct parity surface they represent; and
  - a tiny file-local helper or an added `id` field on `DirectBytesFollowOnSpec` is acceptable only if it replaces the deleted sidecars rather than introducing another mirrored registry.
- Keep scope structural only:
  - do not edit `tests/python/fixture_parity_support.py`, correctness fixture modules under `tests/conformance/fixtures/`, `python/rebar_harness/correctness.py`, published reports, or tracked project-state prose.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from pathlib import Path

source = Path("tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py").read_text(
    encoding="utf-8"
)
for needle in (
    "DIRECT_BYTES_FOLLOW_ON_SPECS",
    "DIRECT_BYTES_FOLLOW_ON_SPEC_IDS",
    "DIRECT_BYTES_FOLLOW_ON_BUNDLES",
):
    assert needle not in source, needle
print("ok")
PY`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
import subprocess

expected_ids = (
    "broader-range-conditional",
    "broader-range-backtracking-heavy",
    "nested-broader-range-alternation",
    "nested-broader-range-conditional",
    "nested-broader-range-backtracking-heavy",
)
collected = subprocess.check_output(
    [
        "./.venv/bin/python",
        "-m",
        "pytest",
        "--collect-only",
        "-q",
        "tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py",
    ],
    text=True,
).splitlines()
target_lines = [
    line
    for line in collected
    if "test_direct_bytes_follow_on_manifests_exclude_only_bytes_rows_from_generic_case_buckets[" in line
    or "test_direct_bytes_follow_on_cases_stay_explicit_with_one_direct_follow_on_anchor[" in line
]
expected = [
    "tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py::"
    f"test_direct_bytes_follow_on_manifests_exclude_only_bytes_rows_from_generic_case_buckets[{spec_id}]"
    for spec_id in expected_ids
] + [
    "tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py::"
    f"test_direct_bytes_follow_on_cases_stay_explicit_with_one_direct_follow_on_anchor[{spec_id}]"
    for spec_id in expected_ids
]
assert target_lines == expected, target_lines
print("ok")
PY`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
import tests.python.test_wider_ranged_repeat_quantified_group_parity_suite as mod

assert tuple(
    key
    for key in mod.WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_DIRECT_TEST_CASE_ID_BUCKETS
    if key.endswith("-bytes-follow-on")
) == (
    "broader-range-conditional-bytes-follow-on",
    "broader-range-backtracking-heavy-bytes-follow-on",
    "nested-broader-range-alternation-bytes-follow-on",
    "nested-broader-range-conditional-bytes-follow-on",
    "nested-broader-range-backtracking-heavy-bytes-follow-on",
)
assert tuple(
    spec.bundle.expected_manifest_id
    for spec in mod.DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES
) == (
    "broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-workflows",
    "broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-workflows",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-workflows",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-workflows",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-workflows",
)
print("ok")
PY`
  - `bash -lc "! rg -n 'DIRECT_BYTES_FOLLOW_ON_SPECS|DIRECT_BYTES_FOLLOW_ON_SPEC_IDS|DIRECT_BYTES_FOLLOW_ON_BUNDLES' tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py"`

## Constraints
- Keep this cleanup structural only. The point is to delete one more mirrored direct-bytes owner layer inside the wider-ranged-repeat parity suite, not to reinterpret the broader `{1,4}` grouped frontier, change which bytes follow-on cases stay explicit, or broaden the suite beyond the current published slice.
- Prefer deriving ids and bundle routing directly from `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` over introducing another top-level tuple/list/map block or another detached helper registry.

## Notes
- `RBR-0709` is the next available architecture-task id in the current checkout:
  - `python3 - <<'PY'
import pathlib, re
existing=set()
for base in ['ops/tasks/ready','ops/tasks/in_progress','ops/tasks/done','ops/tasks/blocked']:
    for path in pathlib.Path(base).glob('RBR-*.md'):
        m=re.match(r'(RBR-\\d+[A-Z]?)', path.name)
        if m:
            existing.add(m.group(1))
text='\\n'.join(pathlib.Path(p).read_text(encoding='utf-8') for p in ['ops/state/backlog.md','ops/state/current_status.md'])
mentioned=set(re.findall(r'RBR-\\d+[A-Z]?', text))
reserved=sorted(mentioned-existing, key=lambda s:(int(re.search(r'\\d+', s).group()), s))
existing_sorted=sorted(existing, key=lambda s:(int(re.search(r'\\d+', s).group()), s))
print('highest_existing_tail:', existing_sorted[-20:])
print('reserved_missing_tail:', reserved[-20:])
PY` reported the highest existing tail as `RBR-0689` through `RBR-0708` and no reserved missing tail ids.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the last recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The detached direct-bytes follow-on sidecars are concrete and bounded in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` currently passes (`1341 passed in 0.96s`);
  - `rg -n 'DIRECT_BYTES_FOLLOW_ON_(SPECS|SPEC_IDS|BUNDLES)|DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES|partition_direct_bytes_follow_on_case_buckets' tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` shows the detached registries are declared once and consumed only by the direct-bytes bucket partitioning call, the direct-test bucket map, and the two direct-bytes follow-on tests in the same file;
  - the inline source probe in Acceptance currently fails exactly on this cleanup with `AssertionError: DIRECT_BYTES_FOLLOW_ON_SPECS`;
  - the final `rg` absence check in Acceptance currently fails exactly on this cleanup because all three target names still exist; and
  - the pytest collection probe plus the bucket-key/manifest-order probe in Acceptance already pass in the current checkout, so they pin behavior rather than future drift.
- This simplification matches the current parity-harness information flow:
  - `ops/tasks/done/RBR-0703-collapse-quantified-alternation-direct-bytes-follow-on-sidecars.md` and `ops/tasks/done/RBR-0707-collapse-branch-local-direct-bytes-follow-on-bundle-sidecar.md` already removed the same style of mirrored direct-bytes owner layers from adjacent parity owners; and
  - `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` already acts as the canonical owner of the wider-ranged-repeat direct-bytes bundle/case pairing, so deleting the remaining id and bundle sidecars removes one more parallel owner layer without changing published correctness coverage.
