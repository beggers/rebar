## RBR-0983: Catch up the direct Pattern `finditer()` bounded trio

Status: done
Owner: feature-implementation
Created: 2026-03-22

## Goal
- Extend the published Python-path `collection_replacement_boundary.py` benchmark surface with the exact direct-`Pattern` bounded `finditer()` trio that the current runtime already publishes on the shared `collection-replacement-workflows` correctness path, keeping this run on the existing `collection-replacement-boundary` owner route instead of widening into another manifest, another helper family, or a native-path detour.

## Pattern Pair
- `re.compile("abc")`
- `re.compile(b"abc")`

## Helper Trio
- `re.compile("abc").finditer("zabcabcx", 1, 7)`
- `re.compile("abc").finditer("zabz", 1, 4)`
- `re.compile(b"abc").finditer(b"zabcabcx", 1, 7)`

## Deliverables
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly three direct-`Pattern` bounded `finditer()` workloads:
  - add `pattern-finditer-bounded-warm-str`;
  - add `pattern-finditer-bounded-no-match-warm-str`; and
  - add `pattern-finditer-bounded-purged-bytes`.
- Keep those three workloads pinned to the already-published correctness anchors above rather than widening the collection/replacement frontier:
  - `pattern-finditer-bounded-warm-str` uses `operation == "pattern.finditer"`, `pattern == "abc"`, `haystack == "zabcabcx"`, `pos == 1`, `endpos == 7`, `flags == 0`, `text_model == "str"`, `cache_mode == "warm"`, and `timing_scope == "pattern-helper-call"`;
  - `pattern-finditer-bounded-no-match-warm-str` uses `operation == "pattern.finditer"`, `pattern == "abc"`, `haystack == "zabz"`, `pos == 1`, `endpos == 4`, `flags == 0`, `text_model == "str"`, `cache_mode == "warm"`, and `timing_scope == "pattern-helper-call"`;
  - `pattern-finditer-bounded-purged-bytes` uses `operation == "pattern.finditer"`, `pattern == "abc"`, `haystack == "zabcabcx"`, `pos == 1`, `endpos == 7`, `flags == 0`, `text_model == "bytes"`, `cache_mode == "purged"`, and `timing_scope == "pattern-helper-call"`;
  - anchor the three workloads to `pattern-finditer-str-bounded`, `pattern-finditer-str-bounded-no-match`, and `pattern-finditer-bytes-bounded`;
  - insert the three-row bounded `Pattern.finditer()` block immediately after `pattern-findall-bounded-purged-bytes` and immediately before `pattern-finditer-literal-warm-str`, preserving the exact order listed above; and
  - do not widen into module-level `finditer()` rows, direct-`Pattern` `split()` or replacement siblings, bounded-wildcard rows, another benchmark manifest, or benchmark-harness churn in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared `collection-replacement-boundary` owner route instead of forking another benchmark suite:
  - add `test_collection_replacement_manifest_keeps_pattern_finditer_bounded_rows_measured(...)` or an equivalent existing assertion so the manifest moves from `96` measured workloads to `99`, preserving the existing positional-indexlike, keyword, compiled-pattern, wrong-text-model, and bounded-`findall()` subsets while adding this new bounded `Pattern.finditer()` trio in the exact order above;
  - extend the standard benchmark anchor-contract definitions with exactly one new direct-`Pattern` collection/replacement bounded-`finditer()` owner-path definition, or a strictly equivalent widening of an existing direct-`Pattern` collection/replacement definition, that maps the three workload ids above to their three published correctness case ids and verifies callback-result parity on the existing owner route; and
  - keep the existing `collection-replacement-boundary` positional-indexlike, keyword, compiled-pattern, wrong-text-model, and bounded-`findall()` ownership checks honest while moving the zero-gap manifest expectation from `96` selected / `96` measured to `99` / `99`.
- `reports/benchmarks/latest.py` is regenerated honestly on the tracked source-tree-shim path:
  - the combined report moves from `935` total / `935` measured / `0` known gaps across `30` manifests to `938` / `938` / `0` across the same `30` manifests;
  - `module_workloads` moves from `927` to `930`;
  - `parser_workloads` stays `8`; and
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `96` selected / `96` measured / `96` workload-count rows to `99` / `99` / `99`, while the matching `REPORT["artifacts"]["manifests"]` entry moves from `96` workload-count rows to `99`, with all three new workload ids publishing `status == "measured"`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-finditer-str-bounded or pattern-finditer-str-bounded-no-match or pattern-finditer-bytes-bounded or literal_collection_direct_test_buckets_cover_selected_frontier'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_pattern_finditer_bounded_rows_measured or standard_benchmark_anchor_contract or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0983-pattern-finditer-bounded-trio.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only. Do not widen the correctness surface or change Rust/Python regex behavior beyond what is required to publish and time the exact three direct-`Pattern` bounded `finditer()` workloads above on the existing `collection-replacement-boundary` owner path.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner route. Do not create another benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.

## Notes
- `RBR-0983` is the next available feature task id in the current checkout:
  - `RBR-0981` is the latest done feature task on the drained direct-`Pattern` collection/replacement correctness frontier;
  - `RBR-0982` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after the drained bounded direct `Pattern.finditer()` correctness publication because the current runtime already publishes the exact trio while the adjacent Python-path benchmark surface still omits it on the same owner route.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-finditer-str-bounded or pattern-finditer-str-bounded-no-match or pattern-finditer-bytes-bounded or literal_collection_direct_test_buckets_cover_selected_frontier'` currently passes (`23 passed`), so the exact bounded direct parity slice is already green in this checkout;
  - `rg -n 'pattern-finditer-(bounded-warm-str|bounded-no-match-warm-str|bounded-purged-bytes)|pattern-finditer-(str-bounded|str-bounded-no-match|bytes-bounded)' benchmarks/workloads/collection_replacement_boundary.py reports/benchmarks/latest.py tests/conformance/fixtures/collection_replacement_workflows.py reports/correctness/latest.py` currently finds only the three published correctness case ids in `tests/conformance/fixtures/collection_replacement_workflows.py` and `reports/correctness/latest.py`, confirming the benchmark workload ids are still absent from the published Python-path benchmark surface; and
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... synthetic Workload.from_dict(...) / workload_to_payload(...) / run_internal_workload_probe(...) for pattern-finditer-bounded-warm-str, pattern-finditer-bounded-no-match-warm-str, and pattern-finditer-bounded-purged-bytes ... PY` returns `status == "measured"` for both adapters on all three synthetic workloads through the current benchmark harness in this checkout.

## Completion
- Added the three bounded direct-`Pattern.finditer()` workloads to `benchmarks/workloads/collection_replacement_boundary.py` in the required slot and order.
- Extended `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` with the matching zero-gap manifest assertion, owner-route anchor contract, and published full-suite summary expectations.
- Regenerated `reports/benchmarks/latest.py`; the tracked publication now reports `938` total / `938` measured / `0` known gaps across `30` manifests, with `930` module workloads and `99` selected/measured rows for `collection-replacement-boundary`.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-finditer-str-bounded or pattern-finditer-str-bounded-no-match or pattern-finditer-bytes-bounded or literal_collection_direct_test_buckets_cover_selected_frontier'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_pattern_finditer_bounded_rows_measured or standard_benchmark_anchor_contract or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0983-pattern-finditer-bounded-trio.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`
