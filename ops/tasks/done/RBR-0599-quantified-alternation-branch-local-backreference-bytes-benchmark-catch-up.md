# RBR-0599: Catch the quantified-alternation branch-local-backreference bytes pair up on the benchmark surface

Status: done
Owner: feature-implementation
Created: 2026-03-18

## Goal
- Extend the published source-tree benchmark surface so the exact bounded `{1,2}` quantified-alternation branch-local-backreference bytes pair expected to be supported by `RBR-0597` produces real `rebar` timings on the existing Python-facing quantified-alternation manifest.

## Deliverables
- `benchmarks/workloads/quantified_alternation_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/quantified_alternation_boundary.py` adds only these six bytes mirrors of the current quantified-alternation branch-local-backreference `str` rows:
  - `module-search-numbered-quantified-alternation-branch-backref-cold-bytes`
  - `module-compile-numbered-quantified-alternation-branch-backref-cold-bytes`
  - `pattern-fullmatch-numbered-quantified-alternation-branch-backref-second-repetition-purged-bytes`
  - `module-compile-named-quantified-alternation-branch-backref-warm-bytes`
  - `module-search-named-quantified-alternation-branch-backref-lower-bound-c-branch-warm-bytes`
  - `pattern-fullmatch-named-quantified-alternation-branch-backref-second-repetition-purged-bytes`
- The new rows stay pinned to the existing Python-path public patterns and haystacks for this exact bounded slice:
  - `rb"a((b|c)\\2){1,2}d"` through `module.search(..., b"zzabbdzz")`, `module.compile`, and `Pattern.fullmatch(b"abbbbd")`;
  - `rb"a(?P<outer>(?P<inner>b|c)(?P=inner)){1,2}d"` through `module.compile`, `module.search(..., b"zzaccdzz")`, and `Pattern.fullmatch(b"accccd")`.
- `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` treat the six new rows as measured source-tree workloads while keeping the quantified-alternation manifest and the combined report at zero known gaps. Reuse the existing quantified-alternation fully measured assertion path by widening the current representative tuple instead of inventing another benchmark family or another quantified-alternation bytes special case.
- Focused and combined benchmark publications move honestly:
  - `quantified-alternation-boundary` moves from `78` total workloads / `78` measured workloads / `0` known gaps to `84` / `84` / `0`;
  - the combined source-tree report moves from `698` total workloads / `698` measured workloads / `0` known gaps to `704` / `704` / `0`.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes the six new branch-local-backreference bytes rows with `implementation_timing.status == "measured"` through the source-tree shim path; this task does not claim built-native full-suite publication.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/quantified_alternation_boundary.py --report .rebar/tmp/rbr-0599-quantified-alternation-branch-local-backreference-bytes-benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark catch-up only. Do not change correctness fixtures, parity suites, or `reports/correctness/latest.py`.
- Keep the publication on the existing Python-facing source-tree benchmark path. Do not broaden into built-native publication, benchmark-harness refactors, or new adapter modes in this run.
- Add only the directly adjacent bytes mirrors for this quantified-alternation branch-local-backreference pair. Do not broaden into bounded, broader-range, open-ended, nested-branch, backtracking-heavy, or conditional quantified-alternation bytes work in this run.

## Notes
- Build on `RBR-0597`.
- 2026-03-18 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `ops/tasks/ready/RBR-0597-quantified-alternation-branch-local-backreference-bytes-parity.md` already pins the exact numbered and named bytes pair for `rb"a((b|c)\\2){1,2}d"` and `rb"a(?P<outer>(?P<inner>b|c)(?P=inner)){1,2}d"`, and its notes already call for a later benchmark follow-on that mirrors the six adjacent `str` rows on the existing quantified-alternation benchmark surface;
  - `benchmarks/workloads/quantified_alternation_boundary.py` currently contains the six quantified-alternation branch-local-backreference `str` workloads for this exact `{1,2}` slice and none of the planned `-bytes` mirrors;
  - `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently treat `quantified-alternation-boundary` as a fully measured `78`-workload manifest whose zero-gap representative tuple already covers the bounded, broader-range, open-ended, nested-branch, conditional, and backtracking-heavy quantified-alternation bytes rows but not this branch-local-backreference bytes pair, so the follow-on can stay on the existing fully measured assertion surface instead of inventing another benchmark family;
  - `reports/benchmarks/latest.py` currently publishes `quantified-alternation-boundary` at `78` total workloads / `78` measured workloads / `0` known gaps and the combined source-tree report at `698` / `698` / `0`; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this planning run still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`, so this benchmark follow-on stays sequenced behind `RBR-0597` until parity lands.
- No further quantified-alternation bytes family should be queued ahead of this benchmark catch-up while the branch-local-backreference mixed `str`/`bytes` slice is still missing its source-tree benchmark mirrors.

## Completion Note
- 2026-03-18: Added the six bounded quantified-alternation branch-local-backreference `bytes` mirror workloads to `benchmarks/workloads/quantified_alternation_boundary.py`, widened the shared zero-gap quantified-alternation expectation tuple to `84` measured / `84` total workloads, and regenerated `reports/benchmarks/latest.py`.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/quantified_alternation_boundary.py --report .rebar/tmp/rbr-0599-quantified-alternation-branch-local-backreference-bytes-benchmarks.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`.
- Published benchmark report now records `quantified-alternation-boundary` at `84` total / `84` measured / `0` known gaps and the combined source-tree report at `704` total / `704` measured / `0` known gaps. `reports/correctness/latest.py` was not changed.
