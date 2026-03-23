## RBR-0987: Catch up the direct Pattern `split()` trio

Status: ready
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Extend the published Python-path `collection_replacement_boundary.py` benchmark surface with the exact direct-`Pattern` `split()` trio that the current runtime already publishes on the shared `collection-replacement-workflows` correctness path, keeping this run on the existing `collection-replacement-boundary` owner route instead of widening into another manifest, another helper family, or a native-path detour.

## Pattern Pair
- `re.compile("abc")`
- `re.compile(b"abc")`

## Helper Trio
- `re.compile("abc").split("zzz")`
- `re.compile("abc").split("abcabc")`
- `re.compile(b"abc").split(b"abczzabc", 1)`

## Deliverables
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly three direct-`Pattern` `split()` workloads:
  - add `pattern-split-no-match-warm-str`;
  - add `pattern-split-repeated-warm-str`; and
  - add `pattern-split-maxsplit-purged-bytes`.
- Keep those three workloads pinned to the already-published correctness anchors above rather than widening the collection/replacement frontier:
  - `pattern-split-no-match-warm-str` uses `operation == "pattern.split"`, `pattern == "abc"`, `haystack == "zzz"`, `flags == 0`, `text_model == "str"`, `cache_mode == "warm"`, and `timing_scope == "pattern-helper-call"`;
  - `pattern-split-repeated-warm-str` uses `operation == "pattern.split"`, `pattern == "abc"`, `haystack == "abcabc"`, `flags == 0`, `text_model == "str"`, `cache_mode == "warm"`, and `timing_scope == "pattern-helper-call"`;
  - `pattern-split-maxsplit-purged-bytes` uses `operation == "pattern.split"`, `pattern == "abc"`, `haystack == "abczzabc"`, `flags == 0`, `maxsplit == 1`, `text_model == "bytes"`, `cache_mode == "purged"`, and `timing_scope == "pattern-helper-call"`;
  - anchor the three workloads to `pattern-split-str-no-match`, `pattern-split-str-repeated`, and `pattern-split-bytes-maxsplit`;
  - insert the three-row direct `Pattern.split()` block immediately after `pattern-finditer-bounded-purged-bytes` and immediately before `pattern-split-maxsplit-indexlike-positional-warm-str`, preserving the exact order listed above; and
  - do not widen into module-level `split()` rows, direct-`Pattern` `findall()` or `finditer()` siblings, keyword/error-contract rows, another benchmark manifest, or benchmark-harness churn in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared `collection-replacement-boundary` owner route instead of forking another benchmark suite:
  - add `test_collection_replacement_manifest_keeps_pattern_split_rows_measured(...)` or an equivalent existing assertion so the manifest moves from `99` measured workloads to `102`, preserving the existing positional-indexlike, keyword, compiled-pattern, wrong-text-model, bounded-`findall()`, and bounded-`finditer()` subsets while adding this new direct `Pattern.split()` trio in the exact order above;
  - extend the standard benchmark anchor-contract definitions with exactly one new direct-`Pattern` collection/replacement `split()` owner-path definition, or a strictly equivalent widening of an existing direct-`Pattern` collection/replacement definition, that maps the three workload ids above to their three published correctness case ids and verifies callback-result parity on the existing owner route; and
  - keep the existing `collection-replacement-boundary` positional-indexlike, keyword, compiled-pattern, wrong-text-model, bounded-`findall()`, and bounded-`finditer()` ownership checks honest while moving the zero-gap manifest expectation from `99` selected / `99` measured to `102` / `102`.
- `reports/benchmarks/latest.py` is regenerated honestly on the tracked source-tree-shim path:
  - the combined report moves from `938` total / `938` measured / `0` known gaps across `30` manifests to `941` / `941` / `0` across the same `30` manifests;
  - `module_workloads` moves from `930` to `933`;
  - `parser_workloads` stays `8`; and
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `99` selected / `99` measured / `99` workload-count rows to `102` / `102` / `102`, while the matching `REPORT["artifacts"]["manifests"]` entry with `manifest_id == "collection-replacement-boundary"` moves from `99` workload-count rows to `102`, with all three new workload ids publishing `status == "measured"`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-split-str-no-match or pattern-split-str-repeated or pattern-split-bytes-maxsplit or literal_collection_direct_test_buckets_cover_selected_frontier'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_pattern_split_rows_measured or standard_benchmark_anchor_contract or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0987-pattern-split-trio.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only. Do not widen the correctness surface or change Rust/Python regex behavior beyond what is required to publish and time the exact three direct-`Pattern` `split()` workloads above on the existing `collection-replacement-boundary` owner path.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner route. Do not create another benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.

## Notes
- `RBR-0987` is the next available feature task id in the current checkout:
  - `RBR-0985` is the latest done feature task on the drained direct-`Pattern` collection/replacement correctness frontier;
  - `RBR-0986` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after the drained direct `Pattern.split()` correctness publication because the current runtime already publishes the exact trio while the adjacent Python-path benchmark surface still omits it on the same owner route.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-split-str-no-match or pattern-split-str-repeated or pattern-split-bytes-maxsplit or literal_collection_direct_test_buckets_cover_selected_frontier'` currently passes (`11 passed`), so the exact direct parity slice is already green in this checkout;
  - `rg -n 'pattern-split-(no-match-warm-str|repeated-warm-str|maxsplit-purged-bytes)|pattern-split-(str-no-match|str-repeated|bytes-maxsplit)' benchmarks/workloads/collection_replacement_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/benchmarks/latest.py tests/conformance/fixtures/collection_replacement_workflows.py reports/correctness/latest.py` currently finds only the three published correctness case ids in `tests/conformance/fixtures/collection_replacement_workflows.py` and `reports/correctness/latest.py`, confirming the benchmark workload ids are still absent from the published Python-path benchmark surface; and
  - `PYTHONPATH=python python3 - <<'PY' ... Workload.from_dict(...) / workload_to_payload(...) / run_internal_workload_probe(...) for pattern-split-no-match-warm-str, pattern-split-repeated-warm-str, and pattern-split-maxsplit-purged-bytes ... PY` returns `status == "measured"` for both adapters on all three synthetic workloads through the current benchmark harness in this checkout.
