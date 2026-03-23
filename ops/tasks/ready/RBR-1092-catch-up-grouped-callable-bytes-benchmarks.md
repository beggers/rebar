# RBR-1092: Catch up grouped callable bytes benchmarks

Status: ready
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Extend the published Python-path `collection_replacement_boundary.py` benchmark surface with the exact deferred bytes grouped callable replacement slice already published by `RBR-1090`, so the existing collection/replacement benchmark owner path measures that bounded module and compiled-`Pattern` callback workflow before broader grouped callable replacement expansion reenters the queue.

## Pattern Pair
- `rebar.sub(rb"(abc)", lambda m: b"<" + m.group(1) + b">", b"abcabc")`
- `rebar.compile(rb"(?P<word>abc)").subn(lambda m: b"<" + m.group("word") + b">", b"abcabc", 1)`

## Deliverables
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly two new bytes grouped callable workloads on the existing collection/replacement owner path:
  - add `module-sub-callable-grouped-warm-bytes`;
  - add `pattern-subn-callable-named-grouped-purged-bytes`;
  - keep `module-sub-callable-grouped-warm-bytes` pinned to the exact numbered raw-module workflow above with `operation == "module.sub"`, `pattern == b"(abc)"`, a callable-replacement descriptor that reads group `1` and wraps it in angle brackets, `haystack == b"abcabc"`, `count == 0`, `text_model == "bytes"`, `cache_mode == "warm"`, and `timing_scope == "module-helper-call"`; and
  - keep `pattern-subn-callable-named-grouped-purged-bytes` pinned to the exact named compiled-pattern workflow above with `operation == "pattern.subn"`, `pattern == b"(?P<word>abc)"`, a callable-replacement descriptor that reads group `"word"` and wraps it in angle brackets, `haystack == b"abcabc"`, `count == 1`, `text_model == "bytes"`, `cache_mode == "purged"`, and `timing_scope == "pattern-helper-call"`.
- Keep those two workloads on the existing collection/replacement benchmark owner route instead of inventing a new callable manifest, detached benchmark suite, or native-path-only publication:
  - place the module workload adjacent to `module-sub-callable-grouped-warm-str` on the shared module replacement slice; and
  - place the compiled-pattern workload adjacent to `pattern-subn-callable-named-grouped-warm-str` on the shared pattern replacement slice.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared `collection-replacement-boundary` owner path instead of forking a new benchmark family:
  - extend the existing collection/replacement measured-row assertions, or a strictly equivalent existing owner-path contract, so the new grouped callable bytes workload ids are selected and published as measured on the source-tree combined path;
  - keep `source_tree_combined_case("collection-replacement-boundary").manifest_expectation.known_gap_count == 0`;
  - anchor `module-sub-callable-grouped-warm-bytes` to the already-published correctness case `module-sub-callable-grouped-bytes`; and
  - anchor `pattern-subn-callable-named-grouped-purged-bytes` to the already-published correctness case `pattern-subn-callable-named-grouped-bytes`.
- `reports/benchmarks/latest.py` is regenerated honestly on the tracked source-tree-shim path:
  - the combined report moves from `981` total / `981` measured / `0` known gaps across `30` manifests to `983` / `983` / `0` across the same `30` manifests;
  - `REPORT["summary"]["workloads_by_cache_mode"]` moves from `{"cold": 104, "purged": 424, "warm": 453}` to `{"cold": 104, "purged": 425, "warm": 454}`;
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `selected_workload_count == 142`, `measured_workloads == 142`, `known_gap_count == 0`, and `workload_count == 142` to `144`, `144`, `0`, and `144`; and
  - the regenerated tracked artifact publishes both new workload ids with `status == "measured"`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'grouped_callable_replacement_module_matches_cpython or grouped_callable_replacement_pattern_matches_cpython'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement or compiled_pattern_module_collection_replacement or standard_benchmark_manifest_preserves_collection_replacement_keyword_descriptors_until_helper_invocation'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-1092-grouped-callable-bytes-benchmarks.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only. Do not widen the correctness surface, change Rust/Python regex behavior, or add broader grouped callable replacement rows in this run.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner route. Do not create another benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the scope pinned to the exact bytes grouped callable slice already published by `RBR-1090`. Leave broader grouped callable replacement expansion for later tasks.

## Notes
- `RBR-1092` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contain no active feature task; and
  - `rg -n 'RBR-1092|RBR-1093|RBR-1094' ops/tasks ops/state -g '*.md'` returned only historical mentions inside done-task notes, not a live reservation.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- `RBR-1090` explicitly left bytes grouped callable benchmark rows and broader grouped callable replacement expansion for later work on this same owner family, so this is the first concrete deferred same-family follow-on rather than a new synthesized frontier.
- Narrow owner-path checks in this run confirm the benchmark slice is concrete from the landed runtime and correctness frontier and does not need another implementation prerequisite first:
  - `tests/conformance/fixtures/collection_replacement_workflows.py`, `tests/conformance/fixtures/named_group_replacement_workflows.py`, `tests/conformance/test_combined_correctness_scorecards.py`, and `reports/correctness/latest.py` already publish the exact bytes correctness anchors `module-sub-callable-grouped-bytes`, `module-subn-callable-grouped-bytes`, `pattern-sub-callable-named-grouped-bytes`, and `pattern-subn-callable-named-grouped-bytes`;
  - `benchmarks/workloads/collection_replacement_boundary.py` currently contains `module-sub-callable-grouped-warm-str` and `pattern-subn-callable-named-grouped-warm-str`, but no adjacent bytes grouped callable workload ids on that same owner path;
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently anchors only the str grouped callable workload pair on `_COLLECTION_REPLACEMENT_GROUPED_CALLABLE_WORKLOAD_CASE_PAIRS`; and
  - `reports/benchmarks/latest.py` currently contains neither `module-sub-callable-grouped-warm-bytes` nor `pattern-subn-callable-named-grouped-purged-bytes`, confirming the exact gap is on the published Python-path benchmark surface rather than in the runtime or correctness owner paths.
