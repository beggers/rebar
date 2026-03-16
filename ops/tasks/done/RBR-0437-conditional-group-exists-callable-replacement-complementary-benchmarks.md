# RBR-0437: Expand bounded two-arm conditional callable-replacement benchmarks across complementary entrypoints

Status: done
Owner: feature-implementation
Created: 2026-03-16

## Goal
- Extend the published benchmark surface so the bounded two-arm conditional callable-replacement workflows already live behind `rebar._rebar` cover the remaining minimal cross-entrypoint slice on `conditional_group_exists_boundary.py` instead of stopping at the earlier numbered module and named compiled-`Pattern` subset.

## Deliverables
- `benchmarks/workloads/conditional_group_exists_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/conditional_group_exists_boundary.py` grows only by the minimal four measured Python-path rows needed to complement the already-published numbered module and named compiled-`Pattern` callable rows on the bounded two-arm conditional family:
  - numbered compiled-`Pattern.sub()` present-capture callable path for `a(b)?c(?(1)d|e)` through the existing `callable_match_group` helper;
  - numbered compiled-`Pattern.subn()` first-match-only companion for the same numbered pattern and helper on `zzabcdacezz`;
  - named module `sub()` present-capture callable path for `a(?P<word>b)?c(?(word)d|e)` through that same helper shape; and
  - named module `subn()` first-match-only companion for the same named pattern and helper on `zzabcdacezz`.
- The new rows reuse `benchmarks/workloads/conditional_group_exists_boundary.py` rather than creating a new benchmark family, and they stay aligned with the already-published callable cases in `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py`.
- `reports/benchmarks/latest.py` records real `rebar` timings for those four workloads while preserving the current source-tree-shim publication path; the combined report moves to `576` total workloads, `554` measured workloads, and `22` known gaps, while `conditional-group-exists-boundary` moves to `64` measured workloads with `0` known gaps.
- The shared source-tree benchmark expectations in `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` absorb the four new measured rows without reviving manifest-local benchmark tests or widening the slice beyond the complementary entrypoints above.
- Verification passes with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_python_benchmark_manifest_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/rbr-0437-conditional-callable-bench.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0423`; do not add new regex or callback execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the consolidated source-tree benchmark assertions instead of reviving manifest-specific benchmark tests.
- Do not widen beyond the four companion rows above; callable exception probes on absent first matches and broader quantified or nested replacement-conditioned follow-ons stay for later planning.

## Notes
- Build on `RBR-0424`, `RBR-0423`, and the existing `conditional_group_exists_boundary.py` benchmark surface.
- The current tracked benchmark publication reports `572` total workloads, `550` measured workloads, `22` known gaps, and `60` measured workloads with `0` known gaps for `conditional-group-exists-boundary`; this task should extend that same benchmark boundary rather than reopen correctness.

## Completion Notes
- Added the four complementary callable rows on `benchmarks/workloads/conditional_group_exists_boundary.py`: numbered compiled-`Pattern` `sub()` / `subn()` plus named module `sub()` / `subn()` for the bounded two-arm conditional replacement family.
- Updated the shared source-tree benchmark expectations so the minimal conditional callable-replacement slice now asserts the full eight-row cross-entrypoint matrix.
- Regenerated the tracked benchmark publication in `reports/benchmarks/latest.py`; the tracked report now shows `576` total workloads, `554` measured workloads, `22` known gaps, and `64` measured workloads with `0` known gaps for `conditional-group-exists-boundary`.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_python_benchmark_manifest_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/rbr-0437-conditional-callable-bench.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`.
