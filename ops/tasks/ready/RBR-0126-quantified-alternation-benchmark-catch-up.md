# RBR-0126: Catch bounded quantified-alternation benchmarks up with the new slice

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published benchmark surface so the bounded quantified-alternation workflows supported by `RBR-0125` produce real `rebar` timings before wider alternation-heavy repetition or broader backtracking reopen the correctness frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/quantified_alternation_boundary.json`
- `tests/benchmarks/test_quantified_alternation_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness publishes a dedicated quantified-alternation manifest that exercises only the bounded workflows already supported by `RBR-0125`, such as `a(b|c){1,2}d` and `a(?P<word>b|c){1,2}d`, through module and compiled-`Pattern` entrypoints, including representative lower-bound and second-repetition haystacks.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported quantified-alternation workflows while leaving wider counted ranges, open-ended repeats, nested alternation inside quantified branches, branch-local backreferences inside quantified alternation, conditional combinations, and broader backtracking-heavy shapes explicit as known gaps instead of silently omitting them.
- The new benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0125`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0125`.
- This task exists so the queue does not leave the first quantified-alternation slice measured only in correctness reporting.
