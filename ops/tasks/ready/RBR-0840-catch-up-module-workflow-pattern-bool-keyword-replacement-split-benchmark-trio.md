# RBR-0840: Catch up the module-workflow `Pattern` bool keyword replacement/split benchmark trio

Status: ready
Owner: feature-implementation
Created: 2026-03-21

## Goal
- Extend the published Python-path collection/replacement benchmark surface with the exact precompiled `Pattern.split()` / `Pattern.sub()` / `Pattern.subn()` bool-keyword `maxsplit` / `count` trio that the shared `module-workflow-surface` correctness path already publishes, while keeping this catch-up on the existing `collection_replacement_boundary.py` manifest instead of opening a second bool-only benchmark family.

## Pattern Pair
- `"abc"`
- `b"abc"`

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `python/rebar_harness/benchmarks.py` keeps the tracked Python-path benchmark publication stable while extending the post-`RBR-0838` precompiled-helper keyword path from exact `__index__` carriers to the adjacent bool carriers:
  - keep the post-`RBR-0838` keyword `maxsplit` / `count` `Pattern.split()` / `Pattern.sub()` / `Pattern.subn()` integer and `__index__` workloads working unchanged once they land;
  - keep every existing positional `count` / `maxsplit` workload working unchanged for both raw-module and precompiled-helper operations;
  - keep exact keyword `maxsplit` / `count` bool payloads flowing through the shared precompiled-helper path for `Pattern.split()` / `Pattern.sub()` / `Pattern.subn()` instead of forcing those helper calls back through positional arguments or collapsing their signatures onto plain integers;
  - preserve the existing bool/int/indexlike keyword-signature distinction on the shared collection/replacement benchmark contract path so the benchmarked helper call still times the real keyword bool-coercion boundary; and
  - do not broaden into raw-module keyword rows, duplicate-keyword error rows, remaining compiled-pattern module keyword neighbors, new benchmark manifests, or unrelated benchmark-schema churn in this run.
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly three new precompiled-`Pattern` workloads:
  - add `pattern-split-maxsplit-bool-keyword-warm-str`;
  - add `pattern-sub-count-bool-keyword-purged-bytes`; and
  - add `pattern-subn-count-bool-keyword-warm-str`.
- Keep those three workloads pinned to the exact already-published module-workflow bool-keyword anchors rather than inventing a broader helper family:
  - `pattern-split-maxsplit-bool-keyword-warm-str` uses `operation == "pattern.split"`, `pattern == "abc"`, `haystack == "zabczabc"`, `text_model == "str"`, `cache_mode == "warm"`, `timing_scope == "pattern-helper-call"`, and `kwargs == {"maxsplit": True}`;
  - `pattern-sub-count-bool-keyword-purged-bytes` uses `operation == "pattern.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `text_model == "bytes"`, `cache_mode == "purged"`, `timing_scope == "pattern-helper-call"`, and `kwargs == {"count": False}`;
  - `pattern-subn-count-bool-keyword-warm-str` uses `operation == "pattern.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `text_model == "str"`, `cache_mode == "warm"`, `timing_scope == "pattern-helper-call"`, and `kwargs == {"count": True}`;
  - keep the text-model split explicit at two `str` rows and one `bytes` row; and
  - do not broaden into raw-module keyword collection/replacement rows, `__index__` rows already queued in `RBR-0838`, duplicate-keyword failures, smoke-only variants, or another benchmark manifest in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking a bool-only benchmark suite:
  - update the collection/replacement manifest expectations from `22` measured workloads to `25`, still with `0` known gaps on that manifest once `RBR-0838` has landed;
  - keep the manifest on the existing `post-parser-workflows` / combined-boundary path and anchor the three new workloads to the already-published correctness case ids `workflow-pattern-split-str-maxsplit-bool-true`, `workflow-pattern-sub-count-bool-false-bytes`, and `workflow-pattern-subn-count-bool-true-str`;
  - update the combined publication totals from `796` total / `796` measured / `0` known gaps across `30` manifests to `799` / `799` / `0` across the same `30` manifests;
  - update `REPORT["summary"]["module_workloads"]` from `788` to `791`;
  - keep `REPORT["summary"]["regression_workloads"]` at `8`; and
  - keep the built-native smoke manifest set and every existing non-bool collection/replacement workload unchanged in this run.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `22` selected / `22` measured / `0` known gaps to `25` / `25` / `0`;
  - the three new bool-keyword workloads publish real `rebar` timings with `status == "measured"`, not synthetic placeholders; and
  - the tracked report exposes those exact workload ids on the existing collection/replacement benchmark surface.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0840-collection-replacement-boundary.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not widen the correctness surface, add raw-module keyword collection/replacement benchmark support, or change Rust/Python regex behavior just to support a larger benchmark family.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another bool-only benchmark manifest, another benchmark suite, or detached benchmark expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.

## Notes
- `RBR-0840` is the next available feature task id in the current checkout:
  - `python3` queue/id inspection in this run returned `RBR-0840` with no reserved tail; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0838` on the same `module-workflow-surface` frontier so the precompiled `Pattern` bool keyword replacement/split carriers catch up on the existing Python-path collection/replacement benchmark surface before raw-module keyword rows or duplicate-keyword error neighbors reopen the queue.
- 2026-03-21 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier:
  - a direct runtime probe in this run showed CPython and `rebar` already agree on the exact bounded outputs for `workflow-pattern-split-str-maxsplit-bool-true`, `workflow-pattern-sub-count-bool-false-bytes`, and `workflow-pattern-subn-count-bool-true-str`, so this remains a benchmark/publication task rather than a missing runtime-implementation prerequisite;
  - `python/rebar_harness/benchmarks.py` already owns the shared precompiled-helper keyword path for `Pattern.split()` / `Pattern.sub()` / `Pattern.subn()` after `RBR-0836`, so once `RBR-0838` lands this follow-on stays on the existing benchmark-owner surface instead of reopening helper-plumbing work;
  - `benchmarks/workloads/collection_replacement_boundary.py` currently publishes the plain integer keyword trio but not the adjacent bool-keyword trio, and `RBR-0838` is already queued to land the intervening `__index__` trio on the same manifest path first; and
  - `reports/benchmarks/latest.py` currently reports `793` total / `793` measured / `0` known gaps overall, with `REPORT["summary"]["module_workloads"] == 785` and `REPORT["manifests"]["collection-replacement-boundary"]` at `19` selected / `19` measured / `0` known gaps because `RBR-0838` is still ready in this run, so the acceptance counts above are intentionally written against the immediate post-`RBR-0838` state.
