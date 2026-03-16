# RBR-0435: Expand bounded two-arm conditional replacement-template benchmarks across complementary entrypoints

Status: ready
Owner: feature-implementation
Created: 2026-03-16

## Goal
- Extend the published benchmark surface so the bounded two-arm conditional replacement-template workflows already live behind `rebar._rebar` cover the remaining minimal cross-entrypoint slice on `conditional_group_exists_boundary.py` instead of stopping at the earlier numbered module and named compiled-`Pattern` subset.

## Deliverables
- `benchmarks/workloads/conditional_group_exists_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/conditional_group_exists_boundary.py` grows only by the minimal four measured Python-path rows needed to complement the already-published numbered module and named compiled-`Pattern` replacement-template rows on the bounded two-arm conditional family:
  - numbered compiled-`Pattern.sub()` present-capture template path for `a(b)?c(?(1)d|e)` with `\\1x`;
  - numbered compiled-`Pattern.subn()` absent-capture template path for the same numbered pattern and template;
  - named module `sub()` present-capture template path for `a(?P<word>b)?c(?(word)d|e)` with `\\g<word>x`; and
  - named module `subn()` absent-capture template path for the same named pattern and template.
- The new rows reuse `benchmarks/workloads/conditional_group_exists_boundary.py` rather than creating a new benchmark family, and they stay aligned with the already-published numbered and named cases in `tests/conformance/fixtures/conditional_group_exists_replacement_template_workflows.py`.
- `reports/benchmarks/latest.py` records real `rebar` timings for those four workloads while preserving the current source-tree-shim publication path; the combined report moves to `572` total workloads, `550` measured workloads, and `22` known gaps, while `conditional-group-exists-boundary` moves to `60` measured workloads with `0` known gaps.
- The shared source-tree benchmark expectations in `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` absorb the four new measured rows without reviving manifest-local benchmark tests or widening the slice beyond the complementary entrypoints above.
- Verification passes with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_python_benchmark_manifest_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/rbr-0435-conditional-template-bench.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0430`; do not add new regex or replacement-template semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the consolidated source-tree benchmark assertions instead of reviving manifest-specific benchmark tests.
- Do not widen beyond the four companion rows above; leave callable-replacement expansion and any deeper conditional replacement-conditioned benchmark work for later planning.

## Notes
- Build on `RBR-0433`, `RBR-0431`, `RBR-0430`, and the existing `conditional_group_exists_boundary.py` benchmark surface.
- The current tracked benchmark publication reports `568` total workloads, `546` measured workloads, `22` known gaps, and `56` measured workloads on `conditional-group-exists-boundary`; this task should extend that same benchmark boundary rather than reopen correctness.
