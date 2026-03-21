# RBR-0850: Catch up the module-workflow module keyword error benchmark pair

Status: ready
Owner: feature-implementation
Created: 2026-03-21

## Goal
- Extend the published Python-path module-boundary benchmark surface with the adjacent raw-module duplicate/unexpected keyword error pair that the shared `module-workflow-surface` correctness path already publishes, while keeping this catch-up on the existing `module_boundary.py` manifest instead of opening another module-keyword benchmark family.

## Pattern Pair
- `"abc"` through `search("abc", "abc", 0, flags=0)`
- `"abc"` through `fullmatch("abc", "abc", missing=1)`

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/module_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `python/rebar_harness/benchmarks.py` keeps the tracked Python-path benchmark publication stable while extending the post-`RBR-0848` raw-module helper keyword path from successful `flags=` keyword carriers to the adjacent keyword-error rows on `search()` and `fullmatch()`:
  - keep the post-`RBR-0848` raw-module `flags=` keyword `search()` / `match()` / `fullmatch()` workloads working unchanged once they land;
  - allow the shared helper path to benchmark a raw-module `search()` call that carries both positional `flags` and keyword `flags`, so the timed call still exercises the real duplicate-keyword rejection boundary instead of collapsing to one carrier before invocation;
  - allow raw-module `fullmatch()` workloads with unexpected keyword payloads on the shared helper path, preserving the timed `TypeError` outcome instead of pre-validating the call away; and
  - keep the existing `expected_exception` benchmark contract on the shared Python-path manifest surface without broadening into raw-module `split()` / `sub()` duplicate/unexpected keyword rows, bytes rows, compiled-pattern module helper rows, new manifests, or unrelated benchmark-schema churn in this run.
- `benchmarks/workloads/module_boundary.py` remains the only benchmark manifest for this slice and grows by exactly two new raw-module workloads:
  - add `module-search-duplicate-flags-keyword-warm-str`; and
  - add `module-fullmatch-unexpected-keyword-purged-str`.
- Keep those two workloads pinned to the exact already-published module-workflow keyword-error anchors rather than inventing a broader helper family:
  - `module-search-duplicate-flags-keyword-warm-str` uses `operation == "module.search"`, `pattern == "abc"`, `haystack == "abc"`, `text_model == "str"`, `cache_mode == "warm"`, `timing_scope == "module-helper-call"`, `flags == 0`, `kwargs == {"flags": 0}`, and `expected_exception == {"type": "TypeError", "message_substring": "multiple values for argument 'flags'"}`;
  - `module-fullmatch-unexpected-keyword-purged-str` uses `operation == "module.fullmatch"`, `pattern == "abc"`, `haystack == "abc"`, `text_model == "str"`, `cache_mode == "purged"`, `timing_scope == "module-helper-call"`, `flags == 0`, `kwargs == {"missing": 1}`, and `expected_exception == {"type": "TypeError", "message_substring": "unexpected keyword argument 'missing'"}`;
  - keep both rows str-only so the benchmark slice stays pinned to the exact published correctness anchors; and
  - do not broaden into bytes variants, error-message matrix expansion, smoke-only variants, or another benchmark manifest in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking a module-keyword benchmark suite:
  - update the module-boundary manifest expectations from `11` measured workloads to `13`, still with `0` known gaps on that manifest once `RBR-0848` has landed;
  - keep the manifest on the existing `post-parser-workflows` / combined-boundary path and anchor the two new workloads to the already-published correctness case ids `workflow-module-search-duplicate-flags-keyword` and `workflow-module-fullmatch-unexpected-keyword`;
  - update the combined publication totals from `811` total / `811` measured / `0` known gaps across `30` manifests to `813` / `813` / `0` across the same `30` manifests;
  - update `REPORT["summary"]["module_workloads"]` from `803` to `805`;
  - keep `REPORT["summary"]["regression_workloads"]` at `8`; and
  - keep the built-native smoke manifest set and every existing non-module-keyword module-boundary workload unchanged in this run.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["module-boundary"]` moves from `selected_workload_count == 11`, `measured_workloads == 11`, and `known_gap_count == 0` to `13`, `13`, and `0`;
  - the two new raw-module keyword-error workloads publish real `rebar` timings with `status == "measured"`, not synthetic placeholders; and
  - the tracked report exposes those exact workload ids on the existing module-boundary benchmark surface.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/module_boundary.py --report .rebar/tmp/rbr-0850-module-boundary.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not widen the correctness surface, add raw-module collection/replacement keyword-error rows, or change Rust/Python regex behavior just to support a larger benchmark family.
- Reuse the existing `module_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another module-keyword benchmark manifest, another benchmark suite, or detached benchmark expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.

## Notes
- `RBR-0850` is the next available feature task id in the current checkout:
  - `RBR-0849` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0848` on the same `module-workflow-surface` frontier so the adjacent raw-module duplicate/unexpected keyword error pair catches up on the existing Python-path `module_boundary.py` benchmark surface before the collection/replacement duplicate/unexpected keyword neighbors reopen the queue.
- 2026-03-21 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_module_keyword_argument_errors_match_cpython` passed in this run (`10 passed in 0.11s`), and a direct runtime probe in this run showed CPython and `rebar` already agree on the exact bounded `TypeError` messages for `search("abc", "abc", 0, flags=0)` and `fullmatch("abc", "abc", missing=1)`, so this remains a benchmark/publication task rather than a missing runtime-implementation prerequisite;
  - `benchmarks/workloads/module_boundary.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and `reports/benchmarks/latest.py` currently stop short of these two raw-module keyword-error rows in the current checkout, even though the shared benchmark harness already supports measured `expected_exception` workloads on other manifests; and
  - `reports/benchmarks/latest.py` currently reports `808` total / `808` measured / `0` known gaps overall, with `REPORT["summary"]["module_workloads"] == 800` and `REPORT["manifests"]["module-boundary"]` at `8` selected / `8` measured / `0` known gaps because `RBR-0848` is still ready in this run, so the acceptance counts above are intentionally written against the immediate post-`RBR-0848` state.
