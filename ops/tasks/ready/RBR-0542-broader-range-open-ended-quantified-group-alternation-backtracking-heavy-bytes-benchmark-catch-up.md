# RBR-0542: Catch the broader-range open-ended grouped backtracking-heavy bytes pair up on the benchmark surface

Status: ready
Owner: feature-implementation
Created: 2026-03-17

## Goal
- Extend the published source-tree benchmark surface so the exact broader-range open-ended `{2,}` grouped backtracking-heavy bytes pair already supported by `RBR-0540` produces real `rebar` timings on the existing Python-facing open-ended manifest.

## Deliverables
- `benchmarks/workloads/open_ended_quantified_group_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/open_ended_quantified_group_boundary.py` adds only these six bytes mirrors of the current broader-range grouped backtracking-heavy `str` rows:
  - `module-compile-numbered-open-ended-group-broader-range-backtracking-heavy-cold-bytes`
  - `module-search-numbered-open-ended-group-broader-range-backtracking-heavy-lower-bound-b-branch-warm-bytes`
  - `pattern-fullmatch-numbered-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-purged-bytes`
  - `module-compile-named-open-ended-group-broader-range-backtracking-heavy-warm-bytes`
  - `module-search-named-open-ended-group-broader-range-backtracking-heavy-second-repetition-bc-then-b-warm-bytes`
  - `pattern-fullmatch-named-open-ended-group-broader-range-backtracking-heavy-purged-bytes`
- The new rows stay pinned to the existing Python-path public patterns and haystacks for this exact bounded slice:
  - `rb"a((bc|b)c){2,}d"` through `module.compile`, `module.search(..., b"zzabcbcdzz")`, and `Pattern.fullmatch(b"abccbcd")`;
  - `rb"a(?P<word>(bc|b)c){2,}d"` through `module.compile`, `module.search(..., b"zzabccbcdzz")`, and `Pattern.fullmatch(b"abcbcbcbcd")`.
- `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` treat the six new rows as measured source-tree workloads while keeping the open-ended manifest and combined report at zero known gaps.
- `tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py` is updated so the new workloads stay benchmark-anchored honestly: the two compile rows map to the published bytes compile metadata cases for this slice, and the four `module.search` / `Pattern.fullmatch` rows join the explicit direct-parity unanchored handling instead of appearing as accidental unanchored rows.
- Focused and combined benchmark publications move honestly:
  - `open-ended-quantified-group-boundary` moves from `48` total workloads / `48` measured workloads / `0` known gaps to `54` / `54` / `0`;
  - the combined source-tree report moves from `638` total workloads / `638` measured workloads / `0` known gaps to `644` / `644` / `0`.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes the six new bytes rows with `implementation_timing.status == "measured"` through the source-tree shim path; this task does not claim built-native full-suite publication.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/open_ended_quantified_group_boundary.py --report .rebar/tmp/rbr-0542-broader-range-open-ended-grouped-backtracking-heavy-bytes-benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark catch-up only. Do not change correctness fixtures, parity suites, or `reports/correctness/latest.py`.
- Keep the publication on the existing Python-facing source-tree benchmark path. Do not broaden into built-native publication, benchmark-harness refactors, or new adapter modes in this run.
- Add only the directly adjacent bytes mirrors for this broader-range grouped backtracking-heavy pair. Do not broaden into another open-ended family, another benchmark family, or a new correctness slice in this run.

## Notes
- Build on `RBR-0540`.
- 2026-03-17 feature-planning probes confirm this task is not stale:
  - `benchmarks/workloads/open_ended_quantified_group_boundary.py` currently contains only the six broader-range grouped backtracking-heavy `str` workloads for this slice and none of the six planned `-bytes` mirrors;
  - `tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py` currently covers only the matching `str` broader-range grouped backtracking-heavy workloads plus older explicit special-unanchored rows, so the bytes benchmark mirrors still need direct benchmark-anchor handling;
  - `reports/benchmarks/latest.py` currently publishes `open-ended-quantified-group-boundary` at `48` total workloads / `48` measured workloads / `0` known gaps and the combined source-tree report at `638` total / `638` measured / `0` known gaps; and
  - `ops/tasks/done/RBR-0540-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-bytes-parity.md` already records successful public-API parity for both target bytes patterns, so these benchmark rows should measure rather than reopen a runtime gap.
