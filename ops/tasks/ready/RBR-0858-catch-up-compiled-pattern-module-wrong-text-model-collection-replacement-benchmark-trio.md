# RBR-0858: Catch up the compiled-pattern module wrong-text-model collection/replacement benchmark trio

Status: ready
Owner: feature-implementation
Created: 2026-03-21

## Goal
- Extend the published Python-path collection/replacement benchmark surface with the adjacent compiled-pattern-first-argument wrong-text-model `split()` / `sub()` / `subn()` `TypeError` trio that the shared `module-workflow-surface` correctness path already publishes, while keeping this catch-up on the existing `collection_replacement_boundary.py` manifest and adding only the minimal benchmark-harness support needed to express a haystack text model that intentionally differs from the compiled pattern.

## Pattern Pair
- `re.compile("abc")` through `split(re.compile("abc"), b"zabczz", 1)` and `sub(re.compile("abc"), "x", b"zabczz", 1)`
- `re.compile(b"abc")` through `subn(re.compile(b"abc"), b"x", "zabczz", 1)`

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `python/rebar_harness/benchmarks.py` keeps the tracked Python-path benchmark publication stable while adding only the bounded mixed-text helper support needed for this shared collection/replacement slice:
  - allow `module.split`, `module.sub`, and `module.subn` workloads on the shared collection/replacement surface to specify a haystack text model that intentionally differs from the workload `text_model`, so a compiled `str` pattern can receive a bytes haystack and a compiled bytes pattern can receive a str haystack without changing how the pattern or replacement payload is materialized;
  - keep the default behavior unchanged when no explicit haystack text-model override is present, so existing manifests still route both pattern and haystack through the current `text_model` path;
  - preserve the real timed `TypeError` outcomes on the shared `expected_exception` path instead of pre-validating these mixed-text helper rows away; and
  - keep this support scoped to the shared `collection_replacement_boundary.py` owner path for the bounded compiled-pattern-first-argument wrong-text-model trio. Do not broaden into raw-module wrong-text-model rows, direct `Pattern` rows, new manifests, or unrelated benchmark-schema churn in this run.
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly three compiled-pattern-first-argument wrong-text-model workloads:
  - add `module-split-on-bytes-string-purged-str-compiled-pattern`;
  - add `module-sub-on-bytes-string-warm-str-compiled-pattern`; and
  - add `module-subn-on-str-string-purged-bytes-compiled-pattern`.
- Keep those three workloads pinned to the exact already-published module-workflow wrong-text-model anchors rather than inventing a broader helper family:
  - `module-split-on-bytes-string-purged-str-compiled-pattern` uses `operation == "module.split"`, `pattern == "abc"`, `haystack == "zabczz"`, `text_model == "str"`, a bounded haystack text-model override for `bytes`, `cache_mode == "purged"`, `timing_scope == "module-helper-call"`, `flags == 0`, `maxsplit == 1`, an explicit compiled-pattern-first-argument marker, and `expected_exception == {"type": "TypeError", "message_substring": "cannot use a string pattern on a bytes-like object"}`;
  - `module-sub-on-bytes-string-warm-str-compiled-pattern` uses `operation == "module.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "zabczz"`, `text_model == "str"`, a bounded haystack text-model override for `bytes`, `cache_mode == "warm"`, `timing_scope == "module-helper-call"`, `flags == 0`, `count == 1`, an explicit compiled-pattern-first-argument marker, and `expected_exception == {"type": "TypeError", "message_substring": "cannot use a string pattern on a bytes-like object"}`;
  - `module-subn-on-str-string-purged-bytes-compiled-pattern` uses `operation == "module.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "zabczz"`, `text_model == "bytes"`, a bounded haystack text-model override for `str`, `cache_mode == "purged"`, `timing_scope == "module-helper-call"`, `flags == 0`, `count == 1`, an explicit compiled-pattern-first-argument marker, and `expected_exception == {"type": "TypeError", "message_substring": "cannot use a bytes pattern on a string-like object"}`;
  - anchor the three workloads to `workflow-module-split-str-compiled-pattern-on-bytes-string`, `workflow-module-sub-str-compiled-pattern-on-bytes-string`, and `workflow-module-subn-bytes-compiled-pattern-on-str-string`;
  - keep the str/bytes split explicit on the shared owner path even though all three rows raise `TypeError`; and
  - do not widen into compiled-pattern keyword rows, search/match/fullmatch/findall/finditer wrong-text-model rows, direct `Pattern` helper rows, smoke-only variants, or another benchmark manifest in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking another compiled-pattern helper benchmark suite:
  - add focused contract coverage for the bounded haystack text-model override on compiled-pattern collection/replacement workloads, proving the override round-trips through manifest loading, callback construction, internal probe execution, and timed `TypeError` matching against CPython;
  - update the collection-replacement manifest expectations from `52` measured workloads to `55`, still with `0` known gaps on that manifest once `RBR-0856` has landed;
  - keep the manifest on the existing `post-parser-workflows` / combined-boundary path and wire the three new workloads to the exact correctness case ids listed above;
  - update the combined publication totals from `831` total / `831` measured / `0` known gaps across `30` manifests to `834` / `834` / `0` across the same `30` manifests;
  - update `REPORT["summary"]["module_workloads"]` from `823` to `826`;
  - keep `REPORT["summary"]["regression_workloads"]` at `8`; and
  - keep the built-native smoke manifest set unchanged in this run.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `selected_workload_count == 52`, `measured_workloads == 52`, and `known_gap_count == 0` to `55`, `55`, and `0`;
  - the three new compiled-pattern-first-argument wrong-text-model workloads publish real `rebar` timings with `status == "measured"`, not placeholders; and
  - the tracked report exposes those exact workload ids on the existing collection/replacement benchmark surface.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0858-compiled-pattern-wrong-text-model.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not widen the correctness surface or change Rust/Python regex behavior just to support a larger benchmark family.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another compiled-pattern module-helper benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.

## Notes
- `RBR-0858` is the next available feature task id in the current checkout:
  - `RBR-0857` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0856` on the same `module-workflow-surface` frontier so the adjacent compiled-pattern-first-argument collection/replacement wrong-text-model trio catches up on the existing Python-path `collection_replacement_boundary.py` benchmark surface before broader compiled-pattern module-helper publication work reopens the queue.
- 2026-03-21 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier but still needs the bounded benchmark-harness prerequisite folded into the same run:
  - `tests/python/test_module_workflow_parity_suite.py` already publishes the exact adjacent correctness anchors `workflow-module-split-str-compiled-pattern-on-bytes-string`, `workflow-module-sub-str-compiled-pattern-on-bytes-string`, and `workflow-module-subn-bytes-compiled-pattern-on-str-string`;
  - direct runtime probes in this run showed CPython and `rebar` already agree on the exact bounded `TypeError` payloads for `split(re.compile("abc"), b"zabczz", 1)`, `sub(re.compile("abc"), "x", b"zabczz", 1)`, and `subn(re.compile(b"abc"), b"x", "zabczz", 1)`, so no Rust or Python regex-behavior prerequisite is missing;
  - the current benchmark workload schema routes `haystack` through the workload-wide `text_model`, which leaves these mixed-text compiled-pattern helper rows unexpressible on the published benchmark surface today even though the runtime behavior already exists; and
  - `reports/benchmarks/latest.py` currently reports `822` total / `822` measured / `0` known gaps overall, with `REPORT["summary"]["module_workloads"] == 814` and `REPORT["manifests"]["collection-replacement-boundary"]` at `43` selected / `43` measured / `0` known gaps because `RBR-0856` is still ready in this run, so the acceptance counts above are intentionally written against the immediate post-`RBR-0856` state.
