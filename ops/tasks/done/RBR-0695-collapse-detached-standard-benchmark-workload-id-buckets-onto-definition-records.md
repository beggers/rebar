# RBR-0695: Collapse detached standard benchmark workload-id buckets onto definition records

Status: done
Owner: architecture-implementation
Created: 2026-03-19

## Goal
- Remove the remaining detached workload-id bucket layer from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the combined benchmark owner keeps one self-contained `StandardBenchmarkAnchorContractDefinition` registry instead of a second top-level block for excluded, legacy, and special-unanchored workload ids.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` stops keeping these workload-id buckets in a detached top-level constant block:
  - delete `EXPECTED_NESTED_GROUP_EXCLUDED_WORKLOAD_IDS`;
  - delete `EXPECTED_GROUPED_ALTERNATION_LEGACY_WRAPPER_WORKLOAD_IDS`;
  - delete `EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_LEGACY_NESTED_WORKLOAD_IDS`;
  - delete `EXPECTED_NESTED_GROUP_REPLACEMENT_SPECIAL_UNANCHORED_WORKLOAD_IDS`; and
  - delete `EXPECTED_OPEN_ENDED_SPECIAL_UNANCHORED_WORKLOAD_IDS`.
- The affected `StandardBenchmarkAnchorContractDefinition` records become the sole owner for those workload-id buckets:
  - the nested-group definition still carries the same two excluded workload ids, but that data now lives on the definition record instead of a detached constant;
  - the grouped-alternation definition still carries the same legacy-wrapper subset and callback-anchor subset, but both are derived from definition-owned data rather than a parallel top-level set;
  - the grouped-alternation-replacement definition still carries the same two legacy nested workload ids from definition-owned data rather than a detached constant; and
  - the nested-group-replacement and open-ended grouped-alternation definitions still carry the same special-unanchored workload ids on their definition records instead of a detached top-level tuple.
- The include/filter path stops depending on the deleted globals:
  - `_is_measured_nested_group_workload(...)`, `_is_non_special_open_ended_workload(...)`, and `_is_non_special_nested_group_replacement_workload(...)` either disappear or stop reading top-level workload-id buckets; and
  - if a tiny helper is still needed, keep it file-local and definition-owned instead of introducing another parallel registry, helper module, or support abstraction.
- Preserve the current benchmark-owner contract surface exactly:
  - the same workloads stay intentionally excluded from the nested-group measured slice;
  - the same grouped-alternation and grouped-alternation-replacement legacy workload ids stay pinned to the same anchored correctness cases;
  - the same nested-group-replacement and open-ended special-unanchored workload ids stay explicit and continue to drive the same direct-parity and special-result coverage; and
  - `STANDARD_BENCHMARK_LEGACY_DEFINITIONS`, `STANDARD_BENCHMARK_CALLBACK_PARITY_DEFINITIONS`, `STANDARD_BENCHMARK_SPECIAL_UNANCHORED_DEFINITIONS`, and `STANDARD_BENCHMARK_SPECIAL_UNANCHORED_RESULT_PARITY_CASES` keep the same effective membership and semantics.
- Keep scope structural only:
  - do not change `python/rebar_harness/benchmarks.py`, workload modules under `benchmarks/workloads/`, tracked benchmark reports, or tracked project-state prose; and
  - do not broaden into removing `OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID`, `OPEN_ENDED_DIRECT_PARITY_BYTES_CASES`, or the manifest-path constants that still have direct non-definition consumers elsewhere in the owner file.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from pathlib import Path

source = Path("tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py").read_text(
    encoding="utf-8"
)
for needle in (
    "EXPECTED_NESTED_GROUP_EXCLUDED_WORKLOAD_IDS",
    "EXPECTED_GROUPED_ALTERNATION_LEGACY_WRAPPER_WORKLOAD_IDS",
    "EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_LEGACY_NESTED_WORKLOAD_IDS",
    "EXPECTED_NESTED_GROUP_REPLACEMENT_SPECIAL_UNANCHORED_WORKLOAD_IDS",
    "EXPECTED_OPEN_ENDED_SPECIAL_UNANCHORED_WORKLOAD_IDS",
):
    assert needle not in source, needle
print("ok")
PY`
  - `bash -lc "! rg -n 'EXPECTED_NESTED_GROUP_EXCLUDED_WORKLOAD_IDS|EXPECTED_GROUPED_ALTERNATION_LEGACY_WRAPPER_WORKLOAD_IDS|EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_LEGACY_NESTED_WORKLOAD_IDS|EXPECTED_NESTED_GROUP_REPLACEMENT_SPECIAL_UNANCHORED_WORKLOAD_IDS|EXPECTED_OPEN_ENDED_SPECIAL_UNANCHORED_WORKLOAD_IDS' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep this cleanup structural only. The point is to delete a second workload-id metadata layer inside the combined benchmark owner, not to reinterpret benchmark behavior, change which rows are intentionally unanchored, or alter what the suite measures.
- Prefer the existing `StandardBenchmarkAnchorContractDefinition` registry over another top-level table or another detached helper layer.

## Notes
- `RBR-0695` is the next available architecture-task id in the current checkout:
  - `python3 - <<'PY'
import pathlib, re
existing=set()
for base in ['ops/tasks/ready','ops/tasks/in_progress','ops/tasks/done','ops/tasks/blocked']:
    for path in pathlib.Path(base).glob('RBR-*.md'):
        m=re.match(r'(RBR-\\d+)', path.name)
        if m:
            existing.add(m.group(1))
text='\\n'.join(pathlib.Path(p).read_text() for p in ['ops/state/backlog.md','ops/state/current_status.md'])
ids=sorted(set(re.findall(r'RBR-\\d+[A-Z]?', text)))
reserved=[rid for rid in ids if rid not in existing]
print('reserved_missing_tail:', reserved[-30:])
print('highest_existing:', sorted(existing)[-10:])
PY` showed only `RBR-0037A` and `RBR-0042A` as reserved/missing ids and `RBR-0694` as the highest numeric task already filed.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in the live checkout before this task was added;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the last recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The detached workload-id bucket layer is concrete and bounded in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently passes (`159 passed, 3 skipped, 1284 subtests passed in 25.84s`);
  - the inline source probe in Acceptance currently fails exactly on this cleanup with `AssertionError: EXPECTED_NESTED_GROUP_EXCLUDED_WORKLOAD_IDS`;
  - the final `rg` absence check in Acceptance currently fails exactly on this cleanup because all five target constants still exist; and
  - `rg -n 'EXPECTED_NESTED_GROUP_EXCLUDED_WORKLOAD_IDS|EXPECTED_GROUPED_ALTERNATION_LEGACY_WRAPPER_WORKLOAD_IDS|EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_LEGACY_NESTED_WORKLOAD_IDS|EXPECTED_NESTED_GROUP_REPLACEMENT_SPECIAL_UNANCHORED_WORKLOAD_IDS|EXPECTED_OPEN_ENDED_SPECIAL_UNANCHORED_WORKLOAD_IDS' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` shows those constants are declared once and consumed only by the standard-definition setup plus the definition-specific include/filter helpers.
- This simplification matches the current benchmark information flow:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` already treats `STANDARD_BENCHMARK_DEFINITIONS` as the canonical registry for standard anchored benchmark slices; and
  - moving the remaining excluded/legacy/special-unanchored workload-id buckets onto those definition records removes one more internal parallel layer without changing the combined benchmark owner boundary.

## Completion Notes
- 2026-03-19: Moved the detached nested-group exclusion, grouped-alternation legacy subsets, grouped-alternation-replacement legacy subset, and nested-group-replacement/open-ended special-unanchored workload ids onto the affected `StandardBenchmarkAnchorContractDefinition` records.
- Added definition-owned `includes_workload(...)` filtering so the standard benchmark include path now reads exclusion and special-unanchored ids from each definition instead of deleted file-global bucket helpers.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, the inline source probe, and the final `rg` absence check from Acceptance.
