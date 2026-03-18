# RBR-0593: Catch the quantified-alternation conditional bytes pair up on the benchmark surface

Status: done
Owner: feature-implementation
Created: 2026-03-18

## Goal
- Extend the published source-tree benchmark surface so the exact bounded `{1,2}` quantified-alternation conditional bytes pair expected to be supported by `RBR-0592` produces real `rebar` timings on the existing Python-facing quantified-alternation manifest.

## Deliverables
- `benchmarks/workloads/quantified_alternation_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/quantified_alternation_boundary.py` adds only these six bytes mirrors of the current quantified-alternation conditional `str` rows:
  - `module-compile-numbered-quantified-alternation-conditional-cold-bytes`
  - `module-search-numbered-quantified-alternation-conditional-lower-bound-b-warm-bytes`
  - `pattern-fullmatch-numbered-quantified-alternation-conditional-second-repetition-mixed-purged-bytes`
  - `module-compile-named-quantified-alternation-conditional-warm-bytes`
  - `module-search-named-quantified-alternation-conditional-absent-warm-bytes`
  - `pattern-fullmatch-named-quantified-alternation-conditional-second-repetition-c-purged-bytes`
- The new rows stay pinned to the existing Python-path public patterns and haystacks for this exact bounded slice:
  - `rb"a((b|c){1,2})?(?(1)d|e)"` through `module.compile`, `module.search(..., b"zzabdzz")`, and `Pattern.fullmatch(b"abcd")`;
  - `rb"a(?P<outer>(b|c){1,2})?(?(outer)d|e)"` through `module.compile`, `module.search(..., b"zzaezz")`, and `Pattern.fullmatch(b"accd")`.
- `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` treat the six new rows as measured source-tree workloads while keeping the quantified-alternation manifest and the combined report at zero known gaps. Reuse the existing quantified-alternation fully measured assertion path by widening the current `quantified-alternation-boundary` representative tuple instead of inventing another benchmark family or another quantified-alternation bytes special case.
- Focused and combined benchmark publications move honestly:
  - `quantified-alternation-boundary` moves from `72` total workloads / `72` measured workloads / `0` known gaps to `78` / `78` / `0`;
  - the combined source-tree report moves from `692` total workloads / `692` measured workloads / `0` known gaps to `698` / `698` / `0`.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes the six new conditional bytes rows with `implementation_timing.status == "measured"` through the source-tree shim path; this task does not claim built-native full-suite publication.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/quantified_alternation_boundary.py --report .rebar/tmp/rbr-0593-quantified-alternation-conditional-bytes-benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark catch-up only. Do not change correctness fixtures, parity suites, or `reports/correctness/latest.py`.
- Keep the publication on the existing Python-facing source-tree benchmark path. Do not broaden into built-native publication, benchmark-harness refactors, or new adapter modes in this run.
- Add only the directly adjacent bytes mirrors for this quantified-alternation conditional pair. Do not broaden into bounded, broader-range, open-ended, nested-branch, backtracking-heavy, or branch-local-backreference quantified-alternation bytes work in this run.

## Notes
- Build on `RBR-0592`.
- 2026-03-18 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `ops/tasks/ready/RBR-0592-quantified-alternation-conditional-bytes-parity.md` already pins the exact numbered and named bytes pair for `rb"a((b|c){1,2})?(?(1)d|e)"` and `rb"a(?P<outer>(b|c){1,2})?(?(outer)d|e)"`, and its notes already call for a later benchmark follow-on that mirrors the six adjacent conditional `str` rows on the existing quantified-alternation benchmark surface;
  - `benchmarks/workloads/quantified_alternation_boundary.py` currently contains the six quantified-alternation conditional `str` workloads for this exact `{1,2}` slice and none of the planned `-bytes` mirrors;
  - `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently treat `quantified-alternation-boundary` as a fully measured `72`-workload manifest whose zero-gap representative tuple already covers the bounded, broader-range, open-ended, nested-branch, and backtracking-heavy quantified-alternation bytes rows but not this conditional bytes pair, so the follow-on can stay on the existing zero-gap assertion surface instead of inventing another benchmark family;
  - `reports/benchmarks/latest.py` currently publishes `quantified-alternation-boundary` at `72` total workloads / `72` measured workloads / `0` known gaps and the combined source-tree report at `692` / `692` / `0`; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this planning run still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`, so this benchmark follow-on stays sequenced behind `RBR-0592` until parity lands.
- No further quantified-alternation bytes family should be queued ahead of this benchmark catch-up while the conditional mixed `str`/`bytes` slice is still missing its source-tree benchmark mirrors.

## Completion
- 2026-03-18: Added the six quantified-alternation conditional bytes workload mirrors to `benchmarks/workloads/quantified_alternation_boundary.py`, widened the shared zero-gap quantified-alternation representative tuple, and regenerated `reports/benchmarks/latest.py`.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` (`31 passed, 989 subtests passed`), `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/quantified_alternation_boundary.py --report .rebar/tmp/rbr-0593-quantified-alternation-conditional-bytes-benchmarks.py` (`78` total / `78` measured / `0` known gaps), and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`.
- The tracked published benchmark artifact now shows `quantified-alternation-boundary` at `78` total workloads / `78` measured workloads / `0` known gaps and the combined source-tree report at `698` total workloads / `698` measured workloads / `0` known gaps, with all six new `-bytes` conditional workload rows published as measured through the source-tree shim path.
