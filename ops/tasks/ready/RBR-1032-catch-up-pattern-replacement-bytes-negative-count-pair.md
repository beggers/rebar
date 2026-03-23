# RBR-1032: Catch up the direct `Pattern.sub()` / `Pattern.subn()` bytes negative-count pair

Status: ready
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Extend the published Python-path `collection_replacement_boundary.py` benchmark surface with the exact direct compiled-pattern `bytes` literal negative-count pair that the current runtime already publishes on the shared `collection-replacement-workflows` correctness path, keeping this run on the existing collection/replacement benchmark owner route instead of widening into another manifest, another helper family, or a native-path detour.

## Pattern Pair
- `re.compile(b"abc").sub(b"x", b"abcabc", -1)`
- `re.compile(b"abc").subn(b"x", b"abcabc", -1)`

## Deliverables
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly two direct compiled-pattern `bytes` literal-replacement workloads:
  - add `pattern-sub-bytes-negative-count-purged-bytes`; and
  - add `pattern-subn-bytes-negative-count-purged-bytes`.
- Keep those two workloads pinned to the already-published correctness anchors above rather than widening the collection/replacement frontier:
  - `pattern-sub-bytes-negative-count-purged-bytes` uses `operation == "pattern.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `flags == 0`, `count == -1`, `text_model == "bytes"`, `cache_mode == "purged"`, and `timing_scope == "pattern-helper-call"`;
  - `pattern-subn-bytes-negative-count-purged-bytes` uses `operation == "pattern.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `flags == 0`, `count == -1`, `text_model == "bytes"`, `cache_mode == "purged"`, and `timing_scope == "pattern-helper-call"`;
  - anchor the two workloads to `pattern-sub-bytes-negative-count` and `pattern-subn-bytes-negative-count`;
  - keep the direct-pattern literal replacement slice adjacent on the existing collection/replacement manifest path, with the measured workload ids ordered as `pattern-sub-no-match-warm-str`, `pattern-sub-single-match-warm-str`, `pattern-sub-negative-count-warm-str`, `pattern-sub-bytes-no-match-purged-bytes`, `pattern-sub-bytes-single-match-purged-bytes`, `pattern-sub-bytes-negative-count-purged-bytes`, `pattern-subn-count-warm-str`, `pattern-subn-repeated-warm-str`, `pattern-subn-negative-count-warm-str`, `pattern-subn-bytes-count-purged-bytes`, `pattern-subn-bytes-repeated-purged-bytes`, and `pattern-subn-bytes-negative-count-purged-bytes`; and
  - do not widen into raw-module rows, grouped-template rows, callable replacement rows, another benchmark manifest, or smoke-workload changes in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared `collection-replacement-boundary` owner route instead of forking another benchmark suite:
  - extend `_PATTERN_COLLECTION_REPLACEMENT_LITERAL_REPLACEMENT_WORKLOAD_CASE_PAIRS`, or tighten an equivalent existing owner-path assertion, so the selected workload ids now publish in the same twelve-row order listed above;
  - extend the direct-pattern literal-replacement anchor coverage, or tighten an equivalent existing standard benchmark anchor contract, so the new workload ids anchor to `pattern-sub-bytes-negative-count` and `pattern-subn-bytes-negative-count` on the existing collection/replacement owner path with callback-result parity still enabled;
  - keep the benchmark comparison on the tracked Python-facing source-tree shim path; and
  - keep the shared collection/replacement benchmark owner surface honest rather than introducing a detached pattern-replacement-only helper file.
- `reports/benchmarks/latest.py` is regenerated honestly on the tracked source-tree-shim path:
  - the combined report moves from `961` total / `961` measured / `0` known gaps across `30` manifests to `963` / `963` / `0` across the same `30` manifests;
  - `module_workloads` moves from `953` to `955`;
  - `parser_workloads` stays `8`;
  - `regression_workloads` stays `8`;
  - `REPORT["summary"]["workloads_by_cache_mode"]` moves from `{"cold": 104, "purged": 410, "warm": 447}` to `{"cold": 104, "purged": 412, "warm": 447}`; and
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `selected_workload_count == 122`, `measured_workloads == 122`, `known_gap_count == 0`, and `workload_count == 122` to `124`, `124`, `0`, and `124`, while the matching `REPORT["artifacts"]["manifests"]` entry with `manifest_id == "collection-replacement-boundary"` moves from `workload_count == 122` to `124`, with both new workload ids publishing `status == "measured"`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_pattern_literal_replacement_helpers_match_cpython and bytes-negative-count'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_pattern_replacement_literal_rows_measured or standard_benchmark_anchor_contract or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-1032-pattern-replacement-bytes-negative-count-pair.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only. Do not widen the correctness surface or change Rust/Python regex behavior beyond what is required to publish and time the exact direct compiled-pattern `bytes` negative-count rows above on the existing `collection-replacement-boundary` owner path.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner route. Do not create another benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the scope pinned to the two exact direct-pattern `bytes` negative-count rows above. Leave raw-module bytes negative-count follow-ons, grouped-template rows, callable replacement rows, and deeper replacement expansion for later tasks.

## Notes
- `RBR-1032` is the next available feature task id in the current checkout:
  - `rg -n "RBR-1032|RBR-1033|RBR-1034" ops/tasks ops/state/current_status.md ops/state/backlog.md` returned no matches in this run; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after `RBR-1030` because the next concrete missing Python-path benchmark rows on the same shared collection/replacement owner route are the adjacent direct compiled-pattern `bytes` negative-count workloads rather than raw-module bytes negative-count follow-ons, grouped-template rows, callable replacement rows, or a new manifest lane.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `RBR-1030` already published the adjacent correctness ids `pattern-sub-bytes-negative-count` and `pattern-subn-bytes-negative-count` on `tests/conformance/fixtures/collection_replacement_workflows.py`;
  - `rg -n 'pattern-sub-bytes-negative-count-purged-bytes|pattern-subn-bytes-negative-count-purged-bytes' benchmarks/workloads/collection_replacement_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/benchmarks/latest.py` currently returns no matches, confirming the exact benchmark workload ids are still absent from the tracked owner-path surfaces;
  - direct runtime probes confirm `rebar.compile(b"abc").sub(b"x", b"abcabc", -1) == re.compile(b"abc").sub(b"x", b"abcabc", -1)` and `rebar.compile(b"abc").subn(b"x", b"abcabc", -1) == re.compile(b"abc").subn(b"x", b"abcabc", -1)` on the live branch; and
  - synthetic benchmark probes built through `rebar_harness.benchmarks.Workload.from_dict(...)`, `workload_to_payload(...)`, and `run_internal_workload_probe(...)` return `status == "measured"` for both adapters on hypothetical workloads `pattern-sub-bytes-negative-count-purged-bytes` and `pattern-subn-bytes-negative-count-purged-bytes`, so the benchmark catch-up can stay on the existing Python-path owner route instead of needing another implementation prerequisite first.
