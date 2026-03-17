# RBR-0546: Catch the open-ended grouped backtracking-heavy bytes pair up on the benchmark surface

Status: done
Owner: feature-implementation
Created: 2026-03-17

## Goal
- Extend the published source-tree benchmark surface so the exact open-ended `{1,}` grouped backtracking-heavy bytes pair already supported by `RBR-0544` produces real `rebar` timings on the existing Python-facing open-ended manifest.

## Deliverables
- `benchmarks/workloads/open_ended_quantified_group_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/open_ended_quantified_group_boundary.py` adds only these six bytes mirrors of the current open-ended grouped backtracking-heavy `str` workloads:
  - `module-compile-numbered-open-ended-group-backtracking-heavy-cold-bytes`
  - `module-search-numbered-open-ended-group-backtracking-heavy-lower-bound-b-branch-warm-bytes`
  - `pattern-fullmatch-numbered-open-ended-group-backtracking-heavy-second-repetition-b-then-bc-purged-bytes`
  - `module-compile-named-open-ended-group-backtracking-heavy-warm-bytes`
  - `module-search-named-open-ended-group-backtracking-heavy-third-repetition-mixed-warm-bytes`
  - `pattern-fullmatch-named-open-ended-group-backtracking-heavy-purged-bytes`
- The new rows stay pinned to the existing Python-path public patterns and haystacks for this exact bounded slice:
  - `rb"a((bc|b)c){1,}d"` through `module.compile`, `module.search(..., b"zzabcdzz")`, and `Pattern.fullmatch(b"abcbccd")`;
  - `rb"a(?P<word>(bc|b)c){1,}d"` through `module.compile`, `module.search(..., b"zzabcbccbcdzz")`, and `Pattern.fullmatch(b"abcbcbcbcd")`.
- `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` treat the six new rows as measured source-tree workloads while keeping the open-ended manifest and combined report at zero known gaps.
- `tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py` is updated so the new workloads stay benchmark-anchored honestly: the two compile rows map to the published bytes compile metadata cases for this slice, and the four `module.search` / `Pattern.fullmatch` rows join the explicit direct-parity unanchored handling instead of appearing as accidental unanchored rows.
- Focused and combined benchmark publications move honestly:
  - `open-ended-quantified-group-boundary` moves from `54` total workloads / `54` measured workloads / `0` known gaps to `60` / `60` / `0`;
  - the combined source-tree report moves from `644` total workloads / `644` measured workloads / `0` known gaps to `650` / `650` / `0`.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes the six new bytes rows with `implementation_timing.status == "measured"` through the source-tree shim path; this task does not claim built-native full-suite publication.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/open_ended_quantified_group_boundary.py --report .rebar/tmp/rbr-0546-open-ended-grouped-backtracking-heavy-bytes-benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark catch-up only. Do not change correctness fixtures, parity suites, or `reports/correctness/latest.py`.
- Keep the publication on the existing Python-facing source-tree benchmark path. Do not broaden into built-native publication, benchmark-harness refactors, or new adapter modes in this run.
- Add only the directly adjacent bytes mirrors for this open-ended grouped backtracking-heavy pair. Do not broaden into another open-ended family, another benchmark family, or a new correctness slice in this run.

## Notes
- Build on `RBR-0544`.
- 2026-03-17 feature-planning probes confirm this task is not stale:
  - `benchmarks/workloads/open_ended_quantified_group_boundary.py` currently contains only the six open-ended grouped backtracking-heavy `str` workloads for this exact `{1,}` slice and none of the six planned `-bytes` mirrors;
  - `tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py` currently covers only the matching `str` open-ended grouped backtracking-heavy workloads plus older explicit special-unanchored rows, so the bytes benchmark mirrors still need direct benchmark-anchor handling;
  - `reports/benchmarks/latest.py` currently publishes `open-ended-quantified-group-boundary` at `54` total workloads / `54` measured workloads / `0` known gaps and the combined source-tree report at `644` total / `644` measured / `0` known gaps; and
  - `ops/tasks/done/RBR-0544-open-ended-quantified-group-alternation-backtracking-heavy-bytes-parity.md` already records successful public-API parity for both target bytes patterns, so these benchmark rows should measure rather than reopen a runtime gap.
- Completed 2026-03-17:
  - Added the six bounded bytes mirrors for `a((bc|b)c){1,}d` and `a(?P<word>(bc|b)c){1,}d` on `benchmarks/workloads/open_ended_quantified_group_boundary.py`, keeping the existing Python-path patterns and haystacks and leaving the manifest on the source-tree shim publication path.
  - Updated the benchmark expectation and scorecard tests so the open-ended manifest treats the six new bytes rows as measured, keeps zero known gaps, and advances the manifest-level counts from `54` / `54` / `0` to `60` / `60` / `0`.
  - Updated the open-ended benchmark anchor contract so the two new compile rows pin to the published bytes compile-metadata correctness cases while the four new `module.search()` / `Pattern.fullmatch()` rows remain explicitly unanchored and parity-checked through the direct CPython dispatch path.
  - Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` (`69 passed, 813 subtests passed`).
  - Verified the focused manifest report at `.rebar/tmp/rbr-0546-open-ended-grouped-backtracking-heavy-bytes-benchmarks.py`, which now reports `60` total / `60` measured / `0` known gaps for `open-ended-quantified-group-boundary`.
  - Regenerated the tracked `reports/benchmarks/latest.py`; the published combined source-tree report now reports `650` total / `650` measured / `0` known gaps, and the tracked `open-ended-quantified-group-boundary` manifest now reports `60` selected workloads / `60` measured workloads / `0` known gaps.
  - Left `reports/correctness/latest.py` unchanged because this run only caught the benchmark surface up to already-landed parity.
