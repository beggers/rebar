# RBR-0717: Collapse branch-local direct bucket-label sidecars onto bundle manifests

Status: done
Owner: architecture-implementation
Created: 2026-03-19

## Goal
- Remove the redundant `bucket_label` strings from `BranchLocalBytesFollowOnSpec` in `tests/python/test_branch_local_backreference_parity_suite.py` so each direct-bytes follow-on bundle manifest id becomes the sole canonical owner of the branch-local direct-test bucket naming.

## Deliverables
- `tests/python/test_branch_local_backreference_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_branch_local_backreference_parity_suite.py` stops defining or consuming these detached bucket-label sidecars:
  - delete the `bucket_label` field from `BranchLocalBytesFollowOnSpec`;
  - delete every `bucket_label=` argument passed when constructing `DIRECT_BYTES_FOLLOW_ON_SPECS`; and
  - delete every `spec.bucket_label` read in the file.
- The direct-test bucket naming derives directly from the canonical follow-on bundles instead of the deleted field:
  - `BRANCH_LOCAL_BACKREFERENCE_DIRECT_TEST_CASE_ID_BUCKETS` no longer reads `spec.bucket_label`;
  - `test_direct_bytes_follow_on_cases_stay_explicit_with_one_direct_follow_on_anchor` no longer reads `spec.bucket_label`; and
  - if a tiny file-local helper is useful, keep it bundle-manifest-driven instead of introducing another detached tuple/list/map block.
- Preserve the current effective naming and ordering exactly:
  - the direct-test bucket keys ending with `-bytes-follow-on` stay exactly `quantified-alternation-branch-local-backreference-bytes-follow-on`, `quantified-nested-group-alternation-branch-local-backreference-bytes-follow-on`, `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-bytes-follow-on`, `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-bytes-follow-on`, `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-bytes-follow-on` in that order; and
  - those five bucket keys still equal the ordered `DIRECT_BYTES_FOLLOW_ON_SPECS` manifest ids with `-workflows` replaced by `-bytes-follow-on`.
- Keep canonical ownership otherwise unchanged:
  - do not change `DIRECT_BYTES_FOLLOW_ON_SPECS` membership, bundle ordering, bytes follow-on case payloads, expected module-search or pattern-fullmatch text maps, unsupported-backend expectations, or `DIRECT_BYTES_FOLLOW_ON_CASES`;
  - do not broaden into `MATCH_CONVENIENCE_MANIFEST_IDS`, `MATCH_GROUP_ACCESS_CASE_IDS`, generated quantified parity specs, fixture modules under `tests/conformance/fixtures/`, or shared helpers in `tests/python/fixture_parity_support.py`; and
  - keep the shared compile/module/pattern buckets and the selected published workflow coverage unchanged.
- Keep scope structural only:
  - do not edit `python/rebar_harness/correctness.py`, published reports, benchmarks, README copy, or tracked project-state prose.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from pathlib import Path

source = Path("tests/python/test_branch_local_backreference_parity_suite.py").read_text(
    encoding="utf-8"
)
for needle in ("bucket_label: str", "bucket_label=", "spec.bucket_label"):
    assert needle not in source, needle
print("ok")
PY`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
import tests.python.test_branch_local_backreference_parity_suite as mod

expected_keys = (
    "quantified-alternation-branch-local-backreference-bytes-follow-on",
    "quantified-nested-group-alternation-branch-local-backreference-bytes-follow-on",
    "nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-bytes-follow-on",
    "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-bytes-follow-on",
    "nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-bytes-follow-on",
)
assert tuple(
    key
    for key in mod.BRANCH_LOCAL_BACKREFERENCE_DIRECT_TEST_CASE_ID_BUCKETS
    if key.endswith("-bytes-follow-on")
) == expected_keys
assert expected_keys == tuple(
    f"{spec.bundle.expected_manifest_id.removesuffix('-workflows')}-bytes-follow-on"
    for spec in mod.DIRECT_BYTES_FOLLOW_ON_SPECS
)
print("ok")
PY`
  - `bash -lc "! rg -n 'bucket_label: str|bucket_label=|spec\\.bucket_label' tests/python/test_branch_local_backreference_parity_suite.py"`

## Constraints
- Keep this cleanup structural only. The point is to delete one more mirrored naming owner layer inside the branch-local direct-bytes follow-on surface, not to reinterpret branch-local backreference behavior, change which bytes cases stay explicit, or broaden the suite beyond the current published slice.
- Prefer deriving bucket keys directly from each follow-on bundle's canonical manifest id over introducing another top-level registry or another copied label field.

## Notes
- `RBR-0717` is the next available architecture-task id in the current checkout:
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
mentioned = set(re.findall(r'RBR-\\d+[A-Z]?', text))
reserved = sorted(mentioned - existing, key=lambda s: (int(re.search(r'\\d+', s).group()), s))
existing_sorted = sorted(existing, key=lambda s: (int(re.search(r'\\d+', s).group()), s))
print('highest_existing_tail:', existing_sorted[-10:])
print('reserved_missing_tail:', reserved[-10:])
PY` reported the highest existing tail as `RBR-0707` through `RBR-0716` and no reserved missing tail ids.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The redundant bucket-label field is concrete and bounded in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py` currently passes (`561 passed in 0.82s`);
  - `rg -n "bucket_label: str|bucket_label=|spec\\.bucket_label" tests/python/test_branch_local_backreference_parity_suite.py` shows the field, constructor arguments, and reads live only in this file's direct-bytes follow-on block plus one assertion;
  - the inline source-absence probe in Acceptance currently fails exactly on this cleanup with `AssertionError: bucket_label: str`;
  - the final `rg` absence check in Acceptance currently fails exactly on this cleanup because the field, constructor arguments, and reads still exist; and
  - the import probe in Acceptance already passes in the current checkout, so it pins the preserved bucket order and the manifest-derived bucket-label contract independently of the structural cleanup.
- This simplification matches the current branch-local parity information flow:
  - `DIRECT_BYTES_FOLLOW_ON_SPECS` already owns the canonical per-manifest bundle ordering plus the bytes-case and expected-text metadata for this direct follow-on surface; and
  - the current `bucket_label` strings are mechanically `spec.bundle.expected_manifest_id.removesuffix("-workflows") + "-bytes-follow-on"`, so deleting them removes one more mirrored owner layer without changing published correctness coverage.

## Completion Notes
- 2026-03-19: Deleted the `bucket_label` field and constructor sidecars from `tests/python/test_branch_local_backreference_parity_suite.py`, added a small bundle-manifest-driven helper for direct-bytes follow-on bucket naming, and switched the direct bucket map plus the direct-follow-on anchor assertion to derive keys from each bundle's canonical manifest id.
- 2026-03-19: Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py` (`561 passed in 0.84s`), the inline source-absence probe (`ok`), the import/bucket-order probe (`ok`), and `bash -lc "! rg -n 'bucket_label: str|bucket_label=|spec\\.bucket_label' tests/python/test_branch_local_backreference_parity_suite.py"`.
