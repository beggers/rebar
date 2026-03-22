# RBR-0953: Catch up the module replacement `count_alias` keyword boundary pair

Status: done
Owner: feature-implementation
Created: 2026-03-22
Completed: 2026-03-22

## Goal
- Extend the published Python-path `collection_replacement_boundary.py` benchmark surface with the exact raw module-level replacement `count_alias` keyword-name rejection pair that `RBR-0951` just published on the shared `module-workflow-surface` correctness path, while keeping this run on the existing raw module collection/replacement keyword owner route and limiting the work to the exact missing benchmark rows plus the matching shared benchmark assertions.

## Pattern Pair
- `re.sub("abc", "x", "abcabc", count_alias=1)`
- `re.subn(b"abc", b"x", b"abcabc", count_alias=1)`

## Deliverables
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly two raw module-helper keyword-error workloads:
  - add `module-sub-count-alias-keyword-purged-str`; and
  - add `module-subn-count-alias-keyword-purged-bytes`.
- Keep those two workloads pinned to the exact `RBR-0951` correctness anchors rather than widening the collection/replacement family:
  - `module-sub-count-alias-keyword-purged-str` uses `operation == "module.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `flags == 0`, `kwargs == {"count_alias": 1}`, `expected_exception == {"type": "TypeError", "message_substring": "unexpected keyword argument 'count_alias'"}`, `text_model == "str"`, `cache_mode == "purged"`, and `timing_scope == "module-helper-call"`;
  - `module-subn-count-alias-keyword-purged-bytes` uses `operation == "module.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `flags == 0`, `kwargs == {"count_alias": 1}`, `expected_exception == {"type": "TypeError", "message_substring": "unexpected keyword argument 'count_alias'"}`, `text_model == "bytes"`, `cache_mode == "purged"`, and `timing_scope == "module-helper-call"`;
  - anchor the two workloads to `workflow-module-sub-count-alias-keyword` and `workflow-module-subn-count-alias-keyword-bytes`;
  - insert `module-sub-count-alias-keyword-purged-str` immediately after `module-sub-unexpected-keyword-after-positional-count-purged-str`;
  - insert `module-subn-count-alias-keyword-purged-bytes` immediately after `module-subn-unexpected-keyword-after-positional-count-purged-bytes`; and
  - do not widen into compiled-pattern-first-argument rows, other raw module keyword-name errors, or another benchmark owner file in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking another raw module keyword benchmark suite:
  - extend the shared `collection-replacement-keyword` benchmark-to-correctness mapping by exactly two entries for the new workload ids above, with anchors `workflow-module-sub-count-alias-keyword` and `workflow-module-subn-count-alias-keyword-bytes`;
  - extend the existing raw module keyword contract coverage so the manifest round-trip checks, callback-time keyword materialization checks, CPython exception-matching checks, and internal workload-probe coverage now include the new raw module replacement `count_alias` pair alongside the already-landed raw module `split()` and `sub()` / `subn()` keyword rows;
  - update `_MODULE_HELPER_COLLECTION_REPLACEMENT_KEYWORD_ERROR_WORKLOAD_IDS` from `7` rows to `9`, adding the two new raw module replacement ids;
  - update the module keyword replacement/split measured-row expectation from `39` workloads to `41`;
  - update the collection-replacement manifest expectations from `87` measured workloads to `89`, still with `0` known gaps on that manifest;
  - update the combined publication totals from `897` total / `897` measured / `0` known gaps across `30` manifests to `899` / `899` / `0` across the same `30` manifests; and
  - update `REPORT["summary"]["module_workloads"]` from `889` to `891`, while keeping `REPORT["summary"]["parser_workloads"]` at `8` and `REPORT["summary"]["regression_workloads"]` at `8`.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `selected_workload_count == 87`, `measured_workloads == 87`, and `known_gap_count == 0` to `89`, `89`, and `0`;
  - `REPORT["artifacts"]["manifests"]` keeps `collection-replacement-boundary` on the same tracked manifest path while moving its `workload_count` from `87` to `89`;
  - the combined tracked summary moves from `897` total / `897` measured / `0` known gaps with `889` module workloads to `899` / `899` / `0` with `891` module workloads; and
  - the two new raw module replacement `count_alias` workloads publish real `rebar` timings with `status == "measured"`, not placeholders.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module-sub-count-alias-keyword or module-subn-count-alias-keyword-bytes or module_workflow_surface_publishes_module_keyword_error_slice_from_direct_cases'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_module_keyword_replacement_and_split_rows_measured or standard_benchmark_manifest_preserves_module_collection_replacement_keyword_descriptors_until_helper_invocation or module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time or module_helper_workflow_keyword_error_callbacks_match_cpython_exceptions or run_internal_workload_probe_measures_module_helper_keyword_error_workloads or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0953-module-replacement-count-alias-keyword-boundary-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only. Do not widen the correctness surface or change Rust/Python regex behavior beyond what is required to publish and time the exact raw module-level replacement `count_alias` keyword pair above on the existing benchmark owner path.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another raw module keyword benchmark manifest, another benchmark suite, or detached benchmark expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.
- Planning probes in this checkout already show that the current benchmark harness can normalize and measure the exact two workload shapes above, so do not widen this run into speculative `python/rebar_harness/benchmarks.py` changes unless a narrowly reproducible regression on this exact owner path appears while landing the two rows.

## Notes
- `RBR-0953` is the next available feature task id in the current checkout:
  - `RBR-0951` is the latest done feature task on this frontier;
  - `RBR-0952` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0951` / `RBR-0952` on the same shared `module-workflow-surface` / `collection-replacement-boundary` frontier so the newly published raw module replacement `count_alias` rejection pair reaches the tracked Python-path benchmark surface before another raw module keyword family widens the queue.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module-sub-count-alias-keyword or module-subn-count-alias-keyword-bytes or module_replacement_unexpected_keyword_names_match_cpython'` currently passes (`28 passed`), so the exact bounded correctness/parity slice is already green in this checkout;
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... re.sub(\"abc\", \"x\", \"abcabc\", count_alias=1) ... rebar.sub(\"abc\", \"x\", \"abcabc\", count_alias=1) ... re.subn(b\"abc\", b\"x\", b\"abcabc\", count_alias=1) ... rebar.subn(b\"abc\", b\"x\", b\"abcabc\", count_alias=1) ... PY` shows CPython and `rebar` already agree on the exact bounded `TypeError.args`: `(\"sub() got an unexpected keyword argument 'count_alias'\",)` for the `str` spelling and `(\"subn() got an unexpected keyword argument 'count_alias'\",)` for the `bytes` spelling;
  - `PYTHONPATH=python:. ./.venv/bin/python - <<'PY' ... run_internal_workload_probe(...) synthetic ids module-sub-count-alias-keyword-purged-str / module-subn-count-alias-keyword-purged-bytes ... PY` returns `status == "measured"` for both synthetic `rebar` probes in this checkout, so the current benchmark harness already measures the exact bounded pair without another prerequisite;
  - `rg -n 'count_alias|module-sub-count-alias-keyword-purged-str|module-subn-count-alias-keyword-purged-bytes' benchmarks/workloads/collection_replacement_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/benchmarks/latest.py` currently returns no matches, so the exact raw module benchmark ids are still absent while the matching correctness anchors are already present; and
  - live tracked reports currently read `1549` total / `1549` passed / `0` unimplemented across `114` manifests in `reports/correctness/latest.py`, plus `897` total / `897` measured / `0` known gaps overall with `collection-replacement-boundary` at `87` selected / `87` measured / `0` known gaps and `module_workloads == 889` in `reports/benchmarks/latest.py`.

## Completion
- 2026-03-22: Added `module-sub-count-alias-keyword-purged-str` and `module-subn-count-alias-keyword-purged-bytes` to `benchmarks/workloads/collection_replacement_boundary.py` immediately after the existing raw module positional-count keyword-error rows, keeping the slice on the shared collection/replacement owner path with the exact `count_alias` kwargs, `abcabc` haystacks, `module-helper-call` timing scope, and `TypeError` substring expectations.
- Updated `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the shared `collection-replacement-keyword` anchor mapping, the module keyword manifest expectation, the benchmark manifest round-trip contract, the callback-time keyword materialization checks, the CPython exception-match coverage, the internal workload-probe coverage, and the published full-suite summary all include the new raw module replacement `count_alias` pair. The module keyword replacement/split measured-row expectation now moves from `39` to `41`.
- Republished `reports/benchmarks/latest.py`. The tracked report remains in the diff and now reads `899` total / `899` measured / `0` known gaps overall with `module_workloads == 891`, while `collection-replacement-boundary` now reads `89` selected / `89` measured / `0` known gaps and its tracked artifact record now reports `workload_count == 89`. The two new workload ids publish real `measured` timings in the tracked report.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module-sub-count-alias-keyword or module-subn-count-alias-keyword-bytes or module_workflow_surface_publishes_module_keyword_error_slice_from_direct_cases'`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_module_keyword_replacement_and_split_rows_measured or standard_benchmark_manifest_preserves_module_collection_replacement_keyword_descriptors_until_helper_invocation or module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time or module_helper_workflow_keyword_error_callbacks_match_cpython_exceptions or run_internal_workload_probe_measures_module_helper_keyword_error_workloads or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0953-module-replacement-count-alias-keyword-boundary-pair.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`.
