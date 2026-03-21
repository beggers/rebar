# RBR-0874: Catch up the compiled-pattern module-compile explicit integer-zero boundary pair

Status: done
Owner: feature-implementation
Created: 2026-03-21

## Goal
- Extend the published Python-path `module_boundary.py` benchmark surface with the first adjacent compiled-pattern-first-argument explicit `flags=0` `compile()` pair that the shared `module-workflow-surface` correctness path already publishes, reusing the bounded compiled-pattern `module.compile(...)` support that `RBR-0872` adds on the same owner route instead of widening the benchmark harness again or jumping ahead to bool-false, rejection, or named-group neighbors.

## Pattern Pair
- `re.compile("abc")` through `compile(re.compile("abc"), flags=0)`
- `re.compile(b"abc")` through `compile(re.compile(b"abc"), flags=0)`

## Deliverables
- `benchmarks/workloads/module_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/module_boundary.py` remains the only benchmark manifest for this slice and grows by exactly two compiled-pattern-first-argument explicit integer-zero `module.compile` workloads:
  - add `module-compile-flags-int-zero-warm-str-compiled-pattern`; and
  - add `module-compile-flags-int-zero-purged-bytes-compiled-pattern`.
- Keep those two workloads pinned to the exact already-published module-workflow compiled-pattern integer-zero compile anchors rather than inventing a broader helper family:
  - `module-compile-flags-int-zero-warm-str-compiled-pattern` uses `operation == "module.compile"`, `pattern == "abc"`, `text_model == "str"`, `cache_mode == "warm"`, `timing_scope == "module-helper-call"`, `flags == 0`, `kwargs == {"flags": 0}`, an explicit compiled-pattern-first-argument marker, and no `expected_exception`;
  - `module-compile-flags-int-zero-purged-bytes-compiled-pattern` uses `operation == "module.compile"`, `pattern == "abc"`, `text_model == "bytes"`, `cache_mode == "purged"`, `timing_scope == "module-helper-call"`, `flags == 0`, `kwargs == {"flags": 0}`, an explicit compiled-pattern-first-argument marker, and no `expected_exception`;
  - anchor the two workloads to `workflow-module-compile-flags-int-zero-str-compiled-pattern` and `workflow-module-compile-flags-int-zero-bytes-compiled-pattern`;
  - keep the explicit integer-zero keyword carrier distinct from the literal default pair that `RBR-0872` adds and from the bool-false, IGNORECASE, or named-group neighbors; and
  - do not widen into NOFLAG spellings, bool-false carriers, compile rejection rows, named-group compile rows, another benchmark manifest, or unrelated benchmark-harness churn in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking another compiled-pattern helper benchmark suite:
  - add focused contract coverage for the bounded compiled-pattern `module.compile(..., flags=0)` pair, proving the rows round-trip through manifest loading, callback construction, internal probe execution, and correctness-anchor mapping while keeping the first-argument compilation outside the timed callback and routing the explicit keyword carrier through the timed helper call;
  - update the module-boundary manifest expectations from `26` measured workloads to `28`, still with `0` known gaps on that manifest once `RBR-0872` has landed;
  - keep the manifest on the existing `post-parser-workflows` / combined-boundary path and wire the two new workloads to the exact correctness case ids listed above;
  - update the combined publication totals from `854` total / `854` measured / `0` known gaps across `30` manifests to `856` / `856` / `0` across the same `30` manifests;
  - update `REPORT["summary"]["module_workloads"]` from `846` to `848`;
  - keep `REPORT["summary"]["regression_workloads"]` at `8`; and
  - keep the built-native smoke manifest set unchanged in this run.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["module-boundary"]` moves from `selected_workload_count == 26`, `measured_workloads == 26`, and `known_gap_count == 0` to `28`, `28`, and `0`;
  - the two new compiled-pattern-first-argument explicit integer-zero `module.compile` workloads publish real `rebar` timings with `status == "measured"`, not placeholders; and
  - the tracked report exposes those exact workload ids on the existing module-boundary benchmark surface.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/module_boundary.py --report .rebar/tmp/rbr-0874-compiled-pattern-module-compile-int-zero-boundary.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not widen the correctness surface or change Rust/Python regex behavior just to support a larger compiled-pattern compile family.
- Reuse the existing `module_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another compiled-pattern compile benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.
- Assume the bounded compiled-pattern `module.compile(...)` support from `RBR-0872` is already in place; if that prerequisite has not landed yet, stop and finish `RBR-0872` first instead of widening this task.

## Notes
- `RBR-0874` is the next available feature task id in the current checkout:
  - `RBR-0872` is already occupied by the ready feature task in `ops/tasks/ready/`;
  - `RBR-0873` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0872` on the same `module-workflow-surface` frontier so the first explicit integer-zero compiled-pattern `module.compile()` keyword-carried pair catches up on the existing Python-path `module_boundary.py` surface before bool-false carriers, compile rejection neighbors, named-group compile publication, or another benchmark family reopens the queue.
- 2026-03-21 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier but still absent from the benchmark surface:
  - `tests/conformance/fixtures/module_workflow_surface.py` already publishes the exact adjacent correctness anchors `workflow-module-compile-flags-int-zero-str-compiled-pattern` and `workflow-module-compile-flags-int-zero-bytes-compiled-pattern`;
  - a direct runtime probe in this run confirmed CPython and `rebar` already agree on the bounded helper behavior for `compile(re.compile("abc"), flags=0)` and `compile(re.compile(b"abc"), flags=0)`, so no Rust or Python regex-behavior prerequisite is missing for this pair;
  - `benchmarks/workloads/module_boundary.py` and `reports/benchmarks/latest.py` currently publish no compiled-pattern explicit integer-zero `module.compile` rows on that owner route; and
  - the acceptance counts above are intentionally written against the immediate post-`RBR-0872` state of `854` total / `854` measured / `0` known gaps overall with `REPORT["summary"]["module_workloads"] == 846` and `REPORT["manifests"]["module-boundary"]` at `26` selected / `26` measured / `0` known gaps.

## Completion
- 2026-03-21: Extended `python/rebar_harness/benchmarks.py` so the shared `module-boundary` owner path accepts only the bounded compiled-pattern-first-argument `module.compile(..., flags=0)` keyword carrier, keeps the first compiled pattern outside the timed callback, and materializes the `flags=0` kwarg inside the timed helper call without reopening bool-false, nonzero-flag, or non-literal neighbors.
- Added `module-compile-flags-int-zero-warm-str-compiled-pattern` and `module-compile-flags-int-zero-purged-bytes-compiled-pattern` to `benchmarks/workloads/module_boundary.py`, and extended `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` with the matching shared anchor/probe/materialization contract plus the updated module-boundary and combined-summary expectations.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/module_boundary.py --report .rebar/tmp/rbr-0874-compiled-pattern-module-compile-int-zero-boundary.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`.
- Confirmed from the tracked `reports/benchmarks/latest.py` diff in this run that `REPORT["manifests"]["module-boundary"]` is now `28` selected / `28` measured / `0` known gaps, that both new workload ids publish `status == "measured"`, and that the combined summary is now `856` total / `856` measured / `0` known gaps with `REPORT["summary"]["module_workloads"] == 848` and `REPORT["summary"]["regression_workloads"] == 8`.
