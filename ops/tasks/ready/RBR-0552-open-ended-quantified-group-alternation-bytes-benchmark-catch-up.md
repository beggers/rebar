# RBR-0552: Catch the open-ended quantified-group alternation bytes pair up on the benchmark surface

Status: ready
Owner: feature-implementation
Created: 2026-03-17

## Goal
- Extend the published source-tree benchmark surface so the exact open-ended `{1,}` grouped-alternation bytes pair already supported by `RBR-0550` produces real `rebar` timings on the existing Python-facing open-ended manifest before broader-range open-ended grouped-alternation bytes publication reopens that family.

## Deliverables
- `benchmarks/workloads/open_ended_quantified_group_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/open_ended_quantified_group_boundary.py` adds only these six bytes mirrors of the current open-ended grouped-alternation `str` rows:
  - `module-compile-numbered-open-ended-group-alternation-cold-bytes`
  - `module-search-numbered-open-ended-group-alternation-lower-bound-bc-warm-bytes`
  - `pattern-fullmatch-numbered-open-ended-group-alternation-third-repetition-mixed-purged-bytes`
  - `module-compile-named-open-ended-group-alternation-warm-bytes`
  - `module-search-named-open-ended-group-alternation-lower-bound-de-warm-bytes`
  - `pattern-fullmatch-named-open-ended-group-alternation-fourth-repetition-de-purged-bytes`
- The new rows stay pinned to the existing Python-path public patterns and haystacks for this exact bounded slice:
  - `rb"a(bc|de){1,}d"` through `module.compile`, `module.search(..., b"zzabcdzz")`, and `Pattern.fullmatch(b"abcbcded")`;
  - `rb"a(?P<word>bc|de){1,}d"` through `module.compile`, `module.search(..., b"zzadedzz")`, and `Pattern.fullmatch(b"adededed")`.
- `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` treat the six new rows as measured source-tree workloads while keeping the open-ended manifest and combined report at zero known gaps.
- `tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py` is updated so the new workloads stay benchmark-anchored honestly: the two compile rows map to the published bytes compile metadata cases for this slice, and the four `module.search` / `Pattern.fullmatch` rows join the explicit direct-parity unanchored handling instead of appearing as accidental unanchored rows.
- Focused and combined benchmark publications move honestly:
  - `open-ended-quantified-group-boundary` moves from `60` total workloads / `60` measured workloads / `0` known gaps to `66` / `66` / `0`;
  - the combined source-tree report moves from `650` total workloads / `650` measured workloads / `0` known gaps to `656` / `656` / `0`.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes the six new bytes rows with `implementation_timing.status == "measured"` through the source-tree shim path; this task does not claim built-native full-suite publication.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/open_ended_quantified_group_boundary.py --report .rebar/tmp/rbr-0552-open-ended-grouped-alternation-bytes-benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark catch-up only. Do not change correctness fixtures, parity suites, or `reports/correctness/latest.py`.
- Keep the publication on the existing Python-facing source-tree benchmark path. Do not broaden into built-native publication, benchmark-harness refactors, or new adapter modes in this run.
- Add only the directly adjacent bytes mirrors for this open-ended grouped-alternation pair. Do not broaden into broader-range open-ended grouped-alternation bytes correctness publication, runtime parity follow-ons, or another benchmark family.

## Notes
- Build on `RBR-0550`.
- 2026-03-17 feature-planning probes confirm this task is not stale:
  - `benchmarks/workloads/open_ended_quantified_group_boundary.py` currently contains only the six open-ended grouped-alternation `str` workloads for this exact `{1,}` slice and none of the six planned `-bytes` mirrors;
  - `tests/benchmarks/test_open_ended_quantified_group_benchmark_correctness_anchor_contract.py` currently anchors only the matching `str` open-ended grouped-alternation workloads, leaves `DIRECT_PARITY_BYTES_CASES` limited to the conditional and backtracking-heavy bytes follow-ons, and therefore still lacks direct benchmark-anchor handling for the already-landed `OPEN_ENDED_ALTERNATION_BYTES_CASES`;
  - `reports/benchmarks/latest.py` currently publishes `open-ended-quantified-group-boundary` at `60` total workloads / `60` measured workloads / `0` known gaps and the combined source-tree report at `650` total / `650` measured / `0` known gaps; and
  - `ops/tasks/done/RBR-0550-open-ended-quantified-group-alternation-bytes-parity.md` already records successful public-API parity for `rb"a(bc|de){1,}d"` and `rb"a(?P<word>bc|de){1,}d"`, so these benchmark rows should measure rather than reopen a runtime gap.
- The surviving follow-on after this task is `RBR-0554`, which should publish the broader-range open-ended `{2,}` grouped-alternation bytes pair on the existing correctness/parity path before bytes parity or benchmark catch-up widen that broader-range family.
