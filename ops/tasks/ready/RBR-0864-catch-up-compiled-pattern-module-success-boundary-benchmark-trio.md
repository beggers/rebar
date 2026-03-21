# RBR-0864: Catch up the compiled-pattern module success boundary benchmark trio

Status: ready
Owner: feature-implementation
Created: 2026-03-21

## Goal
- Extend the published Python-path `module_boundary.py` benchmark surface with the adjacent compiled-pattern-first-argument successful `search()` / `match()` / `fullmatch()` trio that the shared `module-workflow-surface` correctness path already publishes, reusing the bounded module-helper compiled-pattern timing support on that owner path instead of widening the benchmark runner again.

## Pattern Pair
- `re.compile("abc")` through `search(re.compile("abc"), "zzabczz")` and `match(re.compile("abc"), "abcdef")`
- `re.compile(b"abc")` through `fullmatch(re.compile(b"abc"), b"abc")`

## Deliverables
- `benchmarks/workloads/module_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/module_boundary.py` remains the only benchmark manifest for this slice and grows by exactly three compiled-pattern-first-argument success workloads:
  - add `module-search-literal-warm-hit-str-compiled-pattern`;
  - add `module-match-literal-warm-hit-str-compiled-pattern`; and
  - add `module-fullmatch-literal-purged-hit-bytes-compiled-pattern`.
- Keep those three workloads pinned to the exact already-published module-workflow compiled-pattern anchors rather than inventing a broader helper family:
  - `module-search-literal-warm-hit-str-compiled-pattern` uses `operation == "module.search"`, `pattern == "abc"`, `haystack == "zzabczz"`, `text_model == "str"`, `cache_mode == "warm"`, `timing_scope == "module-helper-call"`, `flags == 0`, an explicit compiled-pattern-first-argument marker, and no `expected_exception`;
  - `module-match-literal-warm-hit-str-compiled-pattern` uses `operation == "module.match"`, `pattern == "abc"`, `haystack == "abcdef"`, `text_model == "str"`, `cache_mode == "warm"`, `timing_scope == "module-helper-call"`, `flags == 0`, an explicit compiled-pattern-first-argument marker, and no `expected_exception`;
  - `module-fullmatch-literal-purged-hit-bytes-compiled-pattern` uses `operation == "module.fullmatch"`, `pattern == "abc"`, `haystack == "abc"`, `text_model == "bytes"`, `cache_mode == "purged"`, `timing_scope == "module-helper-call"`, `flags == 0`, an explicit compiled-pattern-first-argument marker, and no `expected_exception`;
  - anchor the three workloads to `workflow-module-search-str-compiled-pattern`, `workflow-module-match-str-compiled-pattern`, and `workflow-module-fullmatch-bytes-compiled-pattern`;
  - keep the str/bytes split explicit on the shared owner path even though all three rows now succeed; and
  - do not widen into wrong-text-model rows beyond `RBR-0862`, bounded wildcard or verbose-regression compiled-pattern rows, keyword carriers, collection/replacement helpers, direct `Pattern` rows, smoke-only variants, or another benchmark manifest in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking another compiled-pattern helper benchmark suite:
  - add focused contract coverage for the bounded compiled-pattern `module.search` / `module.match` / `module.fullmatch` success trio, proving the rows round-trip through manifest loading, callback construction, internal probe execution, and correctness-anchor mapping without recompiling inside the timed callback;
  - update the module-boundary manifest expectations from `16` measured workloads to `19`, still with `0` known gaps on that manifest once `RBR-0862` has landed;
  - keep the manifest on the existing `post-parser-workflows` / combined-boundary path and wire the three new workloads to the exact correctness case ids listed above;
  - update the combined publication totals from `839` total / `839` measured / `0` known gaps across `30` manifests to `842` / `842` / `0` across the same `30` manifests;
  - update `REPORT["summary"]["module_workloads"]` from `831` to `834`;
  - keep `REPORT["summary"]["regression_workloads"]` at `8`; and
  - keep the built-native smoke manifest set unchanged in this run.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["module-boundary"]` moves from `selected_workload_count == 16`, `measured_workloads == 16`, and `known_gap_count == 0` to `19`, `19`, and `0`;
  - the three new compiled-pattern-first-argument success workloads publish real `rebar` timings with `status == "measured"`, not placeholders; and
  - the tracked report exposes those exact workload ids on the existing module-boundary benchmark surface.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/module_boundary.py --report .rebar/tmp/rbr-0864-compiled-pattern-module-success-boundary.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not widen the correctness surface or change Rust/Python regex behavior just to support a larger benchmark family.
- Reuse the existing `module_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another compiled-pattern module-helper benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.

## Notes
- `RBR-0864` is the next available feature task id in the current checkout:
  - `RBR-0862` is already occupied by the ready feature task in `ops/tasks/ready/`;
  - `RBR-0863` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0862` on the same `module-workflow-surface` frontier so the adjacent compiled-pattern-first-argument successful `search()` / `match()` / `fullmatch()` trio catches up on the existing Python-path `module_boundary.py` benchmark surface before bounded wildcard, verbose-regression, or broader compiled-pattern module-helper publication reopens the queue.
- 2026-03-21 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier but depends on the bounded benchmark-path expansion already queued in `RBR-0862`:
  - `tests/python/test_module_workflow_parity_suite.py` already publishes the exact adjacent correctness anchors `workflow-module-search-str-compiled-pattern`, `workflow-module-match-str-compiled-pattern`, and `workflow-module-fullmatch-bytes-compiled-pattern`;
  - direct runtime probes in this run showed CPython and `rebar` already agree on the bounded matched-result payloads for `search(rebar.compile("abc"), "zzabczz")`, `match(rebar.compile("abc"), "abcdef")`, and `fullmatch(rebar.compile(b"abc"), b"abc")`, so no Rust or Python regex-behavior prerequisite is missing;
  - `benchmarks/workloads/module_boundary.py` currently publishes no compiled-pattern module-boundary success rows, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently carries no compiled-pattern module-boundary success anchor-contract definition on that owner path; and
  - the acceptance counts above are intentionally written against the immediate post-`RBR-0862` state of `839` total / `839` measured / `0` known gaps overall with `REPORT["summary"]["module_workloads"] == 831` and `REPORT["manifests"]["module-boundary"]` at `16` selected / `16` measured / `0` known gaps.
