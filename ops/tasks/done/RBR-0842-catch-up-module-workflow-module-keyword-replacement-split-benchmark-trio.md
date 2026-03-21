# RBR-0842: Catch up the module-workflow module keyword replacement/split benchmark trio

Status: done
Owner: feature-implementation
Created: 2026-03-21

## Goal
- Extend the published Python-path collection/replacement benchmark surface with the exact raw-module `split()` / `sub()` / `subn()` keyword `maxsplit` / `count` trio that the shared `module-workflow-surface` correctness path already publishes, while keeping this catch-up on the existing `collection_replacement_boundary.py` manifest instead of opening a second module-keyword benchmark family.

## Pattern Pair
- `"abc"`
- `b"abc"`

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `python/rebar_harness/benchmarks.py` keeps the tracked Python-path benchmark publication stable while extending the post-`RBR-0840` raw-module helper path from positional collection/replacement carriers to exact keyword `maxsplit` / `count` carriers:
  - keep the post-`RBR-0840` precompiled `Pattern.split()` / `Pattern.sub()` / `Pattern.subn()` keyword integer, `__index__`, and bool workloads working unchanged once they land;
  - keep every existing positional `count` / `maxsplit` workload working unchanged for raw-module and precompiled-helper operations;
  - route exact raw-module keyword `maxsplit` / `count` carriers through the shared `module.split()` / `module.sub()` / `module.subn()` benchmark path instead of forcing those helper calls back through positional arguments;
  - allow keyword-backed `maxsplit` and `count` values to stay unresolved until raw helper invocation so the benchmarked call still times the real module-keyword numeric coercion boundary; and
  - do not broaden into raw-module keyword `__index__` or bool carriers, module `flags=` keyword rows, duplicate-keyword error rows, compiled-pattern module helper rows, new benchmark manifests, or unrelated benchmark-schema churn in this run.
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly three new raw-module workloads:
  - add `module-split-maxsplit-keyword-purged-bytes`;
  - add `module-sub-count-keyword-warm-str`; and
  - add `module-subn-count-keyword-purged-bytes`.
- Keep those three workloads pinned to the exact already-published module-workflow keyword anchors rather than inventing a broader helper family:
  - `module-split-maxsplit-keyword-purged-bytes` uses `operation == "module.split"`, `pattern == "abc"`, `haystack == "zabczabc"`, `text_model == "bytes"`, `cache_mode == "purged"`, `timing_scope == "module-helper-call"`, and `kwargs == {"maxsplit": 1}`;
  - `module-sub-count-keyword-warm-str` uses `operation == "module.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `text_model == "str"`, `cache_mode == "warm"`, `timing_scope == "module-helper-call"`, and `kwargs == {"count": 1}`;
  - `module-subn-count-keyword-purged-bytes` uses `operation == "module.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `text_model == "bytes"`, `cache_mode == "purged"`, `timing_scope == "module-helper-call"`, and `kwargs == {"count": 1}`;
  - keep the text-model split explicit at one `str` row and two `bytes` rows; and
  - do not broaden into raw-module keyword `__index__` or bool carriers, `flags=` keyword rows, smoke-only variants, or another benchmark manifest in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking a module-keyword benchmark suite:
  - update the collection/replacement manifest expectations from `25` measured workloads to `28`, still with `0` known gaps on that manifest once `RBR-0840` has landed;
  - keep the manifest on the existing `post-parser-workflows` / combined-boundary path and anchor the three new workloads to the already-published correctness case ids `workflow-module-split-maxsplit-keyword-bytes`, `workflow-module-sub-count-keyword-str`, and `workflow-module-subn-count-keyword-bytes`;
  - update the combined publication totals from `799` total / `799` measured / `0` known gaps across `30` manifests to `802` / `802` / `0` across the same `30` manifests;
  - update `REPORT["summary"]["module_workloads"]` from `791` to `794`;
  - keep `REPORT["summary"]["regression_workloads"]` at `8`; and
  - keep the built-native smoke manifest set and every existing non-module-keyword collection/replacement workload unchanged in this run.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `25` selected / `25` measured / `0` known gaps to `28` / `28` / `0`;
  - the three new raw-module keyword workloads publish real `rebar` timings with `status == "measured"`, not synthetic placeholders; and
  - the tracked report exposes those exact workload ids on the existing collection/replacement benchmark surface.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0842-collection-replacement-boundary.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not widen the correctness surface, add raw-module keyword `__index__` or bool collection/replacement benchmark rows, or change Rust/Python regex behavior just to support a larger benchmark family.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another module-keyword benchmark manifest, another benchmark suite, or detached benchmark expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.

## Notes
- `RBR-0842` is the next available feature task id in the current checkout:
  - `RBR-0841` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0840` on the same `module-workflow-surface` frontier so the raw-module keyword replacement/split trio catches up on the existing Python-path `collection_replacement_boundary.py` benchmark surface before raw-module keyword `__index__` / bool neighbors or duplicate-keyword error rows reopen the queue.
- 2026-03-21 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_module_keyword_argument_calls_match_cpython` passed in this run (`24 passed in 0.11s`), and a direct runtime probe in this run showed CPython and `rebar` already agree on the exact bounded outputs for `split(b"abc", b"zabczabc", maxsplit=1)`, `sub("abc", "x", "abcabc", count=1)`, and `subn(b"abc", b"x", b"abcabc", count=1)`, so this remains a benchmark/publication task rather than a missing runtime-implementation prerequisite;
  - `python/rebar_harness/benchmarks.py` currently times raw-module `split()` / `sub()` / `subn()` through positional `maxsplit` / `count` arguments only and does not yet expose the adjacent raw-module keyword carriers on the shared benchmark path, even though the runtime behavior is already live;
  - `benchmarks/workloads/collection_replacement_boundary.py` currently publishes the raw-module positional `__index__` trio and the precompiled `Pattern` keyword / `__index__` trio, but not the adjacent raw-module keyword trio, so this follow-on stays on the existing manifest instead of inventing another benchmark family; and
  - `reports/benchmarks/latest.py` currently reports `796` total / `796` measured / `0` known gaps overall, with `REPORT["summary"]["module_workloads"] == 788` and `REPORT["manifests"]["collection-replacement-boundary"]` at `22` selected / `22` measured / `0` known gaps because `RBR-0840` is still ready in this run, so the acceptance counts above are intentionally written against the immediate post-`RBR-0840` state.

## Completion Notes
- 2026-03-21: Routed raw-module `split()` / `sub()` / `subn()` keyword `maxsplit` / `count` carriers through the shared benchmark helper path without disturbing the existing positional or `Pattern.*` keyword carriers, and added the exact three bounded module-keyword workloads on `collection_replacement_boundary.py`.
- 2026-03-21: Refreshed the shared benchmark owner-path assertions so the collection/replacement manifest now expects `28` selected / `28` measured / `0` known gaps and the published combined benchmark report now records `802` total / `802` measured / `0` known gaps with `REPORT["summary"]["module_workloads"] == 794`.
- 2026-03-21: Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` (`220 passed, 3 skipped, 1369 subtests passed`), `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0842-collection-replacement-boundary.py` (`28` total / `28` measured / `0` known gaps), and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py` (`802` total / `802` measured / `0` known gaps).
