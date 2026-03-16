# RBR-0443: Catch bounded quantified alternation-heavy conditional replacement benchmarks up with the new slice

Status: ready
Owner: feature-implementation
Created: 2026-03-16

## Goal
- Extend the published benchmark surface so the bounded quantified alternation-heavy conditional replacement workflows already supported by `RBR-0441` produce real Python-path `rebar` timings on `conditional_group_exists_boundary.py` before the remaining callable-exception benchmark gap or deeper replacement-conditioned follow-ons reopen the frontier.

## Deliverables
- `benchmarks/workloads/conditional_group_exists_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/conditional_group_exists_boundary.py` grows only by the minimal eight measured Python-path rows needed to publish the bounded numbered and named quantified alternation-heavy conditional replacement slice already supported by `RBR-0441` across module and compiled-`Pattern` `sub()` / `subn()` entrypoints for `a(b)?c(?(1)(de|df)|(eg|eh)){2}` and `a(?P<word>b)?c(?(word)(de|df)|(eg|eh)){2}`.
- The new rows reuse `benchmarks/workloads/conditional_group_exists_boundary.py` rather than creating a new benchmark family, and they stay aligned with the already-published cases in `tests/conformance/fixtures/conditional_group_exists_quantified_alternation_replacement_workflows.py`.
- `reports/benchmarks/latest.py` records real `rebar` timings for those eight workloads while preserving the current source-tree-shim publication path; the combined report moves to `584` total workloads, `562` measured workloads, and `22` known gaps, while `conditional-group-exists-boundary` moves to `72` measured workloads with `0` known gaps.
- The shared source-tree benchmark expectations in `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` absorb the eight new measured rows without reviving manifest-local benchmark tests or widening beyond the bounded `{2}` alternation-heavy replacement slice above.
- Verification passes with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_python_benchmark_manifest_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/rbr-0443-conditional-quantified-alternation-replacement-bench.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0441`; do not add new regex or replacement semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the consolidated source-tree benchmark assertions instead of reviving manifest-specific benchmark tests.
- Do not widen beyond the eight rows above; leave callable-exception probes on absent first matches and deeper replacement-conditioned follow-ons for later planning.

## Notes
- Build on `RBR-0441`, `RBR-0439`, and the existing `conditional_group_exists_boundary.py` benchmark surface.
- The current tracked benchmark publication reports `576` total workloads, `554` measured workloads, `22` known gaps, and `64` measured workloads with `0` known gaps for `conditional-group-exists-boundary`; this task should extend that same benchmark boundary rather than reopen correctness.
