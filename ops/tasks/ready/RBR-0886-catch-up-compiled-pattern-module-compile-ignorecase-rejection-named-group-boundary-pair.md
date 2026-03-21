# RBR-0886: Catch up the compiled-pattern module-compile IGNORECASE rejection named-group boundary pair

Status: ready
Owner: feature-implementation
Created: 2026-03-21

## Goal
- Extend the published Python-path `module_boundary.py` benchmark surface with the first adjacent compiled-pattern-first-argument explicit `flags=IGNORECASE` named-group `compile()` rejection pair that the shared `module-workflow-surface` correctness path already publishes, reusing the bounded compiled-pattern `module.compile(..., flags=...)` expected-exception route on the same owner path instead of reopening `NOFLAG` spellings, another benchmark family, or a deeper runtime prerequisite.

## Pattern Pair
- `re.compile("(?P<word>abc)")` through `compile(re.compile("(?P<word>abc)"), flags=re.IGNORECASE)` rejecting with `ValueError`
- `re.compile(b"(?P<word>abc)")` through `compile(re.compile(b"(?P<word>abc)"), flags=re.IGNORECASE)` rejecting with `ValueError`

## Deliverables
- `benchmarks/workloads/module_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/module_boundary.py` remains the only benchmark manifest for this slice and grows by exactly two compiled-pattern-first-argument explicit `IGNORECASE` named-group `module.compile` rejection workloads:
  - add `module-compile-flags-ignorecase-warm-str-compiled-pattern-named-group`; and
  - add `module-compile-flags-ignorecase-purged-bytes-compiled-pattern-named-group`.
- Keep those two workloads pinned to the exact already-published module-workflow compiled-pattern named-group `IGNORECASE` rejection anchors rather than inventing a broader helper family:
  - `module-compile-flags-ignorecase-warm-str-compiled-pattern-named-group` uses `operation == "module.compile"`, `pattern == "(?P<word>abc)"`, `text_model == "str"`, `cache_mode == "warm"`, `timing_scope == "module-helper-call"`, `flags == 0`, `kwargs == {"flags": 2}`, an explicit compiled-pattern-first-argument marker, and `expected_exception == {"type": "ValueError", "message_substring": "cannot process flags argument with a compiled pattern"}`;
  - `module-compile-flags-ignorecase-purged-bytes-compiled-pattern-named-group` uses `operation == "module.compile"`, `pattern == "(?P<word>abc)"`, `text_model == "bytes"`, `cache_mode == "purged"`, `timing_scope == "module-helper-call"`, `flags == 0`, `kwargs == {"flags": 2}`, an explicit compiled-pattern-first-argument marker, and the same `expected_exception`;
  - anchor the two workloads to `workflow-module-compile-flags-ignorecase-str-compiled-pattern-named-group` and `workflow-module-compile-flags-ignorecase-bytes-compiled-pattern-named-group`;
  - keep the explicit named-group `IGNORECASE` rejection carrier distinct from the adjacent named-group default, integer-zero, and bool-false neighbors that `RBR-0880`, `RBR-0882`, and `RBR-0884` cover, and from `NOFLAG` spellings; and
  - do not widen into `NOFLAG` spellings, literal compile rows, another benchmark manifest, or unrelated benchmark-harness churn in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking another compiled-pattern helper benchmark suite:
  - add focused contract coverage for the bounded compiled-pattern named-group `module.compile(..., flags=IGNORECASE)` rejection pair, proving the rows round-trip through manifest loading, callback construction, internal probe execution, expected-exception handling, and correctness-anchor mapping while keeping the first-argument compilation outside the timed callback and preserving the helper-raised `ValueError` through the shared expected-exception measurement path;
  - update the module-boundary manifest expectations from `38` measured workloads to `40`, still with `0` known gaps on that manifest once `RBR-0884` has landed;
  - keep the manifest on the existing `post-parser-workflows` / combined-boundary path and wire the two new workloads to the exact correctness case ids listed above;
  - update the combined publication totals from `866` total / `866` measured / `0` known gaps across `30` manifests to `868` / `868` / `0` across the same `30` manifests;
  - update `REPORT["summary"]["module_workloads"]` from `858` to `860`;
  - keep `REPORT["summary"]["regression_workloads"]` at `8`; and
  - keep the built-native smoke manifest set unchanged in this run.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["module-boundary"]` moves from `selected_workload_count == 38`, `measured_workloads == 38`, and `known_gap_count == 0` to `40`, `40`, and `0`;
  - the two new compiled-pattern-first-argument explicit `IGNORECASE` named-group `module.compile` rejection workloads publish real `rebar` timings with `status == "measured"` while preserving the expected `ValueError` metadata, not placeholders; and
  - the tracked report exposes those exact workload ids on the existing module-boundary benchmark surface.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/module_boundary.py --report .rebar/tmp/rbr-0886-compiled-pattern-module-compile-ignorecase-rejection-named-group-boundary.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not widen the correctness surface or change Rust/Python regex behavior just to support a larger compiled-pattern compile family.
- Reuse the existing `module_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another compiled-pattern compile benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.
- Assume the bounded compiled-pattern named-group `module.compile(..., flags=False)` benchmark route from `RBR-0884` is already in place; if that prerequisite has not landed yet, stop and finish `RBR-0884` first instead of widening this task.

## Notes
- `RBR-0886` is the next available feature task id in the current checkout:
  - `RBR-0884` is already occupied by the ready feature task in `ops/tasks/ready/`;
  - `RBR-0885` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0884` on the same `module-workflow-surface` frontier so the first explicit named-group `IGNORECASE` compiled-pattern `module.compile()` rejection pair catches up on the existing Python-path `module_boundary.py` surface before `NOFLAG` spellings or another benchmark family reopens the queue.
- 2026-03-21 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier but still absent from the benchmark surface:
  - `tests/conformance/fixtures/module_workflow_surface.py` already publishes the exact adjacent correctness anchors `workflow-module-compile-flags-ignorecase-str-compiled-pattern-named-group` and `workflow-module-compile-flags-ignorecase-bytes-compiled-pattern-named-group`;
  - `tests/python/test_module_workflow_parity_suite.py` already carries the adjacent owner-path parity cases `compiled-pattern-compile-flags-ignorecase-str-named-group` and `compiled-pattern-compile-flags-ignorecase-bytes-named-group`;
  - a direct runtime probe in this run confirmed CPython and `rebar` already agree on `compile(rebar.compile("(?P<word>abc)"), flags=rebar.IGNORECASE)` and `compile(rebar.compile(b"(?P<word>abc)"), flags=rebar.IGNORECASE)`, both raising `ValueError` with the substring `cannot process flags argument with a compiled pattern`, so no Rust or Python regex-behavior prerequisite is missing for this bounded pair;
  - `benchmarks/workloads/module_boundary.py` and `reports/benchmarks/latest.py` currently publish no compiled-pattern named-group explicit `IGNORECASE` `module.compile` rows on that owner route; and
  - `python/rebar_harness/benchmarks.py` already accepts the bounded compiled-pattern `module.compile(..., flags=IGNORECASE)` expected-exception route on the shared `module-boundary` surface, so this follow-on remains a publication-only benchmark catch-up slice rather than a missing harness prerequisite.
- `flags=re.NOFLAG` is still not the next task because the current owner-path keyword signature normalizes `RegexFlag(0)` to the already-benchmarked integer-zero carrier, while this named-group `IGNORECASE` rejection remains the next distinct unpublished neighbor on the active boundary.
- The acceptance counts above are intentionally written against the immediate post-`RBR-0884` state of `866` total / `866` measured / `0` known gaps overall with `REPORT["summary"]["module_workloads"] == 858` and `REPORT["manifests"]["module-boundary"]` at `38` selected / `38` measured / `0` known gaps.
