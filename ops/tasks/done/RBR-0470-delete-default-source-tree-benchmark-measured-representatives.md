# RBR-0470: Delete default source-tree benchmark measured representatives

Status: done
Owner: architecture-implementation
Created: 2026-03-16

## Goal
- Remove the remaining default empty `representative_measured_workload_ids` bookkeeping from `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS`, so the raw benchmark expectation table stores only real manifest-local measured representative overrides while the existing helper path keeps the current public default shape and derived representative behavior intact.

## Deliverables
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Keep the cleanup on the existing source-tree benchmark expectation path in `tests/benchmarks/benchmark_expectations.py`; do not add a new registry, support module, or generated file.
- `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS` no longer stores `representative_measured_workload_ids: ()` anywhere. Omit that key when a manifest has no manifest-local measured representative override instead of repeating the empty default on each entry.
- Keep the current effective representative-resolution behavior in `source_tree_combined_manifest_representative_measured_workload_ids(...)`:
  - manifests with explicit non-empty measured representative tuples keep those tuples unchanged;
  - shape-backed manifests such as `pattern-boundary` still derive the same representative ids from `shape_expectation`; and
  - slice-backed manifests such as `branch-local-backreference-boundary` still derive the same ordered ids from `SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS`.
- Keep the current caller-facing shape produced by `source_tree_combined_case(...)` and `_public_source_tree_manifest_expectation(...)`:
  - `case["manifest_expectation"]["representative_measured_workload_ids"]` is still present for callers even when the raw table omits it;
  - zero-default manifests such as `collection-replacement-boundary` still expose `()` there; and
  - slice-derived manifests such as `branch-local-backreference-boundary` also keep exposing `()` there while the derived helper continues to return the slice-backed representative ids.
- If you add focused regression coverage in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, keep it narrow:
  - one assertion that raw manifest expectations no longer store empty `representative_measured_workload_ids`;
  - one assertion that a public zero-default manifest expectation still exposes `representative_measured_workload_ids == ()`; and
  - one assertion that `source_tree_combined_manifest_representative_measured_workload_ids(...)` still returns the current derived ids for one shape-backed manifest.
- Keep the cleanup structural only:
  - do not change benchmark workload manifests under `benchmarks/workloads/`;
  - do not change benchmark harness runtime behavior in `python/rebar_harness/benchmarks.py`;
  - do not change workload ids, manifest selectors, published reports, README text, or tracked state files beyond this task file.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_scorecards.py`
  - ```bash
    PYTHONPATH=python ./.venv/bin/python - <<'PY'
    from tests.benchmarks.benchmark_expectations import (
        SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS,
        source_tree_combined_case,
        source_tree_combined_manifest_representative_measured_workload_ids,
    )

    stored_empty_representative_ids = sorted(
        manifest_id
        for manifest_id, expectation in SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS.items()
        if expectation.get("representative_measured_workload_ids") == ()
    )
    assert not stored_empty_representative_ids, stored_empty_representative_ids

    collection_expectation = source_tree_combined_case(
        "collection-replacement-boundary"
    )["manifest_expectation"]
    assert collection_expectation["representative_measured_workload_ids"] == (), (
        collection_expectation
    )

    pattern_expectation = source_tree_combined_case("pattern-boundary")[
        "manifest_expectation"
    ]
    assert pattern_expectation["representative_measured_workload_ids"] == (), (
        pattern_expectation
    )
    assert source_tree_combined_manifest_representative_measured_workload_ids(
        "pattern-boundary"
    ) == (
        "pattern-search-literal-warm-hit",
        "pattern-fullmatch-bytes-purged-hit",
    )
    print("ok")
    PY
    ```

## Constraints
- Prefer deleting repeated default metadata over moving it into another helper constant. The intended end state is a raw manifest expectation table that stores only real measured representative overrides, with the empty public default synthesized in one place and the derived helper continuing to resolve shape-backed and slice-backed representatives.
- Do not broaden this into another round of gap cleanup, scorecard-case reshaping, or workload/report refresh work. This task is only about deleting duplicated empty measured-representative defaults from the raw manifest expectation table.
- Preserve current representative workload ordering exactly. `source_tree_combined_manifest_representative_measured_workload_ids(...)` is order-sensitive, so any helper change must keep the current shape-backed and slice-backed ordering intact.

## Notes
- `RBR-0468` is the active feature task and `RBR-0469` has already landed, so this architecture cleanup starts at `RBR-0470`.
- The runtime dashboard is current and clean for this run (`Generated: 2026-03-16T12:50:43+00:00`, `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `Last Cycle Anomalies: none`), so rule 10 does not apply.
- JSON counts are fully burned down in both tracked and live views:
  - `tracked_json_blob_count: 0`
  - `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
- At task intake, the duplicate default measured metadata was concentrated in `tests/benchmarks/benchmark_expectations.py`:
  - `25` manifest entries still store raw `representative_measured_workload_ids: ()`; and
  - those entries include true zero-default manifests such as `collection-replacement-boundary` plus derived manifests such as `pattern-boundary` and `branch-local-backreference-boundary`, where the effective representative ids already come from shared shape/slice expectation data instead of the empty raw tuple.
- 2026-03-16 intake verification:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_scorecards.py` passes in the current checkout (`11 passed, 464 subtests passed`).
  - the structural Python probe above currently fails exactly on the remaining duplication with the first stored-empty list entries `['branch-local-backreference-boundary', 'collection-replacement-boundary', 'compile-matrix', 'conditional-group-exists-boundary', 'conditional-group-exists-empty-else-boundary', ...]`.

## Completion
- 2026-03-16: Removed every raw `representative_measured_workload_ids: ()` entry from `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS`, leaving the table with only real manifest-local overrides plus existing gap and shape metadata.
- 2026-03-16: Reworked `pattern-boundary` to keep its representative pair on the existing `shape_expectation` path, updated `source_tree_combined_manifest_representative_measured_workload_ids(...)` to tolerate omitted raw representative tuples, and kept `_public_source_tree_manifest_expectation(...)` synthesizing `representative_measured_workload_ids == ()` for callers when the raw table omits that key.
- 2026-03-16: Added focused regression coverage in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` that asserts the raw table no longer stores empty representative tuples, that a zero-default public manifest expectation still exposes `representative_measured_workload_ids == ()`, and that the shape-backed `pattern-boundary` helper still returns the same representative pair.
- 2026-03-16: Verified the cleanup with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_scorecards.py` (`14 passed, 464 subtests passed in 19.51s`) and with the task's structural Python probe (`ok`).
