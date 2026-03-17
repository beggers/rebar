# RBR-0519: Catch the nested broader-range wider-ranged-repeat grouped backtracking-heavy bytes pair up on the benchmark surface

Status: done
Owner: feature-implementation
Created: 2026-03-17

## Goal
- Extend the published source-tree benchmark surface so the exact nested broader `{1,4}` grouped backtracking-heavy bytes pair already supported by `RBR-0518` produces real `rebar` timings on the existing Python-facing wider-ranged-repeat manifest before the next nested broader grouped bytes slice reopens correctness work.

## Deliverables
- `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.py` adds only these seven bytes mirrors of the current nested broader grouped backtracking-heavy `str` rows:
  - `module-compile-numbered-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-cold-bytes`
  - `module-search-numbered-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-lower-bound-b-branch-warm-bytes`
  - `pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-second-repetition-b-then-bc-purged-bytes`
  - `pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-fourth-repetition-mixed-purged-bytes`
  - `module-compile-named-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-warm-bytes`
  - `module-search-named-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-lower-bound-bc-branch-warm-bytes`
  - `pattern-fullmatch-named-wider-ranged-repeat-group-nested-broader-range-backtracking-heavy-second-repetition-bc-then-b-purged-bytes`
- The new rows stay pinned to the existing Python-path public patterns and haystacks for this exact bounded slice:
  - `rb"a(((bc|b)c){1,4})d"` through `module.compile`, `module.search(..., b"zzabcdzz")`, `Pattern.fullmatch(b"abcbccd")`, and `Pattern.fullmatch(b"abcbccbccbcd")`;
  - `rb"a(?P<outer>((bc|b)c){1,4})d"` through `module.compile`, `module.search(..., b"zzabccdzz")`, and `Pattern.fullmatch(b"abccbcd")`.
- `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` treat the seven new rows as measured source-tree workloads while keeping the wider-ranged manifest and combined report at zero known gaps.
- Focused and combined benchmark publications move honestly:
  - `wider-ranged-repeat-quantified-group-boundary` moves from `74` total workloads / `74` measured workloads / `0` known gaps to `81` / `81` / `0`;
  - the combined source-tree report moves from `600` total workloads / `600` measured workloads / `0` known gaps to `607` / `607` / `0`.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes the seven new bytes rows with `implementation_timing.status == "measured"` through the source-tree shim path; this task does not claim built-native full-suite publication.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.py --report .rebar/tmp/rbr-0519-nested-broader-range-backtracking-heavy-bytes-benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark catch-up only. Do not change correctness fixtures, parity suites, or `reports/correctness/latest.py`.
- Keep the publication on the existing Python-facing source-tree benchmark path. Do not broaden into built-native publication, benchmark-harness refactors, or new adapter modes in this run.
- Add only the directly adjacent bytes mirrors for this nested broader grouped backtracking-heavy pair. Do not broaden into the next nested broader bytes correctness slice, open-ended repeats, or another benchmark family.

## Notes
- Build on `RBR-0518`.
- 2026-03-17 feature-planning probes confirm this task is not stale:
  - `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.py` currently contains only the seven `-str` workload ids for this nested broader grouped backtracking-heavy slice and no `-bytes` mirrors;
  - `reports/benchmarks/latest.py` currently publishes `wider-ranged-repeat-quantified-group-boundary` at `74` total workloads / `74` measured workloads / `0` known gaps and the combined source-tree report at `600` total workloads / `600` measured workloads / `0` known gaps; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes now show both target bytes patterns compile and search successfully through `rebar`, so these benchmark rows should measure rather than reopen a runtime gap.
- The surviving follow-on after this task is `RBR-0520`, which should publish the nested broader `{1,4}` grouped-alternation bytes pair on the existing wider-ranged-repeat correctness/parity path before nested broader grouped-conditionals or benchmark catch-up broaden that family.

## Completion
- Added only the seven bytes mirrors for the nested broader `{1,4}` grouped backtracking-heavy numbered/named pair on `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.py`.
- Updated the wider-ranged source-tree benchmark expectations and focused tests so the new bytes rows are treated as measured and the nested grouped backtracking-heavy shape now requires the expanded row set.
- Verified `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed with `32` tests and `612` subtests.
- Verified the narrowed publication at `.rebar/tmp/rbr-0519-nested-broader-range-backtracking-heavy-bytes-benchmarks.py` reported `81` total workloads / `81` measured workloads / `0` known gaps.
- Regenerated the tracked publication at `reports/benchmarks/latest.py` and verified the tracked artifact now reports `607` total workloads / `607` measured workloads / `0` known gaps overall, with `wider-ranged-repeat-quantified-group-boundary` at `81` / `81` / `0` and all seven new bytes rows publishing `implementation_timing.status == "measured"`.
