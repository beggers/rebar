# RBR-0662: Collapse the detached source-tree benchmark expectation module onto the combined owner

Status: done
Owner: architecture-implementation
Created: 2026-03-19
Completed: 2026-03-19

## Goal
- Delete `tests/benchmarks/benchmark_expectations.py` by moving its remaining source-tree benchmark expectation tables, typed records, cached manifest helpers, and scorecard/combined-case builder utilities onto `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, so the tracked source-tree benchmark publication has one owner instead of a detached expectations-only support module beside the existing combined owner.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- Delete `tests/benchmarks/benchmark_expectations.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` becomes the sole owner for the direct source-tree benchmark expectation surface currently isolated in `tests/benchmarks/benchmark_expectations.py`:
  - keep the current typed expectation records and common case wrappers file-local on the owner:
    - `SourceTreeBenchmarkCommonCase`,
      `SourceTreeManifestExpectation`,
      `SourceTreeDeferredExpectation`,
      `SourceTreeScorecardCase`,
      `SourceTreeCombinedCase`,
      `SourceTreeCombinedPatternGroupExpectation`,
      `SourceTreeCombinedManifestShapeExpectation`,
      `SourceTreeCombinedManifestExpectationDefinition`, and
      `SourceTreeCombinedSliceExpectation`
      remain defined on `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`;
    - the owner keeps the current cached source-tree manifest inventory and per-manifest workload selection helpers file-local instead of routing through another detached support layer.
  - keep the current source-tree expectation tables explicit on the owner:
    - `BASE_SOURCE_TREE_MANIFEST_IDS`,
      `ZERO_GAP_PROMOTION_MANIFEST_IDS`,
      `COUNTED_REPEAT_FULLY_MEASURED_MANIFEST_IDS`,
      `ZERO_GAP_FULLY_MEASURED_MANIFEST_CASES`,
      `ZERO_GAP_BYTES_CASES`,
      `SOURCE_TREE_SCORECARD_EXPECTATIONS`,
      `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS`, and
      `SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS`
      still drive the same manifest ids, representative workload ids, slice rows, and known-gap/measured expectations as today.
  - keep the current owner-local source-tree helper surface explicit:
    - `zero_gap_fully_measured_manifest_case(...)`,
      `relative_manifest_path(...)`,
      `run_source_tree_benchmark_scorecard(...)`,
      `source_tree_scorecard_case_ids(...)`,
      `source_tree_scorecard_case(...)`,
      `source_tree_combined_target_manifest_ids(...)`,
      `source_tree_combined_case(...)`,
      `source_tree_combined_manifest_shape_expectation(...)`,
      `source_tree_combined_manifest_representative_measured_workload_ids(...)`,
      `source_tree_combined_slice_manifest_ids(...)`,
      `source_tree_combined_slice_derived_manifest_ids(...)`,
      `source_tree_combined_slice_expectations(...)`,
      `select_source_tree_combined_slice_rows(...)`, and
      `representative_measured_workload_ids(...)`
      still preserve their current ordering, assertion behavior, and manifest/workload filtering on the owner file.
  - keep any tiny helper needed for cache assembly, workload-id filtering, or case construction file-local on `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` instead of creating another `*_support.py`, another detached expectations module, or moving this coverage onto `tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py` or `tests/report_assertions.py`.
- `tests/benchmarks/benchmark_expectations.py` is deleted outright:
  - do not leave an import-only wrapper, compatibility shell, or renamed expectations-specific module behind.
- Keep scope structural only:
  - do not change `python/rebar_harness/benchmarks.py`, benchmark workload modules, `tests/report_assertions.py`, published reports, or tracked project-state prose in this run.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from pathlib import Path

source = Path("tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py").read_text(
    encoding="utf-8"
)
for needle in (
    "class SourceTreeScorecardCase",
    "class SourceTreeCombinedCase",
    "SOURCE_TREE_SCORECARD_EXPECTATIONS =",
    "SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS =",
    "def source_tree_scorecard_case(",
    "def source_tree_combined_case(",
    "def select_source_tree_combined_slice_rows(",
    "def run_source_tree_benchmark_scorecard(",
):
    assert needle in source, needle
assert "from tests.benchmarks.benchmark_expectations import" not in source
print("ok")
PY`
  - `bash -lc "! rg --files tests/benchmarks | rg 'benchmark_expectations\\.py$'"`

## Constraints
- Keep this cleanup structural only. Do not reinterpret source-tree benchmark expectations, change representative-workload promotion, or alter scorecard generation behavior.
- Prefer the existing combined source-tree benchmark owner and file-local helpers over another detached expectation layer or another shared support module.
- Do not move this expectation surface into `tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py`; that owner should stay focused on direct `rebar_harness.benchmarks` contract coverage rather than tracked source-tree publication expectations.

## Notes
- `RBR-0662` is the next available architecture task id in the current checkout:
  - `rg -n "RBR-066[0-9]|RBR-067[0-9]" ops/state/backlog.md ops/state/current_status.md` currently returns only the active feature frontier `RBR-0661`; and
  - `find ops/tasks -maxdepth 2 -type f \( -name 'RBR-0661*' -o -name 'RBR-0662*' -o -name 'RBR-0663*' -o -name 'RBR-0664*' -o -name 'RBR-0665*' -o -name 'RBR-0666*' -o -name 'RBR-0667*' \) | sort` currently returns only `ops/tasks/ready/RBR-0661-nested-broader-range-wider-ranged-repeat-branch-local-backreference-callable-replacement-bytes-pack.md`.
- No blocked architecture task exists to reopen first, and rule 10 does not currently block another architecture cleanup:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the only ready task is the feature-owned `RBR-0661`, with recent architecture and feature task runs completing cleanly.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The detached source-tree benchmark expectation layer is concrete and bounded in the current checkout:
  - `rg -n "from tests\\.benchmarks\\.benchmark_expectations import|import tests\\.benchmarks\\.benchmark_expectations" tests -g '*.py'` currently matches only `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`;
  - `wc -l tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/benchmark_expectations.py` reports `1597` lines for the current owner and `2496` lines for the detached expectation module;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently passes (`41 passed, 1164 subtests passed in 23.98s`);
  - the inline source probe in Acceptance currently fails exactly on this cleanup with `AssertionError: class SourceTreeScorecardCase` because `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` does not yet carry the absorbed expectation definitions; and
  - `bash -lc "! rg --files tests/benchmarks | rg 'benchmark_expectations\\.py$'"` currently fails exactly on this cleanup because the detached module still exists.
- The ownership simplification matches the current benchmark harness shape:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` already owns the tracked source-tree scorecard and combined-manifest assertions that consume this expectation surface; and
  - moving the file-local case tables, manifest-shape definitions, representative-workload helpers, and scorecard runner glue there removes one more detached source-tree benchmark layer without changing the public benchmark harness or report plumbing.

## Completion Note
- 2026-03-19: Moved the detached source-tree benchmark expectation records, manifest inventory, cached manifest/workload selectors, scorecard runner, combined-manifest helpers, and slice-selection helpers directly into `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, keeping the tracked source-tree benchmark publication surface owned by that one file.
- 2026-03-19: Deleted `tests/benchmarks/benchmark_expectations.py` outright after the combined owner absorbed `SourceTreeBenchmarkCommonCase`, `SourceTreeManifestExpectation`, `SourceTreeDeferredExpectation`, `SourceTreeScorecardCase`, `SourceTreeCombinedCase`, `SourceTreeCombinedPatternGroupExpectation`, `SourceTreeCombinedManifestShapeExpectation`, `SourceTreeCombinedManifestExpectationDefinition`, `SourceTreeCombinedSliceExpectation`, the source-tree expectation tables, and the file-local helper surface.
- 2026-03-19: Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` (`41 passed, 1164 subtests passed in 24.02s`), the acceptance inline source probe (`ok`), `bash -lc "! rg --files tests/benchmarks | rg 'benchmark_expectations\\.py$'"` (passes), and `git diff --name-status -- tests/benchmarks/benchmark_expectations.py` (`D`).
