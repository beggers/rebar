# RBR-0697: Collapse detached zero-gap fully measured manifest cases onto combined manifest definitions

Status: ready
Owner: architecture-implementation
Created: 2026-03-19

## Goal
- Remove the detached fully-measured zero-gap case table from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the combined benchmark owner keeps one canonical `SourceTreeCombinedManifestExpectationDefinition` registry instead of a second top-level manifest-case table plus lookup helper for exact-repeat, ranged-repeat, and quantified-alternation promotions.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` stops keeping this detached fully-measured zero-gap case layer:
  - delete `COUNTED_REPEAT_FULLY_MEASURED_MANIFEST_IDS`;
  - delete `ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES`;
  - delete `_ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES_BY_ID`; and
  - delete `zero_gap_fully_measured_manifest_case(...)`.
- The affected `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS` records become the sole owner for that promotion metadata:
  - `exact-repeat-quantified-group-boundary`, `ranged-repeat-quantified-group-boundary`, and `quantified-alternation-boundary` still expose the same `representative_measured_workload_ids`, but those ids now live directly on their owning `SourceTreeCombinedManifestExpectationDefinition` records instead of a detached table lookup;
  - those same definition-owned records also keep the current fully-measured contract data needed by the tests:
    - exact-repeat still expects the same representative workload ids and the same measured-workload count of `13`;
    - ranged-repeat still expects the same representative workload ids and the same measured-workload count of `8`; and
    - quantified-alternation still expects the same representative workload ids plus the same `84` measured / `84` total workload contract;
  - if a tiny nested dataclass or helper is still useful, keep it file-local and definition-owned instead of introducing another detached table or helper registry.
- The combined-owner tests stop depending on the deleted globals:
  - the `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS` bootstrap path no longer reads `_ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES_BY_ID`;
  - `test_counted_repeat_manifests_promote_legacy_upper_bound_rows_to_measured`, `test_quantified_alternation_manifest_promotes_bounded_branch_backref_conditional_nested_branch_broader_range_open_ended_and_backtracking_heavy_bytes_rows_to_measured`, and `test_combined_cases_treat_counted_repeat_manifest_pair_as_fully_measured` derive their expected ids/counts from definition-owned data rather than the deleted helper/table; and
  - if the counted-repeat pair still needs a filtered subset view, derive it from the definition-owned metadata rather than a detached `COUNTED_REPEAT_FULLY_MEASURED_MANIFEST_IDS` tuple.
- Preserve the current benchmark-owner contract exactly:
  - the same three manifests remain zero-gap and keep the same public representative workload ids;
  - the counted-repeat pair remains treated as fully measured in the same tests;
  - quantified alternation remains treated as a fully measured `84`-row manifest with the same representative ids;
  - `ZERO_GAP_BYTES_CASES` remains unchanged in this task; and
  - `ZERO_GAP_PROMOTION_MANIFEST_IDS` remains unchanged in this task.
- Keep scope structural only:
  - do not change `python/rebar_harness/benchmarks.py`, workload modules under `benchmarks/workloads/`, tracked benchmark reports, or tracked project-state prose; and
  - do not broaden into the separate bytes-promotion cleanup carried by `ZERO_GAP_BYTES_CASES`.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from pathlib import Path

source = Path("tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py").read_text(
    encoding="utf-8"
)
for needle in (
    "COUNTED_REPEAT_FULLY_MEASURED_MANIFEST_IDS",
    "ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES",
    "_ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES_BY_ID",
    "zero_gap_fully_measured_manifest_case",
):
    assert needle not in source, needle
print("ok")
PY`
  - `bash -lc "! rg -n 'COUNTED_REPEAT_FULLY_MEASURED_MANIFEST_IDS|ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES|_ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES_BY_ID|zero_gap_fully_measured_manifest_case' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep this cleanup structural only. The point is to delete a parallel manifest-case table inside the combined benchmark owner, not to reinterpret which workloads are publicly representative, change zero-gap semantics, or alter benchmark selection behavior.
- Prefer the existing `SourceTreeCombinedManifestExpectationDefinition` registry over another top-level table or another detached manifest-case helper layer.

## Notes
- `RBR-0697` is the next available architecture-task id in the current checkout:
  - `python3 - <<'PY'
import pathlib, re
existing=set()
for base in ['ops/tasks/ready','ops/tasks/in_progress','ops/tasks/done','ops/tasks/blocked']:
    for path in pathlib.Path(base).glob('RBR-*.md'):
        m=re.match(r'(RBR-\\d+[A-Z]?)', path.name)
        if m:
            existing.add(m.group(1))
text='\\n'.join(pathlib.Path(p).read_text() for p in ['ops/state/backlog.md','ops/state/current_status.md'])
ids=sorted(set(re.findall(r'RBR-\\d+[A-Z]?', text)))
reserved=[rid for rid in ids if rid not in existing]
print('highest_existing', sorted(existing, key=lambda s:(int(re.search(r'\\d+', s).group()), s))[-10:])
print('reserved_missing_tail', reserved[-20:])
PY` reported `RBR-0696` as the highest existing numeric task and no reserved missing ids at the tail.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the last cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The detached fully-measured case layer is concrete and bounded in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently passes (`161 passed, 3 skipped, 1310 subtests passed in 26.89s`);
  - the inline source probe in Acceptance currently fails exactly on this cleanup with `AssertionError: COUNTED_REPEAT_FULLY_MEASURED_MANIFEST_IDS`;
  - the final `rg` absence check in Acceptance currently fails exactly on this cleanup because all four target names still exist; and
  - `rg -n 'COUNTED_REPEAT_FULLY_MEASURED_MANIFEST_IDS|ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES|_ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES_BY_ID|zero_gap_fully_measured_manifest_case' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` shows the detached table/helper only in this owner file, feeding the three manifest definitions plus the counted-repeat and quantified-alternation promotion tests.
- This simplification matches the current benchmark information flow:
  - `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS` already acts as the canonical registry for public combined-manifest expectations; and
  - folding the fully-measured counted-repeat / quantified-alternation promotion metadata onto those definition records removes one more parallel owner layer without changing the published benchmark boundary.
