# RBR-0576: Catch the bounded quantified-alternation bytes pair up on the benchmark surface

Status: done
Owner: feature-implementation
Created: 2026-03-18

## Goal
- Extend the published source-tree benchmark surface so the exact bounded `{1,2}` quantified-alternation bytes pair expected to be supported by `RBR-0574` produces real `rebar` timings on the existing Python-facing quantified-alternation manifest.

## Deliverables
- `benchmarks/workloads/quantified_alternation_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/quantified_alternation_boundary.py` adds only these six bytes mirrors of the current bounded quantified-alternation `str` rows:
  - `module-compile-numbered-quantified-alternation-cold-bytes`
  - `module-search-numbered-quantified-alternation-lower-bound-warm-bytes`
  - `pattern-fullmatch-numbered-quantified-alternation-second-repetition-purged-bytes`
  - `module-compile-named-quantified-alternation-warm-bytes`
  - `module-search-named-quantified-alternation-second-repetition-warm-bytes`
  - `pattern-fullmatch-named-quantified-alternation-lower-bound-purged-bytes`
- The new rows stay pinned to the existing Python-path public patterns and haystacks for this exact bounded slice:
  - `rb"a(b|c){1,2}d"` through `module.compile`, `module.search(..., b"zzacdz")`, and `Pattern.fullmatch(b"abcd")`;
  - `rb"a(?P<word>b|c){1,2}d"` through `module.compile`, `module.search(..., b"zzacbdzz")`, and `Pattern.fullmatch(b"abd")`.
- `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` treat the six new rows as measured source-tree workloads while keeping the quantified-alternation manifest and the combined report at zero known gaps. Reuse the existing quantified-alternation bytes special-case assertions by widening them from the current broader-range plus open-ended bytes set to the bounded plus broader-range plus open-ended bytes set; do not introduce another benchmark family or another quantified-alternation bytes special case.
- Focused and combined benchmark publications move honestly:
  - `quantified-alternation-boundary` moves from `54` total workloads / `54` measured workloads / `0` known gaps to `60` / `60` / `0`;
  - the combined source-tree report moves from `674` total workloads / `674` measured workloads / `0` known gaps to `680` / `680` / `0`.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes the six new bounded bytes rows with `implementation_timing.status == "measured"` through the source-tree shim path; this task does not claim built-native full-suite publication.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/quantified_alternation_boundary.py --report .rebar/tmp/rbr-0576-quantified-alternation-bounded-bytes-benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark catch-up only. Do not change correctness fixtures, parity suites, or `reports/correctness/latest.py`.
- Keep the publication on the existing Python-facing source-tree benchmark path. Do not broaden into built-native publication, benchmark-harness refactors, or new adapter modes in this run.
- Add only the directly adjacent bytes mirrors for this bounded quantified-alternation pair. Do not broaden into broader-range quantified-alternation bytes work, open-ended quantified-alternation bytes work, nested-branch bytes work, conditional bytes work, backtracking-heavy bytes work, or another benchmark family in this run.

## Notes
- Build on `RBR-0574`.
- 2026-03-18 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `benchmarks/workloads/quantified_alternation_boundary.py` currently contains the six bounded quantified-alternation `str` workloads for this exact `{1,2}` slice and already carries the twelve broader-range and open-ended bytes mirrors, but it still contains no bounded `-bytes` rows for the same numbered and named pair;
  - `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently reserve the quantified-alternation bytes special case for the twelve broader-range and open-ended bytes workload ids only, so the bounded bytes catch-up can stay on the existing manifest and special-case test path instead of inventing another benchmark surface;
  - `reports/benchmarks/latest.py` currently publishes `quantified-alternation-boundary` at `54` total workloads / `54` measured workloads / `0` known gaps and the combined source-tree report at `674` / `674` / `0`; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this planning run still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`, so this benchmark follow-on stays sequenced behind `RBR-0574` until parity lands.
- No further quantified-alternation bytes family should be queued ahead of this benchmark catch-up while the bounded mixed `str`/`bytes` slice is still missing its source-tree benchmark mirrors.

## Completion
- Added the six bounded quantified-alternation `bytes` rows on `benchmarks/workloads/quantified_alternation_boundary.py` and widened the existing quantified-alternation `bytes` representative assertions instead of introducing a new benchmark family or a second special case.
- Regenerated `reports/benchmarks/latest.py`; the tracked publication now shows `quantified-alternation-boundary` at `60` total / `60` measured / `0` known gaps and the combined source-tree report at `680` total / `680` measured / `0` known gaps.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/quantified_alternation_boundary.py --report .rebar/tmp/rbr-0576-quantified-alternation-bounded-bytes-benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`
