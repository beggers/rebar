# RBR-0067: Catch literal-alternation benchmarks up with the new branch-selection slice

Status: done
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published benchmark surface so the bounded top-level literal alternation workflows supported by `RBR-0066` produce real `rebar` timings before the queue reopens a new correctness frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/literal_alternation_boundary.json`
- `tests/benchmarks/test_literal_alternation_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness publishes a dedicated literal-alternation manifest that exercises only the bounded top-level branch-selection workflows already supported by `RBR-0066`, such as `ab|ac` through module and compiled-`Pattern` entrypoints.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported literal-alternation workflows while leaving grouped, nested, or otherwise still-unsupported alternation shapes explicit as known gaps instead of silently omitting them.
- The new benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0066`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0064` and `RBR-0066`.
- This task exists so the queue does not reach literal-alternation parity and then leave that newly supported branch-selection surface absent from benchmark reporting.

## Completion
- Added a dedicated `literal-alternation-boundary` benchmark manifest with three measured top-level `ab|ac` workloads and two explicit grouped-alternation gap rows.
- Wired the manifest into the default benchmark suite, added regression coverage in `tests/benchmarks/test_literal_alternation_boundary_benchmarks.py`, and regenerated `reports/benchmarks/latest.json` to publish 76 workloads with 59 measured timings and 17 known gaps.
