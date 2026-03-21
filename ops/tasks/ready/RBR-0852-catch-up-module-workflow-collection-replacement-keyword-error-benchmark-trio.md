# RBR-0852: Catch up the module-workflow collection/replacement keyword error benchmark trio

Status: ready
Owner: feature-implementation
Created: 2026-03-21

## Goal
- Extend the published Python-path collection/replacement benchmark surface with the remaining raw-module `split()` / `sub()` duplicate and unexpected keyword error trio that the shared `module-workflow-surface` correctness path already publishes, while keeping this catch-up on the existing `collection_replacement_boundary.py` manifest instead of opening another module-keyword benchmark family.

## Pattern Pair
- `"abc"` through `split("abc", "abc", 1, maxsplit=1)`
- `"abc"` through `sub("abc", "x", "abc", 1, count=1)` and `sub("abc", "x", "abc", missing=1)`

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `python/rebar_harness/benchmarks.py` keeps the tracked Python-path benchmark publication stable while extending the shared raw-module collection/replacement helper path from successful `maxsplit=` / `count=` keyword carriers to the adjacent keyword-error rows:
  - keep the post-`RBR-0850` raw-module `search()` / `fullmatch()` keyword-error workloads and the existing successful `split()` / `sub()` / `subn()` keyword carrier workloads working unchanged once they land;
  - allow the shared helper path to benchmark a raw-module `split()` call that carries both positional `maxsplit` and keyword `maxsplit`, so the timed call still exercises the real duplicate-keyword rejection boundary instead of collapsing to one carrier before invocation;
  - allow the shared helper path to benchmark raw-module `sub()` calls that carry both positional `count` and keyword `count`, plus the adjacent raw-module `sub()` unexpected-keyword payload, preserving the timed `TypeError` outcomes instead of pre-validating the calls away; and
  - keep the existing `expected_exception` benchmark contract on the shared Python-path collection/replacement surface without broadening into `subn()` keyword-error rows, compiled-pattern module helper rows, bytes rows, new manifests, or unrelated benchmark-schema churn in this run.
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly three new raw-module workloads:
  - add `module-split-duplicate-maxsplit-keyword-purged-str`;
  - add `module-sub-duplicate-count-keyword-warm-str`; and
  - add `module-sub-unexpected-keyword-purged-str`.
- Keep those three workloads pinned to the exact already-published module-workflow keyword-error anchors rather than inventing a broader helper family:
  - `module-split-duplicate-maxsplit-keyword-purged-str` uses `operation == "module.split"`, `pattern == "abc"`, `haystack == "abc"`, `text_model == "str"`, `cache_mode == "purged"`, `timing_scope == "module-helper-call"`, `flags == 0`, `maxsplit == 1`, `kwargs == {"maxsplit": 1}`, and `expected_exception == {"type": "TypeError", "message_substring": "multiple values for argument 'maxsplit'"}`;
  - `module-sub-duplicate-count-keyword-warm-str` uses `operation == "module.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abc"`, `text_model == "str"`, `cache_mode == "warm"`, `timing_scope == "module-helper-call"`, `flags == 0`, `count == 1`, `kwargs == {"count": 1}`, and `expected_exception == {"type": "TypeError", "message_substring": "multiple values for argument 'count'"}`;
  - `module-sub-unexpected-keyword-purged-str` uses `operation == "module.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abc"`, `text_model == "str"`, `cache_mode == "purged"`, `timing_scope == "module-helper-call"`, `flags == 0`, `kwargs == {"missing": 1}`, and `expected_exception == {"type": "TypeError", "message_substring": "unexpected keyword argument 'missing'"}`;
  - keep all three rows str-only so the benchmark slice stays pinned to the exact published correctness anchors; and
  - do not broaden into `subn()` error variants, bytes variants, error-message matrix expansion, smoke-only variants, or another benchmark manifest in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking a collection/replacement keyword-error benchmark suite:
  - update the collection-replacement manifest expectations from `34` measured workloads to `37`, still with `0` known gaps on that manifest once `RBR-0850` has landed;
  - keep the manifest on the existing `post-parser-workflows` / combined-boundary path and anchor the three new workloads to the already-published correctness case ids `workflow-module-split-duplicate-maxsplit-keyword`, `workflow-module-sub-duplicate-count-keyword`, and `workflow-module-sub-unexpected-keyword`;
  - update the combined publication totals from `813` total / `813` measured / `0` known gaps across `30` manifests to `816` / `816` / `0` across the same `30` manifests;
  - update `REPORT["summary"]["module_workloads"]` from `805` to `808`;
  - keep `REPORT["summary"]["regression_workloads"]` at `8`; and
  - keep the built-native smoke manifest set and every existing non-keyword-error collection/replacement workload unchanged in this run.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `selected_workload_count == 34`, `measured_workloads == 34`, and `known_gap_count == 0` to `37`, `37`, and `0`;
  - the three new raw-module keyword-error workloads publish real `rebar` timings with `status == "measured"`, not synthetic placeholders; and
  - the tracked report exposes those exact workload ids on the existing collection/replacement benchmark surface.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0852-collection-replacement.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not widen the correctness surface, add `subn()` or compiled-pattern keyword-error rows, or change Rust/Python regex behavior just to support a larger benchmark family.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another collection/replacement keyword benchmark manifest, another benchmark suite, or detached benchmark expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.

## Notes
- `RBR-0852` is the next available feature task id in the current checkout:
  - `RBR-0851` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0850` on the same `module-workflow-surface` frontier so the remaining raw-module `split()` / `sub()` duplicate and unexpected keyword error trio catches up on the existing Python-path `collection_replacement_boundary.py` benchmark surface before compiled-pattern keyword-error neighbors or broader collection/replacement follow-ons reopen the queue.
- 2026-03-21 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_module_keyword_argument_errors_match_cpython` passed in this run (`10 passed in 0.10s`), and a direct runtime probe in this run showed CPython and `rebar` already agree on the exact bounded `TypeError` messages for `split("abc", "abc", 1, maxsplit=1)`, `sub("abc", "x", "abc", 1, count=1)`, and `sub("abc", "x", "abc", missing=1)`, so this remains a benchmark/publication task rather than a missing runtime-implementation prerequisite;
  - `python/rebar_harness/benchmarks.py` already accepts module `split()` / `sub()` keyword carriers and already measures `expected_exception` workloads on the shared source-tree benchmark path, so the missing surface here is publication coverage rather than missing harness support;
  - `benchmarks/workloads/collection_replacement_boundary.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and `reports/benchmarks/latest.py` currently stop at the successful raw-module `maxsplit=` / `count=` keyword rows and do not yet publish the adjacent duplicate/unexpected keyword-error trio on that manifest; and
  - `reports/benchmarks/latest.py` currently reports `811` total / `811` measured / `0` known gaps overall, with `REPORT["summary"]["module_workloads"] == 803` and `REPORT["manifests"]["collection-replacement-boundary"]` at `34` selected / `34` measured / `0` known gaps because `RBR-0850` is still ready in this run, so the acceptance counts above are intentionally written against the immediate post-`RBR-0850` state.
