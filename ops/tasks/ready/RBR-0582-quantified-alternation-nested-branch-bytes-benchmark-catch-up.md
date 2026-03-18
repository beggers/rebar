# RBR-0582: Catch the quantified-alternation nested-branch bytes pair up on the benchmark surface

Status: ready
Owner: feature-implementation
Created: 2026-03-18

## Goal
- Extend the published source-tree benchmark surface so the exact bounded `{1,2}` quantified-alternation nested-branch bytes pair expected to be supported by `RBR-0580` produces real `rebar` timings on the existing Python-facing quantified-alternation manifest.

## Deliverables
- `benchmarks/workloads/quantified_alternation_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/quantified_alternation_boundary.py` adds only these six bytes mirrors of the current nested-branch quantified-alternation `str` rows:
  - `module-compile-numbered-quantified-alternation-nested-branch-cold-bytes`
  - `module-search-numbered-quantified-alternation-nested-branch-lower-bound-inner-branch-warm-bytes`
  - `pattern-fullmatch-numbered-quantified-alternation-nested-branch-lower-bound-literal-branch-purged-bytes`
  - `module-compile-named-quantified-alternation-nested-branch-warm-bytes`
  - `module-search-named-quantified-alternation-nested-branch-lower-bound-literal-branch-warm-bytes`
  - `pattern-fullmatch-named-quantified-alternation-nested-branch-second-repetition-mixed-purged-bytes`
- The new rows stay pinned to the existing Python-path public patterns and haystacks for this exact bounded slice:
  - `rb"a((b|c)|de){1,2}d"` through `module.compile`, `module.search(..., b"zzabdzz")`, and `Pattern.fullmatch(b"aded")`;
  - `rb"a(?P<word>(b|c)|de){1,2}d"` through `module.compile`, `module.search(..., b"zzadedzz")`, and `Pattern.fullmatch(b"abded")`.
- `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` treat the six new rows as measured source-tree workloads while keeping the quantified-alternation manifest and the combined report at zero known gaps. Reuse the existing quantified-alternation fully measured assertion path by widening the current representative tuple instead of inventing another benchmark family or another quantified-alternation bytes special case.
- Focused and combined benchmark publications move honestly:
  - `quantified-alternation-boundary` moves from `60` total workloads / `60` measured workloads / `0` known gaps to `66` / `66` / `0`;
  - the combined source-tree report moves from `680` total workloads / `680` measured workloads / `0` known gaps to `686` / `686` / `0`.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes the six new nested-branch bytes rows with `implementation_timing.status == "measured"` through the source-tree shim path; this task does not claim built-native full-suite publication.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/quantified_alternation_boundary.py --report .rebar/tmp/rbr-0582-quantified-alternation-nested-branch-bytes-benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark catch-up only. Do not change correctness fixtures, parity suites, or `reports/correctness/latest.py`.
- Keep the publication on the existing Python-facing source-tree benchmark path. Do not broaden into built-native publication, benchmark-harness refactors, or new adapter modes in this run.
- Add only the directly adjacent bytes mirrors for this nested-branch quantified-alternation pair. Do not broaden into bounded, broader-range, or open-ended quantified-alternation bytes work, conditional bytes work, branch-local-backreference bytes work, backtracking-heavy bytes work, or another benchmark family in this run.

## Notes
- Build on `RBR-0580`.
- 2026-03-18 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `benchmarks/workloads/quantified_alternation_boundary.py` currently contains the six nested-branch quantified-alternation `str` workloads for this exact `{1,2}` slice and none of the planned `-bytes` mirrors;
  - `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently treat `quantified-alternation-boundary` as a fully measured `60`-workload manifest with an `18`-id representative tuple covering the bounded, broader-range, and open-ended quantified-alternation bytes rows only, so the follow-on can stay on the existing fully measured assertion surface instead of inventing another benchmark family;
  - `reports/benchmarks/latest.py` currently publishes `quantified-alternation-boundary` at `60` total workloads / `60` measured workloads / `0` known gaps and the combined source-tree report at `680` / `680` / `0`; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this planning run still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`, so this benchmark follow-on stays sequenced behind `RBR-0580` until parity lands.
- No further quantified-alternation bytes family should be queued ahead of this benchmark catch-up while the nested-branch mixed `str`/`bytes` slice is still missing its source-tree benchmark mirrors.
