# RBR-0868: Catch up the compiled-pattern bytes verbose-regression module boundary benchmark pair

Status: done
Owner: feature-implementation
Created: 2026-03-21

## Goal
- Extend the published Python-path `module_boundary.py` benchmark surface with the adjacent compiled-pattern-first-argument bytes verbose-regression successful `search()` / `fullmatch()` pair that the shared `module-workflow-surface` correctness path already publishes, reusing the bounded compiled-pattern module-helper timing path already queued on this owner route instead of widening the regression matrix or reopening broader compiled-pattern module-helper publication work.

## Pattern Pair
- `re.compile(b"^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $", re.VERBOSE | re.MULTILINE)` through `search(..., b"prefix\\nENV_VAR=ABCD\\nsuffix")`
- `re.compile(b"^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $", re.VERBOSE | re.MULTILINE)` through `fullmatch(..., b"ENV_VAR = 123")`

## Deliverables
- `benchmarks/workloads/module_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/module_boundary.py` remains the only benchmark manifest for this slice and grows by exactly two compiled-pattern-first-argument bytes verbose-regression success workloads:
  - add `module-search-verbose-regression-warm-hit-bytes-compiled-pattern`; and
  - add `module-fullmatch-verbose-regression-purged-hit-bytes-compiled-pattern`.
- Keep those two workloads pinned to the exact already-published module-workflow compiled-pattern verbose-regression anchors rather than inventing a broader regression family:
  - `module-search-verbose-regression-warm-hit-bytes-compiled-pattern` uses `operation == "module.search"`, `pattern == "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $"`, `haystack == "prefix\\nENV_VAR=ABCD\\nsuffix"`, `text_model == "bytes"`, `cache_mode == "warm"`, `timing_scope == "module-helper-call"`, `flags == 72`, an explicit compiled-pattern-first-argument marker, and no `expected_exception`;
  - `module-fullmatch-verbose-regression-purged-hit-bytes-compiled-pattern` uses `operation == "module.fullmatch"`, `pattern == "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $"`, `haystack == "ENV_VAR = 123"`, `text_model == "bytes"`, `cache_mode == "purged"`, `timing_scope == "module-helper-call"`, `flags == 72`, an explicit compiled-pattern-first-argument marker, and no `expected_exception`;
  - anchor the two workloads to `workflow-module-search-bytes-verbose-regression-compiled-pattern` and `workflow-module-fullmatch-bytes-verbose-regression-compiled-pattern`;
  - keep the bytes verbose-regression helper pair explicit on the shared owner path rather than folding it into the bounded wildcard trio from `RBR-0866` or the compile-only regression matrix rows; and
  - do not widen into str-side verbose-regression neighbors, multiline-only compile probes, literal or bounded-wildcard rows beyond `RBR-0866`, keyword carriers, collection/replacement helpers, direct `Pattern` rows, smoke-only variants, or another benchmark manifest in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking another compiled-pattern helper benchmark suite:
  - add focused contract coverage for the bytes compiled-pattern verbose-regression `module.search` / `module.fullmatch` success pair, proving the rows round-trip through manifest loading, callback construction, internal probe execution, and correctness-anchor mapping without recompiling inside the timed callback;
  - reuse the bounded compiled-pattern module-helper timing support already present on the shared owner path instead of widening `python/rebar_harness/benchmarks.py` again in this run;
  - update the module-boundary manifest expectations from `22` measured workloads to `24`, still with `0` known gaps on that manifest once `RBR-0866` has landed;
  - keep the manifest on the existing `post-parser-workflows` / combined-boundary path and wire the two new workloads to the exact correctness case ids listed above;
  - update the combined publication totals from `845` total / `845` measured / `0` known gaps across `30` manifests to `847` / `847` / `0` across the same `30` manifests;
  - update `REPORT["summary"]["module_workloads"]` from `837` to `839`;
  - keep `REPORT["summary"]["regression_workloads"]` at `8`; and
  - keep the built-native smoke manifest set unchanged in this run.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["module-boundary"]` moves from `selected_workload_count == 22`, `measured_workloads == 22`, and `known_gap_count == 0` to `24`, `24`, and `0`;
  - the two new compiled-pattern-first-argument bytes verbose-regression success workloads publish real `rebar` timings with `status == "measured"`, not placeholders; and
  - the tracked report exposes those exact workload ids on the existing module-boundary benchmark surface.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/module_boundary.py --report .rebar/tmp/rbr-0868-compiled-pattern-bytes-verbose-regression-module-boundary.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not widen the correctness surface or change Rust/Python regex behavior just to support a larger benchmark family.
- Reuse the existing `module_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another compiled-pattern module-helper benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.

## Notes
- `RBR-0868` is the next available feature task id in the current checkout:
  - `RBR-0866` is already occupied by the ready feature task in `ops/tasks/ready/`;
  - `RBR-0867` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0866` on the same `module-workflow-surface` frontier so the adjacent compiled-pattern-first-argument bytes verbose-regression successful `search()` / `fullmatch()` pair catches up on the existing Python-path `module_boundary.py` benchmark surface before str-side verbose-regression publication or broader compiled-pattern module-helper work reopens the queue.
- 2026-03-21 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and depends only on the bounded benchmark-path expansion already queued in `RBR-0866`:
  - `tests/conformance/fixtures/module_workflow_surface.py` already publishes the exact adjacent correctness anchors `workflow-module-search-bytes-verbose-regression-compiled-pattern` and `workflow-module-fullmatch-bytes-verbose-regression-compiled-pattern`;
  - direct runtime probes in this run showed CPython and `rebar` already agree on the bounded matched-result payloads for `search(rebar.compile(b"^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $", re.VERBOSE | re.MULTILINE), b"prefix\\nENV_VAR=ABCD\\nsuffix")` and `fullmatch(rebar.compile(b"^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $", re.VERBOSE | re.MULTILINE), b"ENV_VAR = 123")`, so no Rust or Python regex-behavior prerequisite is missing;
  - `benchmarks/workloads/module_boundary.py` currently publishes no compiled-pattern bytes verbose-regression rows, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently carries no compiled-pattern bytes verbose-regression anchor-contract definition on that owner path; and
  - the acceptance counts above are intentionally written against the immediate post-`RBR-0866` state of `845` total / `845` measured / `0` known gaps overall with `REPORT["summary"]["module_workloads"] == 837` and `REPORT["manifests"]["module-boundary"]` at `22` selected / `22` measured / `0` known gaps.

## Completion
- 2026-03-21: Added the two compiled-pattern-first-argument bytes verbose-regression success workloads to `benchmarks/workloads/module_boundary.py`, extended the shared source-tree benchmark contract expectations for the bounded bytes verbose pair, and regenerated `reports/benchmarks/latest.py`.
- Published benchmark report check from the tracked artifact now shows `REPORT["summary"] == {"total_workloads": 847, "measured_workloads": 847, "known_gap_count": 0, "module_workloads": 839, "parser_workloads": 8, "regression_workloads": 8}` and `REPORT["manifests"]["module-boundary"] == {"selected_workload_count": 24, "measured_workloads": 24, "known_gap_count": 0}` with both new workload ids marked `status == "measured"`.
- Verification passed with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/module_boundary.py --report .rebar/tmp/rbr-0868-compiled-pattern-bytes-verbose-regression-module-boundary.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`
