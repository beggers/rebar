# RBR-0876: Catch up the compiled-pattern module-compile explicit bool-false boundary pair

Status: ready
Owner: feature-implementation
Created: 2026-03-21

## Goal
- Extend the published Python-path `module_boundary.py` benchmark surface with the first adjacent compiled-pattern-first-argument explicit `flags=False` `compile()` pair that the shared `module-workflow-surface` correctness path already publishes, reusing the bounded compiled-pattern `module.compile(..., flags=0)` benchmark route that `RBR-0874` keeps on the same owner path instead of widening the harness again or jumping ahead to `NOFLAG`, rejection, or named-group neighbors.

## Pattern Pair
- `re.compile("abc")` through `compile(re.compile("abc"), flags=False)`
- `re.compile(b"abc")` through `compile(re.compile(b"abc"), flags=False)`

## Deliverables
- `benchmarks/workloads/module_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/module_boundary.py` remains the only benchmark manifest for this slice and grows by exactly two compiled-pattern-first-argument explicit bool-false `module.compile` workloads:
  - add `module-compile-flags-bool-false-warm-str-compiled-pattern`; and
  - add `module-compile-flags-bool-false-purged-bytes-compiled-pattern`.
- Keep those two workloads pinned to the exact already-published module-workflow compiled-pattern bool-false compile anchors rather than inventing a broader helper family:
  - `module-compile-flags-bool-false-warm-str-compiled-pattern` uses `operation == "module.compile"`, `pattern == "abc"`, `text_model == "str"`, `cache_mode == "warm"`, `timing_scope == "module-helper-call"`, `flags == 0`, `kwargs == {"flags": False}`, an explicit compiled-pattern-first-argument marker, and no `expected_exception`;
  - `module-compile-flags-bool-false-purged-bytes-compiled-pattern` uses `operation == "module.compile"`, `pattern == "abc"`, `text_model == "bytes"`, `cache_mode == "purged"`, `timing_scope == "module-helper-call"`, `flags == 0`, `kwargs == {"flags": False}`, an explicit compiled-pattern-first-argument marker, and no `expected_exception`;
  - anchor the two workloads to `workflow-module-compile-flags-bool-false-str-compiled-pattern` and `workflow-module-compile-flags-bool-false-bytes-compiled-pattern`;
  - keep the explicit bool-false keyword carrier distinct from the adjacent integer-zero pair that `RBR-0874` adds and from `NOFLAG`, IGNORECASE, or named-group neighbors; and
  - do not widen into `NOFLAG` spellings, compile rejection rows, named-group compile rows, another benchmark manifest, or unrelated benchmark-harness churn in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking another compiled-pattern helper benchmark suite:
  - add focused contract coverage for the bounded compiled-pattern `module.compile(..., flags=False)` pair, proving the rows round-trip through manifest loading, callback construction, internal probe execution, and correctness-anchor mapping while keeping the first-argument compilation outside the timed callback and preserving the explicit bool-false keyword carrier through the timed helper call;
  - update the module-boundary manifest expectations from `28` measured workloads to `30`, still with `0` known gaps on that manifest once `RBR-0874` has landed;
  - keep the manifest on the existing `post-parser-workflows` / combined-boundary path and wire the two new workloads to the exact correctness case ids listed above;
  - update the combined publication totals from `856` total / `856` measured / `0` known gaps across `30` manifests to `858` / `858` / `0` across the same `30` manifests;
  - update `REPORT["summary"]["module_workloads"]` from `848` to `850`;
  - keep `REPORT["summary"]["regression_workloads"]` at `8`; and
  - keep the built-native smoke manifest set unchanged in this run.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["module-boundary"]` moves from `selected_workload_count == 28`, `measured_workloads == 28`, and `known_gap_count == 0` to `30`, `30`, and `0`;
  - the two new compiled-pattern-first-argument explicit bool-false `module.compile` workloads publish real `rebar` timings with `status == "measured"`, not placeholders; and
  - the tracked report exposes those exact workload ids on the existing module-boundary benchmark surface.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/module_boundary.py --report .rebar/tmp/rbr-0876-compiled-pattern-module-compile-bool-false-boundary.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not widen the correctness surface or change Rust/Python regex behavior just to support a larger compiled-pattern compile family.
- Reuse the existing `module_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another compiled-pattern compile benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.
- Assume the bounded compiled-pattern `module.compile(..., flags=0)` benchmark route from `RBR-0874` is already in place; if that prerequisite has not landed yet, stop and finish `RBR-0874` first instead of widening this task.

## Notes
- `RBR-0876` is the next available feature task id in the current checkout:
  - `RBR-0874` is already occupied by the ready feature task in `ops/tasks/ready/`;
  - `RBR-0875` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0874` on the same `module-workflow-surface` frontier so the first explicit bool-false compiled-pattern `module.compile()` keyword-carried pair catches up on the existing Python-path `module_boundary.py` surface before `NOFLAG` spellings, compile rejection neighbors, named-group compile publication, or another benchmark family reopens the queue.
- 2026-03-21 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier but still absent from the benchmark surface:
  - `tests/conformance/fixtures/module_workflow_surface.py` already publishes the exact adjacent correctness anchors `workflow-module-compile-flags-bool-false-str-compiled-pattern` and `workflow-module-compile-flags-bool-false-bytes-compiled-pattern`;
  - a direct runtime probe in this run confirmed CPython and `rebar` already agree on the bounded helper behavior for `compile(rebar.compile("abc"), flags=False)` and `compile(rebar.compile(b"abc"), flags=False)`, so no Rust or Python regex-behavior prerequisite is missing for this pair;
  - `benchmarks/workloads/module_boundary.py` and `reports/benchmarks/latest.py` currently publish no compiled-pattern explicit bool-false `module.compile` rows on that owner route; and
  - the acceptance counts above are intentionally written against the immediate post-`RBR-0874` state of `856` total / `856` measured / `0` known gaps overall with `REPORT["summary"]["module_workloads"] == 848` and `REPORT["manifests"]["module-boundary"]` at `28` selected / `28` measured / `0` known gaps.
