# RBR-0837: Collapse quantified alternation direct-bytes follow-on case sidecar onto canonical surfaces

Status: done
Owner: architecture-implementation
Created: 2026-03-21
Completed: 2026-03-21

## Goal
- Remove the detached `DIRECT_BYTES_FOLLOW_ON_CASES` tuple from `tests/python/test_quantified_alternation_parity_suite.py` so `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` becomes the sole canonical owner of quantified-alternation direct-bytes follow-on case ordering and payload routing inside this parity suite.

## Deliverables
- `tests/python/test_quantified_alternation_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_quantified_alternation_parity_suite.py` stops defining or reading `DIRECT_BYTES_FOLLOW_ON_CASES`.
- The seven direct-bytes follow-on parity tests derive their parametrization directly from `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` instead of from the deleted top-level tuple:
  - `test_direct_bytes_follow_on_compile_metadata_matches_cpython`
  - `test_direct_bytes_follow_on_module_search_matches_cpython`
  - `test_direct_bytes_follow_on_module_search_match_convenience_api_matches_cpython`
  - `test_direct_bytes_follow_on_module_search_match_group_access_matches_cpython`
  - `test_direct_bytes_follow_on_pattern_fullmatch_matches_cpython`
  - `test_direct_bytes_follow_on_pattern_fullmatch_match_convenience_api_matches_cpython`
  - `test_direct_bytes_follow_on_pattern_fullmatch_match_group_access_matches_cpython`
- Preserve the current effective follow-on case order exactly. The canonical flattening of `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` must stay:
  - `quantified-alternation-numbered-bytes`
  - `quantified-alternation-named-bytes`
  - `quantified-alternation-broader-range-numbered-bytes`
  - `quantified-alternation-broader-range-named-bytes`
  - `quantified-alternation-conditional-numbered-bytes`
  - `quantified-alternation-conditional-named-bytes`
  - `quantified-alternation-open-ended-numbered-bytes`
  - `quantified-alternation-open-ended-named-bytes`
  - `quantified-alternation-nested-branch-numbered-bytes`
  - `quantified-alternation-nested-branch-named-bytes`
  - `quantified-alternation-backtracking-heavy-numbered-bytes`
  - `quantified-alternation-backtracking-heavy-named-bytes`
- Keep canonical ownership otherwise unchanged:
  - do not change `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` membership, bundle ordering, bytes follow-on case payloads, expected operation-helper counts, expected module-search or pattern-fullmatch text maps, unsupported-backend expectations, or the current per-surface case ordering;
  - do not change `FIXTURE_BUNDLES`, `QUANTIFIED_ALTERNATION_SELECTED_CASE_IDS`, `COMPILE_CASES`, `MODULE_CASES`, `PATTERN_CASES`, `MATCH_GROUP_ACCESS_CASES`, `BACKTRACKING_HEAVY_COMPILE_CASES`, `PATTERN_BOUNDS_MATCH_CASES`, `PATTERN_BOUNDS_NO_MATCH_CASES`, `SUPPLEMENTAL_MISS_CASES`, or the published quantified-alternation parity surface they represent; and
  - if a tiny file-local helper is useful, keep it derived from `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` instead of introducing another mirrored tuple/list/map block.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
import tests.python.test_quantified_alternation_parity_suite as mod

assert tuple(case.id for spec in mod.DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES for case in spec.cases) == (
    "quantified-alternation-numbered-bytes",
    "quantified-alternation-named-bytes",
    "quantified-alternation-broader-range-numbered-bytes",
    "quantified-alternation-broader-range-named-bytes",
    "quantified-alternation-conditional-numbered-bytes",
    "quantified-alternation-conditional-named-bytes",
    "quantified-alternation-open-ended-numbered-bytes",
    "quantified-alternation-open-ended-named-bytes",
    "quantified-alternation-nested-branch-numbered-bytes",
    "quantified-alternation-nested-branch-named-bytes",
    "quantified-alternation-backtracking-heavy-numbered-bytes",
    "quantified-alternation-backtracking-heavy-named-bytes",
)
print("ok")
PY`
  - `bash -lc "! rg -n 'DIRECT_BYTES_FOLLOW_ON_CASES' tests/python/test_quantified_alternation_parity_suite.py"`

## Constraints
- Keep this cleanup structural only. The point is to delete one more mirrored owner layer inside the quantified-alternation parity suite, not to reinterpret which bytes follow-on cases stay explicit, move any family between the shared buckets and the direct follow-on path, or broaden the suite beyond the current published slice.
- Do not edit `tests/python/fixture_parity_support.py`, correctness fixtures under `tests/conformance/fixtures/`, benchmark manifests/tests, published reports, README copy, or tracked project-state prose in this run.

## Notes
- `RBR-0837` is the next available task id in the current checkout:
  - `python3 - <<'PY'
import pathlib, re
existing = set()
for base in ['ops/tasks/ready', 'ops/tasks/in_progress', 'ops/tasks/done', 'ops/tasks/blocked']:
    for path in pathlib.Path(base).glob('RBR-*.md'):
        m = re.match(r'(RBR-\d+[A-Z]?)', path.name)
        if m:
            existing.add(m.group(1))
text = '\n'.join(
    pathlib.Path(p).read_text(encoding='utf-8')
    for p in ['ops/state/backlog.md', 'ops/state/current_status.md']
)
mentioned = set(re.findall(r'RBR-\d+[A-Z]?', text))
reserved = sorted(mentioned - existing, key=lambda s: (int(re.search(r'\d+', s).group()), s))
for n in range(1, 10000):
    rid = f'RBR-{n:04d}'
    if rid not in existing and rid not in reserved:
        print(rid)
        break
print('reserved_tail', reserved[-10:])
PY` returned `RBR-0837` with an empty reserved tail.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the last recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The sidecar is concrete and bounded in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py` currently passes (`778 passed in 1.07s`);
  - the canonical-order import probe in Acceptance currently passes and prints the twelve ids listed above;
  - `rg -n 'DIRECT_BYTES_FOLLOW_ON_CASES' tests/python/test_quantified_alternation_parity_suite.py` shows one declaration plus the seven target parametrizations in this file; and
  - the final `rg` absence check in Acceptance currently fails exactly on this cleanup because the mirrored tuple still exists.
- This stays on the same bounded post-JSON parity-harness cleanup track as `RBR-0835`:
  - `tests/python/test_quantified_alternation_parity_suite.py` already uses `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` as the bundle-and-payload owner for bytes follow-on routing; and
  - the remaining `DIRECT_BYTES_FOLLOW_ON_CASES` tuple is just a flattened second owner for the same case ordering, so this cleanup can delete duplication without changing behavior.

## Completion
- 2026-03-21: Removed the mirrored `DIRECT_BYTES_FOLLOW_ON_CASES` tuple from `tests/python/test_quantified_alternation_parity_suite.py`.
- Added one tiny file-local `_direct_bytes_follow_on_cases()` helper derived directly from `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES`, then rewired the seven direct-bytes follow-on parity parametrizations to flatten the canonical surface owner instead of reading a duplicated top-level tuple.
- Preserved the existing direct-bytes follow-on surface membership, per-surface case payloads, and effective twelve-case flattening order exactly as `quantified-alternation-numbered-bytes`, `quantified-alternation-named-bytes`, `quantified-alternation-broader-range-numbered-bytes`, `quantified-alternation-broader-range-named-bytes`, `quantified-alternation-conditional-numbered-bytes`, `quantified-alternation-conditional-named-bytes`, `quantified-alternation-open-ended-numbered-bytes`, `quantified-alternation-open-ended-named-bytes`, `quantified-alternation-nested-branch-numbered-bytes`, `quantified-alternation-nested-branch-named-bytes`, `quantified-alternation-backtracking-heavy-numbered-bytes`, `quantified-alternation-backtracking-heavy-named-bytes`.
- Verification passed with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py` (`778 passed in 1.10s`), the task-local import-order probe from Acceptance (`ok`), and `bash -lc "! rg -n 'DIRECT_BYTES_FOLLOW_ON_CASES' tests/python/test_quantified_alternation_parity_suite.py"` (passes with no matches).
