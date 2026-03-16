# RBR-0469: Delete default source-tree benchmark gap metadata

Status: done
Owner: architecture-implementation
Created: 2026-03-16

## Goal
- Remove the remaining default-valued gap bookkeeping from `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS` so the shared benchmark expectation table stores only real gap inventories and non-empty representative gap subsets, while the existing helper path continues to synthesize the public zero-gap shape for callers.

## Deliverables
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Keep the cleanup on the existing source-tree benchmark expectation path in `tests/benchmarks/benchmark_expectations.py`; do not add a new registry, generated file, or benchmark-support module.
- `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS` no longer stores raw `known_gap_count` fields anywhere. After `RBR-0466`, every current nonzero count in that table is already derivable from `known_gap_workload_ids`, and every zero count can be synthesized by default.
- Zero-gap manifest entries in `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS` also stop storing `representative_known_gap_workload_ids: ()`. Omit that key when the representative gap tuple is empty instead of repeating the default on each manifest.
- Preserve the current public caller-facing shape produced by the shared helpers:
  - `source_tree_combined_case(manifest_id)["manifest_expectation"]["known_gap_count"]` is still present and correct for both zero-gap and gapped manifests;
  - `source_tree_combined_case(manifest_id)["manifest_expectation"]["representative_known_gap_workload_ids"]` is still present and equals `()` for zero-gap manifests; and
  - gapped manifests that intentionally keep a representative known-gap subset, such as `literal-flag-boundary`, preserve the current tuple and ordering exactly.
- Keep `source_tree_scorecard_case(...)`, `source_tree_combined_case(...)`, and `expected_summary_for_manifests(...)` on the existing normalization path. Prefer extending `_public_source_tree_manifest_expectation(...)` or the smallest adjacent helper over threading another normalization layer through the tests.
- If you add focused regression coverage in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, keep it narrow:
  - one assertion that raw manifest expectations no longer store default `known_gap_count` or empty `representative_known_gap_workload_ids`; and
  - one assertion that the public `manifest_expectation` returned for a zero-gap manifest still exposes `known_gap_count == 0` and `representative_known_gap_workload_ids == ()`.
- Keep the cleanup structural only:
  - do not change benchmark workload manifests under `benchmarks/workloads/`;
  - do not change benchmark harness runtime behavior in `python/rebar_harness/benchmarks.py`;
  - do not change workload ids, manifest selectors, published reports, README text, or tracked state files beyond this task file.
- Verification uses a structural command that isolates this cleanup from the unrelated benchmark-summary drift still owned by `RBR-0467`:
  ```bash
  PYTHONPATH=python .venv/bin/python - <<'PY'
  from tests.benchmarks.benchmark_expectations import (
      SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS,
      source_tree_combined_case,
      source_tree_scorecard_case,
  )

  stored_known_gap_counts = {
      manifest_id: expectation["known_gap_count"]
      for manifest_id, expectation in SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.items()
      if "known_gap_count" in expectation
  }
  assert not stored_known_gap_counts, stored_known_gap_counts

  stored_empty_representative_gap_ids = sorted(
      manifest_id
      for manifest_id, expectation in SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.items()
      if expectation.get("representative_known_gap_workload_ids") == ()
  )
  assert not stored_empty_representative_gap_ids, stored_empty_representative_gap_ids

  pattern_expectation = source_tree_combined_case("pattern-boundary")["manifest_expectation"]
  assert pattern_expectation["known_gap_count"] == 0, pattern_expectation
  assert pattern_expectation["representative_known_gap_workload_ids"] == (), pattern_expectation

  literal_flag_expectation = source_tree_combined_case("literal-flag-boundary")[
      "manifest_expectation"
  ]
  assert literal_flag_expectation["known_gap_count"] == 2, literal_flag_expectation
  assert literal_flag_expectation["representative_known_gap_workload_ids"] == (
      "module-search-ignorecase-ascii-cold-gap",
  ), literal_flag_expectation

  post_parser = source_tree_scorecard_case("post-parser-workflows")
  assert post_parser["manifest_expectations"]["pattern-boundary"]["known_gap_count"] == 0
  assert post_parser["manifest_expectations"]["literal-flag-boundary"]["known_gap_count"] == 2
  print("ok")
  PY
  ```

## Constraints
- Prefer deleting repeated default metadata over moving it into another helper constant. The intended end state is a raw manifest expectation table that stores only real inventories and non-empty representative subsets, with public defaults synthesized in one place.
- Do not broaden this into representative measured-workload cleanup, slice-expectation reordering, or another round of report-summary refresh work. This task is only about deleting duplicated gap defaults from the raw manifest expectation table.
- Preserve the current public representative known-gap semantics exactly. This task should not change which gap workload ids the tests assert for gapped manifests; it should only stop storing empty defaults and redundant raw counts.

## Notes
- `RBR-0467` is already filed in `ops/tasks/ready/`, and `RBR-0468` is reserved in `ops/state/backlog.md`, so this architecture cleanup starts at `RBR-0469`.
- The runtime dashboard is current and clean for this run (`Generated: 2026-03-16T12:11:49+00:00`, `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `Last Cycle Anomalies: none`), so rule 10 does not apply.
- JSON counts are fully burned down in both tracked and live views:
  - `tracked_json_blob_count: 0`
  - `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
- In the current checkout, the duplicate default gap metadata is still concentrated in `tests/benchmarks/benchmark_expectations.py`:
  - `20` manifest entries still store raw `known_gap_count: 0`;
  - the `regression-matrix` entry still stores a redundant raw `known_gap_count: 1` even though its `known_gap_workload_ids` inventory is already explicit; and
  - `20` manifest entries still store `representative_known_gap_workload_ids: ()`.
- The broad benchmark scorecard suites are currently red for unrelated publication drift that belongs to `RBR-0467`, not this cleanup. The live rerun reports `15` known gaps / `573` measured workloads while the tracked summary assertions still expect the pre-`RBR-0465` `16`-gap / `572`-measured publication, so do not use those broad suites as this task's acceptance gate.
- 2026-03-16 verification: the structural command above fails in the current checkout with the stored-count list beginning `['branch-local-backreference-boundary', 'collection-replacement-boundary', 'compile-matrix', ...]`, which is the exact remaining duplication this task is meant to delete.

## Completion
- 2026-03-16: Removed stored `known_gap_count` fields from `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS` and deleted empty `representative_known_gap_workload_ids: ()` entries from zero-gap manifests, leaving the raw table with only explicit gap inventories and non-empty representative gap subsets.
- 2026-03-16: Kept the public helper shape unchanged on the existing normalization path by synthesizing `known_gap_count` and defaulting `representative_known_gap_workload_ids` to `()` in `_public_source_tree_manifest_expectation(...)`, and by using that same defaulted representative-gap path when resolving single-manifest `source_tree_scorecard_case(...)` definitions.
- 2026-03-16: Added focused regression coverage in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` for the zero-gap raw/default cleanup and reran `PYTHONPATH=python ./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'manifest_gap_inventories or zero_gap_manifests' -q` (`2 passed`).
- 2026-03-16: Verified the structural cleanup with a repo-local Python probe that confirmed no raw manifest expectations still store `known_gap_count` or empty representative-gap tuples, `source_tree_combined_case("pattern-boundary")` still returns `known_gap_count == 0` and `representative_known_gap_workload_ids == ()`, `literal-flag-boundary` still reports the same representative known-gap tuple, and `source_tree_scorecard_case("post-parser-workflows")` still derives `0` for `collection-replacement-boundary` and `2` for `literal-flag-boundary`.
- 2026-03-16: The task's pasted verification snippet has one stale lookup: `source_tree_scorecard_case("post-parser-workflows")["manifest_expectations"]["pattern-boundary"]` raises `KeyError` because that scorecard case does not include `pattern-boundary`. The equivalent zero-gap scorecard-path check above passed against the zero-gap manifest that case does include.
