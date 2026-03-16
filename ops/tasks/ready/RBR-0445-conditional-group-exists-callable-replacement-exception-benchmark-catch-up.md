# RBR-0445: Catch bounded two-arm conditional callable-replacement exception benchmarks up

Status: ready
Owner: feature-implementation
Created: 2026-03-16

## Goal
- Extend the published benchmark surface so the bounded two-arm conditional callable-replacement exception workflows already published and passing through the Python-facing `rebar` path produce real source-tree timings instead of remaining an explicitly deferred benchmark hole.

## Deliverables
- `benchmarks/workloads/conditional_group_exists_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/conditional_group_exists_boundary.py` grows only by the minimal four measured Python-path rows needed to benchmark the already-published absent-capture callable exception slice for the exact numbered and named patterns `a(b)?c(?(1)d|e)` and `a(?P<word>b)?c(?(word)d|e)`:
  - numbered module `subn()` absent-capture callable path on `zzacezz` with `count=1` through the existing `callable_match_group` helper pinned to group `1`;
  - numbered compiled-`Pattern.subn()` absent-capture callable path on the same haystack and helper;
  - named module `subn()` absent-capture callable path on `zzacezz` with `count=1` through that same helper shape pinned to `word`; and
  - named compiled-`Pattern.subn()` absent-capture callable path on the same haystack and helper.
- Those four rows stay on `benchmarks/workloads/conditional_group_exists_boundary.py` rather than creating a new benchmark family, and they keep the callable helper pinned to the missing capture so the bounded CPython `TypeError` surface remains the thing being timed.
- The shared source-tree benchmark expectations absorb those four new measured exception rows without reviving manifest-local benchmark tests or widening into deeper nested conditional callable shapes, quantified callable slices, branch-local-backreference-conditioned callable flows, or broader backtracking-heavy conditionals.
- `reports/benchmarks/latest.py` records real `rebar` timings for the four new workloads while preserving the current source-tree-shim publication path; the combined report moves to `588` total workloads, `566` measured workloads, and `22` known gaps, while `conditional-group-exists-boundary` moves to `76` measured workloads with `0` known gaps.
- Verification passes with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_python_benchmark_manifest_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/rbr-0445-conditional-callable-exception-bench.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`.

## Constraints
- Keep this task scoped to benchmark catch-up for callable replacement behavior already published in `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py`; do not add new regex, callback, exception, or replacement semantics here.
- Reuse the existing source-tree benchmark adapter/provenance machinery and the consolidated shared benchmark assertions instead of adding another manifest-local benchmark test module or another benchmark family.
- Do not widen beyond the four absent-capture `subn()` exception rows above; later module-boundary compile catch-up and any deeper callable conditional follow-ons stay for later planning.

## Notes
- Build on `RBR-0437`, the current `conditional-group-exists-boundary` benchmark surface, and the already-passing callable correctness/parity slice in `tests/python/test_callable_replacement_parity_suite.py`.
- The current tracked benchmark publication reports `584` total workloads, `562` measured workloads, and `22` known gaps, with `conditional-group-exists-boundary` already fully measured at `72` workloads; this task should widen that same shared benchmark surface rather than reopen correctness or parity.
