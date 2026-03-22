# RBR-0947: Catch up the raw module `split()` unexpected-keyword str/bytes boundary pair

Status: done
Owner: feature-implementation
Created: 2026-03-22
Completed: 2026-03-22

## Goal
- Extend the published Python-path `collection_replacement_boundary.py` benchmark surface with the exact raw module-level `split()` unexpected-keyword str/bytes pair that `RBR-0945` just published on the shared `module-workflow-surface` correctness path, while keeping this work on the existing raw module collection/replacement keyword owner route and limiting the run to the exact missing benchmark rows plus the matching shared benchmark assertions.

## Pattern Pair
- `re.split("abc", "abc", missing=1)`
- `re.split(b"abc", b"abc", missing=1)`

## Deliverables
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly two raw module-helper keyword-error workloads:
  - add `module-split-unexpected-keyword-purged-str`; and
  - add `module-split-unexpected-keyword-purged-bytes`.
- Keep those two workloads pinned to the exact `RBR-0945` correctness anchors rather than widening the collection/replacement family:
  - `module-split-unexpected-keyword-purged-str` uses `operation == "module.split"`, `pattern == "abc"`, `haystack == "abc"`, `flags == 0`, `kwargs == {"missing": 1}`, `expected_exception == {"type": "TypeError", "message_substring": "unexpected keyword argument 'missing'"}`, `text_model == "str"`, `cache_mode == "purged"`, and `timing_scope == "module-helper-call"`;
  - `module-split-unexpected-keyword-purged-bytes` uses `operation == "module.split"`, `pattern == "abc"`, `haystack == "abc"`, `flags == 0`, `kwargs == {"missing": 1}`, `expected_exception == {"type": "TypeError", "message_substring": "unexpected keyword argument 'missing'"}`, `text_model == "bytes"`, `cache_mode == "purged"`, and `timing_scope == "module-helper-call"`;
  - anchor the two workloads to `workflow-module-split-unexpected-keyword` and `workflow-module-split-unexpected-keyword-bytes`;
  - insert `module-split-unexpected-keyword-purged-str` immediately after `module-split-duplicate-maxsplit-keyword-purged-str`;
  - insert `module-split-unexpected-keyword-purged-bytes` immediately after `module-split-unexpected-keyword-purged-str` and immediately before `module-split-duplicate-maxsplit-keyword-purged-str-compiled-pattern`; and
  - do not widen into other raw module `split()` keyword forms, compiled-pattern-first-argument rows, `sub()` / `subn()` rows, or another benchmark owner file in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking another raw module keyword benchmark suite:
  - extend the shared `collection-replacement-keyword` benchmark-to-correctness mapping by exactly two entries for the new workload ids above, with anchors `workflow-module-split-unexpected-keyword` and `workflow-module-split-unexpected-keyword-bytes`;
  - extend the existing raw module keyword contract coverage so the manifest round-trip checks, callback-time keyword materialization checks, CPython exception-matching checks, and internal workload-probe coverage now include the new raw module `split()` unexpected-keyword pair alongside the already-landed raw module `split()` duplicate-maxsplit row and raw module `sub()` / `subn()` keyword rows;
  - update `_MODULE_HELPER_COLLECTION_REPLACEMENT_KEYWORD_ERROR_WORKLOAD_IDS` from `5` rows to `7`, adding the two new raw module `split()` ids;
  - update the module keyword replacement/split measured-row expectation from `37` workloads to `39`;
  - update the collection-replacement manifest expectations from `85` measured workloads to `87`, still with `0` known gaps on that manifest;
  - update the combined publication totals from `893` total / `893` measured / `0` known gaps across `30` manifests to `895` / `895` / `0` across the same `30` manifests; and
  - update `REPORT["summary"]["module_workloads"]` from `885` to `887`, while keeping `REPORT["summary"]["parser_workloads"]` at `8` and `REPORT["summary"]["regression_workloads"]` at `8`.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `selected_workload_count == 85`, `measured_workloads == 85`, and `known_gap_count == 0` to `87`, `87`, and `0`;
  - `REPORT["artifacts"]["manifests"]` keeps `collection-replacement-boundary` on the same tracked manifest path while moving its `workload_count` from `85` to `87`;
  - the combined tracked summary moves from `893` total / `893` measured / `0` known gaps with `885` module workloads to `895` / `895` / `0` with `887` module workloads; and
  - the two new raw module `split()` unexpected-keyword workloads publish real `rebar` timings with `status == "measured"`, not placeholders.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module-split-unexpected-keyword or module_workflow_surface_publishes_module_keyword_error_slice_from_direct_cases'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_module_keyword_replacement_and_split_rows_measured or standard_benchmark_manifest_preserves_module_collection_replacement_keyword_descriptors_until_helper_invocation or module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time or module_helper_workflow_keyword_error_callbacks_match_cpython_exceptions or run_internal_workload_probe_measures_module_helper_keyword_error_workloads or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0947-raw-module-split-unexpected-keyword-str-bytes-boundary-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only. Do not widen the correctness surface or change Rust/Python regex behavior beyond what is required to publish and time the exact raw module-level `split()` unexpected-keyword pair above on the existing benchmark owner path.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another raw module keyword benchmark manifest, another benchmark suite, or detached benchmark expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.
- Planning probes in this checkout already show that the current benchmark harness can normalize and measure the exact two workload shapes above, so do not widen this run into speculative `python/rebar_harness/benchmarks.py` changes unless a narrowly reproducible regression on this exact owner path appears while landing the two rows.

## Notes
- `RBR-0947` is the next available feature task id in the current checkout:
  - `RBR-0945` is the latest done feature task on this frontier;
  - `RBR-0946` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0945` / `RBR-0946` on the same shared `module-workflow-surface` / `collection-replacement-boundary` frontier so the newly published raw module `split()` unexpected-keyword pair reaches the tracked Python-path benchmark surface before another raw module keyword family widens the queue.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... re.split(\"abc\", \"abc\", missing=1) ... rebar.split(\"abc\", \"abc\", missing=1) ... re.split(b\"abc\", b\"abc\", missing=1) ... rebar.split(b\"abc\", b\"abc\", missing=1) ... PY` shows CPython and `rebar` already agree on the exact bounded `TypeError.args`: `(\"split() got an unexpected keyword argument 'missing'\",)` for both the `str` and `bytes` spellings;
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... load_manifest(Path(\"benchmarks/workloads/collection_replacement_boundary.py\")) ... workload_to_payload(...) ... run_internal_workload_probe(...) ... synthetic ids module-split-unexpected-keyword-purged-str / module-split-unexpected-keyword-purged-bytes ... PY` returns `status == "measured"` for both synthetic `rebar` probes in this checkout, so the current benchmark harness already measures the exact bounded pair without another prerequisite;
  - `rg -n 'module-split-unexpected-keyword-purged-(str|bytes)\\b' benchmarks/workloads/collection_replacement_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/benchmarks/latest.py` returned no matches in this run, so the exact raw module benchmark ids are still absent while the matching correctness anchors are already present;
  - `reports/correctness/latest.py` currently reports `1547` total / `1547` passed / `0` unimplemented across `114` manifests; and
  - `reports/benchmarks/latest.py` currently reports `893` total / `893` measured / `0` known gaps overall, with `collection-replacement-boundary` at `85` selected / `85` measured / `0` known gaps and `module_workloads == 885`.

## Completion
- 2026-03-22: Added `module-split-unexpected-keyword-purged-str` and `module-split-unexpected-keyword-purged-bytes` to `benchmarks/workloads/collection_replacement_boundary.py` immediately after `module-split-duplicate-maxsplit-keyword-purged-str`, keeping the exact raw `module.split` `missing=1` signature, the `workflow-module-split-unexpected-keyword` / `workflow-module-split-unexpected-keyword-bytes` anchor pair, and the existing shared manifest owner path.
- Updated `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the shared `collection-replacement-keyword` mapping, the raw module keyword contract coverage, the callback-time keyword materialization checks, the CPython exception-matching checks, and the internal workload-probe coverage now include the new raw module `split()` unexpected-keyword str/bytes pair. The raw module keyword-error source-id set now contains `7` rows, the module keyword replacement/split measured-row expectation moves to `39`, and the full published summary expectation moves to `895` total / `895` measured / `0` known gaps with `887` module workloads.
- Republished `reports/benchmarks/latest.py`. The tracked report remains in the diff and now reads `895` total / `895` measured / `0` known gaps across `30` manifests, with `collection-replacement-boundary` at `87` selected / `87` measured / `0` known gaps, the manifest artifact `workload_count` at `87`, and `REPORT["summary"]["module_workloads"] == 887`. The two new raw module `split()` rows publish real `rebar` timings with `status == "measured"`.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module-split-unexpected-keyword or module_workflow_surface_publishes_module_keyword_error_slice_from_direct_cases'`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_module_keyword_replacement_and_split_rows_measured or standard_benchmark_manifest_preserves_module_collection_replacement_keyword_descriptors_until_helper_invocation or module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time or module_helper_workflow_keyword_error_callbacks_match_cpython_exceptions or run_internal_workload_probe_measures_module_helper_keyword_error_workloads or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0947-raw-module-split-unexpected-keyword-str-bytes-boundary-pair.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`.
