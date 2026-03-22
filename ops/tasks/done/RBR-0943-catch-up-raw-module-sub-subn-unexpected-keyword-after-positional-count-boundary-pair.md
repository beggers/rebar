# RBR-0943: Catch up the raw module `sub()` / `subn()` unexpected-keyword-after-positional-count boundary pair

Status: done
Owner: feature-implementation
Created: 2026-03-22
Completed: 2026-03-22

## Goal
- Extend the published Python-path `collection_replacement_boundary.py` benchmark surface with the exact raw module-level positional-count-plus-unexpected-keyword rejection pair that the shared `module-workflow-surface` correctness path already publishes, while keeping this catch-up on the existing module-helper collection/replacement keyword owner route and limiting the run to the exact missing benchmark rows plus the matching shared benchmark assertions.

## Pattern Pair
- `re.sub("abc", "x", "abc", 1, missing=1)`
- `re.subn(b"abc", b"x", b"abc", 1, missing=1)`

## Deliverables
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly two raw module-helper keyword-error workloads:
  - add `module-sub-unexpected-keyword-after-positional-count-purged-str`; and
  - add `module-subn-unexpected-keyword-after-positional-count-purged-bytes`.
- Keep those two workloads pinned to the exact already-published raw module correctness anchors rather than widening the collection/replacement family:
  - `module-sub-unexpected-keyword-after-positional-count-purged-str` uses `operation == "module.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abc"`, `flags == 0`, `count == 1`, `kwargs == {"missing": 1}`, `expected_exception == {"type": "TypeError", "message_substring": "unexpected keyword argument 'missing'"}`, `text_model == "str"`, `cache_mode == "purged"`, and `timing_scope == "module-helper-call"`;
  - `module-subn-unexpected-keyword-after-positional-count-purged-bytes` uses `operation == "module.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abc"`, `flags == 0`, `count == 1`, `kwargs == {"missing": 1}`, `expected_exception == {"type": "TypeError", "message_substring": "unexpected keyword argument 'missing'"}`, `text_model == "bytes"`, `cache_mode == "purged"`, and `timing_scope == "module-helper-call"`;
  - anchor the two workloads to `workflow-module-sub-unexpected-keyword-after-positional-count` and `workflow-module-subn-unexpected-keyword-after-positional-count-bytes`;
  - insert `module-sub-unexpected-keyword-after-positional-count-purged-str` immediately after `module-sub-unexpected-keyword-purged-str` and immediately before `module-sub-duplicate-count-keyword-warm-str-compiled-pattern`;
  - insert `module-subn-unexpected-keyword-after-positional-count-purged-bytes` immediately after `module-subn-unexpected-keyword-purged-bytes` and immediately before `module-subn-count-keyword-purged-bytes-compiled-pattern`; and
  - do not widen into raw module duplicate-keyword rows beyond what is already published, compiled-pattern variants, pattern-helper keyword rows, or another benchmark owner file in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking another raw module keyword benchmark suite:
  - extend the shared `collection-replacement-keyword` benchmark-to-correctness mapping by exactly two entries for the new workload ids above, with anchors `workflow-module-sub-unexpected-keyword-after-positional-count` and `workflow-module-subn-unexpected-keyword-after-positional-count-bytes`;
  - extend the existing raw module keyword contract coverage so the manifest round-trip checks, callback-time numeric-field materialization checks, CPython exception-matching checks, and internal workload-probe coverage now include the new raw module positional-count-plus-unexpected-keyword pair alongside the already-landed raw module `split()` / `sub()` / `subn()` keyword rows;
  - update the module keyword replacement/split measured-row expectation from `35` workloads to `37`;
  - update the collection-replacement manifest expectations from `83` measured workloads to `85`, still with `0` known gaps on that manifest;
  - update the combined publication totals from `891` total / `891` measured / `0` known gaps across `30` manifests to `893` / `893` / `0` across the same `30` manifests; and
  - update `REPORT["summary"]["module_workloads"]` from `883` to `885`, while keeping `REPORT["summary"]["parser_workloads"]` at `8` and `REPORT["summary"]["regression_workloads"]` at `8`.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `selected_workload_count == 83`, `measured_workloads == 83`, and `known_gap_count == 0` to `85`, `85`, and `0`;
  - `REPORT["artifacts"]["manifests"]` keeps `collection-replacement-boundary` on the same tracked manifest path while moving its `workload_count` from `83` to `85`;
  - the combined tracked summary moves from `891` total / `891` measured / `0` known gaps with `883` module workloads to `893` / `893` / `0` with `885` module workloads; and
  - the two new raw module positional-count-plus-unexpected-keyword workloads publish real `rebar` timings with `status == "measured"`, not placeholders.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module-sub-unexpected-keyword-after-positional-count or module-subn-unexpected-keyword-after-positional-count-bytes'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_module_keyword_replacement_and_split_rows_measured or module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time or module_helper_workflow_keyword_error_callbacks_match_cpython_exceptions or run_internal_workload_probe_measures_module_helper_keyword_error_workloads or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0943-raw-module-sub-subn-unexpected-keyword-after-positional-count-boundary-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only. Do not widen the correctness surface or change Rust/Python regex behavior beyond what is required to publish and time the exact raw module-level positional-count-plus-unexpected-keyword pair above on the existing benchmark owner path.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another raw module keyword benchmark manifest, another benchmark suite, or detached benchmark expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.
- Planning probes in this checkout already show that the current benchmark harness can normalize and measure the exact two workload shapes above, so do not widen this run into speculative `python/rebar_harness/benchmarks.py` changes unless a narrowly reproducible regression on this exact owner path appears while landing the two rows.

## Notes
- `RBR-0943` is the next available task id in the current checkout:
  - `RBR-0941` is the latest done feature task on this frontier;
  - `RBR-0942` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0941` / `RBR-0942` on the same shared `module-workflow-surface` / `collection-replacement-boundary` frontier so the already-published raw module positional-count-plus-unexpected-keyword pair reaches the tracked Python-path benchmark surface before another module-helper keyword family widens the queue.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module-sub-unexpected-keyword-after-positional-count or module-subn-unexpected-keyword-after-positional-count-bytes'` currently passes in this checkout (`4 passed, 1361 deselected`);
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... re.sub(\"abc\", \"x\", \"abc\", 1, missing=1) ... rebar.sub(\"abc\", \"x\", \"abc\", 1, missing=1) ... re.subn(b\"abc\", b\"x\", b\"abc\", 1, missing=1) ... rebar.subn(b\"abc\", b\"x\", b\"abc\", 1, missing=1) ... PY` shows CPython and `rebar` already agree on the exact bounded `TypeError.args`: `(\"sub() got an unexpected keyword argument 'missing'\",)` and `(\"subn() got an unexpected keyword argument 'missing'\",)`;
  - task-local synthetic benchmark probes created from the existing raw module `module-sub-unexpected-keyword-purged-str` and `module-subn-unexpected-keyword-purged-bytes` workloads, with only `count` changed to `1` and the ids rewritten to the new `-after-positional-count-` spellings, both return `status == "measured"` for `rebar` in this checkout;
  - `rg -n --pcre2 'module-sub-unexpected-keyword-after-positional-count-purged-str(?!-compiled-pattern)|module-subn-unexpected-keyword-after-positional-count-purged-bytes(?!-compiled-pattern)' benchmarks/workloads/collection_replacement_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/benchmarks/latest.py` returned no matches in this run, so the exact raw module benchmark ids are still absent while the compiled-pattern variants remain published on the same owner path;
  - `reports/correctness/latest.py` currently reports `1545` total / `1545` passed / `0` unimplemented across `114` manifests; and
  - `reports/benchmarks/latest.py` currently reports `891` total / `891` measured / `0` known gaps overall, with `collection-replacement-boundary` at `83` selected / `83` measured / `0` known gaps and `module_workloads == 883`.

## Completion
- Added `module-sub-unexpected-keyword-after-positional-count-purged-str` and `module-subn-unexpected-keyword-after-positional-count-purged-bytes` to `benchmarks/workloads/collection_replacement_boundary.py` in the required raw-module slots between the existing unexpected-keyword rows and the compiled-pattern follow-ons.
- Extended `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` on the existing shared contract path: the `collection-replacement-keyword` anchor map now includes both new raw-module ids, the raw-module keyword manifest-contract coverage now round-trips and callback-checks the new positional-count-plus-unexpected-keyword pair, the module keyword measured-row expectation moved from `35` to `37`, the collection-replacement manifest moved from `83` measured rows to `85`, and the combined full-suite summary moved from `891` / `891` / `0` to `893` / `893` / `0` with `885` module workloads.
- Republished `reports/benchmarks/latest.py`. The tracked artifact remains in the diff and now reports `893` total workloads, `893` measured workloads, `0` known gaps, `885` module workloads, and `collection-replacement-boundary` at `85` selected / `85` measured / `0` known gaps; both new raw-module positional-count rows publish with `status == "measured"`.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module-sub-unexpected-keyword-after-positional-count or module-subn-unexpected-keyword-after-positional-count-bytes'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_module_keyword_replacement_and_split_rows_measured or module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time or module_helper_workflow_keyword_error_callbacks_match_cpython_exceptions or run_internal_workload_probe_measures_module_helper_keyword_error_workloads or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_manifest_preserves_module_collection_replacement_keyword_descriptors_until_helper_invocation or collection_replacement_manifest_keeps_module_keyword_replacement_and_split_rows_measured or module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time or module_helper_workflow_keyword_error_callbacks_match_cpython_exceptions or run_internal_workload_probe_measures_module_helper_keyword_error_workloads or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0943-raw-module-sub-subn-unexpected-keyword-after-positional-count-boundary-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`
