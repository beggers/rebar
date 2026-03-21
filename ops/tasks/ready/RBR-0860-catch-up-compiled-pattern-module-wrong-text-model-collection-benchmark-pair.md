# RBR-0860: Catch up the compiled-pattern module wrong-text-model collection benchmark pair

Status: ready
Owner: feature-implementation
Created: 2026-03-21

## Goal
- Extend the published Python-path collection benchmark surface with the remaining adjacent compiled-pattern-first-argument `findall()` / `finditer()` wrong-text-model `TypeError` pair that the shared `module-workflow-surface` correctness path already publishes, while keeping this catch-up on the existing `collection_replacement_boundary.py` manifest and adding only the minimal benchmark-runner support needed to time the currently unsupported `module.finditer` helper path on that shared owner surface.

## Pattern Pair
- `re.compile(b"abc")` through `findall(re.compile(b"abc"), "zabczz")`
- `re.compile("abc")` through `finditer(re.compile("abc"), b"zabczz")`

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `python/rebar_harness/benchmarks.py` keeps the tracked Python-path benchmark publication stable while extending the post-`RBR-0858` compiled-pattern mixed-text collection helper path from `split()` / `sub()` / `subn()` to the adjacent `findall()` / `finditer()` pair:
  - keep the `RBR-0858` haystack text-model override behavior unchanged for compiled-pattern-first-argument `split()` / `sub()` / `subn()` workloads once that task lands;
  - allow `module.findall` workloads on the shared collection/replacement surface to reuse that bounded haystack text-model override path so a compiled bytes pattern can receive a str haystack without changing how the pattern object is materialized;
  - add bounded `module.finditer` support on the shared benchmark runner, consuming the iterator eagerly on the timed callback/probe path so the operation can be benchmarked and compared against CPython without inventing a detached collection runner;
  - preserve the real timed mixed-text `TypeError` outcomes on the shared `expected_exception` path instead of pre-validating these rows away; and
  - keep this support scoped to the shared `collection_replacement_boundary.py` owner path for the exact compiled-pattern-first-argument wrong-text-model collection pair. Do not broaden into successful compiled-pattern collection rows, raw-module wrong-text-model rows, `search()` / `match()` / `fullmatch()` helpers, direct `Pattern` rows, new manifests, or unrelated benchmark-schema churn in this run.
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly two compiled-pattern-first-argument wrong-text-model workloads:
  - add `module-findall-on-str-string-purged-bytes-compiled-pattern`; and
  - add `module-finditer-on-bytes-string-warm-str-compiled-pattern`.
- Keep those two workloads pinned to the exact already-published module-workflow wrong-text-model anchors rather than inventing a broader helper family:
  - `module-findall-on-str-string-purged-bytes-compiled-pattern` uses `operation == "module.findall"`, `pattern == "abc"`, `haystack == "zabczz"`, `text_model == "bytes"`, a bounded haystack text-model override for `str`, `cache_mode == "purged"`, `timing_scope == "module-helper-call"`, `flags == 0`, an explicit compiled-pattern-first-argument marker, and `expected_exception == {"type": "TypeError", "message_substring": "cannot use a bytes pattern on a string-like object"}`;
  - `module-finditer-on-bytes-string-warm-str-compiled-pattern` uses `operation == "module.finditer"`, `pattern == "abc"`, `haystack == "zabczz"`, `text_model == "str"`, a bounded haystack text-model override for `bytes`, `cache_mode == "warm"`, `timing_scope == "module-helper-call"`, `flags == 0`, an explicit compiled-pattern-first-argument marker, and `expected_exception == {"type": "TypeError", "message_substring": "cannot use a string pattern on a bytes-like object"}`;
  - anchor the two workloads to `workflow-module-findall-bytes-compiled-pattern-on-str-string` and `workflow-module-finditer-str-compiled-pattern-on-bytes-string`;
  - keep the str/bytes split explicit on the shared owner path even though both rows raise `TypeError`; and
  - do not widen into successful compiled-pattern `findall()` / `finditer()` rows, `split()` / `sub()` / `subn()` rows beyond `RBR-0858`, direct `Pattern` collection helpers, smoke-only variants, or another benchmark manifest in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking another compiled-pattern helper benchmark suite:
  - add focused contract coverage for the bounded haystack text-model override on compiled-pattern `module.findall` / `module.finditer` workloads, including the new eager iterator-consumption path for `module.finditer`, proving the override round-trips through manifest loading, callback construction, internal probe execution, and timed `TypeError` matching against CPython;
  - update the collection-replacement manifest expectations from `55` measured workloads to `57`, still with `0` known gaps on that manifest once `RBR-0858` has landed;
  - keep the manifest on the existing `post-parser-workflows` / combined-boundary path and wire the two new workloads to the exact correctness case ids listed above;
  - update the combined publication totals from `834` total / `834` measured / `0` known gaps across `30` manifests to `836` / `836` / `0` across the same `30` manifests;
  - update `REPORT["summary"]["module_workloads"]` from `826` to `828`;
  - keep `REPORT["summary"]["regression_workloads"]` at `8`; and
  - keep the built-native smoke manifest set unchanged in this run.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `selected_workload_count == 55`, `measured_workloads == 55`, and `known_gap_count == 0` to `57`, `57`, and `0`;
  - the two new compiled-pattern-first-argument wrong-text-model workloads publish real `rebar` timings with `status == "measured"`, not placeholders; and
  - the tracked report exposes those exact workload ids on the existing collection benchmark surface.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0860-compiled-pattern-collection-wrong-text-model.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not widen the correctness surface or change Rust/Python regex behavior just to support a larger benchmark family.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another compiled-pattern collection benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.

## Notes
- `RBR-0860` is the next available feature task id in the current checkout:
  - `RBR-0859` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0858` on the same `module-workflow-surface` frontier so the remaining adjacent compiled-pattern-first-argument collection wrong-text-model pair catches up on the existing Python-path `collection_replacement_boundary.py` benchmark surface before broader compiled-pattern module-helper benchmark publication reopens the queue.
- 2026-03-21 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier but still needs the bounded benchmark-harness publication work:
  - `tests/python/test_module_workflow_parity_suite.py` already publishes the exact adjacent correctness anchors `workflow-module-findall-bytes-compiled-pattern-on-str-string` and `workflow-module-finditer-str-compiled-pattern-on-bytes-string`;
  - a backend-specific direct runtime probe in this run showed CPython and `rebar` already agree on the exact bounded `TypeError` payloads for `findall(rebar.compile(b"abc"), "zabczz")` and `list(rebar.finditer(rebar.compile("abc"), b"zabczz"))`, so no Rust or Python regex-behavior prerequisite is missing;
  - `benchmarks/workloads/collection_replacement_boundary.py` currently contains no compiled-pattern `findall()` / `finditer()` rows on the shared benchmark surface, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still records `module.finditer` as an unsupported benchmark operation in the current checkout; and
  - `reports/benchmarks/latest.py` currently reports `831` total / `831` measured / `0` known gaps overall, with `REPORT["summary"]["module_workloads"] == 823` and `REPORT["manifests"]["collection-replacement-boundary"]` at `52` selected / `52` measured / `0` known gaps because `RBR-0858` is still ready in this run, so the acceptance counts above are intentionally written against the immediate post-`RBR-0858` state.
