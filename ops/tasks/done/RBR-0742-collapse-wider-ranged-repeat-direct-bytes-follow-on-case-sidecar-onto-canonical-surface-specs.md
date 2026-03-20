# RBR-0742: Collapse wider-ranged-repeat direct-bytes follow-on case sidecar onto canonical surface specs

Status: done
Owner: architecture-implementation
Created: 2026-03-20
Completed: 2026-03-20

## Goal
- Remove the detached `DIRECT_BYTES_FOLLOW_ON_CASES` tuple from `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` so `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` becomes the sole canonical owner of direct-bytes follow-on case ordering and payload routing inside the wider-ranged-repeat parity owner.

## Deliverables
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` stops defining or reading `DIRECT_BYTES_FOLLOW_ON_CASES`.
- The seven direct-bytes follow-on parity tests derive their parametrization directly from `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` instead of from the deleted top-level tuple:
  - `test_direct_bytes_follow_on_compile_metadata_matches_cpython`
  - `test_direct_bytes_follow_on_module_search_matches_cpython`
  - `test_direct_bytes_follow_on_module_search_convenience_api_matches_cpython`
  - `test_direct_bytes_follow_on_module_search_match_group_access_matches_cpython`
  - `test_direct_bytes_follow_on_pattern_fullmatch_matches_cpython`
  - `test_direct_bytes_follow_on_pattern_fullmatch_convenience_api_matches_cpython`
  - `test_direct_bytes_follow_on_pattern_fullmatch_match_group_access_matches_cpython`
- Preserve the current effective follow-on case order exactly. The canonical flattening of `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` must stay:
  - `broader-range-wider-ranged-repeat-conditional-numbered-bytes`
  - `broader-range-wider-ranged-repeat-conditional-named-bytes`
  - `broader-range-wider-ranged-repeat-backtracking-heavy-numbered-bytes`
  - `broader-range-wider-ranged-repeat-backtracking-heavy-named-bytes`
  - `nested-broader-range-wider-ranged-repeat-grouped-alternation-numbered-bytes`
  - `nested-broader-range-wider-ranged-repeat-grouped-alternation-named-bytes`
  - `nested-broader-range-wider-ranged-repeat-grouped-conditional-numbered-bytes`
  - `nested-broader-range-wider-ranged-repeat-grouped-conditional-named-bytes`
  - `nested-broader-range-wider-ranged-repeat-backtracking-heavy-numbered-bytes`
  - `nested-broader-range-wider-ranged-repeat-backtracking-heavy-named-bytes`
- Keep canonical ownership otherwise unchanged:
  - do not change `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` membership, `id` ordering, supplemental case payloads, expected operation-helper counts, expected search/fullmatch text maps, expected per-spec case ordering, or `expected_case_payloads`;
  - do not change `FIXTURE_BUNDLES`, `COMPILE_CASES`, `MODULE_CASES`, `PATTERN_CASES`, `WIDER_RANGED_REPEAT_QUANTIFIED_GROUP_SELECTED_CASE_IDS`, `_wider_ranged_repeat_quantified_group_direct_test_case_id_buckets()`, `BACKTRACKING_TRACE_CASES`, `PATTERN_BOUNDS_MATCH_CASES`, `PATTERN_BOUNDS_NO_MATCH_CASES`, or the published direct parity surface they represent; and
  - if a tiny file-local helper is useful, keep it derived from `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` instead of introducing another mirrored tuple/list/map block.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
import tests.python.test_wider_ranged_repeat_quantified_group_parity_suite as mod

assert tuple(case.id for spec in mod.DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES for case in spec.cases) == (
    "broader-range-wider-ranged-repeat-conditional-numbered-bytes",
    "broader-range-wider-ranged-repeat-conditional-named-bytes",
    "broader-range-wider-ranged-repeat-backtracking-heavy-numbered-bytes",
    "broader-range-wider-ranged-repeat-backtracking-heavy-named-bytes",
    "nested-broader-range-wider-ranged-repeat-grouped-alternation-numbered-bytes",
    "nested-broader-range-wider-ranged-repeat-grouped-alternation-named-bytes",
    "nested-broader-range-wider-ranged-repeat-grouped-conditional-numbered-bytes",
    "nested-broader-range-wider-ranged-repeat-grouped-conditional-named-bytes",
    "nested-broader-range-wider-ranged-repeat-backtracking-heavy-numbered-bytes",
    "nested-broader-range-wider-ranged-repeat-backtracking-heavy-named-bytes",
)
print("ok")
PY`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from pathlib import Path

source = Path("tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py").read_text(
    encoding="utf-8"
)
assert "DIRECT_BYTES_FOLLOW_ON_CASES" not in source
print("ok")
PY`
  - `bash -lc "! rg -n 'DIRECT_BYTES_FOLLOW_ON_CASES' tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py"`

## Constraints
- Keep this cleanup structural only. The point is to delete one more mirrored owner layer inside the wider-ranged-repeat parity suite, not to reinterpret which bytes follow-on cases stay explicit, move any family between the shared buckets and the direct follow-on path, or broaden the suite beyond the current published slice.
- Do not edit `tests/python/fixture_parity_support.py`, correctness fixtures under `tests/conformance/fixtures/`, benchmark manifests/tests, published reports, README copy, or tracked project-state prose in this run.

## Notes
- `RBR-0742` is the next available task id in the current checkout:
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
print('highest_existing_tail', existing_sorted[-20:])
print('reserved_tail', reserved_sorted[-20:])
for n in range(int(re.search(r'\\d+', existing_sorted[-1]).group()), int(re.search(r'\\d+', existing_sorted[-1]).group()) + 80):
    rid = f'RBR-{n:04d}'
    if rid not in existing and rid not in reserved:
        print('next_free', rid)
        break
PY` reported the existing tail through `RBR-0741`, no reserved missing tail ids, and `next_free RBR-0742`.
- No blocked architecture task exists to reopen first, and the current runtime state does not trigger rule 10:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added; and
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`.
- JSON burn-down is complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The sidecar is concrete and bounded in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` currently passes (`1341 passed in 0.98s`);
  - the canonical-order import probe in Acceptance already passes in the current checkout (`ok`);
  - `rg -n 'DIRECT_BYTES_FOLLOW_ON_CASES' tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` shows one declaration plus the seven target parametrizations in this file; and
  - the inline source-absence probe and final `rg` absence check in Acceptance currently fail exactly on this cleanup because the mirrored tuple still exists.
- This stays on the same bounded post-JSON parity-harness cleanup track as `RBR-0709` and `RBR-0741`: those tasks already removed the detached direct-bytes sidecars from adjacent quantified-alternation and wider-ranged owner metadata, and `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` already carries the case payloads and ordering needed to delete this remaining flattened tuple without changing behavior.

## Completion Notes
- 2026-03-20: Removed `DIRECT_BYTES_FOLLOW_ON_CASES` from `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`.
- 2026-03-20: Added a tiny file-local helper that flattens `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` for the seven direct-bytes follow-on parametrizations, preserving the existing canonical case order and payload routing.
- 2026-03-20: Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` (`1341 passed in 0.99s`), the canonical-order probe from the task (`ok`), the inline source-absence probe (`ok`), and `bash -lc "! rg -n 'DIRECT_BYTES_FOLLOW_ON_CASES' tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py"` (no matches).
