# RBR-0693: Collapse the detached standard benchmark anchor case ids onto definition records

Status: ready
Owner: architecture-implementation
Created: 2026-03-19

## Goal
- Remove the detached `EXPECTED_*_ANCHOR_CASE_IDS` layer from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by folding each standard benchmark anchor map onto its owning `StandardBenchmarkAnchorContractDefinition`, so the combined benchmark owner keeps one self-contained definition registry instead of a second parallel case-id block more than a thousand lines away.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` stops keeping the standard benchmark anchor expectations in a detached top-level case-id registry:
  - delete `EXPECTED_COMPILE_ANCHOR_CASE_IDS`;
  - delete `EXPECTED_OPTIONAL_GROUP_CONDITIONAL_ANCHOR_CASE_IDS`;
  - delete `EXPECTED_NESTED_GROUP_ANCHOR_CASE_IDS`;
  - delete `EXACT_REPEAT_EXPECTED_ANCHOR_CASE_IDS`;
  - delete `RANGED_REPEAT_EXPECTED_ANCHOR_CASE_IDS`;
  - delete `EXPECTED_GROUPED_ALTERNATION_ANCHOR_CASE_IDS`;
  - delete `EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_ANCHOR_CASE_IDS`;
  - delete `EXPECTED_NESTED_GROUP_REPLACEMENT_ANCHOR_CASE_IDS`; and
  - delete `EXPECTED_OPEN_ENDED_ANCHOR_CASE_IDS`.
- The `STANDARD_BENCHMARK_DEFINITIONS` registry becomes the sole owner for those anchor expectations:
  - each `StandardBenchmarkAnchorContractDefinition` carries its own `expected_anchor_case_ids` data directly, or derives it from data stored directly on that same definition record, instead of pointing at one of the deleted top-level tables;
  - if grouped-alternation or grouped-alternation-replacement callback parity still needs a smaller subset than the full anchor map, derive that subset from definition-owned data rather than keeping a second detached anchor-case table;
  - keep `_anchored_case_ids(...)`, `_expected_anchored_pairs(...)`, `_expected_callback_anchor_case_ids(...)`, and the existing benchmark-owner tests behaving exactly as they do today; and
  - do not introduce another parallel `*_ANCHOR_CASE_IDS` registry elsewhere in the file.
- Preserve the current contract surface exactly:
  - the same manifests stay attached to the same standard definitions;
  - the same anchored workload ids stay pinned to the same published correctness case ids;
  - the grouped-alternation legacy wrapper subset, nested-group excluded workloads, nested-group-replacement special unanchored workloads, open-ended special unanchored workloads, and open-ended direct-bytes supplemental cases keep the same semantics and expectation coverage; and
  - the standard benchmark callback-result parity, special-unanchored result parity, and manifest/workload selection assertions keep passing without changing their expected ids.
- Keep scope structural only:
  - do not change `python/rebar_harness/benchmarks.py`, benchmark workload modules under `benchmarks/workloads/`, tracked reports, or tracked project-state prose;
  - do not broaden into deleting `COMPILE_MATRIX_MANIFEST_PATH`, `REGRESSION_MATRIX_MANIFEST_PATH`, or the other manifest-path constants that still have direct non-definition consumers elsewhere in the owner file; and
  - keep any tiny helper needed for definition-owned callback-subset derivation file-local on `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` instead of introducing another support module.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from pathlib import Path

source = Path("tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py").read_text(
    encoding="utf-8"
)
for needle in (
    "EXPECTED_COMPILE_ANCHOR_CASE_IDS",
    "EXPECTED_OPTIONAL_GROUP_CONDITIONAL_ANCHOR_CASE_IDS",
    "EXPECTED_NESTED_GROUP_ANCHOR_CASE_IDS",
    "EXACT_REPEAT_EXPECTED_ANCHOR_CASE_IDS",
    "RANGED_REPEAT_EXPECTED_ANCHOR_CASE_IDS",
    "EXPECTED_GROUPED_ALTERNATION_ANCHOR_CASE_IDS",
    "EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_ANCHOR_CASE_IDS",
    "EXPECTED_NESTED_GROUP_REPLACEMENT_ANCHOR_CASE_IDS",
    "EXPECTED_OPEN_ENDED_ANCHOR_CASE_IDS",
):
    assert needle not in source, needle
print("ok")
PY`
  - `bash -lc "! rg -n 'EXPECTED_COMPILE_ANCHOR_CASE_IDS|EXPECTED_OPTIONAL_GROUP_CONDITIONAL_ANCHOR_CASE_IDS|EXPECTED_NESTED_GROUP_ANCHOR_CASE_IDS|EXACT_REPEAT_EXPECTED_ANCHOR_CASE_IDS|RANGED_REPEAT_EXPECTED_ANCHOR_CASE_IDS|EXPECTED_GROUPED_ALTERNATION_ANCHOR_CASE_IDS|EXPECTED_GROUPED_ALTERNATION_REPLACEMENT_ANCHOR_CASE_IDS|EXPECTED_NESTED_GROUP_REPLACEMENT_ANCHOR_CASE_IDS|EXPECTED_OPEN_ENDED_ANCHOR_CASE_IDS' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep this cleanup structural only. The point is to delete a parallel expectation layer inside the combined benchmark owner, not to reinterpret benchmark behavior, change anchor matching, or alter which workloads are measured versus intentionally unanchored.
- Prefer the existing `StandardBenchmarkAnchorContractDefinition` registry over another top-level case-id table or another detached helper layer.

## Notes
- `RBR-0693` is the next available architecture-task id in the current checkout:
  - `rg -n 'RBR-0693|RBR-0694|RBR-0695|RBR-0696|RBR-0697|RBR-0698|RBR-0699|RBR-0700' ops/state/backlog.md ops/state/current_status.md` returned no reserved future ids in that range; and
  - `find ops/tasks -maxdepth 2 -type f | rg 'RBR-0693|RBR-0694|RBR-0695|RBR-0696|RBR-0697|RBR-0698|RBR-0699|RBR-0700' | sort` returned no task file before this one was added.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in the live checkout before this task was added;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the last cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The detached anchor-case layer is concrete and bounded in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently passes (`159 passed, 3 skipped, 1284 subtests passed in 26.05s`);
  - the inline source probe in Acceptance currently fails exactly on this cleanup with `AssertionError: EXPECTED_COMPILE_ANCHOR_CASE_IDS`;
  - the final `rg` absence check in Acceptance currently fails exactly on this cleanup because all nine target constants still exist; and
  - `rg -n '\\bEXPECTED_COMPILE_ANCHOR_CASE_IDS\\b|\\bEXPECTED_OPTIONAL_GROUP_CONDITIONAL_ANCHOR_CASE_IDS\\b|\\bEXPECTED_NESTED_GROUP_ANCHOR_CASE_IDS\\b|\\bEXACT_REPEAT_EXPECTED_ANCHOR_CASE_IDS\\b|\\bRANGED_REPEAT_EXPECTED_ANCHOR_CASE_IDS\\b|\\bEXPECTED_GROUPED_ALTERNATION_ANCHOR_CASE_IDS\\b|\\bEXPECTED_GROUPED_ALTERNATION_REPLACEMENT_ANCHOR_CASE_IDS\\b|\\bEXPECTED_NESTED_GROUP_REPLACEMENT_ANCHOR_CASE_IDS\\b|\\bEXPECTED_OPEN_ENDED_ANCHOR_CASE_IDS\\b' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` shows those tables are declared once and consumed only by the standard-definition setup plus the grouped-alternation callback subset.
- This simplification matches the current benchmark information flow:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` already treats `STANDARD_BENCHMARK_DEFINITIONS` as the canonical registry for standard anchored benchmark slices; and
  - keeping the per-definition anchor ids on those definition records removes one more internal parallel layer without changing the combined benchmark owner boundary.
