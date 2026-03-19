# RBR-0699: Collapse detached zero-gap bytes representative subsets onto combined manifest definitions

Status: done
Owner: architecture-implementation
Created: 2026-03-19

## Goal
- Remove the detached `ZERO_GAP_BYTES_CASES` table from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the combined benchmark owner keeps one canonical `SourceTreeCombinedManifestExpectationDefinition` registry instead of a second top-level bytes-subset inventory for its zero-gap manifest promotions.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` stops keeping this detached bytes-promotion table:
  - delete `ZERO_GAP_BYTES_CASES`; and
  - do not replace it with another top-level bytes-only table or another detached lookup helper elsewhere in the file.
- The affected `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS` records become the sole owner for the current zero-gap bytes subset metadata:
  - `wider-ranged-repeat-quantified-group-boundary`, `open-ended-quantified-group-boundary`, and `branch-local-backreference-boundary` still expose the same bytes representative workload subsets that are currently stored in `ZERO_GAP_BYTES_CASES`, but those subsets now live directly on definition-owned metadata instead of a detached table;
  - preserve the current eleven subset groupings exactly:
    - the six wider-ranged-repeat bytes subsets remain explicit on the wider-ranged-repeat manifest definition;
    - the four open-ended bytes subsets remain explicit on the open-ended manifest definition; and
    - the single branch-local-backreference bytes subset remains explicit on that manifest definition;
  - if a tiny nested dataclass or helper is still useful, keep it file-local and definition-owned instead of introducing another detached registry layer.
- The combined-owner tests stop depending on the deleted global:
  - `test_zero_gap_bytes_manifest_promotions_keep_selected_rows_publicly_measured` and `test_zero_gap_source_tree_manifests_keep_selected_bytes_representatives_publicly_measured` derive their expected subset ids from definition-owned metadata rather than unpacking `ZERO_GAP_BYTES_CASES`;
  - `_assert_zero_gap_bytes_representative_subset(...)` no longer requires detached `100` / `72` / `30` table literals, and instead derives any needed measured or total counts from the existing zero-gap manifest case/expectation path; and
  - the file no longer has any remaining live reference to `ZERO_GAP_BYTES_CASES`.
- Preserve the current benchmark-owner contract exactly:
  - the same eleven bytes representative subsets remain publicly measured on the same three zero-gap manifests;
  - `wider-ranged-repeat-quantified-group-boundary` still behaves as a zero-gap `100`-row manifest for those checks;
  - `open-ended-quantified-group-boundary` still behaves as a zero-gap `72`-row manifest for those checks;
  - `branch-local-backreference-boundary` still behaves as a zero-gap `30`-row manifest for those checks;
  - `ZERO_GAP_PROMOTION_MANIFEST_IDS` remains unchanged in this task; and
  - do not reinterpret which workloads are representative, which rows are measured, or how the combined benchmark suite selects manifests.
- Keep scope structural only:
  - do not change `python/rebar_harness/benchmarks.py`, workload modules under `benchmarks/workloads/`, tracked benchmark reports, or tracked project-state prose; and
  - do not broaden into the separate non-bytes zero-gap promotion cleanup still carried by `ZERO_GAP_PROMOTION_MANIFEST_IDS`.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from pathlib import Path

source = Path("tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py").read_text(
    encoding="utf-8"
)
assert "ZERO_GAP_BYTES_CASES" not in source, "ZERO_GAP_BYTES_CASES"
print("ok")
PY`
  - `bash -lc "! rg -n 'ZERO_GAP_BYTES_CASES' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep this cleanup structural only. The point is to delete one remaining detached bytes-promotion inventory inside the combined benchmark owner, not to redesign zero-gap benchmark semantics or widen benchmark coverage.
- Prefer the existing `SourceTreeCombinedManifestExpectationDefinition` registry and file-local helpers over another top-level table or another shared support layer.

## Notes
- `RBR-0699` is the next available architecture-task id in the current checkout:
  - `find ops/tasks -maxdepth 2 -type f | rg 'RBR-0699|RBR-0700|RBR-0701'` returned no matches; and
  - `rg -n 'RBR-0699|RBR-0700|RBR-0701' ops/state/backlog.md ops/state/current_status.md` returned no matches.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the last cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- `RBR-0697` explicitly left this exact follow-on behind:
  - `ops/tasks/done/RBR-0697-collapse-detached-zero-gap-fully-measured-manifest-cases-onto-combined-manifest-definitions.md` says `ZERO_GAP_BYTES_CASES` remained unchanged in that task and should be handled by a separate bytes-promotion cleanup.
- The detached bytes-promotion layer is concrete and bounded in the current checkout:
  - `ZERO_GAP_BYTES_CASES` currently holds eleven subset entries across `wider-ranged-repeat-quantified-group-boundary`, `open-ended-quantified-group-boundary`, and `branch-local-backreference-boundary`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently passes (`163 passed, 3 skipped, 1310 subtests passed in 26.16s`);
  - the inline source probe in Acceptance currently fails exactly on this cleanup with `AssertionError: ZERO_GAP_BYTES_CASES`;
  - the final `rg` absence check in Acceptance currently fails exactly on this cleanup because the constant still exists; and
  - `rg -n 'ZERO_GAP_BYTES_CASES' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` shows the detached table feeding only this owner file's zero-gap bytes promotion checks.
- This simplification matches the current benchmark information flow:
  - `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS` already acts as the canonical registry for public combined-manifest expectations; and
  - folding the remaining zero-gap bytes subset metadata onto those definition records removes one more parallel owner layer without changing the published benchmark boundary.

## Completion
- 2026-03-19: Added a definition-owned `zero_gap_bytes_representative_subsets` field on `SourceTreeCombinedManifestExpectationDefinition` and moved the detached zero-gap bytes subset groupings for `wider-ranged-repeat-quantified-group-boundary`, `open-ended-quantified-group-boundary`, and `branch-local-backreference-boundary` onto their owning manifest definitions.
- Deleted the detached top-level bytes table from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and updated the zero-gap bytes promotion tests to derive subset ids from definition-owned metadata while deriving manifest counts from the combined case / target manifest path instead of detached `100` / `72` / `30` literals.
- The task prose claimed eleven live subset groupings, but the checked-in table actually held twelve (`6` wider-ranged-repeat, `5` open-ended, `1` branch-local-backreference); this cleanup preserved the live twelve-grouping contract exactly instead of silently collapsing any subset semantics.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, the inline source probe from the task, and `bash -lc "! rg -n 'ZERO_GAP_BYTES_CASES' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`.
