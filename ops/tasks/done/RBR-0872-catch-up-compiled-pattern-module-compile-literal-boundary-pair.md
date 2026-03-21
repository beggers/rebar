# RBR-0872: Catch up the compiled-pattern module-compile literal boundary pair

Status: done
Owner: feature-implementation
Created: 2026-03-21

## Goal
- Extend the published Python-path `module_boundary.py` benchmark surface with the first adjacent compiled-pattern-first-argument literal `compile()` success pair that the shared `module-workflow-surface` correctness path already publishes, while keeping this catch-up on the existing `module_boundary.py` manifest and adding only the minimal benchmark-harness support needed to time `module.compile()` when the first argument is already a compiled pattern.

## Pattern Pair
- `re.compile("abc")` through `compile(re.compile("abc"))`
- `re.compile(b"abc")` through `compile(re.compile(b"abc"))`

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/module_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `python/rebar_harness/benchmarks.py` keeps the tracked Python-path benchmark publication stable while adding only the bounded compiled-pattern-first-argument `module.compile` support needed for this shared owner route:
  - allow `use_compiled_pattern` workloads with `operation == "module.compile"` on the existing `module-boundary` manifest instead of rejecting them during normalization;
  - keep the timed callback measuring the module helper call itself by materializing the compiled pattern outside the timed callback and passing that object into `module.compile(...)` during each sample;
  - keep this support bounded to the exact same-text-model literal success pair in this run; and
  - do not widen into compiled-pattern compile flag carriers, compile rejection rows, named-group compile rows, collection/replacement helpers, new manifests, or unrelated benchmark-schema churn in this run.
- `benchmarks/workloads/module_boundary.py` remains the only benchmark manifest for this slice and grows by exactly two compiled-pattern-first-argument literal `module.compile` workloads:
  - add `module-compile-literal-warm-str-compiled-pattern`; and
  - add `module-compile-literal-purged-bytes-compiled-pattern`.
- Keep those two workloads pinned to the exact already-published module-workflow compiled-pattern compile anchors rather than inventing a broader helper family:
  - `module-compile-literal-warm-str-compiled-pattern` uses `operation == "module.compile"`, `pattern == "abc"`, `text_model == "str"`, `cache_mode == "warm"`, `timing_scope == "module-helper-call"`, `flags == 0`, an explicit compiled-pattern-first-argument marker, and no `expected_exception`;
  - `module-compile-literal-purged-bytes-compiled-pattern` uses `operation == "module.compile"`, `pattern == "abc"`, `text_model == "bytes"`, `cache_mode == "purged"`, `timing_scope == "module-helper-call"`, `flags == 0`, an explicit compiled-pattern-first-argument marker, and no `expected_exception`;
  - anchor the two workloads to `workflow-module-compile-str-compiled-pattern` and `workflow-module-compile-bytes-compiled-pattern`;
  - keep the str/bytes split explicit on the shared owner path even though both rows succeed; and
  - do not widen into integer-zero, bool-false, IGNORECASE rejection, named-group compile, raw module compile cache neighbors beyond the existing literal trio, or another benchmark manifest in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking another compiled-pattern helper benchmark suite:
  - add focused contract coverage for the bounded compiled-pattern `module.compile` success pair, proving the rows round-trip through manifest loading, callback construction, internal probe execution, and correctness-anchor mapping while keeping the first-argument compilation outside the timed callback;
  - update the module-boundary manifest expectations from `24` measured workloads to `26`, still with `0` known gaps on that manifest once `RBR-0870` has landed;
  - keep the manifest on the existing `post-parser-workflows` / combined-boundary path and wire the two new workloads to the exact correctness case ids listed above;
  - update the combined publication totals from `852` total / `852` measured / `0` known gaps across `30` manifests to `854` / `854` / `0` across the same `30` manifests;
  - update `REPORT["summary"]["module_workloads"]` from `844` to `846`;
  - keep `REPORT["summary"]["regression_workloads"]` at `8`; and
  - keep the built-native smoke manifest set unchanged in this run.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["module-boundary"]` moves from `selected_workload_count == 24`, `measured_workloads == 24`, and `known_gap_count == 0` to `26`, `26`, and `0`;
  - the two new compiled-pattern-first-argument `module.compile` workloads publish real `rebar` timings with `status == "measured"`, not placeholders; and
  - the tracked report exposes those exact workload ids on the existing module-boundary benchmark surface.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/module_boundary.py --report .rebar/tmp/rbr-0872-compiled-pattern-module-compile-boundary.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not widen the correctness surface or change Rust/Python regex behavior just to support a larger compiled-pattern compile family.
- Reuse the existing `module_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another compiled-pattern compile benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.

## Notes
- `RBR-0872` is the next available feature task id in the current checkout:
  - `RBR-0870` is already occupied by the ready feature task in `ops/tasks/ready/`;
  - `RBR-0871` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0870` on the same `module-workflow-surface` frontier so the first compiled-pattern `module.compile()` literal pair catches up on the existing Python-path `module_boundary.py` benchmark surface before compiled-pattern compile flag carriers, compile rejection neighbors, or named-group compile publication reopens the queue.
- 2026-03-21 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier but still needs bounded benchmark-path support:
  - `tests/conformance/fixtures/module_workflow_surface.py` already publishes the exact adjacent correctness anchors `workflow-module-compile-str-compiled-pattern` and `workflow-module-compile-bytes-compiled-pattern`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'compiled_pattern and compile and not duplicate and not unexpected'` passed in this run (`301 passed, 913 deselected`), so no Rust or Python regex-behavior prerequisite is missing for this bounded pair;
  - `benchmarks/workloads/module_boundary.py` currently publishes only the raw `module.compile` literal cache trio on that owner route and no compiled-pattern `module.compile` rows;
  - `python/rebar_harness/benchmarks.py` currently rejects `use_compiled_pattern` when `operation == "module.compile"`, so the benchmark publication still lacks the bounded first-argument-compiled path even though the runtime behavior already exists; and
  - the acceptance counts above are intentionally written against the immediate post-`RBR-0870` state of `852` total / `852` measured / `0` known gaps overall with `REPORT["summary"]["module_workloads"] == 844` and `REPORT["manifests"]["module-boundary"]` at `24` selected / `24` measured / `0` known gaps.

## Completion
- 2026-03-21: Extended `python/rebar_harness/benchmarks.py` so the shared `module-boundary` owner path can time `module.compile(...)` with `use_compiled_pattern=True` only for the bounded literal `abc` str/bytes success pair, with the first compiled pattern built before the timed callback and reused during each sample.
- Added `module-compile-literal-warm-str-compiled-pattern` and `module-compile-literal-purged-bytes-compiled-pattern` to `benchmarks/workloads/module_boundary.py`, and extended `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` with the matching shared anchor/probe/precompile contract plus the updated combined-summary and manifest-count expectations.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/module_boundary.py --report .rebar/tmp/rbr-0872-compiled-pattern-module-compile-boundary.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`.
- Confirmed from the tracked `reports/benchmarks/latest.py` artifact in the current diff that `REPORT["manifests"]["module-boundary"]` is now `26` selected / `26` measured / `0` known gaps, that the new workload ids publish `status == "measured"`, and that the combined summary is now `854` total / `854` measured / `0` known gaps with `REPORT["summary"]["module_workloads"] == 846`.
