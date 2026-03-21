# RBR-0882: Catch up the compiled-pattern module-compile integer-zero named-group boundary pair

Status: ready
Owner: feature-implementation
Created: 2026-03-21

## Goal
- Extend the published Python-path `module_boundary.py` benchmark surface with the first adjacent compiled-pattern-first-argument explicit `flags=0` named-group `compile()` success pair that the shared `module-workflow-surface` correctness path already publishes, while keeping this catch-up on the existing `module_boundary.py` manifest and widening benchmark-path support only enough to time the bounded named-group integer-zero `module.compile()` keyword pair.

## Pattern Pair
- `re.compile("(?P<word>abc)")` through `compile(re.compile("(?P<word>abc)"), flags=0)`
- `re.compile(b"(?P<word>abc)")` through `compile(re.compile(b"(?P<word>abc)"), flags=0)`

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/module_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `python/rebar_harness/benchmarks.py` keeps the tracked Python-path benchmark publication stable while widening compiled-pattern-first-argument `module.compile` support only enough for this adjacent named-group integer-zero pair on the existing owner route:
  - allow `use_compiled_pattern` workloads with `operation == "module.compile"` on the existing `module-boundary` manifest to accept the bounded named-group pattern `(?P<word>abc)` with `kwargs == {"flags": 0}` for same-text-model str/bytes success rows alongside the already-landed literal integer-zero pair and the default named-group pair from `RBR-0880`;
  - keep the timed callback measuring the module helper call itself by materializing the compiled pattern outside the timed callback and passing that object into `module.compile(...)` during each sample;
  - keep this support bounded to the exact same-text-model named-group explicit integer-zero pair in this run; and
  - do not widen into named-group bool-false carriers, named-group `IGNORECASE` rejection rows, `NOFLAG` spellings, other named-group patterns, new manifests, or unrelated benchmark-schema churn in this run.
- `benchmarks/workloads/module_boundary.py` remains the only benchmark manifest for this slice and grows by exactly two compiled-pattern-first-argument named-group explicit integer-zero `module.compile` workloads:
  - add `module-compile-flags-int-zero-warm-str-compiled-pattern-named-group`; and
  - add `module-compile-flags-int-zero-purged-bytes-compiled-pattern-named-group`.
- Keep those two workloads pinned to the exact already-published module-workflow compiled-pattern named-group integer-zero compile anchors rather than inventing a broader helper family:
  - `module-compile-flags-int-zero-warm-str-compiled-pattern-named-group` uses `operation == "module.compile"`, `pattern == "(?P<word>abc)"`, `text_model == "str"`, `cache_mode == "warm"`, `timing_scope == "module-helper-call"`, `flags == 0`, `kwargs == {"flags": 0}`, an explicit compiled-pattern-first-argument marker, and no `expected_exception`;
  - `module-compile-flags-int-zero-purged-bytes-compiled-pattern-named-group` uses `operation == "module.compile"`, `pattern == "(?P<word>abc)"`, `text_model == "bytes"`, `cache_mode == "purged"`, `timing_scope == "module-helper-call"`, `flags == 0`, `kwargs == {"flags": 0}`, an explicit compiled-pattern-first-argument marker, and no `expected_exception`;
  - anchor the two workloads to `workflow-module-compile-flags-int-zero-str-compiled-pattern-named-group` and `workflow-module-compile-flags-int-zero-bytes-compiled-pattern-named-group`;
  - keep the explicit integer-zero keyword carrier distinct from the adjacent default named-group pair that `RBR-0880` adds and from the later bool-false, `IGNORECASE`, or `NOFLAG` neighbors; and
  - do not widen into named-group bool-false carriers, named-group `IGNORECASE` rejection rows, literal compile rows, another benchmark manifest, or unrelated benchmark-harness churn in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking another compiled-pattern helper benchmark suite:
  - add focused contract coverage for the bounded compiled-pattern named-group `module.compile(..., flags=0)` pair, proving the rows round-trip through manifest loading, callback construction, internal probe execution, and correctness-anchor mapping while keeping the first-argument compilation outside the timed callback and routing the explicit integer-zero keyword carrier through the timed helper call;
  - update the module-boundary manifest expectations from `34` measured workloads to `36`, still with `0` known gaps on that manifest once `RBR-0880` has landed;
  - keep the manifest on the existing `post-parser-workflows` / combined-boundary path and wire the two new workloads to the exact correctness case ids listed above;
  - update the combined publication totals from `862` total / `862` measured / `0` known gaps across `30` manifests to `864` / `864` / `0` across the same `30` manifests;
  - update `REPORT["summary"]["module_workloads"]` from `854` to `856`;
  - keep `REPORT["summary"]["regression_workloads"]` at `8`; and
  - keep the built-native smoke manifest set unchanged in this run.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["module-boundary"]` moves from `selected_workload_count == 34`, `measured_workloads == 34`, and `known_gap_count == 0` to `36`, `36`, and `0`;
  - the two new compiled-pattern-first-argument named-group explicit integer-zero `module.compile` workloads publish real `rebar` timings with `status == "measured"`, not placeholders; and
  - the tracked report exposes those exact workload ids on the existing module-boundary benchmark surface.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/module_boundary.py --report .rebar/tmp/rbr-0882-compiled-pattern-module-compile-int-zero-named-group-boundary.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not widen the correctness surface or change Rust/Python regex behavior just to support a larger compiled-pattern compile family.
- Reuse the existing `module_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another compiled-pattern compile benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.
- Assume the bounded compiled-pattern named-group `module.compile(...)` success benchmark route from `RBR-0880` is already in place; if that prerequisite has not landed yet, stop and finish `RBR-0880` first instead of widening this task.

## Notes
- `RBR-0882` is the next available feature task id in the current checkout:
  - `RBR-0880` is already occupied by the ready feature task in `ops/tasks/ready/`;
  - `RBR-0881` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0880` on the same `module-workflow-surface` frontier so the first explicit integer-zero compiled-pattern named-group `module.compile()` keyword-carried pair catches up on the existing Python-path `module_boundary.py` benchmark surface before named-group bool-false carriers, named-group `IGNORECASE` rejections, `NOFLAG` spellings, or another benchmark family reopens the queue.
- 2026-03-21 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier but still absent from the benchmark surface:
  - `tests/conformance/fixtures/module_workflow_surface.py` already publishes the exact adjacent correctness anchors `workflow-module-compile-flags-int-zero-str-compiled-pattern-named-group` and `workflow-module-compile-flags-int-zero-bytes-compiled-pattern-named-group`;
  - `tests/python/test_module_workflow_parity_suite.py` already carries the adjacent owner-path parity cases `compiled-pattern-compile-flags-int-zero-str-named-group` and `compiled-pattern-compile-flags-int-zero-bytes-named-group`;
  - a direct runtime probe in this run confirmed CPython and `rebar` already agree on `compile(rebar.compile("(?P<word>abc)"), flags=0)` and `compile(rebar.compile(b"(?P<word>abc)"), flags=0)`, returning matching compiled-pattern metadata for `pattern`, `flags`, `groupindex`, and `groups`, so no Rust or Python regex-behavior prerequisite is missing for this bounded pair;
  - `benchmarks/workloads/module_boundary.py` and `reports/benchmarks/latest.py` currently publish no compiled-pattern named-group explicit integer-zero `module.compile` rows on that owner route; and
  - `python/rebar_harness/benchmarks.py` currently limits compiled-pattern `module.compile` benchmark validation to the bounded literal success and keyword carriers plus the adjacent default named-group success pair that `RBR-0880` introduces, so the benchmark publication still lacks this named-group explicit integer-zero pair even though the runtime behavior already exists.
- The acceptance counts above are intentionally written against the immediate post-`RBR-0880` state of `862` total / `862` measured / `0` known gaps overall with `REPORT["summary"]["module_workloads"] == 854` and `REPORT["manifests"]["module-boundary"]` at `34` selected / `34` measured / `0` known gaps.
