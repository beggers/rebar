# RBR-0848: Catch up the module-workflow module `flags=` keyword benchmark trio

Status: done
Owner: feature-implementation
Created: 2026-03-21

## Goal
- Extend the published Python-path module-boundary benchmark surface with the exact raw-module `search()` / `match()` / `fullmatch()` `flags=` keyword trio that the shared `module-workflow-surface` correctness path already publishes, while keeping this catch-up on the existing `module_boundary.py` manifest instead of opening a second module-keyword benchmark family.

## Pattern Pair
- `"abc"`
- `b"abc"`

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/module_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `python/rebar_harness/benchmarks.py` keeps the tracked Python-path benchmark publication stable while extending the raw-module helper keyword path from replacement/split-only kwargs to the adjacent `flags=` carriers on `search()` / `match()` / `fullmatch()`:
  - keep the post-`RBR-0846` raw-module `split()` / `sub()` / `subn()` keyword integer, `__index__`, and bool workloads working unchanged once they land;
  - allow benchmark workload `kwargs == {"flags": ...}` for `module.search`, `module.match`, and `module.fullmatch` on the shared helper path instead of forcing those calls back through positional `flags`;
  - materialize the exact keyword `flags` value at helper invocation so the benchmarked call still times the real raw-module keyword-argument boundary instead of a pre-coerced positional fallback; and
  - do not broaden into duplicate-keyword or unexpected-keyword error rows, compiled-pattern module helper rows, pattern keyword workloads, new benchmark manifests, or unrelated benchmark-schema churn in this run.
- `benchmarks/workloads/module_boundary.py` remains the only benchmark manifest for this slice and grows by exactly three new raw-module workloads:
  - add `module-search-flags-keyword-warm-str`;
  - add `module-match-flags-keyword-purged-bytes`; and
  - add `module-fullmatch-flags-keyword-warm-str`.
- Keep those three workloads pinned to the exact already-published module-workflow keyword anchors rather than inventing a broader helper family:
  - `module-search-flags-keyword-warm-str` uses `operation == "module.search"`, `pattern == "abc"`, `haystack == "zAbc"`, `text_model == "str"`, `cache_mode == "warm"`, `timing_scope == "module-helper-call"`, and `kwargs == {"flags": 2}`;
  - `module-match-flags-keyword-purged-bytes` uses `operation == "module.match"`, `pattern == "abc"`, `haystack == "Abc"`, `text_model == "bytes"`, `cache_mode == "purged"`, `timing_scope == "module-helper-call"`, and `kwargs == {"flags": 2}`;
  - `module-fullmatch-flags-keyword-warm-str` uses `operation == "module.fullmatch"`, `pattern == "abc"`, `haystack == "Abc"`, `text_model == "str"`, `cache_mode == "warm"`, `timing_scope == "module-helper-call"`, and `kwargs == {"flags": 2}`;
  - keep the text-model split explicit at two `str` rows and one `bytes` row; and
  - do not broaden into duplicate-keyword failures, unexpected-keyword failures, replacement/split rows, smoke-only variants, or another benchmark manifest in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking a module-keyword benchmark suite:
  - update the module-boundary manifest expectations from `8` measured workloads to `11`, still with `0` known gaps on that manifest once `RBR-0846` has landed;
  - keep the manifest on the existing `post-parser-workflows` / combined-boundary path and anchor the three new workloads to the already-published correctness case ids `workflow-module-search-flags-keyword-str`, `workflow-module-match-flags-keyword-bytes`, and `workflow-module-fullmatch-flags-keyword-str`;
  - update the combined publication totals from `808` total / `808` measured / `0` known gaps across `30` manifests to `811` / `811` / `0` across the same `30` manifests;
  - update `REPORT["summary"]["module_workloads"]` from `800` to `803`;
  - keep `REPORT["summary"]["regression_workloads"]` at `8`; and
  - keep the built-native smoke manifest set and every existing non-module-keyword module-boundary workload unchanged in this run.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["module-boundary"]` moves from `selected_workload_count == 8`, `measured_workloads == 8`, and `known_gap_count == 0` to `11`, `11`, and `0`;
  - the three new raw-module `flags=` keyword workloads publish real `rebar` timings with `status == "measured"`, not synthetic placeholders; and
  - the tracked report exposes those exact workload ids on the existing module-boundary benchmark surface.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/module_boundary.py --report .rebar/tmp/rbr-0848-module-boundary.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not widen the correctness surface, add duplicate-keyword or unexpected-keyword benchmark rows, or change Rust/Python regex behavior just to support a larger benchmark family.
- Reuse the existing `module_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another module-keyword benchmark manifest, another benchmark suite, or detached benchmark expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.

## Notes
- `RBR-0848` is the next available feature task id in the current checkout:
  - `RBR-0847` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0846` on the same `module-workflow-surface` frontier so the raw-module `flags=` keyword search/match/fullmatch trio catches up on the existing Python-path `module_boundary.py` benchmark surface before duplicate-keyword error neighbors reopen the queue.
- 2026-03-21 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_module_keyword_argument_calls_match_cpython` passed in this run (`24 passed in 0.12s`), and a direct runtime probe in this run showed CPython and `rebar` already agree on the exact bounded outputs for `search("abc", "zAbc", flags=re.IGNORECASE)`, `match(b"abc", b"Abc", flags=re.IGNORECASE)`, and `fullmatch("abc", "Abc", flags=re.IGNORECASE)`, so this remains a benchmark/publication task rather than a missing runtime-implementation prerequisite;
  - `python/rebar_harness/benchmarks.py` currently limits raw-module keyword benchmark execution to `split()` / `sub()` / `subn()`, so the existing benchmark path still does not expose the adjacent raw-module `flags=` keyword trio even though the runtime behavior is already live;
  - `benchmarks/workloads/module_boundary.py` currently publishes the baseline module-boundary search/match/fullmatch rows but not the adjacent raw-module `flags=` keyword trio, so this follow-on stays on the existing manifest instead of inventing another benchmark family; and
  - `reports/benchmarks/latest.py` currently reports `805` total / `805` measured / `0` known gaps overall, with `REPORT["summary"]["module_workloads"] == 797` and `REPORT["manifests"]["module-boundary"]` at `8` selected / `8` measured / `0` known gaps because `RBR-0846` is still ready in this run, so the acceptance counts above are intentionally written against the immediate post-`RBR-0846` state.

## Completion
- Extended `python/rebar_harness/benchmarks.py` so raw-module `module.search`, `module.match`, and `module.fullmatch` workloads may carry `kwargs={"flags": ...}` and dispatch through the real keyword helper path without falling back to positional `flags`.
- Added the three bounded raw-module `flags=` keyword workloads to `benchmarks/workloads/module_boundary.py` and anchored them on the shared benchmark contract path in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Added focused benchmark-suite coverage that keeps those workload ids pinned to the published correctness case ids `workflow-module-search-flags-keyword-str`, `workflow-module-match-flags-keyword-bytes`, and `workflow-module-fullmatch-flags-keyword-str`, plus a callback-time materialization check for `kwargs.flags`.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/module_boundary.py --report .rebar/tmp/rbr-0848-module-boundary.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`
- Republished `reports/benchmarks/latest.py`; the tracked report now shows `811` total workloads, `811` measured workloads, `0` known gaps, `803` module workloads overall, and `REPORT["manifests"]["module-boundary"]` at `11` selected / `11` measured / `0` known gaps across the existing shared manifest.
- Published correctness scorecard unchanged.
