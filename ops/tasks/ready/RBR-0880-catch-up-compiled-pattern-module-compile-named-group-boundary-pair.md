# RBR-0880: Catch up the compiled-pattern module-compile named-group boundary pair

Status: ready
Owner: feature-implementation
Created: 2026-03-21

## Goal
- Extend the published Python-path `module_boundary.py` benchmark surface with the first adjacent compiled-pattern-first-argument named-group `compile()` success pair that the shared `module-workflow-surface` correctness path already publishes, while keeping this catch-up on the existing `module_boundary.py` manifest and widening benchmark-path support only enough to time the bounded named-group `module.compile()` success pair.

## Pattern Pair
- `re.compile("(?P<word>abc)")` through `compile(re.compile("(?P<word>abc)"))`
- `re.compile(b"(?P<word>abc)")` through `compile(re.compile(b"(?P<word>abc)"))`

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/module_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `python/rebar_harness/benchmarks.py` keeps the tracked Python-path benchmark publication stable while widening compiled-pattern-first-argument `module.compile` support only enough for this adjacent named-group pair on the existing owner route:
  - allow `use_compiled_pattern` workloads with `operation == "module.compile"` on the existing `module-boundary` manifest to accept the bounded named-group pattern `(?P<word>abc)` for same-text-model str/bytes success rows alongside the already-landed literal pair;
  - keep the timed callback measuring the module helper call itself by materializing the compiled pattern outside the timed callback and passing that object into `module.compile(...)` during each sample;
  - keep this support bounded to the exact same-text-model named-group success pair in this run; and
  - do not widen into named-group flag carriers, named-group `IGNORECASE` rejection rows, `NOFLAG` spellings, other named-group patterns, new manifests, or unrelated benchmark-schema churn in this run.
- `benchmarks/workloads/module_boundary.py` remains the only benchmark manifest for this slice and grows by exactly two compiled-pattern-first-argument named-group `module.compile` workloads:
  - add `module-compile-named-group-warm-str-compiled-pattern`; and
  - add `module-compile-named-group-purged-bytes-compiled-pattern`.
- Keep those two workloads pinned to the exact already-published module-workflow compiled-pattern named-group compile anchors rather than inventing a broader helper family:
  - `module-compile-named-group-warm-str-compiled-pattern` uses `operation == "module.compile"`, `pattern == "(?P<word>abc)"`, `text_model == "str"`, `cache_mode == "warm"`, `timing_scope == "module-helper-call"`, `flags == 0`, an explicit compiled-pattern-first-argument marker, and no `expected_exception`;
  - `module-compile-named-group-purged-bytes-compiled-pattern` uses `operation == "module.compile"`, `pattern == "(?P<word>abc)"`, `text_model == "bytes"`, `cache_mode == "purged"`, `timing_scope == "module-helper-call"`, `flags == 0`, an explicit compiled-pattern-first-argument marker, and no `expected_exception`;
  - anchor the two workloads to `workflow-module-compile-str-compiled-pattern-named-group` and `workflow-module-compile-bytes-compiled-pattern-named-group`;
  - keep the str/bytes split explicit on the shared owner path even though both rows succeed; and
  - do not widen into named-group integer-zero, bool-false, or `IGNORECASE` keyword neighbors, literal compile rows, another benchmark manifest, or unrelated benchmark-harness churn in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking another compiled-pattern helper benchmark suite:
  - add focused contract coverage for the bounded compiled-pattern named-group `module.compile` success pair, proving the rows round-trip through manifest loading, callback construction, internal probe execution, and correctness-anchor mapping while keeping the first-argument compilation outside the timed callback;
  - update the module-boundary manifest expectations from `32` measured workloads to `34`, still with `0` known gaps on that manifest once `RBR-0878` has landed;
  - keep the manifest on the existing `post-parser-workflows` / combined-boundary path and wire the two new workloads to the exact correctness case ids listed above;
  - update the combined publication totals from `860` total / `860` measured / `0` known gaps across `30` manifests to `862` / `862` / `0` across the same `30` manifests;
  - update `REPORT["summary"]["module_workloads"]` from `852` to `854`;
  - keep `REPORT["summary"]["regression_workloads"]` at `8`; and
  - keep the built-native smoke manifest set unchanged in this run.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["module-boundary"]` moves from `selected_workload_count == 32`, `measured_workloads == 32`, and `known_gap_count == 0` to `34`, `34`, and `0`;
  - the two new compiled-pattern-first-argument named-group `module.compile` workloads publish real `rebar` timings with `status == "measured"`, not placeholders; and
  - the tracked report exposes those exact workload ids on the existing module-boundary benchmark surface.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/module_boundary.py --report .rebar/tmp/rbr-0880-compiled-pattern-module-compile-named-group-boundary.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not widen the correctness surface or change Rust/Python regex behavior just to support a larger compiled-pattern compile family.
- Reuse the existing `module_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another compiled-pattern compile benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.
- Assume the bounded compiled-pattern `module.compile(..., flags=IGNORECASE)` rejection benchmark route from `RBR-0878` is already in place; if that prerequisite has not landed yet, stop and finish `RBR-0878` first instead of widening this task.

## Notes
- `RBR-0880` is the next available feature task id in the current checkout:
  - `RBR-0878` is already occupied by the ready feature task in `ops/tasks/ready/`;
  - `RBR-0879` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0878` on the same `module-workflow-surface` frontier so the first adjacent compiled-pattern named-group `module.compile()` success pair catches up on the existing Python-path `module_boundary.py` benchmark surface before named-group flag carriers, `NOFLAG` spellings, or another benchmark family reopens the queue.
- 2026-03-21 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier but still absent from the benchmark surface:
  - `tests/conformance/fixtures/module_workflow_surface.py` already publishes the exact adjacent correctness anchors `workflow-module-compile-str-compiled-pattern-named-group` and `workflow-module-compile-bytes-compiled-pattern-named-group`;
  - a direct runtime probe in this run confirmed CPython and `rebar` already agree on `compile(rebar.compile("(?P<word>abc)"))` and `compile(rebar.compile(b"(?P<word>abc)"))`, returning matching compiled-pattern metadata for `pattern`, `flags`, `groupindex`, and `groups`, so no Rust or Python regex-behavior prerequisite is missing for this bounded pair;
  - `benchmarks/workloads/module_boundary.py` and `reports/benchmarks/latest.py` currently publish no compiled-pattern named-group `module.compile` rows on that owner route; and
  - `python/rebar_harness/benchmarks.py` currently validates compiled-pattern `module.compile` workloads only for the bounded `abc` str/bytes literal success pair plus the already-landed keyword/rejection neighbors, so the benchmark publication still lacks this adjacent named-group success pair even though the runtime behavior already exists.
- The acceptance counts above are intentionally written against the immediate post-`RBR-0878` state of `860` total / `860` measured / `0` known gaps overall with `REPORT["summary"]["module_workloads"] == 852` and `REPORT["manifests"]["module-boundary"]` at `32` selected / `32` measured / `0` known gaps.
