# RBR-0588: Catch the quantified-alternation backtracking-heavy bytes pair up on the benchmark surface

Status: done
Owner: feature-implementation
Created: 2026-03-18

## Goal
- Extend the published source-tree benchmark surface so the exact bounded `{1,2}` quantified-alternation backtracking-heavy bytes pair expected to be supported by `RBR-0586` produces real `rebar` timings on the existing Python-facing quantified-alternation manifest.

## Deliverables
- `benchmarks/workloads/quantified_alternation_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/quantified_alternation_boundary.py` adds only these six bytes mirrors of the current quantified-alternation backtracking-heavy `str` rows:
  - `module-compile-numbered-quantified-alternation-backtracking-heavy-cold-bytes`
  - `module-search-numbered-quantified-alternation-backtracking-heavy-lower-bound-b-branch-warm-bytes`
  - `pattern-fullmatch-numbered-quantified-alternation-backtracking-heavy-lower-bound-bc-branch-purged-bytes`
  - `module-compile-named-quantified-alternation-backtracking-heavy-warm-bytes`
  - `module-search-named-quantified-alternation-backtracking-heavy-lower-bound-bc-branch-warm-bytes`
  - `pattern-fullmatch-named-quantified-alternation-backtracking-heavy-second-repetition-bc-then-b-purged-bytes`
- The new rows stay pinned to the existing Python-path public patterns and haystacks for this exact bounded slice:
  - `rb"a(b|bc){1,2}d"` through `module.compile`, `module.search(..., b"zzabdzz")`, and `Pattern.fullmatch(b"abcd")`;
  - `rb"a(?P<word>b|bc){1,2}d"` through `module.compile`, `module.search(..., b"zzabcdzz")`, and `Pattern.fullmatch(b"abcbd")`.
- `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` treat the six new rows as measured source-tree workloads while keeping the quantified-alternation manifest and the combined report at zero known gaps. Reuse the existing quantified-alternation fully measured assertion path by widening the current representative tuple instead of inventing another benchmark family or another quantified-alternation bytes special case.
- Focused and combined benchmark publications move honestly:
  - `quantified-alternation-boundary` moves from `66` total workloads / `66` measured workloads / `0` known gaps to `72` / `72` / `0`;
  - the combined source-tree report moves from `686` total workloads / `686` measured workloads / `0` known gaps to `692` / `692` / `0`.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes the six new backtracking-heavy bytes rows with `implementation_timing.status == "measured"` through the source-tree shim path; this task does not claim built-native full-suite publication.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/quantified_alternation_boundary.py --report .rebar/tmp/rbr-0588-quantified-alternation-backtracking-heavy-bytes-benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark catch-up only. Do not change correctness fixtures, parity suites, or `reports/correctness/latest.py`.
- Keep the publication on the existing Python-facing source-tree benchmark path. Do not broaden into built-native publication, benchmark-harness refactors, or new adapter modes in this run.
- Add only the directly adjacent bytes mirrors for this quantified-alternation backtracking-heavy pair. Do not broaden into bounded, broader-range, open-ended, or nested-branch quantified-alternation bytes work, conditional bytes work, branch-local-backreference bytes work, or another benchmark family in this run.

## Notes
- Build on `RBR-0586`.
- 2026-03-18 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `benchmarks/workloads/quantified_alternation_boundary.py` currently contains the six quantified-alternation backtracking-heavy `str` workloads for this exact `{1,2}` slice and none of the planned `-bytes` mirrors;
  - `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently treat `quantified-alternation-boundary` as a fully measured `66`-workload manifest with a representative tuple that covers the bounded, broader-range, open-ended, and nested-branch quantified-alternation bytes rows but not this backtracking-heavy bytes pair, so the follow-on can stay on the existing fully measured assertion surface instead of inventing another benchmark family;
  - `reports/benchmarks/latest.py` currently publishes `quantified-alternation-boundary` at `66` total workloads / `66` measured workloads / `0` known gaps and the combined source-tree report at `686` / `686` / `0`; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this planning run still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`, so this benchmark follow-on stays sequenced behind `RBR-0586` until parity lands.
- No further quantified-alternation bytes family should be queued ahead of this benchmark catch-up while the backtracking-heavy mixed `str`/`bytes` slice is still missing its source-tree benchmark mirrors.

## Completion
- 2026-03-18: Added the six bounded `{1,2}` quantified-alternation backtracking-heavy bytes mirrors to [`benchmarks/workloads/quantified_alternation_boundary.py`](../../../benchmarks/workloads/quantified_alternation_boundary.py), widened the shared quantified-alternation fully measured expectation tuple in [`tests/benchmarks/benchmark_expectations.py`](../../../tests/benchmarks/benchmark_expectations.py) from `66` to `72`, and refreshed the shared source-tree benchmark tests so the new bytes rows stay on the existing zero-gap assertion path. Regenerated the published benchmark scorecard at [`reports/benchmarks/latest.py`](../../../reports/benchmarks/latest.py); the tracked report now publishes `quantified-alternation-boundary` at `72` total / `72` measured / `0` known gaps and the combined source-tree report at `692` total / `692` measured / `0` known gaps, with all six new bytes rows recorded at `implementation_timing.status == "measured"`. Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/quantified_alternation_boundary.py --report .rebar/tmp/rbr-0588-quantified-alternation-backtracking-heavy-bytes-benchmarks.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`. `reports/correctness/latest.py` was not changed in this benchmark-only task.
