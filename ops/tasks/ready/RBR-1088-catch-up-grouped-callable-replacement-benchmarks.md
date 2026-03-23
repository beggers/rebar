# RBR-1088: Catch up grouped callable replacement benchmarks

Status: ready
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Extend the published Python-path `collection_replacement_boundary.py` benchmark surface with the exact deferred str grouped callable replacement slice already published by `RBR-1086`, so the existing collection/replacement benchmark owner path measures that bounded module and compiled-`Pattern` callback workflow before bytes publication or broader grouped replacement expansion reenters the queue.

## Pattern Pair
- `rebar.sub("(abc)", lambda m: f"<{m.group(1)}>", "abcabc")`
- `rebar.compile("(?P<word>abc)").subn(lambda m: f"<{m.group('word')}>", "abcabc", 1)`

## Deliverables
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly two new str grouped callable workloads on the existing collection/replacement owner path:
  - add `module-sub-callable-grouped-warm-str`;
  - add `pattern-subn-callable-named-grouped-warm-str`;
  - keep `module-sub-callable-grouped-warm-str` pinned to the exact numbered raw-module workflow above with `operation == "module.sub"`, `pattern == "(abc)"`, a callable-replacement descriptor that reads group `1` and wraps it in angle brackets, `haystack == "abcabc"`, `count == 0`, `text_model == "str"`, `cache_mode == "warm"`, and `timing_scope == "module-helper-call"`; and
  - keep `pattern-subn-callable-named-grouped-warm-str` pinned to the exact named compiled-pattern workflow above with `operation == "pattern.subn"`, `pattern == "(?P<word>abc)"`, a callable-replacement descriptor that reads group `"word"` and wraps it in angle brackets, `haystack == "abcabc"`, `count == 1`, `text_model == "str"`, `cache_mode == "warm"`, and `timing_scope == "pattern-helper-call"`.
- Keep those two workloads on the existing collection/replacement benchmark owner route instead of inventing a new callable manifest, detached benchmark suite, or native-path-only publication:
  - place the module workload adjacent to `module-sub-template-warm-str` on the shared module replacement slice; and
  - place the compiled-pattern workload adjacent to `pattern-subn-grouped-template-warm-str` on the shared pattern replacement slice.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared `collection-replacement-boundary` owner path instead of forking a new benchmark family:
  - extend the existing collection/replacement measured-row assertions, or a strictly equivalent existing owner-path contract, so the new grouped callable workload ids are selected and published as measured on the source-tree combined path;
  - keep `source_tree_combined_case("collection-replacement-boundary").manifest_expectation.known_gap_count == 0`;
  - anchor `module-sub-callable-grouped-warm-str` to the already-published correctness case `module-sub-callable-grouped-str`; and
  - anchor `pattern-subn-callable-named-grouped-warm-str` to the already-published correctness case `pattern-subn-callable-named-grouped-str`.
- `reports/benchmarks/latest.py` is regenerated honestly on the tracked source-tree-shim path:
  - the combined report moves from `979` total / `979` measured / `0` known gaps across `30` manifests to `981` / `981` / `0` across the same `30` manifests;
  - `REPORT["summary"]["workloads_by_cache_mode"]` moves from `{"cold": 104, "purged": 424, "warm": 451}` to `{"cold": 104, "purged": 424, "warm": 453}`;
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `selected_workload_count == 140`, `measured_workloads == 140`, `known_gap_count == 0`, and `workload_count == 140` to `142`, `142`, `0`, and `142`; and
  - the regenerated tracked artifact publishes both new workload ids with `status == "measured"`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'grouped_callable_replacement_module_matches_cpython or grouped_callable_replacement_pattern_matches_cpython'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement or compiled_pattern_module_collection_replacement or standard_benchmark_manifest_preserves_collection_replacement_keyword_descriptors_until_helper_invocation'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-1088-grouped-callable-benchmarks.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only. Do not widen the correctness surface, change Rust/Python regex behavior, or add bytes grouped callable publication in this run.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner route. Do not create another benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the scope pinned to the exact str grouped callable slice already published by `RBR-1086`. Leave bytes publication and broader grouped callable replacement expansion for later tasks.

## Notes
- `RBR-1088` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/done/` currently runs through `RBR-1087`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contain no live `RBR-1088` task file; and
  - `rg -n 'RBR-1088|RBR-1089|RBR-1090' ops/tasks ops/state -g '*.md'` returned only historical mentions inside done-task notes, not a live reservation.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- `RBR-1086` explicitly deferred simple grouped callable benchmark catch-up ahead of bytes publication or broader grouped replacement expansion on this same owner family, so this is the first concrete deferred same-family follow-on rather than a new synthesized frontier.
- 2026-03-23 feature-planning probes confirm the benchmark slice is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `reports/benchmarks/latest.py` currently contains neither `module-sub-callable-grouped-warm-str` nor `pattern-subn-callable-named-grouped-warm-str`, confirming the exact paired benchmark rows are still absent from the tracked publication;
  - `benchmarks/workloads/collection_replacement_boundary.py` currently contains `module-sub-template-warm-str` and `pattern-subn-grouped-template-warm-str` but no simple grouped callable rows, confirming the gap is on the existing collection/replacement benchmark path rather than in a missing manifest family;
  - `reports/correctness/latest.py` already publishes `module-sub-callable-grouped-str` and `pattern-subn-callable-named-grouped-str`, confirming the exact correctness anchors are already live; and
  - `tests/python/test_callable_replacement_parity_suite.py` already keeps `test_grouped_callable_replacement_module_matches_cpython` and `test_grouped_callable_replacement_pattern_matches_cpython` green for the exact str grouped callable owner path, so this task can stay benchmark-only.
