# RBR-0200: Catch bounded nested two-arm conditional replacement benchmarks up with the new slice

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published benchmark surface so the bounded nested two-arm conditional replacement workflows supported by `RBR-0199` produce real `rebar` timings before quantified replacement-conditioned conditionals, branch-local-backreference arms, or broader backtracking reopen the correctness frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/conditional_group_exists_boundary.json`
- `tests/benchmarks/test_conditional_group_exists_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness updates the existing `conditional_group_exists_boundary` manifest to exercise only the bounded nested replacement workflows already supported by `RBR-0199`, anchored by a new numbered `module.sub()` or `module.subn()` row for `a(b)?c(?(1)(?(1)d|e)|f)` and any directly adjacent numbered or named companion rows needed to publish that exact slice cleanly.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported nested two-arm conditional replacement workflows while leaving replacement templates that read captures, callable replacements, quantified repeats, deeper nesting, branch-local backreferences, and broader backtracking shapes explicit as known gaps instead of silently omitting them.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0199`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0199`.
- Keep this slice in the existing `conditional_group_exists_boundary` manifest rather than inventing a second benchmark family for the same bounded two-arm conditional surface.
- This task exists so the queue does not reach bounded nested two-arm conditional replacement parity and then leave that newly supported slice absent from benchmark reporting.
