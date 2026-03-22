# RBR-0933: Catch up the direct `Pattern.sub()` / `Pattern.subn()` unexpected-keyword-after-positional-count boundary pair

Status: done
Owner: feature-implementation
Created: 2026-03-22

## Goal
- Extend the published Python-path `collection_replacement_boundary.py` benchmark surface with the exact direct `Pattern.sub()` / `Pattern.subn()` positional-count-plus-extra-keyword rejection pair that `RBR-0931` just published on the shared `module-workflow-surface` correctness path, while keeping this work on the existing direct bound-`Pattern` collection/replacement keyword owner route and limiting the run to the exact missing benchmark rows plus the matching shared benchmark assertions.

## Pattern Pair
- `re.compile("abc").sub("x", "abc", 1, missing=1)`
- `re.compile(b"abc").subn(b"x", b"abc", 1, missing=1)`

## Deliverables
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly two direct-`Pattern` keyword-error workloads:
  - add `pattern-sub-unexpected-keyword-after-positional-count-warm-str`; and
  - add `pattern-subn-unexpected-keyword-after-positional-count-warm-bytes`.
- Keep those two workloads pinned to the exact `RBR-0931` correctness anchors rather than widening the collection/replacement family:
  - `pattern-sub-unexpected-keyword-after-positional-count-warm-str` uses `operation == "pattern.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abc"`, `flags == 0`, `count == 1`, `kwargs == {"missing": 1}`, `expected_exception == {"type": "TypeError", "message_substring": "sub() takes at most 3 arguments (4 given)"}`, `text_model == "str"`, `cache_mode == "warm"`, and `timing_scope == "pattern-helper-call"`;
  - `pattern-subn-unexpected-keyword-after-positional-count-warm-bytes` uses `operation == "pattern.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abc"`, `flags == 0`, `count == 1`, `kwargs == {"missing": 1}`, `expected_exception == {"type": "TypeError", "message_substring": "subn() takes at most 3 arguments (4 given)"}`, `text_model == "bytes"`, `cache_mode == "warm"`, and `timing_scope == "pattern-helper-call"`;
  - anchor the two workloads to `workflow-pattern-sub-unexpected-keyword-after-positional-count-str` and `workflow-pattern-subn-unexpected-keyword-after-positional-count-bytes`;
  - insert `pattern-sub-unexpected-keyword-after-positional-count-warm-str` immediately after `pattern-sub-unexpected-keyword-warm-str` and immediately before `pattern-sub-on-bytes-string-warm-str`; and
  - insert `pattern-subn-unexpected-keyword-after-positional-count-warm-bytes` immediately after `pattern-subn-unexpected-keyword-warm-bytes` and immediately before `pattern-subn-on-str-string-purged-bytes`.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking another direct-`Pattern` collection/replacement benchmark suite:
  - extend the shared `collection-replacement-keyword` benchmark-to-correctness mapping by exactly two entries for the new workload ids above, with anchors `workflow-pattern-sub-unexpected-keyword-after-positional-count-str` and `workflow-pattern-subn-unexpected-keyword-after-positional-count-bytes`;
  - extend the existing direct pattern-helper keyword contract coverage so the manifest round-trip, callback-time keyword materialization, and CPython exception-matching checks now cover the positional-count-plus-extra-keyword pair alongside the already-landed `Pattern.sub()` / `Pattern.subn()` keyword rows;
  - update the direct `Pattern` keyword replacement/split measured-row expectation from `17` workloads to `19`;
  - update the collection-replacement manifest expectations from `77` measured workloads to `79`, still with `0` known gaps on that manifest;
  - update the combined publication totals from `885` total / `885` measured / `0` known gaps across `30` manifests to `887` / `887` / `0` across the same `30` manifests;
  - update `REPORT["summary"]["module_workloads"]` from `877` to `879`; and
  - keep `REPORT["summary"]["parser_workloads"]` at `8` and `REPORT["summary"]["regression_workloads"]` at `8`.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `selected_workload_count == 77`, `measured_workloads == 77`, and `known_gap_count == 0` to `79`, `79`, and `0`;
  - `REPORT["artifacts"]["manifests"]` keeps `collection-replacement-boundary` on the same tracked manifest path while moving its `workload_count` from `77` to `79`;
  - the combined tracked summary moves from `885` total / `885` measured / `0` known gaps with `877` module workloads to `887` / `887` / `0` with `879` module workloads; and
  - the two new direct-`Pattern` keyword-error workloads publish real `rebar` timings with `status == "measured"`, not placeholders.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-sub-unexpected-keyword-after-positional-count-str or pattern-subn-unexpected-keyword-after-positional-count-bytes'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_keyword or pattern_helper_collection_replacement or collection_replacement_manifest_keeps_pattern_keyword_replacement_and_split_rows_measured or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0933-pattern-sub-subn-unexpected-keyword-after-positional-count-boundary-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only. Do not widen the correctness surface or change Rust/Python regex behavior beyond what is required to publish and time the exact direct `Pattern.sub()` / `Pattern.subn()` pair above on the existing benchmark owner path.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another direct-`Pattern` collection/replacement benchmark manifest, another benchmark suite, or detached benchmark expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.
- Planning probes in this checkout already show that the current benchmark harness can normalize and measure the exact two workload shapes above, so do not widen this run into speculative `python/rebar_harness/benchmarks.py` changes unless a narrowly reproducible regression on this exact owner path appears while landing the two rows.

## Notes
- `RBR-0933` is the next available feature task id in the current checkout:
  - `RBR-0931` is the latest done feature task on this frontier;
  - `RBR-0932` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0931` on the same shared `module-workflow-surface` / `collection-replacement-boundary` frontier so the newly published direct `Pattern.sub()` / `Pattern.subn()` positional-count keyword-error pair reaches the tracked Python-path benchmark surface before another bound-pattern helper family reopens the queue.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... re.compile("abc").sub("x", "abc", 1, missing=1) ... rebar.compile("abc").sub("x", "abc", 1, missing=1) ... re.compile(b"abc").subn(b"x", b"abc", 1, missing=1) ... rebar.compile(b"abc").subn(b"x", b"abc", 1, missing=1) ... PY` shows CPython and `rebar` agree on the exact direct `TypeError.args`: `("sub() takes at most 3 arguments (4 given)",)` and `("subn() takes at most 3 arguments (4 given)",)`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-sub-unexpected-keyword-after-positional-count-str or pattern-subn-unexpected-keyword-after-positional-count-bytes'` is already green in this checkout, so the direct `Pattern.sub()` / `Pattern.subn()` owner path exposes the exact bounded error pair that this task needs to benchmark;
  - a synthetic `workload_from_payload(workload_to_payload(...))` probe that starts from `pattern-sub-unexpected-keyword-warm-str` and `pattern-subn-unexpected-keyword-warm-bytes`, then sets `count == 1` and the new workload ids, succeeds for both rows in this checkout, so the current benchmark payload model already supports the exact positional-count-plus-extra-keyword shape;
  - `run_internal_workload_probe(...)` against those two synthetic workload payloads returns `status == "measured"` for the `rebar` adapter in this checkout, so the existing timed callback path already measures the exact bounded pair without further harness work; and
  - `rg -n 'pattern-sub-unexpected-keyword-after-positional-count-warm-str|pattern-subn-unexpected-keyword-after-positional-count-warm-bytes' benchmarks/workloads tests/benchmarks reports/benchmarks` returned no matches in this run, so the exact benchmark workloads are still absent while `reports/benchmarks/latest.py` remains at `885` total / `885` measured / `0` known gaps overall and `collection-replacement-boundary` remains at `77` selected / `77` measured / `0` known gaps.

## Completion
- 2026-03-22: Added `pattern-sub-unexpected-keyword-after-positional-count-warm-str` and `pattern-subn-unexpected-keyword-after-positional-count-warm-bytes` to `benchmarks/workloads/collection_replacement_boundary.py`, extended the shared collection/replacement keyword benchmark anchors and direct pattern-helper contract coverage in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and fixed the narrowly reproducible direct-pattern benchmark callback regression in `python/rebar_harness/benchmarks.py` so a positional `count` is preserved when an unrelated keyword is also present.
- Republished `reports/benchmarks/latest.py` with `887` total / `887` measured / `0` known gaps across `30` manifests, `879` module workloads, and `collection-replacement-boundary` at `79` selected / `79` measured / `0` known gaps; both new workload ids publish `status == "measured"`.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-sub-unexpected-keyword-after-positional-count-str or pattern-subn-unexpected-keyword-after-positional-count-bytes'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_keyword or pattern_helper_collection_replacement or collection_replacement_manifest_keeps_pattern_keyword_replacement_and_split_rows_measured or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0933-pattern-sub-subn-unexpected-keyword-after-positional-count-boundary-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`
