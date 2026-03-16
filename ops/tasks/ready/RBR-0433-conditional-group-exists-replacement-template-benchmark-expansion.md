# RBR-0433: Expand bounded two-arm conditional replacement-template benchmarks

Status: ready
Owner: feature-implementation
Created: 2026-03-16

## Goal
- Extend the published benchmark surface so the bounded two-arm conditional replacement-template workflows already live behind `rebar._rebar` cover the rest of the minimal cross-entrypoint template slice on `conditional_group_exists_boundary.py` instead of stopping at one numbered `module.sub()` row.

## Deliverables
- `benchmarks/workloads/conditional_group_exists_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/conditional_group_exists_boundary.py` grows only by the minimal three measured Python-path rows needed to complement the already-published numbered `module.sub()` replacement-template row on the bounded two-arm conditional family:
  - numbered `module.subn()` absent-capture template path for `a(b)?c(?(1)d|e)` with `\\1x`;
  - named compiled-`Pattern.sub()` present-capture template path for `a(?P<word>b)?c(?(word)d|e)` with `\\g<word>x`; and
  - named compiled-`Pattern.subn()` absent-capture template path for the same named pattern and template.
- The new rows reuse `benchmarks/workloads/conditional_group_exists_boundary.py` rather than creating a new benchmark family, and they stay aligned with the already-published cases in `tests/conformance/fixtures/conditional_group_exists_replacement_template_workflows.py`.
- `reports/benchmarks/latest.py` records real `rebar` timings for those three workloads while preserving the current source-tree-shim publication path; the combined report moves to `568` total workloads, `546` measured workloads, and `22` known gaps, while `conditional-group-exists-boundary` moves to `56` measured workloads with `0` known gaps.
- The shared source-tree benchmark expectations in `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` absorb the three new measured rows without reviving manifest-local benchmark tests or widening the slice beyond the minimal companion entrypoints above.
- Verification passes with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_python_benchmark_manifest_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/rbr-0433-conditional-template-bench.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0430`; do not add new regex or replacement-template semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the consolidated source-tree benchmark assertions instead of reviving manifest-specific benchmark tests.
- Do not widen beyond the three companion rows above; leave the complementary named module and numbered compiled-`Pattern` template entrypoints for later planning work once this minimal slice lands.

## Notes
- Build on `RBR-0431`, `RBR-0430`, `RBR-0426`, and the existing `conditional_group_exists_boundary.py` benchmark surface.
- `RBR-0431`'s completion note and the fixture-backed correctness manifest already anchor these exact workflows on the shared conditional replacement-template path.
- The current tracked benchmark publication reports `565` total workloads, `543` measured workloads, `22` known gaps, and `53` measured workloads on `conditional-group-exists-boundary`; this task should extend that same benchmark boundary rather than reopen correctness.
