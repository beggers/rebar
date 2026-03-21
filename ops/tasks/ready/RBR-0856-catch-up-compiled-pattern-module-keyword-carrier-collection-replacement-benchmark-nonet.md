# RBR-0856: Catch up the compiled-pattern module keyword-carrier collection/replacement benchmark nonet

Status: ready
Owner: feature-implementation
Created: 2026-03-21

## Goal
- Extend the published Python-path collection/replacement benchmark surface with the remaining successful compiled-pattern-first-argument `split()` / `sub()` / `subn()` `maxsplit=` / `count=` keyword-carrier nonet that the shared `module-workflow-surface` correctness path already publishes, while keeping this catch-up on the existing `collection_replacement_boundary.py` manifest instead of opening a separate compiled-pattern module-helper benchmark family.

## Pattern Pair
- `re.compile("abc")` through `split(re.compile("abc"), "zabczabc", maxsplit=1)`, `sub(re.compile("abc"), "x", "abcabc", count=1)`, `sub(re.compile("abc"), "x", "abcabc", count=True)`, and `subn(re.compile("abc"), "x", "abcabcabc", count=__index__(2))`
- `re.compile(b"abc")` through `split(re.compile(b"abc"), b"zabcabcabc", maxsplit=__index__(2))`, `split(re.compile(b"abc"), b"abcabc", maxsplit=False)`, `sub(re.compile(b"abc"), b"x", b"abcabcabc", count=__index__(2))`, `subn(re.compile(b"abc"), b"x", b"abcabc", count=1)`, and `subn(re.compile(b"abc"), b"x", b"abcabc", count=False)`

## Deliverables
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly nine compiled-pattern-first-argument keyword-carrier workloads, reusing the helper path added by `RBR-0854` instead of widening benchmark schema or support code again:
  - add `module-split-maxsplit-keyword-purged-str-compiled-pattern`;
  - add `module-split-maxsplit-indexlike-keyword-purged-bytes-compiled-pattern`;
  - add `module-split-maxsplit-bool-keyword-purged-bytes-compiled-pattern`;
  - add `module-sub-count-keyword-warm-str-compiled-pattern`;
  - add `module-sub-count-indexlike-keyword-warm-bytes-compiled-pattern`;
  - add `module-sub-count-bool-keyword-warm-str-compiled-pattern`;
  - add `module-subn-count-keyword-purged-bytes-compiled-pattern`;
  - add `module-subn-count-indexlike-keyword-purged-str-compiled-pattern`; and
  - add `module-subn-count-bool-keyword-purged-bytes-compiled-pattern`.
- Keep those nine workloads pinned to the exact already-published module-workflow compiled-pattern keyword-carrier anchors rather than inventing a broader helper family:
  - `module-split-maxsplit-keyword-purged-str-compiled-pattern` uses `operation == "module.split"`, `pattern == "abc"`, `haystack == "zabczabc"`, `text_model == "str"`, `cache_mode == "purged"`, `timing_scope == "module-helper-call"`, `flags == 0`, an explicit compiled-pattern-first-argument marker, and `kwargs == {"maxsplit": 1}`;
  - `module-split-maxsplit-indexlike-keyword-purged-bytes-compiled-pattern` uses `operation == "module.split"`, `pattern == "abc"`, `haystack == "zabcabcabc"`, `text_model == "bytes"`, `cache_mode == "purged"`, `timing_scope == "module-helper-call"`, `flags == 0`, an explicit compiled-pattern-first-argument marker, and `kwargs == {"maxsplit": {"type": "indexlike", "value": 2}}`;
  - `module-split-maxsplit-bool-keyword-purged-bytes-compiled-pattern` uses `operation == "module.split"`, `pattern == "abc"`, `haystack == "abcabc"`, `text_model == "bytes"`, `cache_mode == "purged"`, `timing_scope == "module-helper-call"`, `flags == 0`, an explicit compiled-pattern-first-argument marker, and `kwargs == {"maxsplit": False}`;
  - `module-sub-count-keyword-warm-str-compiled-pattern` uses `operation == "module.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `text_model == "str"`, `cache_mode == "warm"`, `timing_scope == "module-helper-call"`, `flags == 0`, an explicit compiled-pattern-first-argument marker, and `kwargs == {"count": 1}`;
  - `module-sub-count-indexlike-keyword-warm-bytes-compiled-pattern` uses `operation == "module.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabcabc"`, `text_model == "bytes"`, `cache_mode == "warm"`, `timing_scope == "module-helper-call"`, `flags == 0`, an explicit compiled-pattern-first-argument marker, and `kwargs == {"count": {"type": "indexlike", "value": 2}}`;
  - `module-sub-count-bool-keyword-warm-str-compiled-pattern` uses `operation == "module.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `text_model == "str"`, `cache_mode == "warm"`, `timing_scope == "module-helper-call"`, `flags == 0`, an explicit compiled-pattern-first-argument marker, and `kwargs == {"count": True}`;
  - `module-subn-count-keyword-purged-bytes-compiled-pattern` uses `operation == "module.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `text_model == "bytes"`, `cache_mode == "purged"`, `timing_scope == "module-helper-call"`, `flags == 0`, an explicit compiled-pattern-first-argument marker, and `kwargs == {"count": 1}`;
  - `module-subn-count-indexlike-keyword-purged-str-compiled-pattern` uses `operation == "module.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabcabc"`, `text_model == "str"`, `cache_mode == "purged"`, `timing_scope == "module-helper-call"`, `flags == 0`, an explicit compiled-pattern-first-argument marker, and `kwargs == {"count": {"type": "indexlike", "value": 2}}`; and
  - `module-subn-count-bool-keyword-purged-bytes-compiled-pattern` uses `operation == "module.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `text_model == "bytes"`, `cache_mode == "purged"`, `timing_scope == "module-helper-call"`, `flags == 0`, an explicit compiled-pattern-first-argument marker, and `kwargs == {"count": False}`.
- Keep this nonet on the shared collection/replacement owner path and do not broaden beyond the exact adjacent compiled-pattern keyword-carrier slice:
  - anchor the nine workloads to `workflow-module-split-maxsplit-keyword-str-compiled-pattern`, `workflow-module-split-maxsplit-indexlike-bytes-compiled-pattern`, `workflow-module-split-maxsplit-bool-false-bytes-compiled-pattern`, `workflow-module-sub-count-keyword-str-compiled-pattern`, `workflow-module-sub-count-indexlike-bytes-compiled-pattern`, `workflow-module-sub-count-bool-true-str-compiled-pattern`, `workflow-module-subn-count-keyword-bytes-compiled-pattern`, `workflow-module-subn-count-indexlike-str-compiled-pattern`, and `workflow-module-subn-count-bool-false-bytes-compiled-pattern`;
  - keep the shared `collection_replacement_boundary.py` manifest as the only benchmark manifest for this slice;
  - keep all existing raw-module and direct-`Pattern` collection/replacement rows unchanged; and
  - do not widen into compiled-pattern keyword-error rows, wrong-text-model rows, direct `Pattern` keyword carriers, new manifests, or unrelated benchmark-harness churn in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking a compiled-pattern module-helper benchmark suite:
  - update the collection-replacement manifest expectations from `43` measured workloads to `52`, still with `0` known gaps on that manifest once `RBR-0854` has landed;
  - keep the manifest on the existing `post-parser-workflows` / combined-boundary path and wire the nine new workloads to the exact correctness case ids listed above;
  - update the combined publication totals from `822` total / `822` measured / `0` known gaps across `30` manifests to `831` / `831` / `0` across the same `30` manifests;
  - update `REPORT["summary"]["module_workloads"]` from `814` to `823`;
  - keep `REPORT["summary"]["regression_workloads"]` at `8`; and
  - keep the built-native smoke manifest set unchanged in this run.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `selected_workload_count == 43`, `measured_workloads == 43`, and `known_gap_count == 0` to `52`, `52`, and `0`;
  - the nine new compiled-pattern-first-argument keyword-carrier workloads publish real `rebar` timings with `status == "measured"`, not placeholders; and
  - the tracked report exposes those exact workload ids on the existing collection/replacement benchmark surface.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0856-compiled-pattern-keyword-carriers.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not widen the correctness surface, change Rust/Python regex behavior, or broaden the compiled-pattern benchmark route beyond the exact keyword-carrier nonet.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another compiled-pattern module-helper benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.

## Notes
- `RBR-0856` is the next available feature task id in the current checkout:
  - `RBR-0855` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0854` on the same `module-workflow-surface` frontier so the remaining successful compiled-pattern-first-argument collection/replacement keyword carriers catch up on the existing Python-path `collection_replacement_boundary.py` benchmark surface before wrong-text-model follow-ons or broader compiled-pattern module-helper publication work reopen the queue.
- 2026-03-21 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'compiled_pattern and keyword and (split or sub or subn) and not unexpected and not duplicate'` passed in this run (`18 passed, 1190 deselected in 0.14s`), and a direct runtime probe in this run showed CPython and `rebar` already agree on the exact nine bounded compiled-pattern-first-argument `split()` / `sub()` / `subn()` keyword-carrier outcomes listed above, so this remains a benchmark/publication task rather than a missing runtime-implementation prerequisite;
  - `benchmarks/workloads/collection_replacement_boundary.py` currently contains `0` compiled-pattern collection/replacement rows on the shared benchmark surface even though the correctness owner already publishes the full adjacent nine-row keyword-carrier slice;
  - `RBR-0854` is already queued immediately ahead of this task to land the shared compiled-pattern-first-argument benchmark path and the six adjacent compiled-pattern keyword-error rows on the same owner manifest; and
  - `reports/benchmarks/latest.py` currently reports `816` total / `816` measured / `0` known gaps overall, with `REPORT["summary"]["module_workloads"] == 808` and `REPORT["manifests"]["collection-replacement-boundary"]` at `37` selected / `37` measured / `0` known gaps because `RBR-0854` is still ready in this run, so the acceptance counts above are intentionally written against the immediate post-`RBR-0854` state.
