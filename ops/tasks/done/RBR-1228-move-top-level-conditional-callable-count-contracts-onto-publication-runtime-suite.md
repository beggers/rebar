Status: done
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining top-level conditional-group-exists callable count-contract round-trip block that still lives inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by moving it onto the existing runtime-contract owner in `tests/benchmarks/test_benchmark_publication_runtime_contracts.py`, so the giant combined benchmark suite stops owning payload-only callback/count coverage that does not depend on its broader scorecard or manifest-selection assertions.

## Deliverables
- `tests/benchmarks/test_benchmark_publication_runtime_contracts.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Extend `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` so it becomes the owner for the current top-level conditional callable count-contract round-trip block now embedded in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Move these existing tests into that dedicated runtime-contract file without widening their scope or changing their assertion surfaces:
  - `test_conditional_group_exists_callable_negative_count_str_workloads_round_trip_preserves_suffix_only_callback_payloads`
  - `test_conditional_group_exists_callable_none_count_str_workloads_round_trip_preserves_suffix_only_callback_payloads`
  - `test_conditional_group_exists_callable_none_count_bytes_workloads_round_trip_preserves_suffix_only_callback_payloads`
- Keep the extracted runtime surface pinned to current live behavior exactly:
  - preserve the current live selection of top-level `conditional-group-exists-boundary` callable `sub()` and `subn()` rows for the negative-count `str` slice and the `count is None` `str` and `bytes` slices, but rebuild that selection directly from the live manifest in the runtime-contract suite instead of importing helper constants or selectors from the giant combined suite;
  - preserve the exact serialized replacement descriptor contract for every moved row, including `{"type": "callable_match_group", "group": 1 or "word", "suffix": "x"}` and the current callback-signature expectations of `("", "x")` for `str` and `(b"", b"x")` for `bytes`;
  - preserve the exact `count` contract for each moved row, including `-1` for the negative-count slice and `None` for the none-count slices; and
  - preserve the current CPython outcome contract exactly, including the negative-count short-circuit results (`"abcdaceabcd"` / `("abcdaceabcd", 0)`) and the current `TypeError` substring matching for the none-count rows after payload round-trip.
- Reuse the existing runtime-contract suite instead of adding another layer:
  - keep `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` as the owner for this extracted block;
  - keep using the existing benchmark helpers already in the test tree rather than importing the giant combined suite into the runtime-contract suite; and
  - do not add a new `*_support.py` module, a new sibling runtime-contract suite, or wrappers/aliases left behind in the combined suite.
- Delete the moved tests from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` instead of leaving wrappers, aliases, or duplicate copies behind.
- Keep this cleanup structural and bounded to the two files above; do not change `python/rebar_harness/benchmarks.py`, benchmark workload manifests, correctness fixtures, reports, README text, or tracked ops/state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_publication_runtime_contracts.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists_callable_negative_count_str_workloads_round_trip_preserves_suffix_only_callback_payloads or conditional_group_exists_callable_none_count_str_workloads_round_trip_preserves_suffix_only_callback_payloads or conditional_group_exists_callable_none_count_bytes_workloads_round_trip_preserves_suffix_only_callback_payloads'`
- `bash -lc "! rg -n 'def test_(conditional_group_exists_callable_negative_count_str_workloads_round_trip_preserves_suffix_only_callback_payloads|conditional_group_exists_callable_none_count_str_workloads_round_trip_preserves_suffix_only_callback_payloads|conditional_group_exists_callable_none_count_bytes_workloads_round_trip_preserves_suffix_only_callback_payloads)' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Notes
- Completed 2026-03-24: moved the three top-level conditional callable count-contract round-trip tests into `tests/benchmarks/test_benchmark_publication_runtime_contracts.py`, rebuilt their workload selection directly from the live `conditional-group-exists-boundary` manifest, deleted the duplicate combined-suite copies, and kept the existing callback payload signatures, `count` values, CPython negative-count results, and none-count `TypeError` message matching unchanged.
- Verified 2026-03-24 with `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_publication_runtime_contracts.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists_callable_negative_count_str_workloads_round_trip_preserves_suffix_only_callback_payloads or conditional_group_exists_callable_none_count_str_workloads_round_trip_preserves_suffix_only_callback_payloads or conditional_group_exists_callable_none_count_bytes_workloads_round_trip_preserves_suffix_only_callback_payloads'` (`3 passed, 224 deselected`) and `bash -lc "! rg -n 'def test_(conditional_group_exists_callable_negative_count_str_workloads_round_trip_preserves_suffix_only_callback_payloads|conditional_group_exists_callable_none_count_str_workloads_round_trip_preserves_suffix_only_callback_payloads|conditional_group_exists_callable_none_count_bytes_workloads_round_trip_preserves_suffix_only_callback_payloads)' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` (no matches).
