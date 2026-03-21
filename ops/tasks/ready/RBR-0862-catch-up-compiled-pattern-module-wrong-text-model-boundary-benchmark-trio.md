# RBR-0862: Catch up the compiled-pattern module wrong-text-model boundary benchmark trio

Status: ready
Owner: feature-implementation
Created: 2026-03-21

## Goal
- Extend the published Python-path `module_boundary.py` benchmark surface with the adjacent compiled-pattern-first-argument `search()` / `match()` / `fullmatch()` wrong-text-model `TypeError` trio that the shared `module-workflow-surface` correctness path already publishes, while widening the benchmark runner only enough to time those exact mixed-text helper rows on the existing module-boundary owner path.

## Pattern Pair
- `re.compile("abc")` through `search(re.compile("abc"), b"abc")` and `fullmatch(re.compile("abc"), b"abc")`
- `re.compile(b"abc")` through `match(re.compile(b"abc"), "abc")`

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/module_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `python/rebar_harness/benchmarks.py` keeps the tracked Python-path benchmark publication stable while widening the bounded compiled-pattern module-helper path only enough for this exact module-boundary trio:
  - extend compiled-pattern-first-argument benchmark support from the current `module.split` / `module.sub` / `module.subn` collection-replacement slice to the adjacent `module.search`, `module.match`, and `module.fullmatch` helper trio on the shared source-tree shim path;
  - keep compiled-pattern benchmark rows requiring `cache_mode` values that exclude compile time from the timed callback, and do not broaden into `cold` compiled-pattern module-helper timing in this run;
  - widen the bounded `haystack_text_model` override validation from `collection-replacement-boundary` just enough to cover the exact compiled-pattern-first-argument wrong-text-model `module.search` / `module.match` / `module.fullmatch` trio on `module-boundary`;
  - preserve the real timed mixed-text `TypeError` outcomes on the shared `expected_exception` path instead of pre-validating these rows away; and
  - keep this support scoped to the existing `module_boundary.py` owner path for the exact compiled-pattern-first-argument wrong-text-model trio. Do not broaden into successful compiled-pattern `search()` / `match()` / `fullmatch()` rows, keyword-argument carriers, `split()` / `findall()` / `finditer()` / `sub()` / `subn()` rows beyond `RBR-0860`, direct `Pattern` rows, new manifests, or unrelated benchmark-schema churn in this run.
- `benchmarks/workloads/module_boundary.py` remains the only benchmark manifest for this slice and grows by exactly three compiled-pattern-first-argument wrong-text-model workloads:
  - add `module-search-on-bytes-string-warm-str-compiled-pattern`;
  - add `module-match-on-str-string-purged-bytes-compiled-pattern`; and
  - add `module-fullmatch-on-bytes-string-warm-str-compiled-pattern`.
- Keep those three workloads pinned to the exact already-published module-workflow wrong-text-model anchors rather than inventing a broader helper family:
  - `module-search-on-bytes-string-warm-str-compiled-pattern` uses `operation == "module.search"`, `pattern == "abc"`, `haystack == "abc"`, `text_model == "str"`, a bounded haystack text-model override for `bytes`, `cache_mode == "warm"`, `timing_scope == "module-helper-call"`, `flags == 0`, an explicit compiled-pattern-first-argument marker, and `expected_exception == {"type": "TypeError", "message_substring": "cannot use a string pattern on a bytes-like object"}`;
  - `module-match-on-str-string-purged-bytes-compiled-pattern` uses `operation == "module.match"`, `pattern == "abc"`, `haystack == "abc"`, `text_model == "bytes"`, a bounded haystack text-model override for `str`, `cache_mode == "purged"`, `timing_scope == "module-helper-call"`, `flags == 0`, an explicit compiled-pattern-first-argument marker, and `expected_exception == {"type": "TypeError", "message_substring": "cannot use a bytes pattern on a string-like object"}`;
  - `module-fullmatch-on-bytes-string-warm-str-compiled-pattern` uses `operation == "module.fullmatch"`, `pattern == "abc"`, `haystack == "abc"`, `text_model == "str"`, a bounded haystack text-model override for `bytes`, `cache_mode == "warm"`, `timing_scope == "module-helper-call"`, `flags == 0`, an explicit compiled-pattern-first-argument marker, and `expected_exception == {"type": "TypeError", "message_substring": "cannot use a string pattern on a bytes-like object"}`;
  - anchor the three workloads to `workflow-module-search-str-compiled-pattern-on-bytes-string`, `workflow-module-match-bytes-compiled-pattern-on-str-string`, and `workflow-module-fullmatch-str-compiled-pattern-on-bytes-string`;
  - keep the str/bytes split explicit on the shared owner path even though all three rows raise `TypeError`; and
  - do not widen into successful compiled-pattern `search()` / `match()` / `fullmatch()` rows, raw-module wrong-text-model rows, `split()` / `findall()` / `finditer()` / `sub()` / `subn()` rows, smoke-only variants, or another benchmark manifest in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking another compiled-pattern helper benchmark suite:
  - add focused contract coverage for the bounded haystack text-model override on compiled-pattern `module.search` / `module.match` / `module.fullmatch` workloads, proving the override round-trips through manifest loading, callback construction, internal probe execution, and timed `TypeError` matching against CPython;
  - update the module-boundary manifest expectations from `13` measured workloads to `16`, still with `0` known gaps on that manifest;
  - keep the manifest on the existing `post-parser-workflows` / combined-boundary path and wire the three new workloads to the exact correctness case ids listed above;
  - update the combined publication totals from `834` total / `834` measured / `0` known gaps across `30` manifests to `837` / `837` / `0` across the same `30` manifests;
  - update `REPORT["summary"]["module_workloads"]` from `826` to `829`;
  - keep `REPORT["summary"]["regression_workloads"]` at `8`; and
  - keep the built-native smoke manifest set unchanged in this run.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["module-boundary"]` moves from `selected_workload_count == 13`, `measured_workloads == 13`, and `known_gap_count == 0` to `16`, `16`, and `0`;
  - the three new compiled-pattern-first-argument wrong-text-model workloads publish real `rebar` timings with `status == "measured"`, not placeholders; and
  - the tracked report exposes those exact workload ids on the existing module-boundary benchmark surface.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/module_boundary.py --report .rebar/tmp/rbr-0862-compiled-pattern-module-boundary-wrong-text-model.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not widen the correctness surface or change Rust/Python regex behavior just to support a larger benchmark family.
- Reuse the existing `module_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another compiled-pattern module-helper benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.

## Notes
- `RBR-0862` is the next available feature task id in the current checkout:
  - `RBR-0860` is already occupied by the ready feature task in `ops/tasks/ready/`;
  - `RBR-0861` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0860` on the same `module-workflow-surface` frontier so the adjacent compiled-pattern-first-argument `search()` / `match()` / `fullmatch()` wrong-text-model trio catches up on the existing Python-path `module_boundary.py` benchmark surface before broader compiled-pattern module-helper benchmark publication reopens the queue.
- 2026-03-21 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier but still needs the bounded benchmark-harness prerequisite folded into the same run:
  - `tests/conformance/fixtures/module_workflow_surface.py` already publishes the exact adjacent correctness anchors `workflow-module-search-str-compiled-pattern-on-bytes-string`, `workflow-module-match-bytes-compiled-pattern-on-str-string`, and `workflow-module-fullmatch-str-compiled-pattern-on-bytes-string`;
  - direct runtime probes in this run showed CPython and `rebar` already agree on the exact bounded `TypeError` payloads for `search(rebar.compile("abc"), b"abc")`, `match(rebar.compile(b"abc"), "abc")`, and `fullmatch(rebar.compile("abc"), b"abc")`, so no Rust or Python regex-behavior prerequisite is missing;
  - `python/rebar_harness/benchmarks.py` currently restricts compiled-pattern benchmark workloads to `module.split`, `module.sub`, and `module.subn`, and it currently restricts `haystack_text_model` overrides to the `collection-replacement-boundary` manifest, so these module-boundary rows are still unexpressible on the published benchmark surface today even though the runtime behavior already exists; and
  - `benchmarks/workloads/module_boundary.py` plus `reports/benchmarks/latest.py` currently publish no compiled-pattern module-helper rows, so the acceptance counts above are intentionally written against the immediate post-`RBR-0860` state.
