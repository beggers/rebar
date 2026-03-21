# RBR-0854: Catch up the compiled-pattern module keyword-error collection/replacement benchmark sextet

Status: ready
Owner: feature-implementation
Created: 2026-03-21

## Goal
- Extend the published Python-path collection/replacement benchmark surface with the adjacent compiled-pattern-first-argument `split()` / `sub()` / `subn()` duplicate and unexpected keyword sextet that the shared `module-workflow-surface` correctness path already publishes, while keeping this catch-up on the existing `collection_replacement_boundary.py` manifest instead of opening a separate compiled-pattern module-helper benchmark family.

## Pattern Pair
- `re.compile("abc")` through `split(re.compile("abc"), "abc", 1, maxsplit=1)`, `sub(re.compile("abc"), "x", "abc", 1, count=1)`, and `sub(re.compile("abc"), "x", "abc", missing=1)`
- `re.compile(b"abc")` through `split(re.compile(b"abc"), b"abc", missing=1)`, `subn(re.compile(b"abc"), b"x", b"abc", 1, count=1)`, and `subn(re.compile(b"abc"), b"x", b"abc", missing=1)`

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `python/rebar_harness/benchmarks.py` keeps the tracked Python-path benchmark publication stable while extending the shared collection/replacement helper path from raw-pattern keyword-error rows to the exact compiled-pattern-first-argument keyword-error sextet:
  - allow bounded `module.split`, `module.sub`, and `module.subn` workloads on the shared collection/replacement surface to request that the first helper argument be a backend-compiled pattern object built from the manifest `pattern` and `flags`, while the timed callback still measures the module helper call rather than pattern compilation;
  - preserve the real duplicate-keyword rejection boundary for `split()` / `sub()` / `subn()` by keeping the positional `maxsplit` / `count` carriers present alongside keyword `maxsplit` / `count` in the timed call instead of pre-collapsing them before invocation;
  - preserve the adjacent compiled-pattern unexpected-keyword `TypeError` outcomes on the existing `expected_exception` path instead of rejecting those workloads during manifest normalization; and
  - keep this support scoped to the shared `collection_replacement_boundary.py` surface. Do not broaden into successful compiled-pattern keyword carriers, raw-module rows, compiled-pattern `search()` / `match()` / `fullmatch()` helpers, direct `Pattern` method rows, new manifests, or unrelated benchmark-schema churn in this run.
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly six new compiled-pattern-first-argument workloads:
  - add `module-split-duplicate-maxsplit-keyword-purged-str-compiled-pattern`;
  - add `module-split-unexpected-keyword-purged-bytes-compiled-pattern`;
  - add `module-sub-duplicate-count-keyword-warm-str-compiled-pattern`;
  - add `module-sub-unexpected-keyword-purged-str-compiled-pattern`;
  - add `module-subn-duplicate-count-keyword-warm-bytes-compiled-pattern`; and
  - add `module-subn-unexpected-keyword-purged-bytes-compiled-pattern`.
- Keep those six workloads pinned to the exact already-published module-workflow keyword-error anchors rather than inventing a broader helper family:
  - `module-split-duplicate-maxsplit-keyword-purged-str-compiled-pattern` uses `operation == "module.split"`, `pattern == "abc"`, `haystack == "abc"`, `text_model == "str"`, `cache_mode == "purged"`, `timing_scope == "module-helper-call"`, `flags == 0`, `maxsplit == 1`, an explicit compiled-pattern-first-argument marker, `kwargs == {"maxsplit": 1}`, and `expected_exception == {"type": "TypeError", "message_substring": "multiple values for argument 'maxsplit'"}`;
  - `module-split-unexpected-keyword-purged-bytes-compiled-pattern` uses `operation == "module.split"`, `pattern == "abc"`, `haystack == "abc"`, `text_model == "bytes"`, `cache_mode == "purged"`, `timing_scope == "module-helper-call"`, `flags == 0`, an explicit compiled-pattern-first-argument marker, `kwargs == {"missing": 1}`, and `expected_exception == {"type": "TypeError", "message_substring": "unexpected keyword argument 'missing'"}`;
  - `module-sub-duplicate-count-keyword-warm-str-compiled-pattern` uses `operation == "module.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abc"`, `text_model == "str"`, `cache_mode == "warm"`, `timing_scope == "module-helper-call"`, `flags == 0`, `count == 1`, an explicit compiled-pattern-first-argument marker, `kwargs == {"count": 1}`, and `expected_exception == {"type": "TypeError", "message_substring": "multiple values for argument 'count'"}`;
  - `module-sub-unexpected-keyword-purged-str-compiled-pattern` uses `operation == "module.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abc"`, `text_model == "str"`, `cache_mode == "purged"`, `timing_scope == "module-helper-call"`, `flags == 0`, an explicit compiled-pattern-first-argument marker, `kwargs == {"missing": 1}`, and `expected_exception == {"type": "TypeError", "message_substring": "unexpected keyword argument 'missing'"}`;
  - `module-subn-duplicate-count-keyword-warm-bytes-compiled-pattern` uses `operation == "module.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abc"`, `text_model == "bytes"`, `cache_mode == "warm"`, `timing_scope == "module-helper-call"`, `flags == 0`, `count == 1`, an explicit compiled-pattern-first-argument marker, `kwargs == {"count": 1}`, and `expected_exception == {"type": "TypeError", "message_substring": "multiple values for argument 'count'"}`;
  - `module-subn-unexpected-keyword-purged-bytes-compiled-pattern` uses `operation == "module.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abc"`, `text_model == "bytes"`, `cache_mode == "purged"`, `timing_scope == "module-helper-call"`, `flags == 0`, an explicit compiled-pattern-first-argument marker, `kwargs == {"missing": 1}`, and `expected_exception == {"type": "TypeError", "message_substring": "unexpected keyword argument 'missing'"}`;
  - keep the str and bytes split explicit at the already-published correctness anchors; and
  - do not broaden into successful compiled-pattern keyword carriers, wrong-text-model rows, direct `Pattern` keyword errors, smoke-only variants, or another benchmark manifest in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking a compiled-pattern module-helper benchmark suite:
  - update the collection-replacement manifest expectations from `37` measured workloads to `43`, still with `0` known gaps on that manifest once `RBR-0852` has landed;
  - keep the manifest on the existing `post-parser-workflows` / combined-boundary path and anchor the six new workloads to the already-published correctness case ids `workflow-module-split-duplicate-maxsplit-keyword-str-compiled-pattern`, `workflow-module-split-unexpected-keyword-bytes-compiled-pattern`, `workflow-module-sub-duplicate-count-keyword-str-compiled-pattern`, `workflow-module-sub-unexpected-keyword-str-compiled-pattern`, `workflow-module-subn-duplicate-count-keyword-bytes-compiled-pattern`, and `workflow-module-subn-unexpected-keyword-bytes-compiled-pattern`;
  - update the combined publication totals from `816` total / `816` measured / `0` known gaps across `30` manifests to `822` / `822` / `0` across the same `30` manifests;
  - update `REPORT["summary"]["module_workloads"]` from `808` to `814`;
  - keep `REPORT["summary"]["regression_workloads"]` at `8`; and
  - keep the built-native smoke manifest set and every existing raw-module or direct-`Pattern` collection/replacement workload unchanged in this run.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `selected_workload_count == 37`, `measured_workloads == 37`, and `known_gap_count == 0` to `43`, `43`, and `0`;
  - the six new compiled-pattern-first-argument keyword-error workloads publish real `rebar` timings with `status == "measured"`, not synthetic placeholders; and
  - the tracked report exposes those exact workload ids on the existing collection/replacement benchmark surface.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0854-compiled-pattern-keyword-errors.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not widen the correctness surface, add successful compiled-pattern keyword-carrier workloads, or change Rust/Python regex behavior just to support a larger benchmark family.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another compiled-pattern module-helper benchmark manifest, another benchmark suite, or detached benchmark expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.

## Notes
- `RBR-0854` is the next available feature task id in the current checkout:
  - `RBR-0853` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0852` on the same `module-workflow-surface` frontier so the adjacent compiled-pattern-first-argument collection/replacement keyword-error slice catches up on the existing Python-path `collection_replacement_boundary.py` benchmark surface before successful compiled-pattern keyword carriers or broader compiled-pattern module-helper follow-ons reopen the queue.
- 2026-03-21 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'compiled_pattern and keyword and (split or sub or subn)'` passed in this run (`30 passed, 1178 deselected in 0.14s`), and a direct runtime probe in this run showed CPython and `rebar` already agree on the exact bounded `TypeError` messages for the six compiled-pattern-first-argument `split()` / `sub()` / `subn()` duplicate and unexpected keyword cases, so this remains a benchmark/publication task rather than a missing runtime-implementation prerequisite;
  - `python/rebar_harness/benchmarks.py` currently has no compiled-pattern-first-argument workload shape on the shared module-helper benchmark path, so the published collection/replacement surface still cannot time the adjacent compiled-pattern module-helper keyword-error slice even though the runtime behavior already exists;
  - `benchmarks/workloads/collection_replacement_boundary.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and `reports/benchmarks/latest.py` currently stop at raw-module and direct-`Pattern` collection/replacement keyword rows and do not yet publish any compiled-pattern-first-argument collection/replacement workloads on that manifest; and
  - `reports/benchmarks/latest.py` currently reports `813` total / `813` measured / `0` known gaps overall, with `REPORT["summary"]["module_workloads"] == 805` and `REPORT["manifests"]["collection-replacement-boundary"]` at `34` selected / `34` measured / `0` known gaps because `RBR-0852` is still ready in this run, so the acceptance counts above are intentionally written against the immediate post-`RBR-0852` state.
