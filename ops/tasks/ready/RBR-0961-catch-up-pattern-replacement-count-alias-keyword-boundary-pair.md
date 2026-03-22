# RBR-0961: Catch up the pattern replacement `count_alias` keyword boundary pair

Status: ready
Owner: feature-implementation
Created: 2026-03-22

## Goal
- Extend the published Python-path `collection_replacement_boundary.py` benchmark surface with the exact bound `Pattern.sub()` / `Pattern.subn()` `count_alias` keyword-name rejection pair that `RBR-0959` just published on the shared `module-workflow-surface` correctness path, while keeping this run on the existing direct-`Pattern` collection/replacement keyword-error owner route and limiting the work to the exact missing benchmark rows plus the matching shared benchmark assertions.

## Pattern Pair
- `re.compile("abc").sub("x", "abcabc", count_alias=1)`
- `re.compile(b"abc").subn(b"x", b"abcabc", count_alias=1)`

## Deliverables
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly two direct-`Pattern` keyword-error workloads:
  - add `pattern-sub-count-alias-keyword-warm-str`; and
  - add `pattern-subn-count-alias-keyword-warm-bytes`.
- Keep those two workloads pinned to the exact `RBR-0959` correctness anchors rather than widening the collection/replacement family:
  - `pattern-sub-count-alias-keyword-warm-str` uses `operation == "pattern.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `flags == 0`, `kwargs == {"count_alias": 1}`, `expected_exception == {"type": "TypeError", "message_substring": "'count_alias' is an invalid keyword argument for sub()"}`, `text_model == "str"`, `cache_mode == "warm"`, and `timing_scope == "pattern-helper-call"`;
  - `pattern-subn-count-alias-keyword-warm-bytes` uses `operation == "pattern.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `flags == 0`, `kwargs == {"count_alias": 1}`, `expected_exception == {"type": "TypeError", "message_substring": "'count_alias' is an invalid keyword argument for subn()"}`, `text_model == "bytes"`, `cache_mode == "warm"`, and `timing_scope == "pattern-helper-call"`;
  - anchor the two workloads to `workflow-pattern-sub-count-alias-keyword-str` and `workflow-pattern-subn-count-alias-keyword-bytes`;
  - insert `pattern-sub-count-alias-keyword-warm-str` immediately after `pattern-sub-unexpected-keyword-after-positional-count-warm-str`;
  - insert `pattern-subn-count-alias-keyword-warm-bytes` immediately after `pattern-subn-unexpected-keyword-after-positional-count-warm-bytes`; and
  - do not widen into raw-module rows, compiled-pattern-first-argument rows, other direct-`Pattern` keyword-name errors, or another benchmark owner file in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared collection/replacement source-tree benchmark contract path instead of forking another direct-`Pattern` keyword benchmark suite:
  - extend the shared `collection-replacement-keyword` benchmark-to-correctness mapping by exactly two entries for the new workload ids above, with anchors `workflow-pattern-sub-count-alias-keyword-str` and `workflow-pattern-subn-count-alias-keyword-bytes`;
  - update `test_collection_replacement_manifest_keeps_pattern_keyword_replacement_and_split_rows_measured(...)` so the direct-`Pattern` keyword measured-row expectation moves from `19` workloads to `21`;
  - extend the existing direct-`Pattern` keyword contract coverage so the benchmark manifest round-trip checks, CPython exception-matching checks, and internal workload-probe coverage now include the new `Pattern.sub()` / `Pattern.subn()` `count_alias` pair alongside the already-landed split and replacement keyword rows;
  - keep that contract work on the existing direct-`Pattern` owner path instead of creating another contract helper family or detached manifest;
  - update the collection-replacement manifest expectations from `91` measured workloads to `93`, still with `0` known gaps on that manifest;
  - update the combined publication totals from `901` total / `901` measured / `0` known gaps across `30` manifests to `903` / `903` / `0` across the same `30` manifests; and
  - update `REPORT["summary"]["module_workloads"]` from `893` to `895`, while keeping `REPORT["summary"]["parser_workloads"]` at `8` and `REPORT["summary"]["regression_workloads"]` at `8`.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `selected_workload_count == 91`, `measured_workloads == 91`, and `known_gap_count == 0` to `93`, `93`, and `0`;
  - `REPORT["artifacts"]["manifests"]` keeps `collection-replacement-boundary` on the same tracked manifest path while moving its `workload_count` from `91` to `93`;
  - the combined tracked summary moves from `901` total / `901` measured / `0` known gaps with `893` module workloads to `903` / `903` / `0` with `895` module workloads; and
  - the two new direct-`Pattern` replacement `count_alias` workloads publish real `rebar` timings with `status == "measured"`, not placeholders.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern_replacement_unexpected_keyword_names_match_cpython or module_workflow_surface_publishes_pattern_keyword_error_slice_from_direct_cases'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_pattern_keyword_replacement_and_split_rows_measured or pattern_helper_collection_replacement_keyword_error_callbacks_match_cpython_exceptions or run_internal_workload_probe_measures_pattern_helper_keyword_error_workloads'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0961-pattern-replacement-count-alias-keyword-boundary-pair.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only. Do not widen the correctness surface or change Rust/Python regex behavior beyond what is required to publish and time the exact bound `Pattern.sub()` / `Pattern.subn()` `count_alias` keyword pair above on the existing benchmark owner path.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another direct-`Pattern` keyword benchmark manifest, another benchmark suite, or detached benchmark expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.
- Planning probes in this checkout already show that the current benchmark harness can normalize and measure the exact two workload shapes above, so do not widen this run into speculative `python/rebar_harness/benchmarks.py` changes unless a narrowly reproducible regression on this exact owner path appears while landing the two rows.

## Notes
- `RBR-0961` is the next available feature task id in the current checkout:
  - `RBR-0959` is the latest done feature task on this frontier;
  - `RBR-0960` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0959` / `RBR-0960` on the same shared `module-workflow-surface` / `collection-replacement-boundary` frontier so the newly published bound-pattern replacement `count_alias` rejection pair reaches the tracked Python-path benchmark surface before another collection/replacement keyword family widens the queue.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern_replacement_unexpected_keyword_names_match_cpython or module_workflow_surface_publishes_pattern_keyword_error_slice_from_direct_cases'` currently passes (`13 passed`), so the exact bounded correctness/parity slice is already green in this checkout;
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... re.compile('abc').sub('x', 'abcabc', count_alias=1) ... rebar.compile('abc').sub('x', 'abcabc', count_alias=1) ... re.compile(b'abc').subn(b'x', b'abcabc', count_alias=1) ... rebar.compile(b'abc').subn(b'x', b'abcabc', count_alias=1) ... PY` shows CPython and `rebar` already agree on the exact bounded `TypeError.args`: `("'count_alias' is an invalid keyword argument for sub()",)` for the `str` spelling and `("'count_alias' is an invalid keyword argument for subn()",)` for the `bytes` spelling;
  - `PYTHONPATH=python:. ./.venv/bin/python - <<'PY' ... _pattern_helper_collection_replacement_keyword_error_workload(...) synthetic count_alias probes ... run_internal_workload_probe(...) ... PY` returns `status == "measured"` for both adapters on both synthetic workload shapes in this checkout; and
  - `pattern-sub-count-alias-keyword-warm-str` and `pattern-subn-count-alias-keyword-warm-bytes` are currently absent from `benchmarks/workloads/collection_replacement_boundary.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and `reports/benchmarks/latest.py`, while the matching correctness anchors are already present in `tests/conformance/fixtures/module_workflow_surface.py` and `reports/correctness/latest.py`.
