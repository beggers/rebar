# RBR-0564: Catch the quantified-alternation open-ended bytes pair up on the benchmark surface

Status: done
Owner: feature-implementation
Created: 2026-03-17

## Goal
- Extend the published source-tree benchmark surface so the exact open-ended `{1,}` quantified-alternation bytes pair supported by `RBR-0561` produces real `rebar` timings on the existing Python-facing quantified-alternation manifest.

## Deliverables
- `benchmarks/workloads/quantified_alternation_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/quantified_alternation_boundary.py` adds only these six bytes mirrors of the current open-ended quantified-alternation `str` rows:
  - `module-compile-numbered-quantified-alternation-open-ended-cold-bytes`
  - `module-search-numbered-quantified-alternation-open-ended-lower-bound-b-warm-bytes`
  - `pattern-fullmatch-numbered-quantified-alternation-open-ended-fourth-repetition-bcbc-purged-bytes`
  - `module-compile-named-quantified-alternation-open-ended-warm-bytes`
  - `module-search-named-quantified-alternation-open-ended-lower-bound-c-warm-bytes`
  - `pattern-fullmatch-named-quantified-alternation-open-ended-fourth-repetition-bcbc-purged-bytes`
- The new rows stay pinned to the existing Python-path public patterns and haystacks for this exact bounded slice:
  - `rb"a(b|c){1,}d"` through `module.compile`, `module.search(..., b"zzabdzz")`, and `Pattern.fullmatch(b"abcbcd")`;
  - `rb"a(?P<word>b|c){1,}d"` through `module.compile`, `module.search(..., b"zzacdzz")`, and `Pattern.fullmatch(b"abcbcd")`.
- `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` treat the six new rows as measured source-tree workloads while keeping the quantified-alternation manifest and the combined report at zero known gaps.
- Focused and combined benchmark publications move honestly:
  - `quantified-alternation-boundary` moves from `42` total workloads / `42` measured workloads / `0` known gaps to `48` / `48` / `0`;
  - the combined source-tree report moves from `662` total workloads / `662` measured workloads / `0` known gaps to `668` / `668` / `0`.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes the six new bytes rows with `implementation_timing.status == "measured"` through the source-tree shim path; this task does not claim built-native full-suite publication.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/quantified_alternation_boundary.py --report .rebar/tmp/rbr-0564-quantified-alternation-open-ended-bytes-benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark catch-up only. Do not change correctness fixtures, parity suites, or `reports/correctness/latest.py`.
- Keep the publication on the existing Python-facing source-tree benchmark path. Do not broaden into built-native publication, benchmark-harness refactors, or new adapter modes in this run.
- Add only the directly adjacent bytes mirrors for this open-ended quantified-alternation pair. Do not broaden into broader-range quantified-alternation bytes work, nested-branch bytes work, conditional bytes work, or another benchmark family in this run.

## Completion
- 2026-03-17: Added the six open-ended quantified-alternation bytes workloads to `benchmarks/workloads/quantified_alternation_boundary.py`, promoted them as measured representatives in the source-tree benchmark expectation/test surface, verified `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, verified `.rebar/tmp/rbr-0564-quantified-alternation-open-ended-bytes-benchmarks.py` at `48` total workloads / `48` measured workloads / `0` known gaps, and republished `reports/benchmarks/latest.py` at `668` total workloads / `668` measured workloads / `0` known gaps with `quantified-alternation-boundary` at `48` / `48` / `0`.

## Notes
- Build on `RBR-0561`.
- 2026-03-17 feature-planning probes seeded this task from the then-current tracked frontier:
  - `benchmarks/workloads/quantified_alternation_boundary.py` currently contains the six open-ended quantified-alternation `str` workloads for this exact `{1,}` slice and none of the six planned `-bytes` mirrors;
  - `tests/benchmarks/benchmark_expectations.py` still leaves `quantified-alternation-boundary` on the generic zero-gap manifest definition, and the shared source-tree benchmark suites currently contain no quantified-alternation-specific bytes assertions;
  - `reports/benchmarks/latest.py` currently publishes `quantified-alternation-boundary` at `42` total workloads / `42` measured workloads / `0` known gaps and the combined source-tree report at `662` / `662` / `0`; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from that planning run still raised `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`, so the benchmark follow-on stayed queued behind parity until later landings closed the gap.
