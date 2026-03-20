# RBR-0741: Collapse quantified-alternation direct-bytes follow-on case sidecar onto canonical surface specs

Status: ready
Owner: architecture-implementation
Created: 2026-03-20

## Goal
- Remove the detached `DIRECT_BYTES_FOLLOW_ON_CASES` tuple from `tests/python/test_quantified_alternation_parity_suite.py` so `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` becomes the sole canonical owner of direct-bytes follow-on case ordering and payload routing inside the quantified-alternation parity owner.

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
  - do not change `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` membership, `id` ordering, supplemental case payloads, expected operation-helper counts, expected search/fullmatch text maps, or the current per-spec case ordering;
  - do not change `FIXTURE_BUNDLES`, `COMPILE_CASES`, `MODULE_CASES`, `PATTERN_CASES`, `QUANTIFIED_ALTERNATION_SELECTED_CASE_IDS`, `_quantified_alternation_direct_test_case_id_buckets()`, `SUPPLEMENTAL_NO_MATCH_CASES`, `BACKTRACKING_TRACE_CASES`, `PATTERN_BOUNDS_MATCH_CASES`, `PATTERN_BOUNDS_NO_MATCH_CASES`, or the published direct parity surface they represent; and
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
- `RBR-0741` is the next available task id in the current checkout:
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
for n in range(int(re.search(r'\\d+', existing_sorted[-1]).group()), int(re.search(r'\\d+', existing_sorted[-1]).group()) + 80):
    rid = f'RBR-{n:04d}'
    if rid not in existing and rid not in reserved:
        print('next_free', rid)
        break
PY` reported the existing tail through `RBR-0740`, no reserved missing tail ids, and `next_free RBR-0741`.
- No blocked architecture task exists to reopen first, and the current runtime state does not trigger rule 10:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added; and
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`.
- JSON burn-down is complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The sidecar is concrete and bounded in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py` currently passes (`778 passed in 1.06s`);
  - the canonical-order import probe in Acceptance already passes in the current checkout (`ok`);
  - `rg -n 'DIRECT_BYTES_FOLLOW_ON_CASES' tests/python/test_quantified_alternation_parity_suite.py` shows one declaration plus the seven target parametrizations in this file; and
  - the final `rg` absence check in Acceptance currently fails exactly on this cleanup because the mirrored tuple still exists.
- This stays on the same bounded post-JSON parity-harness cleanup track as `RBR-0703`, `RBR-0711`, `RBR-0721`, and `RBR-0739`: those tasks already removed adjacent direct-bytes and direct-test sidecars from this owner path or its sibling suites, and `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` already carries the case payloads and ordering needed to delete this remaining flattened tuple without changing behavior.
