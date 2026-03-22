# RBR-0957: Catch up the compiled-pattern module replacement `count_alias` keyword boundary pair

Status: done
Owner: feature-implementation
Created: 2026-03-22
Completed: 2026-03-22

## Goal
- Extend the published Python-path `collection_replacement_boundary.py` benchmark surface with the exact compiled-pattern-first-argument module-level replacement `count_alias` keyword-name rejection pair that `RBR-0955` just published on the shared `module-workflow-surface` correctness path, while keeping this run on the existing compiled-pattern collection/replacement keyword-error owner route and limiting the work to the exact missing benchmark rows plus the matching shared benchmark assertions.

## Pattern Pair
- `re.sub(re.compile("abc"), "x", "abcabc", count_alias=1)`
- `re.subn(re.compile(b"abc"), b"x", b"abcabc", count_alias=1)`

## Deliverables
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly two compiled-pattern-first-argument module-helper keyword-error workloads:
  - add `module-sub-count-alias-keyword-purged-str-compiled-pattern`; and
  - add `module-subn-count-alias-keyword-purged-bytes-compiled-pattern`.
- Keep those two workloads pinned to the exact `RBR-0955` correctness anchors rather than widening the collection/replacement family:
  - `module-sub-count-alias-keyword-purged-str-compiled-pattern` uses `operation == "module.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `flags == 0`, `use_compiled_pattern == True`, `kwargs == {"count_alias": 1}`, `expected_exception == {"type": "TypeError", "message_substring": "unexpected keyword argument 'count_alias'"}`, `text_model == "str"`, `cache_mode == "purged"`, and `timing_scope == "module-helper-call"`;
  - `module-subn-count-alias-keyword-purged-bytes-compiled-pattern` uses `operation == "module.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `flags == 0`, `use_compiled_pattern == True`, `kwargs == {"count_alias": 1}`, `expected_exception == {"type": "TypeError", "message_substring": "unexpected keyword argument 'count_alias'"}`, `text_model == "bytes"`, `cache_mode == "purged"`, and `timing_scope == "module-helper-call"`;
  - anchor the two workloads to `workflow-module-sub-count-alias-keyword-str-compiled-pattern` and `workflow-module-subn-count-alias-keyword-bytes-compiled-pattern`;
  - insert `module-sub-count-alias-keyword-purged-str-compiled-pattern` immediately after `module-sub-unexpected-keyword-after-positional-count-purged-str-compiled-pattern`;
  - insert `module-subn-count-alias-keyword-purged-bytes-compiled-pattern` immediately after `module-subn-unexpected-keyword-after-positional-count-purged-bytes-compiled-pattern`; and
  - do not widen into raw-module rows, other compiled-pattern keyword-name errors, or another benchmark owner file in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared compiled-pattern source-tree benchmark contract path instead of forking another benchmark suite:
  - extend the shared `collection-replacement-keyword` benchmark-to-correctness mapping by exactly two entries for the new workload ids above, with anchors `workflow-module-sub-count-alias-keyword-str-compiled-pattern` and `workflow-module-subn-count-alias-keyword-bytes-compiled-pattern`;
  - extend `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC.expected_source_workload_ids` from `8` rows to `10`, adding the two new compiled-pattern replacement ids immediately after the existing after-positional-count `sub` / `subn` rows;
  - extend the existing compiled-pattern keyword-error contract coverage so the manifest round-trip checks, CPython exception-matching checks, callback-time field-materialization expectations, and internal workload-probe coverage now include the new compiled-pattern replacement `count_alias` pair alongside the already-landed compiled-pattern `split()` and `sub()` / `subn()` keyword-error rows;
  - update the compiled-pattern module-helper keyword-error measured-row expectation from `8` workloads to `10`;
  - update the collection-replacement manifest expectations from `89` measured workloads to `91`, still with `0` known gaps on that manifest;
  - update the combined publication totals from `899` total / `899` measured / `0` known gaps across `30` manifests to `901` / `901` / `0` across the same `30` manifests; and
  - update `REPORT["summary"]["module_workloads"]` from `891` to `893`, while keeping `REPORT["summary"]["parser_workloads"]` at `8` and `REPORT["summary"]["regression_workloads"]` at `8`.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `selected_workload_count == 89`, `measured_workloads == 89`, and `known_gap_count == 0` to `91`, `91`, and `0`;
  - `REPORT["artifacts"]["manifests"]` keeps `collection-replacement-boundary` on the same tracked manifest path while moving its `workload_count` from `89` to `91`;
  - the combined tracked summary moves from `899` total / `899` measured / `0` known gaps with `891` module workloads to `901` / `901` / `0` with `893` module workloads; and
  - the two new compiled-pattern replacement `count_alias` workloads publish real `rebar` timings with `status == "measured"`, not placeholders.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'compiled_pattern_module_replacement_unexpected_keyword_names_match_cpython or compiled_pattern_module_keyword_frontier_publishes_after_positional_count_cases_on_shared_owner_path or compiled_pattern_module_keyword_argument_errors_match_cpython'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_compiled_pattern_module_helper_keyword_error_rows_measured or standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_keyword_error_rows_until_helper_invocation or compiled_pattern_module_helper_keyword_error_callbacks_match_cpython_exceptions or run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_error_workloads or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0957-compiled-pattern-module-replacement-count-alias-keyword-boundary-pair.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only. Do not widen the correctness surface or change Rust/Python regex behavior beyond what is required to publish and time the exact compiled-pattern-first-argument replacement `count_alias` pair above on the existing benchmark owner path.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another compiled-pattern keyword benchmark manifest, another benchmark suite, or detached benchmark expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.
- Planning probes in this checkout already show that the current benchmark harness can normalize and measure the exact two workload shapes above, so do not widen this run into speculative `python/rebar_harness/benchmarks.py` changes unless a narrowly reproducible regression on this exact owner path appears while landing the two rows.

## Notes
- `RBR-0957` is the next available feature task id in the current checkout:
  - `RBR-0955` is the latest done feature task on this frontier;
  - `RBR-0956` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0955` / `RBR-0956` on the same shared `module-workflow-surface` / `collection-replacement-boundary` frontier so the newly published compiled-pattern replacement `count_alias` rejection pair reaches the tracked Python-path benchmark surface before another module-workflow keyword family widens the queue.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'compiled_pattern_module_replacement_unexpected_keyword_names_match_cpython or compiled_pattern_module_keyword_argument_errors_match_cpython'` currently passes in this checkout, so the exact bounded correctness/parity slice is already green;
  - `PYTHONPATH=python:. ./.venv/bin/python - <<'PY' ... synthetic module-sub-count-alias-keyword-purged-str-compiled-pattern / module-subn-count-alias-keyword-purged-bytes-compiled-pattern probes ... PY` returns `status == "measured"` for both CPython and `rebar`, so the current benchmark harness already measures the exact bounded pair without another prerequisite;
  - `rg -n 'module-sub-count-alias-keyword-purged-str-compiled-pattern|module-subn-count-alias-keyword-purged-bytes-compiled-pattern' benchmarks/workloads/collection_replacement_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/benchmarks/latest.py` currently returns no matches, so the exact compiled-pattern benchmark ids are still absent while the matching correctness anchors are already present; and
  - live tracked reports currently read `1551` total / `1551` passed / `0` unimplemented across `114` manifests in `reports/correctness/latest.py`, plus `899` total / `899` measured / `0` known gaps overall with `collection-replacement-boundary` at `89` selected / `89` measured / `0` known gaps and `module_workloads == 891` in `reports/benchmarks/latest.py`.

## Completion
- 2026-03-22: Added `module-sub-count-alias-keyword-purged-str-compiled-pattern` and `module-subn-count-alias-keyword-purged-bytes-compiled-pattern` to `benchmarks/workloads/collection_replacement_boundary.py` immediately after the existing compiled-pattern after-positional-count replacement keyword-error rows, keeping the slice on the existing collection/replacement benchmark owner path with the bounded `abcabc` replacement calls and exact `count_alias` `TypeError` substrings.
- Updated `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the shared `collection-replacement-keyword` anchor mapping, the compiled-pattern module-helper keyword-error contract spec, the measured-row expectations, and the published full-suite summary checks now cover the two new compiled-pattern replacement `count_alias` rows without creating another manifest or suite. The collection/replacement module-keyword measured-row count now reads `43`, and the compiled-pattern module-helper keyword-error subset now reads `10`.
- Republished `reports/benchmarks/latest.py`. The tracked report remains in the diff and now reads `901` total / `901` measured / `0` known gaps across `30` manifests, with `collection-replacement-boundary` at `91` selected / `91` measured / `0` known gaps and `module_workloads == 893`. The tracked scorecard now includes both `module-sub-count-alias-keyword-purged-str-compiled-pattern` and `module-subn-count-alias-keyword-purged-bytes-compiled-pattern` as `status == "measured"` rows with real `rebar` timings.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'compiled_pattern_module_replacement_unexpected_keyword_names_match_cpython or compiled_pattern_module_keyword_frontier_publishes_after_positional_count_cases_on_shared_owner_path or compiled_pattern_module_keyword_argument_errors_match_cpython'`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0957-compiled-pattern-module-replacement-count-alias-keyword-boundary-pair.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`, and `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_compiled_pattern_module_helper_keyword_error_rows_measured or standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_keyword_error_rows_until_helper_invocation or compiled_pattern_module_helper_keyword_error_callbacks_match_cpython_exceptions or run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_error_workloads or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`.
