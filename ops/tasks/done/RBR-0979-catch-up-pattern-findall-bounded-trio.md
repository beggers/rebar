## RBR-0979: Catch up the direct Pattern `findall()` bounded trio

Status: done
Owner: feature-implementation
Created: 2026-03-22

## Goal
- Extend the published Python-path `collection_replacement_boundary.py` benchmark surface with the exact direct-`Pattern` bounded `findall()` trio that the current runtime already publishes on the shared `collection-replacement-workflows` correctness path, keeping this run on the existing `collection-replacement-boundary` owner route instead of widening into another manifest, another helper family, or a native-path detour.

## Pattern Pair
- `re.compile("abc")`
- `re.compile(b"abc")`

## Helper Trio
- `re.compile("abc").findall("zabcabcz", 1, 7)`
- `re.compile("abc").findall("zabz", 1, 4)`
- `re.compile(b"abc").findall(b"zabcabcz", 1, 7)`

## Deliverables
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly three direct-`Pattern` bounded `findall()` workloads:
  - add `pattern-findall-bounded-warm-str`;
  - add `pattern-findall-bounded-no-match-warm-str`; and
  - add `pattern-findall-bounded-purged-bytes`.
- Keep those three workloads pinned to the already-published correctness anchors above rather than widening the collection/replacement frontier:
  - `pattern-findall-bounded-warm-str` uses `operation == "pattern.findall"`, `pattern == "abc"`, `haystack == "zabcabcz"`, `pos == 1`, `endpos == 7`, `flags == 0`, `text_model == "str"`, `cache_mode == "warm"`, and `timing_scope == "pattern-helper-call"`;
  - `pattern-findall-bounded-no-match-warm-str` uses `operation == "pattern.findall"`, `pattern == "abc"`, `haystack == "zabz"`, `pos == 1`, `endpos == 4`, `flags == 0`, `text_model == "str"`, `cache_mode == "warm"`, and `timing_scope == "pattern-helper-call"`;
  - `pattern-findall-bounded-purged-bytes` uses `operation == "pattern.findall"`, `pattern == "abc"`, `haystack == "zabcabcz"`, `pos == 1`, `endpos == 7`, `flags == 0`, `text_model == "bytes"`, `cache_mode == "purged"`, and `timing_scope == "pattern-helper-call"`;
  - anchor the three workloads to `workflow-pattern-findall-str-bounded`, `workflow-pattern-findall-str-bounded-no-match`, and `workflow-pattern-findall-bytes-bounded`;
  - insert the three-row bounded `Pattern.findall()` block immediately after `pattern-split-on-bytes-string-warm-str` and immediately before `pattern-finditer-literal-warm-str`, preserving the exact order listed above; and
  - do not widen into module-level `findall()` rows, direct-`Pattern` `finditer()` follow-ons, split/sub/subn carriers, another benchmark manifest, or benchmark-harness churn in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared `collection-replacement-boundary` owner route instead of forking another benchmark suite:
  - add `test_collection_replacement_manifest_keeps_pattern_findall_bounded_rows_measured(...)` or an equivalent existing assertion so the manifest moves from `93` measured workloads to `96`, preserving the existing positional-indexlike, keyword, compiled-pattern, and wrong-text-model subsets while adding this new bounded `Pattern.findall()` trio in the exact order above;
  - extend the standard benchmark anchor-contract definitions with exactly one new direct-`Pattern` collection/replacement bounded-`findall()` owner-path definition, or a strictly equivalent widening of an existing direct-`Pattern` collection/replacement definition, that maps the three workload ids above to their three `workflow-pattern-findall-*` anchors and verifies callback-result parity on the existing owner route; and
  - keep the existing `collection-replacement-boundary` positional-indexlike, keyword, compiled-pattern, and wrong-text-model ownership checks honest while moving the zero-gap manifest expectation from `93` selected / `93` measured to `96` / `96`.
- `reports/benchmarks/latest.py` is regenerated honestly on the tracked source-tree-shim path:
  - the combined report moves from `932` total / `932` measured / `0` known gaps across `30` manifests to `935` / `935` / `0` across the same `30` manifests;
  - `module_workloads` moves from `924` to `927`;
  - `parser_workloads` stays `8`; and
  - `REPORT["manifests"]["collection-replacement-boundary"]` plus the matching `REPORT["artifacts"]["manifests"]` entry move from `93` selected / `93` measured / `93` workload-count rows to `96` / `96` / `96`, with all three new workload ids publishing `status == "measured"`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-findall-str-bounded or pattern-findall-str-bounded-no-match or pattern-findall-bytes-bounded or literal_collection_direct_test_buckets_cover_selected_frontier'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_pattern_findall_bounded_rows_measured or standard_benchmark_anchor_contract or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0979-pattern-findall-bounded-trio.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only. Do not widen the correctness surface or change Rust/Python regex behavior beyond what is required to publish and time the exact three direct-`Pattern` bounded `findall()` workloads above on the existing `collection-replacement-boundary` owner path.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner route. Do not create another benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.

## Notes
- `RBR-0979` is the next available feature task id in the current checkout:
  - `RBR-0977` is the latest done feature task on the drained `collection-replacement-workflows` correctness frontier;
  - `RBR-0978` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after the drained bounded `Pattern.findall()` correctness publication because the current runtime already matches the exact trio while the adjacent Python-path benchmark surface still omits it on the same owner route.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-findall-str-bounded or pattern-findall-str-bounded-no-match or pattern-findall-bytes-bounded or literal_collection_direct_test_buckets_cover_selected_frontier'` currently passes (`15 passed`), so the exact bounded direct parity slice is already green in this checkout;
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... Workload.from_dict(...) / workload_to_payload(...) / run_internal_workload_probe(...) synthetic pattern-findall-bounded-warm-str, pattern-findall-bounded-no-match-warm-str, and pattern-findall-bounded-purged-bytes ... PY` returns `status == "measured"` for both adapters on all three synthetic workloads through the current benchmark harness in this checkout; and
  - `rg -n 'pattern-findall-bounded-warm-str|pattern-findall-bounded-no-match-warm-str|pattern-findall-bounded-purged-bytes|workflow-pattern-findall-str-bounded|workflow-pattern-findall-str-bounded-no-match|workflow-pattern-findall-bytes-bounded' benchmarks/workloads/collection_replacement_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/benchmarks/latest.py` currently returns no matches, while `reports/benchmarks/latest.py` still reports `932` total / `932` measured / `0` known gaps overall with `collection-replacement-boundary` fixed at `93` selected / `93` measured / `93` workload-count rows and `module_workloads == 924`.

## Completion Note
- Added the three bounded direct `Pattern.findall()` rows to `benchmarks/workloads/collection_replacement_boundary.py` immediately after `pattern-split-on-bytes-string-warm-str`, kept the block on the existing owner route, and anchored it in the shared benchmark suite to the published `collection_replacement_workflows` correctness ids `pattern-findall-str-bounded`, `pattern-findall-str-bounded-no-match`, and `pattern-findall-bytes-bounded`.
- Verified:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-findall-str-bounded or pattern-findall-str-bounded-no-match or pattern-findall-bytes-bounded or literal_collection_direct_test_buckets_cover_selected_frontier'` -> `15 passed`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_pattern_findall_bounded_rows_measured or (collection-replacement-pattern-findall-bounded and (test_standard_benchmark_workloads_stay_pinned_to_exact_case_ids or test_standard_benchmark_workload_callbacks_match_anchor_case_results)) or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'` -> `4 passed`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0979-pattern-findall-bounded-trio.py` -> `96` total / `96` measured / `0` known gaps
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py` -> published `935` total / `935` measured / `0` known gaps, `927` module workloads, and `collection-replacement-boundary` at `96` selected / `96` measured / `96` workload-count rows with all three new workload ids marked `measured`
