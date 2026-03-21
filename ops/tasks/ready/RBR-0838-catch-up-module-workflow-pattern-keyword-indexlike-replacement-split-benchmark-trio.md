# RBR-0838: Catch up the module-workflow `Pattern` keyword `__index__` replacement/split benchmark trio

Status: ready
Owner: feature-implementation
Created: 2026-03-21

## Goal
- Extend the published Python-path collection/replacement benchmark surface with the exact precompiled `Pattern.split()` / `Pattern.sub()` / `Pattern.subn()` keyword `__index__` `maxsplit` / `count` trio that the shared `module-workflow-surface` correctness path already publishes, while keeping this catch-up on the existing `collection_replacement_boundary.py` manifest instead of opening a second keyword-only benchmark family.

## Pattern Pair
- `"abc"`
- `b"abc"`

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `python/rebar_harness/benchmarks.py` keeps the tracked Python-path benchmark publication stable while extending the post-`RBR-0836` precompiled-helper keyword path from plain integer carriers to exact keyword `__index__` carriers:
  - keep the post-`RBR-0836` keyword `maxsplit` / `count` `Pattern.split()` / `Pattern.sub()` / `Pattern.subn()` workloads working unchanged once they land;
  - keep every existing positional `count` / `maxsplit` workload working unchanged for both raw-module and precompiled-helper operations;
  - keep exact keyword `maxsplit` / `count` descriptors flowing through the shared precompiled-helper path for `Pattern.split()` / `Pattern.sub()` / `Pattern.subn()` instead of forcing those helper calls back through positional arguments;
  - allow descriptor-backed keyword `maxsplit` and `count` values to stay unresolved until precompiled helper invocation so the benchmarked helper call times the real keyword `__index__` coercion boundary; and
  - do not broaden into the remaining keyword bool collection/replacement carriers, raw-module keyword rows, remaining pattern keyword window rows, new benchmark manifests, or unrelated benchmark-schema churn in this run.
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly three new precompiled-`Pattern` workloads:
  - add `pattern-split-maxsplit-indexlike-keyword-warm-str`;
  - add `pattern-sub-count-indexlike-keyword-purged-bytes`; and
  - add `pattern-subn-count-indexlike-keyword-warm-str`.
- Keep those three workloads pinned to the exact already-published module-workflow keyword anchors rather than inventing a broader helper family:
  - `pattern-split-maxsplit-indexlike-keyword-warm-str` uses `operation == "pattern.split"`, `pattern == "abc"`, `haystack == "zabcabcabc"`, `text_model == "str"`, `cache_mode == "warm"`, `timing_scope == "pattern-helper-call"`, and `kwargs == {"maxsplit": {"type": "indexlike", "value": 2}}`;
  - `pattern-sub-count-indexlike-keyword-purged-bytes` uses `operation == "pattern.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabcabc"`, `text_model == "bytes"`, `cache_mode == "purged"`, `timing_scope == "pattern-helper-call"`, and `kwargs == {"count": {"type": "indexlike", "value": 2}}`;
  - `pattern-subn-count-indexlike-keyword-warm-str` uses `operation == "pattern.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabcabc"`, `text_model == "str"`, `cache_mode == "warm"`, `timing_scope == "pattern-helper-call"`, and `kwargs == {"count": {"type": "indexlike", "value": 2}}`;
  - keep the text-model split explicit at two `str` rows and one `bytes` row; and
  - do not broaden into keyword bool collection/replacement carriers, raw-module keyword rows, smoke-only variants, or another benchmark manifest in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking a keyword-only benchmark suite:
  - update the collection/replacement manifest expectations from `19` measured workloads to `22`, still with `0` known gaps on that manifest once `RBR-0836` has landed;
  - keep the manifest on the existing `post-parser-workflows` / combined-boundary path and anchor the three new workloads to the already-published correctness case ids `workflow-pattern-split-str-maxsplit-indexlike`, `workflow-pattern-sub-count-indexlike-bytes`, and `workflow-pattern-subn-count-indexlike-str`;
  - update the combined publication totals from `793` total / `793` measured / `0` known gaps across `30` manifests to `796` / `796` / `0` across the same `30` manifests;
  - update `REPORT["summary"]["module_workloads"]` from `785` to `788`;
  - keep `REPORT["summary"]["regression_workloads"]` at `8`; and
  - keep the built-native smoke manifest set and every existing non-keyword-`__index__` workload unchanged in this run.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `19` selected / `19` measured / `0` known gaps to `22` / `22` / `0`;
  - the three new keyword `__index__` workloads publish real `rebar` timings with `status == "measured"`, not synthetic placeholders; and
  - the tracked report exposes those exact workload ids on the existing collection/replacement benchmark surface.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0838-collection-replacement-boundary.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not widen the correctness surface, add raw-module keyword collection/replacement benchmark support, or change Rust/Python regex behavior just to support a larger benchmark family.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another keyword-only benchmark manifest, another benchmark suite, or detached benchmark expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.

## Notes
- `RBR-0838` is the next available feature task id in the current checkout:
  - `python3` queue/id inspection in this run returned `RBR-0838` with no reserved tail; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0836` on the same `module-workflow-surface` frontier so the precompiled `Pattern` keyword `__index__` replacement/split carriers catch up on the existing Python-path collection/replacement benchmark surface before the adjacent bool keyword trio or raw-module keyword rows reopen the queue.
- 2026-03-21 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier:
  - a direct runtime probe in this run showed CPython and `rebar` already agree on the exact bounded outputs for `workflow-pattern-split-str-maxsplit-indexlike`, `workflow-pattern-sub-count-indexlike-bytes`, and `workflow-pattern-subn-count-indexlike-str`, so this remains a benchmark/publication task rather than a missing runtime-implementation prerequisite;
  - `python/rebar_harness/benchmarks.py` does not yet publish these exact keyword `__index__` carriers on the precompiled helper path in the current checkout because `RBR-0836` still needs to land first, so the acceptance counts above are intentionally written against the immediate post-`RBR-0836` state;
  - `benchmarks/workloads/collection_replacement_boundary.py` already owns the adjacent precompiled `Pattern` collection/replacement surface, so this slice can stay on the existing manifest path instead of inventing another benchmark family; and
  - `reports/benchmarks/latest.py` currently reports `790` total / `790` measured / `0` known gaps overall, with `REPORT["summary"]["module_workloads"] == 782` and `REPORT["manifests"]["collection-replacement-boundary"]` at `16` selected / `16` measured / `0` known gaps because `RBR-0836` is still ready in this run.
