# RBR-0866: Catch up the compiled-pattern bounded wildcard module boundary benchmark trio

Status: done
Owner: feature-implementation
Created: 2026-03-21

## Goal
- Extend the published Python-path `module_boundary.py` benchmark surface with the adjacent compiled-pattern-first-argument bounded-wildcard successful `search()` / `match()` / `fullmatch()` trio that the shared `module-workflow-surface` correctness path already publishes, reusing the bounded compiled-pattern module-helper timing path already queued in `RBR-0864` instead of widening the benchmark runner again.

## Pattern Pair
- `re.compile("a.c", re.IGNORECASE)` through `search(re.compile("a.c", re.IGNORECASE), "ABC")`
- `re.compile("a.c")` through `match(re.compile("a.c"), "abc")` and `fullmatch(re.compile("a.c"), "abc")`

## Deliverables
- `benchmarks/workloads/module_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/module_boundary.py` remains the only benchmark manifest for this slice and grows by exactly three compiled-pattern-first-argument bounded-wildcard success workloads:
  - add `module-search-bounded-wildcard-ignorecase-warm-hit-str-compiled-pattern`;
  - add `module-match-bounded-wildcard-warm-hit-str-compiled-pattern`; and
  - add `module-fullmatch-bounded-wildcard-purged-hit-str-compiled-pattern`.
- Keep those three workloads pinned to the exact already-published module-workflow compiled-pattern bounded-wildcard anchors rather than inventing a broader helper family:
  - `module-search-bounded-wildcard-ignorecase-warm-hit-str-compiled-pattern` uses `operation == "module.search"`, `pattern == "a.c"`, `haystack == "ABC"`, `text_model == "str"`, `cache_mode == "warm"`, `timing_scope == "module-helper-call"`, `flags == 2`, an explicit compiled-pattern-first-argument marker, and no `expected_exception`;
  - `module-match-bounded-wildcard-warm-hit-str-compiled-pattern` uses `operation == "module.match"`, `pattern == "a.c"`, `haystack == "abc"`, `text_model == "str"`, `cache_mode == "warm"`, `timing_scope == "module-helper-call"`, `flags == 0`, an explicit compiled-pattern-first-argument marker, and no `expected_exception`;
  - `module-fullmatch-bounded-wildcard-purged-hit-str-compiled-pattern` uses `operation == "module.fullmatch"`, `pattern == "a.c"`, `haystack == "abc"`, `text_model == "str"`, `cache_mode == "purged"`, `timing_scope == "module-helper-call"`, `flags == 0`, an explicit compiled-pattern-first-argument marker, and no `expected_exception`;
  - anchor the three workloads to `workflow-module-search-str-bounded-wildcard-ignorecase-compiled-pattern`, `workflow-module-match-str-bounded-wildcard-compiled-pattern`, and `workflow-module-fullmatch-str-bounded-wildcard-compiled-pattern`;
  - keep the bounded wildcard family explicit on the shared owner path rather than folding it into the literal compiled-pattern trio from `RBR-0864`; and
  - do not widen into wrong-text-model rows beyond `RBR-0862`, literal compiled-pattern success rows beyond `RBR-0864`, verbose-regression neighbors, keyword carriers, collection/replacement helpers, direct `Pattern` rows, smoke-only variants, or another benchmark manifest in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking another compiled-pattern helper benchmark suite:
  - add focused contract coverage for the bounded compiled-pattern wildcard `module.search` / `module.match` / `module.fullmatch` success trio, proving the rows round-trip through manifest loading, callback construction, internal probe execution, and correctness-anchor mapping without recompiling inside the timed callback;
  - reuse the bounded compiled-pattern module-helper timing support and callback expectations that `RBR-0864` leaves on the shared owner path instead of widening `python/rebar_harness/benchmarks.py` again in this run;
  - update the module-boundary manifest expectations from `19` measured workloads to `22`, still with `0` known gaps on that manifest once `RBR-0864` has landed;
  - keep the manifest on the existing `post-parser-workflows` / combined-boundary path and wire the three new workloads to the exact correctness case ids listed above;
  - update the combined publication totals from `842` total / `842` measured / `0` known gaps across `30` manifests to `845` / `845` / `0` across the same `30` manifests;
  - update `REPORT["summary"]["module_workloads"]` from `834` to `837`;
  - keep `REPORT["summary"]["regression_workloads"]` at `8`; and
  - keep the built-native smoke manifest set unchanged in this run.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["module-boundary"]` moves from `selected_workload_count == 19`, `measured_workloads == 19`, and `known_gap_count == 0` to `22`, `22`, and `0`;
  - the three new compiled-pattern-first-argument bounded-wildcard success workloads publish real `rebar` timings with `status == "measured"`, not placeholders; and
  - the tracked report exposes those exact workload ids on the existing module-boundary benchmark surface.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/module_boundary.py --report .rebar/tmp/rbr-0866-compiled-pattern-bounded-wildcard-module-boundary.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not widen the correctness surface or change Rust/Python regex behavior just to support a larger benchmark family.
- Reuse the existing `module_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another compiled-pattern module-helper benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.

## Notes
- `RBR-0866` is the next available feature task id in the current checkout:
  - `RBR-0864` is already occupied by the ready feature task in `ops/tasks/ready/`;
  - `RBR-0865` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0864` on the same `module-workflow-surface` frontier so the adjacent compiled-pattern-first-argument bounded-wildcard successful `search()` / `match()` / `fullmatch()` trio catches up on the existing Python-path `module_boundary.py` benchmark surface before verbose-regression or broader compiled-pattern module-helper publication reopens the queue.
- 2026-03-21 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and depends only on the bounded benchmark-path expansion already queued in `RBR-0864`:
  - `tests/conformance/fixtures/module_workflow_surface.py` already publishes the exact adjacent correctness anchors `workflow-module-search-str-bounded-wildcard-ignorecase-compiled-pattern`, `workflow-module-match-str-bounded-wildcard-compiled-pattern`, and `workflow-module-fullmatch-str-bounded-wildcard-compiled-pattern`;
  - a direct runtime probe in this run showed CPython and `rebar` already agree on the bounded matched-result payloads for `search(rebar.compile("a.c", re.IGNORECASE), "ABC")`, `match(rebar.compile("a.c"), "abc")`, and `fullmatch(rebar.compile("a.c"), "abc")`, so no Rust or Python regex-behavior prerequisite is missing;
  - `benchmarks/workloads/module_boundary.py` currently publishes no compiled-pattern bounded-wildcard rows, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently carries no compiled-pattern bounded-wildcard anchor-contract definition on that owner path; and
  - the acceptance counts above are intentionally written against the immediate post-`RBR-0864` state of `842` total / `842` measured / `0` known gaps overall with `REPORT["summary"]["module_workloads"] == 834` and `REPORT["manifests"]["module-boundary"]` at `19` selected / `19` measured / `0` known gaps.

## Completion
- 2026-03-21: Added the three compiled-pattern-first-argument bounded-wildcard success workloads on `benchmarks/workloads/module_boundary.py`, extended the shared source-tree contract coverage for manifest loading / anchor pinning / internal probes / precompiled callback timing, and regenerated `reports/benchmarks/latest.py` to publish the new module-boundary rows.
- Published benchmark report check from the tracked artifact now shows `REPORT["summary"] == {"total_workloads": 845, "measured_workloads": 845, "known_gap_count": 0, "module_workloads": 837, "parser_workloads": 8, "regression_workloads": 8}` and `REPORT["manifests"]["module-boundary"] == {"selected_workload_count": 22, "measured_workloads": 22, "known_gap_count": 0}` with all three new workload ids marked `status == "measured"`.
- Adjacent harness fix: `python/rebar_harness/benchmarks.py` now avoids replaying nonzero helper flags into precompiled `module.search()` / `module.match()` / `module.fullmatch()` benchmark callbacks, so the compiled-pattern IGNORECASE search row executes with CPython-compatible helper arguments while still keeping compilation outside the timed callback.
- Verification passed with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/module_boundary.py --report .rebar/tmp/rbr-0866-compiled-pattern-bounded-wildcard-module-boundary.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`
