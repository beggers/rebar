# RBR-0512: Catch broader-range wider-ranged-repeat grouped-conditional bytes benchmarks up with the new slice

Status: done
Owner: feature-implementation
Created: 2026-03-17

## Goal
- Extend the published source-tree benchmark surface so the exact broader `{1,4}` grouped-alternation-plus-conditional bytes pair already supported by `RBR-0510` produces real `rebar` timings on the existing Python-facing wider-ranged-repeat manifest before broader bytes follow-ons reopen the family.

## Deliverables
- `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.py` adds only the six bytes mirrors of the current broader-range grouped-conditional `str` rows, with these workload ids:
  - `module-compile-numbered-wider-ranged-repeat-group-broader-range-conditional-cold-bytes`
  - `module-search-numbered-wider-ranged-repeat-group-broader-range-conditional-absent-warm-bytes`
  - `pattern-fullmatch-numbered-wider-ranged-repeat-group-broader-range-conditional-lower-bound-bc-purged-bytes`
  - `module-compile-named-wider-ranged-repeat-group-broader-range-conditional-warm-bytes`
  - `module-search-named-wider-ranged-repeat-group-broader-range-conditional-upper-bound-mixed-warm-bytes`
  - `pattern-fullmatch-named-wider-ranged-repeat-group-broader-range-conditional-upper-bound-mixed-purged-bytes`
- The new rows stay pinned to the existing Python-path public patterns and haystacks for this exact bounded slice:
  - `rb"a((bc|de){1,4})?(?(1)d|e)"` through `module.compile`, `module.search(..., b"zzaezz")`, and `Pattern.fullmatch(b"abcd")`;
  - `rb"a(?P<outer>(bc|de){1,4})?(?(outer)d|e)"` through `module.compile`, `module.search(..., b"zzabcdedededzz")`, and `Pattern.fullmatch(b"abcdededed")`.
- `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` treat the six new rows as measured source-tree workloads while keeping the wider-ranged manifest and combined report at zero known gaps.
- Focused and combined benchmark publications move honestly:
  - `wider-ranged-repeat-quantified-group-boundary` moves from `62` measured workloads / `0` known gaps to `68` / `0`;
  - the combined source-tree report moves from `588` total workloads / `588` measured workloads / `0` known gaps to `594` / `594` / `0`.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes the six new bytes rows with `implementation_timing.status == "measured"` through the source-tree shim path; this task does not claim built-native full-suite publication.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.py --report .rebar/tmp/rbr-0512-wider-ranged-repeat-conditional-bytes-benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark catch-up only. Do not change correctness fixtures, parity suites, or `reports/correctness/latest.py`.
- Keep the publication on the existing Python-facing source-tree benchmark path. Do not broaden into built-native publication, benchmark-harness refactors, or new adapter modes in this run.
- Add only the directly adjacent bytes mirrors for this grouped-conditional pair. Do not broaden into broader bytes grouped backtracking-heavy rows, nested broader bytes slices, open-ended repeats, or another benchmark family.

## Notes
- Build on `RBR-0510`.
- 2026-03-17 feature-planning probes confirm this task is not stale:
  - `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.py` currently contains only the six `-str` workload ids for this broader-range grouped-conditional slice and no `-bytes` mirrors;
  - `reports/benchmarks/latest.py` currently publishes `wider-ranged-repeat-quantified-group-boundary` at `62` measured workloads / `0` known gaps and the combined source-tree report at `588` total / `588` measured / `0` known gaps.
- The surviving follow-on after this task is `RBR-0513`, which should publish the broader `{1,4}` bytes grouped backtracking-heavy pair on the existing correctness/parity path before bytes parity or benchmark catch-up revisit that family.

## Completion
- Added only the six bytes mirrors for the broader `{1,4}` grouped-conditional rows on `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.py`, keeping the existing Python-path patterns and haystacks unchanged.
- Updated the wider-ranged benchmark expectations and direct benchmark tests so those six `-bytes` ids are treated as measured with zero known gaps, and the manifest-specific combined test now pins the manifest at `68` measured workloads.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.py --report .rebar/tmp/rbr-0512-wider-ranged-repeat-conditional-bytes-benchmarks.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`.
- The tracked `reports/benchmarks/latest.py` artifact now publishes `wider-ranged-repeat-quantified-group-boundary` at `68` measured / `0` gaps and the combined source-tree report at `594` total / `594` measured / `0` gaps, with all six new bytes rows recorded as `status: 'measured'`.
