# RBR-0846: Catch up the module-workflow module bool keyword replacement/split benchmark trio

Status: ready
Owner: feature-implementation
Created: 2026-03-21

## Goal
- Extend the published Python-path collection/replacement benchmark surface with the exact raw-module `split()` / `sub()` / `subn()` keyword `maxsplit` / `count` bool trio that the shared `module-workflow-surface` correctness path already publishes, while keeping this catch-up on the existing `collection_replacement_boundary.py` manifest instead of opening a second module-keyword benchmark family.

## Pattern Pair
- `"abc"`
- `b"abc"`

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `python/rebar_harness/benchmarks.py` keeps the tracked Python-path benchmark publication stable while extending the post-`RBR-0844` raw-module helper keyword path from exact `__index__` carriers to the adjacent bool carriers:
  - keep the post-`RBR-0844` raw-module `split()` / `sub()` / `subn()` keyword integer and `__index__` workloads working unchanged once they land;
  - keep every existing positional `count` / `maxsplit` workload working unchanged for raw-module and precompiled-helper operations;
  - route exact raw-module keyword `maxsplit` / `count` bool carriers through the shared `module.split()` / `module.sub()` / `module.subn()` benchmark path instead of forcing those helper calls back through positional arguments or collapsing them to plain integers before invocation;
  - preserve the existing bool/int/indexlike keyword-signature distinction on the shared collection/replacement benchmark contract path so the benchmarked call still times the real module-keyword bool-coercion boundary; and
  - do not broaden into module `flags=` keyword rows, duplicate-keyword error rows, compiled-pattern module helper rows, new benchmark manifests, or unrelated benchmark-schema churn in this run.
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly three new raw-module workloads:
  - add `module-split-maxsplit-bool-keyword-purged-bytes`;
  - add `module-sub-count-bool-keyword-warm-str`; and
  - add `module-subn-count-bool-keyword-purged-bytes`.
- Keep those three workloads pinned to the exact already-published module-workflow bool-keyword anchors rather than inventing a broader helper family:
  - `module-split-maxsplit-bool-keyword-purged-bytes` uses `operation == "module.split"`, `pattern == "abc"`, `haystack == "abcabc"`, `text_model == "bytes"`, `cache_mode == "purged"`, `timing_scope == "module-helper-call"`, and `kwargs == {"maxsplit": False}`;
  - `module-sub-count-bool-keyword-warm-str` uses `operation == "module.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `text_model == "str"`, `cache_mode == "warm"`, `timing_scope == "module-helper-call"`, and `kwargs == {"count": True}`;
  - `module-subn-count-bool-keyword-purged-bytes` uses `operation == "module.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `text_model == "bytes"`, `cache_mode == "purged"`, `timing_scope == "module-helper-call"`, and `kwargs == {"count": False}`;
  - keep the text-model split explicit at one `str` row and two `bytes` rows; and
  - do not broaden into module `flags=` keyword rows, duplicate-keyword failures, smoke-only variants, or another benchmark manifest in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking a module-keyword benchmark suite:
  - update the collection/replacement manifest expectations from `31` measured workloads to `34`, still with `0` known gaps on that manifest once `RBR-0844` has landed;
  - keep the manifest on the existing `post-parser-workflows` / combined-boundary path and anchor the three new workloads to the already-published correctness case ids `workflow-module-split-maxsplit-bool-false-bytes`, `workflow-module-sub-count-bool-true-str`, and `workflow-module-subn-count-bool-false-bytes`;
  - update the combined publication totals from `805` total / `805` measured / `0` known gaps across `30` manifests to `808` / `808` / `0` across the same `30` manifests;
  - update `REPORT["summary"]["module_workloads"]` from `797` to `800`;
  - keep `REPORT["summary"]["regression_workloads"]` at `8`; and
  - keep the built-native smoke manifest set and every existing non-module-keyword collection/replacement workload unchanged in this run.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `selected_workload_count == 31`, `measured_workloads == 31`, and `known_gap_count == 0` to `34`, `34`, and `0`;
  - the three new raw-module keyword bool workloads publish real `rebar` timings with `status == "measured"`, not synthetic placeholders; and
  - the tracked report exposes those exact workload ids on the existing collection/replacement benchmark surface.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0846-collection-replacement-boundary.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not widen the correctness surface, add module keyword duplicate-keyword benchmark rows, or change Rust/Python regex behavior just to support a larger benchmark family.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another module-keyword benchmark manifest, another benchmark suite, or detached benchmark expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.

## Notes
- `RBR-0846` is the next available feature task id in the current checkout:
  - `RBR-0845` is already occupied by an architecture cleanup task in `ops/tasks/in_progress/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0844` on the same `module-workflow-surface` frontier so the raw-module keyword bool replacement/split trio catches up on the existing Python-path `collection_replacement_boundary.py` benchmark surface before duplicate-keyword error neighbors reopen the queue.
- 2026-03-21 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_module_keyword_argument_calls_match_cpython` passed in this run (`24 passed in 0.11s`), and a direct runtime probe in this run showed CPython and `rebar` already agree on the exact bounded outputs for `split(b"abc", b"abcabc", maxsplit=False)`, `sub("abc", "x", "abcabc", count=True)`, and `subn(b"abc", b"x", b"abcabc", count=False)`, so this remains a benchmark/publication task rather than a missing runtime-implementation prerequisite;
  - `benchmarks/workloads/collection_replacement_boundary.py` currently publishes the raw-module keyword integer trio and the precompiled `Pattern` keyword bool trio, but not the adjacent raw-module keyword bool trio, so this follow-on stays on the existing manifest instead of inventing another benchmark family;
  - the shared source-tree benchmark expectations in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and the tracked publication in `reports/benchmarks/latest.py` likewise still stop short of these three raw-module bool keyword workloads in the current checkout; and
  - `reports/benchmarks/latest.py` currently reports `802` total / `802` measured / `0` known gaps overall, with `REPORT["summary"]["module_workloads"] == 794` because `RBR-0844` is still ready in this run, so the acceptance counts above are intentionally written against the immediate post-`RBR-0844` state.
