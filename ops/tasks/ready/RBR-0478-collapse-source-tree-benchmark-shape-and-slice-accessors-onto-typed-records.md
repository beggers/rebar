# RBR-0478: Collapse source-tree benchmark shape and slice accessors onto typed records

Status: ready
Owner: architecture-implementation
Created: 2026-03-16

## Goal
- Replace the remaining dict-shaped source-tree benchmark shape and slice expectation accessors in `tests/benchmarks/benchmark_expectations.py` with explicit typed records, so the benchmark suites stop coupling to long lists of string keys when they read shared slice filters, pattern-group metadata, and shape-backed representative coverage.

## Deliverables
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/benchmark_expectations.py` exposes explicit typed records for the remaining public source-tree benchmark expectation accessors:
  - `source_tree_combined_manifest_shape_expectation(...)`
  - `source_tree_combined_slice_expectations(...)`
- The typed accessors cover the currently anonymous payloads that those helpers expose today:
  - manifest-shape expectations expose `representative_measured_workload_ids` and `pattern_groups`
  - pattern-group entries expose `slice_id`, `patterns`, `minimum_rows`, `required_operations`, `required_categories`, `search_haystacks`, `search_haystack_substrings`, and `pattern_haystacks`
  - slice expectations expose `manifest_id`, `slice_id`, `required_syntax_features`, `excluded_syntax_features`, `required_categories`, `excluded_categories`, `required_id_suffix`, `expected_workload_ids`, `expected_patterns`, `expected_operations`, `expected_haystacks`, `required_row_categories`, and `expected_status`
- `source_tree_combined_manifest_shape_expectation(...)` and `source_tree_combined_slice_expectations(...)` no longer return plain `dict` objects, and `pattern_groups` no longer contains dict entries. Keep the typed records local to `tests/benchmarks/benchmark_expectations.py`; do not add a new support module.
- The existing helper flow that consumes those accessors also stops indexing them through string keys:
  - `source_tree_combined_manifest_representative_measured_workload_ids(...)`
  - `_workload_matches_source_tree_combined_slice(...)`
  - `select_source_tree_combined_slice_rows(...)`
  - `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- Preserve the current benchmark data and ordering exactly:
  - keep the current manifest ids returned by `source_tree_combined_slice_manifest_ids()`
  - keep the current slice ids and slice ordering under `SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS`
  - keep the current pattern-group ids and ordering under `wider-ranged-repeat-quantified-group-boundary`
  - keep the existing expected workload ids, patterns, operations, statuses, row-category requirements, and haystack expectations unchanged
- Keep the cleanup structural only:
  - do not change files under `benchmarks/workloads/`
  - do not change runtime behavior in `python/rebar_harness/benchmarks.py`
  - do not change published reports, README text, or tracked state files beyond this task file
  - do not broaden this into typing the full raw `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS` table or another source-tree scorecard-case refactor; this task is only about the remaining shape/slice accessors and their direct consumers
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `rg -n 'expectation\\[\"(expected_workload_ids|required_categories|required_id_suffix|required_syntax_features|excluded_syntax_features|excluded_categories|expected_patterns|expected_operations|expected_haystacks|expected_status|required_row_categories|slice_id)\"\\]|shape_expectation\\[\"(representative_measured_workload_ids|pattern_groups)\"\\]|pattern_group\\[\"(slice_id|patterns|minimum_rows|required_operations|required_categories|search_haystacks|search_haystack_substrings|pattern_haystacks)\"\\]' tests/benchmarks/benchmark_expectations.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
    The post-change result must be no matches.
  - ```bash
    PYTHONPATH=python ./.venv/bin/python - <<'PY'
    from tests.benchmarks.benchmark_expectations import (
        source_tree_combined_manifest_shape_expectation,
        source_tree_combined_slice_expectations,
    )

    shape = source_tree_combined_manifest_shape_expectation(
        "wider-ranged-repeat-quantified-group-boundary"
    )
    slice_expectation = source_tree_combined_slice_expectations(
        "branch-local-backreference-boundary"
    )[0]

    assert not isinstance(shape, dict), type(shape)
    assert not isinstance(shape.pattern_groups[0], dict), type(shape.pattern_groups[0])
    assert not isinstance(slice_expectation, dict), type(slice_expectation)

    assert shape.pattern_groups[0].slice_id == "nested-broader-range-grouped-alternation"
    assert shape.representative_measured_workload_ids
    assert slice_expectation.manifest_id == "branch-local-backreference-boundary"
    assert slice_expectation.expected_workload_ids
    print("ok")
    PY
    ```

## Constraints
- Prefer a few small local `dataclass` or `NamedTuple` types in `tests/benchmarks/benchmark_expectations.py` over another renamed dict-normalization layer. The intended end state is one explicit typed expectation surface, not another helper that still returns anonymous mappings.
- Keep the current canonical expectation data in the existing module. If `_combined_slice_expectation(...)` becomes a typed constructor or `source_tree_combined_manifest_shape_expectation(...)` normalizes raw nested data into typed records, keep that logic local to `tests/benchmarks/benchmark_expectations.py`; do not split it into a registry or support file.
- Preserve the current subtest intent and representative-coverage assertions. This task should change how the shared expectation metadata is represented and consumed, not what the benchmark suites verify.

## Notes
- `RBR-0477` is already queued as the ready-head feature task, and the current runtime dashboard is clean (`Generated: 2026-03-16T15:40:00+00:00`, `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `Last Cycle Anomalies: none`), so rule 10 does not apply.
- JSON counts remain fully burned down in both tracked and live views:
  - `tracked_json_blob_count: 0`
  - `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
- The remaining string-key coupling is concentrated in three places:
  - `tests/benchmarks/test_source_tree_benchmark_scorecards.py:87-88` still flattens `source_tree_combined_slice_expectations(...)` through `expectation["expected_workload_ids"]`
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py:148-460` still indexes shape, slice, and pattern-group payloads through string keys across the combined-suite regressions
  - `tests/benchmarks/benchmark_expectations.py:1407` and `tests/benchmarks/benchmark_expectations.py:1926-1936` still read slice-expectation fields through anonymous dict keys inside the shared helper path
- Current file sizes underline why this is still a useful bounded simplification:
  - `tests/benchmarks/benchmark_expectations.py`: `1948` lines
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`: `502` lines
  - `tests/benchmarks/test_source_tree_benchmark_scorecards.py`: `208` lines
- 2026-03-16 intake verification:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passes in the current checkout (`16 passed, 467 subtests passed in 19.76s`).
  - `rg -n 'expectation\\[\"(expected_workload_ids|required_categories|required_id_suffix|required_syntax_features|excluded_syntax_features|excluded_categories|expected_patterns|expected_operations|expected_haystacks|expected_status|required_row_categories|slice_id)\"\\]|shape_expectation\\[\"(representative_measured_workload_ids|pattern_groups)\"\\]|pattern_group\\[\"(slice_id|patterns|minimum_rows|required_operations|required_categories|search_haystacks|search_haystack_substrings|pattern_haystacks)\"\\]' tests/benchmarks/benchmark_expectations.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently returns `22` matches, which is the exact string-key benchmark plumbing this task should delete rather than rename.
  - The typed-record probe above currently fails with `AssertionError: <class 'dict'>`, which is the exact remaining accessor shape this task is meant to replace.
