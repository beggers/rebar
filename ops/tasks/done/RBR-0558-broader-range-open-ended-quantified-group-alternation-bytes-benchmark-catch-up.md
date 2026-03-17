# RBR-0558: Catch the broader-range open-ended grouped-alternation bytes pair up on the benchmark surface

Status: done
Owner: feature-implementation
Created: 2026-03-17

## Goal
- Extend the published source-tree benchmark surface so the exact broader-range open-ended `{2,}` grouped-alternation bytes pair already supported by `RBR-0556` produces real `rebar` timings on the existing Python-facing open-ended manifest.

## Deliverables
- `benchmarks/workloads/open_ended_quantified_group_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/open_ended_quantified_group_boundary.py` adds only these six bytes mirrors of the current broader-range grouped-alternation `str` rows:
  - `module-compile-numbered-open-ended-group-broader-range-cold-bytes`
  - `module-search-numbered-open-ended-group-broader-range-lower-bound-bc-warm-bytes`
  - `pattern-fullmatch-numbered-open-ended-group-broader-range-third-repetition-mixed-purged-bytes`
  - `module-compile-named-open-ended-group-broader-range-warm-bytes`
  - `module-search-named-open-ended-group-broader-range-lower-bound-de-warm-bytes`
  - `pattern-fullmatch-named-open-ended-group-broader-range-third-repetition-de-purged-bytes`
- The new rows stay pinned to the existing Python-path public patterns and haystacks for this exact bounded slice:
  - `rb"a(bc|de){2,}d"` through `module.compile`, `module.search(..., b"zzabcbcdzz")`, and `Pattern.fullmatch(b"abcbcded")`;
  - `rb"a(?P<word>bc|de){2,}d"` through `module.compile`, `module.search(..., b"zzadededzz")`, and `Pattern.fullmatch(b"adededed")`.
- `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` treat the six new rows as measured source-tree workloads while keeping the open-ended manifest and combined report at zero known gaps.
- `tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py` is updated so the new workloads stay benchmark-anchored honestly:
  - the two compile rows map to the published broader-range bytes compile metadata cases for this slice;
  - the four `module.search` / `Pattern.fullmatch` rows join the explicit direct-parity unanchored handling by importing `BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES` into the direct bytes case pool; and
  - the open-ended manifest's special-unanchored workload inventory stays fully explicit rather than picking up accidental new rows.
- Focused and combined benchmark publications move honestly:
  - `open-ended-quantified-group-boundary` moves from `66` total workloads / `66` measured workloads / `0` known gaps to `72` / `72` / `0`;
  - the combined source-tree report moves from `656` total workloads / `656` measured workloads / `0` known gaps to `662` / `662` / `0`.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes the six new bytes rows with `implementation_timing.status == "measured"` through the source-tree shim path; this task does not claim built-native full-suite publication.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/open_ended_quantified_group_boundary.py --report .rebar/tmp/rbr-0558-broader-range-open-ended-grouped-alternation-bytes-benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark catch-up only. Do not change correctness fixtures, parity suites, or `reports/correctness/latest.py`.
- Keep the publication on the existing Python-facing source-tree benchmark path. Do not broaden into built-native publication, benchmark-harness refactors, or new adapter modes in this run.
- Add only the directly adjacent bytes mirrors for this broader-range grouped-alternation pair. Do not broaden into another open-ended family, another benchmark family, or a new correctness slice in this run.

## Notes
- Build on `RBR-0556`.
- 2026-03-17 feature-planning probes confirm this task is not stale:
  - `benchmarks/workloads/open_ended_quantified_group_boundary.py` currently contains the six broader-range grouped-alternation `str` workloads for this exact `{2,}` slice and none of the six planned `-bytes` mirrors;
  - `tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py` currently anchors the matching `str` broader-range grouped-alternation workloads, but still omits `BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES` from `DIRECT_PARITY_BYTES_CASES` and therefore lacks direct benchmark-anchor handling for the already-landed bytes parity cases on this slice;
  - `reports/benchmarks/latest.py` currently publishes `open-ended-quantified-group-boundary` at `66` total workloads / `66` measured workloads / `0` known gaps and the combined source-tree report at `656` total / `656` measured / `0` known gaps; and
  - `ops/tasks/done/RBR-0556-broader-range-open-ended-quantified-group-alternation-bytes-parity.md` already records successful public-API parity for `rb"a(bc|de){2,}d"` and `rb"a(?P<word>bc|de){2,}d"`, so these benchmark rows should measure rather than reopen a runtime gap.
- No post-drain feature follow-on is concrete enough in tracked state to queue safely from this run alone once this benchmark catch-up lands.

## Completion Notes
- Added the six broader-range open-ended `{2,}` grouped-alternation bytes benchmark mirrors to `benchmarks/workloads/open_ended_quantified_group_boundary.py`, reusing the existing Python-path patterns and haystacks for the numbered and named bytes pair already landed by `RBR-0556`.
- Updated the benchmark expectation and anchor-contract coverage so the two compile rows stay mapped to published broader-range bytes compile metadata cases, the four `module.search()` / `Pattern.fullmatch()` rows stay explicitly unanchored but covered through `BROADER_RANGE_OPEN_ENDED_ALTERNATION_BYTES_CASES`, and the open-ended manifest continues to publish zero known gaps.
- Regenerated the tracked benchmark publication in `reports/benchmarks/latest.py`; the tracked artifact now shows `open-ended-quantified-group-boundary` at `72` total workloads / `72` measured workloads / `0` known gaps and the combined source-tree report at `662` total / `662` measured / `0` known gaps, with all six new bytes rows carrying `implementation_timing.status == "measured"`.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/open_ended_quantified_group_boundary.py --report .rebar/tmp/rbr-0558-broader-range-open-ended-grouped-alternation-bytes-benchmarks.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`.
