# RBR-0705: Collapse source-tree manifest-role sidecars onto combined manifest definitions

Status: done
Owner: architecture-implementation
Created: 2026-03-19

## Goal
- Remove the detached `BASE_SOURCE_TREE_MANIFEST_IDS` and `ZERO_GAP_PROMOTION_MANIFEST_IDS` tables from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the combined benchmark owner keeps one canonical `SourceTreeCombinedManifestExpectationDefinition` registry instead of separate manifest-role sidecars.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` stops keeping these detached manifest-role registries:
  - delete `BASE_SOURCE_TREE_MANIFEST_IDS`;
  - delete `ZERO_GAP_PROMOTION_MANIFEST_IDS`; and
  - do not replace them with another top-level tuple/set block or another detached lookup helper elsewhere in the file.
- The affected `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS` records become the sole owner for that role metadata:
  - `source_tree_combined_target_manifest_ids()` derives base-manifest exclusion from definition-owned metadata instead of `BASE_SOURCE_TREE_MANIFEST_IDS`;
  - `test_zero_gap_manifest_representative_promotions_keep_selected_rows_measured` derives its manifest ids from definition-owned metadata instead of `ZERO_GAP_PROMOTION_MANIFEST_IDS`; and
  - if a tiny file-local helper or added bool field is useful, keep it definition-owned instead of introducing another detached registry layer.
- Preserve the current benchmark-owner contract exactly:
  - `compile-matrix` and `regression-matrix` remain the only manifests excluded from `source_tree_combined_target_manifest_ids()`;
  - `source_tree_combined_target_manifest_ids()` keeps the same published manifest order as today after those two base manifests are excluded;
  - the zero-gap promotion manifest set remains exactly `grouped-named-boundary`, `numbered-backreference-boundary`, `nested-group-boundary`, and `optional-group-boundary` in that order; and
  - do not change `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS` representative workload ids, known-gap expectations, fully measured expectations, zero-gap bytes representative subsets, or slice expectations except as needed to attach the deleted role metadata to the owning records.
- Keep scope structural only:
  - do not change `python/rebar_harness/benchmarks.py`, workload modules under `benchmarks/workloads/`, tracked benchmark reports, or tracked project-state prose; and
  - do not broaden into removing `OPTIONAL_GROUP_CONDITIONAL_WORKLOAD_ID` or `OPEN_ENDED_DIRECT_PARITY_BYTES_CASES` in this task.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from pathlib import Path

source = Path("tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py").read_text(
    encoding="utf-8"
)
for needle in ("BASE_SOURCE_TREE_MANIFEST_IDS", "ZERO_GAP_PROMOTION_MANIFEST_IDS"):
    assert needle not in source, needle
print("ok")
PY`
  - `bash -lc "! rg -n 'BASE_SOURCE_TREE_MANIFEST_IDS|ZERO_GAP_PROMOTION_MANIFEST_IDS' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep this cleanup structural only. The point is to delete one more parallel manifest-role owner layer inside the combined benchmark owner, not to reinterpret representative promotion, change which manifests are publicly measured, or alter source-tree benchmark selection semantics.
- Prefer the existing `SourceTreeCombinedManifestExpectationDefinition` registry over another top-level manifest-id table or another detached support helper.

## Notes
- `RBR-0705` is the correct frontier id for this queue even though an old historical numeric hole still exists:
  - the live task tail is `RBR-0704`;
  - `rg -n "RBR-0705" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked` returned no matches; and
  - `ops/state/backlog.md` and `ops/state/current_status.md` do not reserve any missing tail ids beyond `RBR-0704`.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the last recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The detached manifest-role layer is concrete and bounded in the current checkout:
  - `ops/tasks/done/RBR-0697-collapse-detached-zero-gap-fully-measured-manifest-cases-onto-combined-manifest-definitions.md` and `ops/tasks/done/RBR-0701-collapse-derived-standard-benchmark-param-registries.md` both explicitly left `BASE_SOURCE_TREE_MANIFEST_IDS` and/or `ZERO_GAP_PROMOTION_MANIFEST_IDS` for later cleanup;
  - `rg -n 'BASE_SOURCE_TREE_MANIFEST_IDS|ZERO_GAP_PROMOTION_MANIFEST_IDS' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` shows the two registries are declared once and consumed only by `source_tree_combined_target_manifest_ids()` and the zero-gap promotion test in the same owner file;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently passes (`167 passed, 3 skipped, 1334 subtests passed in 26.49s`);
  - the inline source probe in Acceptance currently fails exactly on this cleanup with `AssertionError: BASE_SOURCE_TREE_MANIFEST_IDS`; and
  - the final `rg` absence check in Acceptance currently fails exactly on this cleanup because both target names still exist.
- This simplification matches the current benchmark information flow:
  - `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS` already acts as the canonical registry for combined-manifest known-gap, fully measured, shape, and zero-gap bytes metadata; and
  - folding the remaining base-manifest and zero-gap-promotion role flags onto those definition records removes one more parallel owner layer without changing the published benchmark boundary.

## Completion
- Folded the remaining base-manifest exclusion and zero-gap promotion role metadata onto `SourceTreeCombinedManifestExpectationDefinition` via definition-owned boolean flags in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Updated `source_tree_combined_target_manifest_ids()` and the zero-gap promotion test to derive manifest ids from those owning records instead of detached sidecar tables, while keeping the same excluded-manifest and promotion-manifest order contracts.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, the inline source probe, and the `rg` absence check from this task.
