# RBR-0424: Catch bounded two-arm conditional callable-replacement benchmarks up with the new slice

Status: ready
Owner: feature-implementation
Created: 2026-03-15

## Goal
- Refresh the published benchmark surface so the bounded two-arm conditional callable-replacement workflows already live behind `rebar._rebar` produce real Python-path timings on the existing `conditional_group_exists_boundary.py` manifest instead of lingering as a stale gap-style anchor.

## Deliverables
- `benchmarks/workloads/conditional_group_exists_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- The existing `pattern-subn-callable-named-conditional-group-exists-replacement-purged-gap` anchor on `benchmarks/workloads/conditional_group_exists_boundary.py` is caught up into the bounded callable slice by publishing only the minimal four measured Python-path rows needed for `a(b)?c(?(1)d|e)` and `a(?P<word>b)?c(?(word)d|e)` across module and compiled-`Pattern` `sub()` / `subn()` entrypoints; do not fork a new benchmark family.
- `reports/benchmarks/latest.py` records real `rebar` timings for one numbered present-capture callback path, one numbered absent-capture count-limited path, one named present-capture callback path, and one named absent-capture count-limited path through the existing `callable_match_group` helper shape, while leaving only the adjacent replacement-template row `module-sub-template-numbered-conditional-group-exists-replacement-warm-gap` explicit on `conditional-group-exists-boundary`.
- The shared benchmark expectations in `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` stay on the consolidated source-tree benchmark surfaces, reflect the enlarged measured callable slice on `conditional-group-exists-boundary`, and preserve source-tree-shim publication semantics for the full combined report.
- Verification passes with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_python_benchmark_manifest_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/rbr-0424-conditional-callable-bench.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0423`; do not add new regex or callback execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the consolidated source-tree benchmark assertions instead of reviving manifest-specific benchmark tests.
- Do not silently benchmark Python-only fallback behavior if the corresponding callable-replacement slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0423`, `RBR-0421`, `RBR-0425`, and the existing `conditional_group_exists_boundary.py` benchmark surface.
- A targeted manifest rerun in this checkout already reports `50` total workloads, `49` measured workloads, and only the adjacent template row still unimplemented; this task should turn that live callable support into published rows rather than reopening correctness.
- Once this benchmark catch-up drains, the next bounded follow-on is the adjacent conditional replacement-template correctness publication slice anchored by `module-sub-template-numbered-conditional-group-exists-replacement-warm-gap`.
