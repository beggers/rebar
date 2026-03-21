# RBR-0835: Collapse branch-local direct-bytes follow-on case sidecar onto canonical specs

Status: ready
Owner: architecture-implementation
Created: 2026-03-21

## Goal
- Remove the detached `DIRECT_BYTES_FOLLOW_ON_CASES` tuple from `tests/python/test_branch_local_backreference_parity_suite.py` so `DIRECT_BYTES_FOLLOW_ON_SPECS` becomes the sole canonical owner of direct-bytes follow-on case ordering and payload routing inside the branch-local backreference parity owner.

## Deliverables
- `tests/python/test_branch_local_backreference_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_branch_local_backreference_parity_suite.py` stops defining or reading `DIRECT_BYTES_FOLLOW_ON_CASES`.
- The seven direct-bytes follow-on parity tests derive their parametrization directly from `DIRECT_BYTES_FOLLOW_ON_SPECS` instead of from the deleted top-level tuple:
  - `test_direct_bytes_follow_on_compile_metadata_matches_cpython`
  - `test_direct_bytes_follow_on_module_search_matches_cpython`
  - `test_direct_bytes_follow_on_module_search_match_convenience_api_matches_cpython`
  - `test_direct_bytes_follow_on_module_search_match_group_access_matches_cpython`
  - `test_direct_bytes_follow_on_pattern_fullmatch_matches_cpython`
  - `test_direct_bytes_follow_on_pattern_fullmatch_match_convenience_api_matches_cpython`
  - `test_direct_bytes_follow_on_pattern_fullmatch_match_group_access_matches_cpython`
- Preserve the current effective follow-on case order exactly. The canonical flattening of `DIRECT_BYTES_FOLLOW_ON_SPECS` must stay:
  - `quantified-alternation-branch-local-numbered-bytes`
  - `quantified-alternation-branch-local-named-bytes`
  - `quantified-nested-group-alternation-branch-local-numbered-bytes`
  - `quantified-nested-group-alternation-branch-local-named-bytes`
  - `nested-broader-range-wider-ranged-repeat-branch-local-numbered-bytes`
  - `nested-broader-range-wider-ranged-repeat-branch-local-named-bytes`
  - `nested-broader-range-open-ended-branch-local-numbered-bytes`
  - `nested-broader-range-open-ended-branch-local-named-bytes`
  - `nested-broader-range-open-ended-branch-local-backreference-conditional-numbered-bytes`
  - `nested-broader-range-open-ended-branch-local-backreference-conditional-named-bytes`
- Keep canonical ownership otherwise unchanged:
  - do not change `DIRECT_BYTES_FOLLOW_ON_SPECS` membership, bundle ordering, bytes follow-on case payloads, expected operation-helper counts, expected module-search or pattern-fullmatch text maps, unsupported-backend expectations, or the current per-spec case ordering;
  - do not change `FIXTURE_BUNDLES`, `SUPPORTED_DIRECT_BYTES_PATTERNS`, `PUBLISHED_CASES`, `CASES_BY_ID`, `COMPILE_CASES`, `MODULE_CASES`, `PATTERN_CASES`, `WORKFLOW_CASES`, `BRANCH_LOCAL_BACKREFERENCE_SELECTED_CASE_IDS`, `MATCH_CONVENIENCE_CASE_IDS`, `MATCH_GROUP_ACCESS_CASE_IDS`, or the published direct parity surface they represent; and
  - if a tiny file-local helper is useful, keep it derived from `DIRECT_BYTES_FOLLOW_ON_SPECS` instead of introducing another mirrored tuple/list/map block.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
import tests.python.test_branch_local_backreference_parity_suite as mod

assert tuple(case.id for spec in mod.DIRECT_BYTES_FOLLOW_ON_SPECS for case in spec.cases) == (
    "quantified-alternation-branch-local-numbered-bytes",
    "quantified-alternation-branch-local-named-bytes",
    "quantified-nested-group-alternation-branch-local-numbered-bytes",
    "quantified-nested-group-alternation-branch-local-named-bytes",
    "nested-broader-range-wider-ranged-repeat-branch-local-numbered-bytes",
    "nested-broader-range-wider-ranged-repeat-branch-local-named-bytes",
    "nested-broader-range-open-ended-branch-local-numbered-bytes",
    "nested-broader-range-open-ended-branch-local-named-bytes",
    "nested-broader-range-open-ended-branch-local-backreference-conditional-numbered-bytes",
    "nested-broader-range-open-ended-branch-local-backreference-conditional-named-bytes",
)
print("ok")
PY`
  - `bash -lc "! rg -n 'DIRECT_BYTES_FOLLOW_ON_CASES' tests/python/test_branch_local_backreference_parity_suite.py"`

## Constraints
- Keep this cleanup structural only. The point is to delete one more mirrored owner layer inside the branch-local backreference parity suite, not to reinterpret which bytes follow-on cases stay explicit, move any family between the shared buckets and the direct follow-on path, or broaden the suite beyond the current published slice.
- Do not edit `tests/python/fixture_parity_support.py`, correctness fixtures under `tests/conformance/fixtures/`, benchmark manifests/tests, published reports, README copy, or tracked project-state prose in this run.

## Notes
- `RBR-0835` is the next available task id in the current checkout:
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
for n in range(1, 10000):
    rid = f'RBR-{n:04d}'
    if rid not in existing and rid not in reserved:
        print(rid)
        break
print('reserved_tail', reserved[-10:])
PY` returned `RBR-0835` with an empty reserved tail.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the last recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The sidecar is concrete and bounded in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py` currently passes (`561 passed in 0.81s`);
  - the canonical-order import probe in Acceptance currently passes and prints the ten ids listed above;
  - `rg -n 'DIRECT_BYTES_FOLLOW_ON_CASES' tests/python/test_branch_local_backreference_parity_suite.py` shows one declaration plus the seven target parametrizations in this file; and
  - the final `rg` absence check in Acceptance currently fails exactly on this cleanup because the mirrored tuple still exists.
- This stays on the same bounded post-JSON parity-harness cleanup track as `RBR-0707`, `RBR-0719`, `RBR-0741`, and `RBR-0742`: those tasks already removed adjacent branch-local bundle-label and direct-test sidecars plus the equivalent direct-bytes case sidecars from sibling suites, and `DIRECT_BYTES_FOLLOW_ON_SPECS` already carries the case payloads and ordering needed to delete this remaining flattened tuple without changing behavior.
