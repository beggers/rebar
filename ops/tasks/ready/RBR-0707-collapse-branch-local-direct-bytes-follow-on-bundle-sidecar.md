# RBR-0707: Collapse branch-local direct-bytes follow-on bundle sidecar onto canonical spec records

Status: ready
Owner: architecture-implementation
Created: 2026-03-19

## Goal
- Remove the mirrored `DIRECT_BYTES_FOLLOW_ON_BUNDLES` tuple from `tests/python/test_branch_local_backreference_parity_suite.py` so `DIRECT_BYTES_FOLLOW_ON_SPECS` becomes the sole canonical owner for branch-local direct-bytes follow-on bundle ordering and routing.

## Deliverables
- `tests/python/test_branch_local_backreference_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_branch_local_backreference_parity_suite.py` stops defining `DIRECT_BYTES_FOLLOW_ON_BUNDLES`.
- The two local consumers derive follow-on bundle ordering directly from `DIRECT_BYTES_FOLLOW_ON_SPECS` instead of the deleted tuple:
  - `COMPILE_CASES, MODULE_CASES, PATTERN_CASES = partition_direct_bytes_follow_on_case_buckets(...)` no longer reads `DIRECT_BYTES_FOLLOW_ON_BUNDLES`.
  - `test_branch_local_backreference_mixed_text_model_manifests_keep_explicit_direct_bytes_follow_on_routing` no longer reads `DIRECT_BYTES_FOLLOW_ON_BUNDLES`.
- Preserve the current effective ordering and routing exactly:
  - the direct-bytes follow-on bundle order stays exactly `quantified-alternation-branch-local-backreference-workflows`, `quantified-nested-group-alternation-branch-local-backreference-workflows`, `nested-broader-range-wider-ranged-repeat-quantified-group-alternation-branch-local-backreference-workflows`, `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-workflows`, `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-workflows`;
  - the `@pytest.mark.parametrize("spec", DIRECT_BYTES_FOLLOW_ON_SPECS, ids=lambda spec: spec.bundle.manifest.manifest_id)` ids stay unchanged; and
  - `COMPILE_CASES`, `MODULE_CASES`, `PATTERN_CASES`, `DIRECT_BYTES_FOLLOW_ON_CASES`, and `BRANCH_LOCAL_BACKREFERENCE_DIRECT_TEST_CASE_ID_BUCKETS` keep the same effective case membership and ordering as today.
- Keep canonical ownership unchanged:
  - do not change `DIRECT_BYTES_FOLLOW_ON_SPECS` membership, `BranchLocalBytesFollowOnSpec` fields, bytes follow-on case payloads, expected module-search or pattern-fullmatch text maps, unsupported-backend expectations, or the selected bundle cases; and
  - do not broaden into `GENERATED_QUANTIFIED_BRANCH_LOCAL_PARITY_SPEC_BY_MANIFEST_ID`, `GENERATED_STR_BRANCH_LOCAL_CANDIDATE_TEXTS_BY_MANIFEST_ID`, `GENERATED_BYTES_BRANCH_LOCAL_CANDIDATE_TEXTS_BY_MANIFEST_ID`, `MATCH_GROUP_ACCESS_CASE_IDS`, or other unrelated registries in this file.
- Keep scope structural only:
  - do not edit `tests/python/fixture_parity_support.py`, `python/rebar_harness/correctness.py`, correctness fixture modules under `tests/conformance/fixtures/`, published reports, or tracked project-state prose.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from pathlib import Path

source = Path("tests/python/test_branch_local_backreference_parity_suite.py").read_text(
    encoding="utf-8"
)
assert "DIRECT_BYTES_FOLLOW_ON_BUNDLES" not in source
print("ok")
PY`
  - `bash -lc "! rg -n 'DIRECT_BYTES_FOLLOW_ON_BUNDLES' tests/python/test_branch_local_backreference_parity_suite.py"`

## Constraints
- Keep this cleanup structural only. The point is to delete one more mirrored bundle-order owner layer inside the branch-local parity owner, not to reinterpret the branch-local backreference frontier, change which direct-bytes cases stay explicit, or alter the generic compile/module/pattern bucket partitioning.
- Prefer deriving the bundle list directly from `DIRECT_BYTES_FOLLOW_ON_SPECS` over introducing another detached tuple, helper registry, or copied manifest-id table.

## Notes
- `RBR-0707` is the next available architecture-task id in the current checkout:
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
print('highest_existing_tail:', existing_sorted[-15:])
print('reserved_missing_tail:', reserved[-15:])
PY` reported the highest existing tail as `RBR-0692` through `RBR-0706` and no reserved missing tail ids.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the last recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The detached bundle sidecar is concrete and bounded in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py` currently passes (`561 passed in 0.81s`);
  - `rg -n "DIRECT_BYTES_FOLLOW_ON_BUNDLES|DIRECT_BYTES_FOLLOW_ON_SPECS" tests/python/test_branch_local_backreference_parity_suite.py` shows `DIRECT_BYTES_FOLLOW_ON_BUNDLES` is declared once and consumed only by the direct-bytes bucket partitioning call and the mixed-text-model routing test in the same file;
  - the inline source probe in Acceptance currently fails exactly on this cleanup with `AssertionError`; and
  - the final `rg` absence check in Acceptance currently fails exactly on this cleanup because `DIRECT_BYTES_FOLLOW_ON_BUNDLES` still exists at the declaration and both local call sites.
- This simplification matches the current parity-harness information flow:
  - `DIRECT_BYTES_FOLLOW_ON_SPECS` already owns the per-manifest bundle, bytes-case, bucket-label, and expected-search/fullmatch metadata for this branch-local follow-on surface; and
  - deleting the mirrored bundle tuple removes one more parallel owner layer without changing the published correctness slice or the direct-bytes follow-on routing contract.
