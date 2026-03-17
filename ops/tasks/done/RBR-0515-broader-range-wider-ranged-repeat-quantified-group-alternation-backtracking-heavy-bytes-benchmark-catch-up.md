# RBR-0515: Catch the broader-range wider-ranged-repeat grouped backtracking-heavy bytes pair up on the benchmark surface

Status: done
Owner: feature-implementation
Created: 2026-03-17

## Goal
- Extend the published source-tree benchmark surface so the exact broader `{1,4}` grouped backtracking-heavy bytes pair already supported by `RBR-0514` produces real `rebar` timings on the existing Python-facing wider-ranged-repeat manifest before nested broader bytes follow-ons reopen the family.

## Deliverables
- `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.py` adds only these six bytes mirrors of the current broader-range grouped backtracking-heavy `str` rows:
  - `module-compile-numbered-wider-ranged-repeat-group-broader-range-backtracking-heavy-cold-bytes`
  - `module-search-numbered-wider-ranged-repeat-group-broader-range-backtracking-heavy-lower-bound-b-branch-warm-bytes`
  - `pattern-fullmatch-numbered-wider-ranged-repeat-group-broader-range-backtracking-heavy-second-repetition-b-then-bc-purged-bytes`
  - `module-compile-named-wider-ranged-repeat-group-broader-range-backtracking-heavy-warm-bytes`
  - `module-search-named-wider-ranged-repeat-group-broader-range-backtracking-heavy-lower-bound-bc-branch-warm-bytes`
  - `pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-backtracking-heavy-fourth-repetition-mixed-purged-bytes`
- The new rows stay pinned to the existing Python-path public patterns and haystacks for this exact bounded slice:
  - `rb"a((bc|b)c){1,4}d"` through `module.compile`, `module.search(..., b"zzabcdzz")`, and `Pattern.fullmatch(b"abcbccd")`;
  - `rb"a(?P<word>(bc|b)c){1,4}d"` through `module.compile`, `module.search(..., b"zzabccdzz")`, and `Pattern.fullmatch(b"abcbccbccbcd")`.
- `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` treat the six new rows as measured source-tree workloads while keeping the wider-ranged manifest and combined report at zero known gaps.
- Focused and combined benchmark publications move honestly:
  - `wider-ranged-repeat-quantified-group-boundary` moves from `68` measured workloads / `0` known gaps to `74` / `0`;
  - the combined source-tree report moves from `594` total workloads / `594` measured workloads / `0` known gaps to `600` / `600` / `0`.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes the six new bytes rows with `implementation_timing.status == "measured"` through the source-tree shim path; this task does not claim built-native full-suite publication.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.py --report .rebar/tmp/rbr-0515-wider-ranged-repeat-backtracking-heavy-bytes-benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark catch-up only. Do not change correctness fixtures, parity suites, or `reports/correctness/latest.py`.
- Keep the publication on the existing Python-facing source-tree benchmark path. Do not broaden into built-native publication, benchmark-harness refactors, or new adapter modes in this run.
- Add only the directly adjacent bytes mirrors for this grouped backtracking-heavy pair. Do not broaden into nested broader bytes slices, correctness publication, runtime parity follow-ons, open-ended repeats, or another benchmark family.

## Notes
- Build on `RBR-0514`.
- 2026-03-17 feature-planning probes confirm this task is not stale:
  - `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.py` currently contains only the six `-str` workload ids for this broader-range grouped backtracking-heavy slice and no `-bytes` mirrors;
  - `reports/benchmarks/latest.py` currently publishes `wider-ranged-repeat-quantified-group-boundary` at `68` measured workloads / `0` known gaps and the combined source-tree report at `594` total / `594` measured / `0` known gaps; and
  - `RBR-0514` has already converted `rb"a((bc|b)c){1,4}d"` and `rb"a(?P<word>(bc|b)c){1,4}d"` to real Rust-backed behavior on the public `rebar` path, so these benchmark rows should now measure rather than reopen a runtime gap.
- The surviving follow-on after this task is `RBR-0517`, which should publish the nested broader `{1,4}` bytes grouped backtracking-heavy pair on the existing correctness/parity path before bytes parity or benchmark catch-up revisit that family.
- 2026-03-17 feature-implementation: Added the six broader-range grouped backtracking-heavy bytes rows on the existing wider-ranged manifest, updated the source-tree expectation/test hooks, and regenerated `reports/benchmarks/latest.py`. The tracked report now publishes `wider-ranged-repeat-quantified-group-boundary` at `74` measured workloads / `0` known gaps and the combined source-tree suite at `600` total workloads / `600` measured workloads / `0` known gaps. Verification passed with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.py --report .rebar/tmp/rbr-0515-wider-ranged-repeat-backtracking-heavy-bytes-benchmarks.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`.
