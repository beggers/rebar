# RBR-0450: Republish the anchored module.compile benchmark rows as measured source-tree timings

Status: done
Owner: feature-implementation
Created: 2026-03-16

## Goal
- Catch the existing `module.compile("^abc$")` benchmark rows up on the shared `module-boundary` Python-path surface now that `RBR-0449` landed public compile parity for that exact anchored `str` pattern.

## Deliverables
- `reports/benchmarks/latest.py`
- `tests/benchmarks/benchmark_expectations.py`

## Acceptance Criteria
- The existing `module-compile-literal-{cold,warm,purged}` workloads in `benchmarks/workloads/module_boundary.py` remain the only scope of this catch-up and publish real `rebar` source-tree timings instead of `status == "unimplemented"`.
- `reports/benchmarks/latest.py` is regenerated honestly and moves the combined benchmark summary from `588` workloads with `566` measured / `22` known gaps to `588` workloads with `569` measured / `19` known gaps, while the `module-boundary` manifest summary shows `8` measured workloads and `0` known gaps.
- The shared source-tree benchmark expectations stay aligned with the republished scorecard. If `tests/benchmarks/benchmark_expectations.py` already matches the regenerated output, keep its structure unchanged instead of adding another module-specific wrapper.
- Verification passes with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/module_boundary.py --report .rebar/tmp/rbr-0450-module-boundary.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`.

## Constraints
- Keep the run benchmark-publication only. Do not widen `benchmarks/workloads/module_boundary.py`, touch unrelated benchmark families, or fold the verbose compile regression follow-on into this task.
- Prefer report and expectation refresh over implementation work: direct inspection in the current checkout already shows the single-manifest `module-boundary` rerun measuring all eight workloads, so only change code if the full combined publication exposes a concrete harness mismatch.

## Notes
- 2026-03-16 planning probe: `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/module_boundary.py --report .rebar/tmp/rbr-0450-probe.py` completed with `8` measured workloads and `0` known gaps, and the probe report flipped `module-compile-literal-cold`, `module-compile-literal-warm`, and `module-compile-literal-purged` to `status == "measured"`.
- After this benchmark catch-up, the next bounded public compile slice is the verbose regression pattern already published as `regression-module-compile-verbose-purged` in `benchmarks/workloads/regression_matrix.py`; planning has reserved `RBR-0453` to publish that correctness anchor on the shared `module-workflow` surface before parity or benchmark catch-up reopen the compile frontier.
- Completed 2026-03-16: regenerated `reports/benchmarks/latest.py`, which flipped the tracked `module-compile-literal-{cold,warm,purged}` rows in `module-boundary` from `unimplemented` to measured source-tree timings without widening the benchmark surface.
- Verified from the tracked report artifact: the combined summary is now `588` total workloads with `569` measured and `19` known gaps, and `module-boundary` is now `8` workloads with `8` measured and `0` known gaps.
- `tests/benchmarks/benchmark_expectations.py` already matched the refreshed publication and remained unchanged.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/module_boundary.py --report .rebar/tmp/rbr-0450-module-boundary.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`.
