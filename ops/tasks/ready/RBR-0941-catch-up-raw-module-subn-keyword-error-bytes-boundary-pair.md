# RBR-0941: Catch up the raw module `subn()` keyword-error bytes boundary pair

Status: ready
Owner: feature-implementation
Created: 2026-03-22

## Goal
- Extend the published Python-path `collection_replacement_boundary.py` benchmark surface with the exact raw module-level `subn()` bytes duplicate-count and unexpected-keyword rejection pair that `RBR-0939` just published on the shared `module-workflow-surface` correctness path, while keeping this work on the existing module-helper collection/replacement keyword owner route and limiting the run to the exact missing benchmark rows plus the matching shared benchmark assertions.

## Pattern Pair
- `re.subn(b"abc", b"x", b"abc", 1, count=1)`
- `re.subn(b"abc", b"x", b"abc", missing=1)`

## Deliverables
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly two raw module-helper keyword-error workloads:
  - add `module-subn-duplicate-count-keyword-warm-bytes`; and
  - add `module-subn-unexpected-keyword-purged-bytes`.
- Keep those two workloads pinned to the exact `RBR-0939` correctness anchors rather than widening the collection/replacement family:
  - `module-subn-duplicate-count-keyword-warm-bytes` uses `operation == "module.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abc"`, `flags == 0`, `count == 1`, `kwargs == {"count": 1}`, `expected_exception == {"type": "TypeError", "message_substring": "multiple values for argument 'count'"}`, `text_model == "bytes"`, `cache_mode == "warm"`, and `timing_scope == "module-helper-call"`;
  - `module-subn-unexpected-keyword-purged-bytes` uses `operation == "module.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abc"`, `flags == 0`, `kwargs == {"missing": 1}`, `expected_exception == {"type": "TypeError", "message_substring": "unexpected keyword argument 'missing'"}`, `text_model == "bytes"`, `cache_mode == "purged"`, and `timing_scope == "module-helper-call"`;
  - anchor the two workloads to `workflow-module-subn-duplicate-count-keyword-bytes` and `workflow-module-subn-unexpected-keyword-bytes`;
  - insert `module-subn-duplicate-count-keyword-warm-bytes` immediately after `module-subn-count-indexlike-keyword-purged-bytes`;
  - insert `module-subn-unexpected-keyword-purged-bytes` immediately after `module-subn-duplicate-count-keyword-warm-bytes` and immediately before `module-subn-count-keyword-purged-bytes-compiled-pattern`; and
  - do not widen into the later raw module positional-count-plus-extra-keyword pair, compiled-pattern variants, or another benchmark owner file in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking another raw module keyword benchmark suite:
  - extend the shared `collection-replacement-keyword` benchmark-to-correctness mapping by exactly two entries for the new workload ids above, with anchors `workflow-module-subn-duplicate-count-keyword-bytes` and `workflow-module-subn-unexpected-keyword-bytes`;
  - extend the existing raw module keyword contract coverage so the manifest round-trip checks, callback-time numeric-field materialization checks, and measured-row expectations now include the new raw module `subn()` bytes pair alongside the already-landed raw module `split()` and `sub()` keyword rows;
  - update the module keyword replacement/split measured-row expectation from `33` workloads to `35`;
  - update the collection-replacement manifest expectations from `81` measured workloads to `83`, still with `0` known gaps on that manifest;
  - update the combined publication totals from `889` total / `889` measured / `0` known gaps across `30` manifests to `891` / `891` / `0` across the same `30` manifests; and
  - update `REPORT["summary"]["module_workloads"]` from `881` to `883`, while keeping `REPORT["summary"]["parser_workloads"]` at `8` and `REPORT["summary"]["regression_workloads"]` at `8`.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `selected_workload_count == 81`, `measured_workloads == 81`, and `known_gap_count == 0` to `83`, `83`, and `0`;
  - `REPORT["artifacts"]["manifests"]` keeps `collection-replacement-boundary` on the same tracked manifest path while moving its `workload_count` from `81` to `83`;
  - the combined tracked summary moves from `889` total / `889` measured / `0` known gaps with `881` module workloads to `891` / `891` / `0` with `883` module workloads; and
  - the two new raw module `subn()` bytes keyword-error workloads publish real `rebar` timings with `status == "measured"`, not placeholders.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module-subn-duplicate-count-keyword-bytes or module-subn-unexpected-keyword-bytes'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_manifest_keeps_module_keyword_replacement_and_split_rows_measured or standard_benchmark_manifest_preserves_module_collection_replacement_keyword_descriptors_until_helper_invocation or module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0941-raw-module-subn-keyword-error-bytes-boundary-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only. Do not widen the correctness surface or change Rust/Python regex behavior beyond what is required to publish and time the exact raw module-level `subn()` bytes pair above on the existing benchmark owner path.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another raw module keyword benchmark manifest, another benchmark suite, or detached benchmark expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.
- Planning probes in this checkout already show that the current benchmark harness can normalize and measure the exact two workload shapes above, so do not widen this run into speculative `python/rebar_harness/benchmarks.py` changes unless a narrowly reproducible regression on this exact owner path appears while landing the two rows.

## Notes
- `RBR-0941` is the next available feature task id in the current checkout:
  - `RBR-0939` is the latest done feature task on this frontier;
  - `RBR-0940` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0939` / `RBR-0940` on the same shared `module-workflow-surface` / `collection-replacement-boundary` frontier so the newly published raw module `subn()` bytes keyword-error pair reaches the tracked Python-path benchmark surface before the later positional-count follow-on or another module-helper keyword family widens the queue.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... MODULE_KEYWORD_ERROR_CASES ... case_id in {'module-subn-duplicate-count-keyword-bytes', 'module-subn-unexpected-keyword-bytes'} ... PY` shows CPython and `rebar` already agree on the exact bounded `TypeError.args`: `("subn() got multiple values for argument 'count'",)` and `("subn() got an unexpected keyword argument 'missing'",)`;
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... load_manifest(...) ... run_internal_workload_probe(...) ... synthetic ids module-subn-duplicate-count-keyword-warm-bytes / module-subn-unexpected-keyword-purged-bytes ... PY` returns `status == "measured"` for both synthetic `rebar` probes in this checkout, so the current benchmark harness already measures the exact bounded pair without another prerequisite;
  - `rg -nP 'module-subn-duplicate-count-keyword-warm-bytes(?!-compiled-pattern)|module-subn-unexpected-keyword-purged-bytes(?!-compiled-pattern)' benchmarks/workloads tests/benchmarks reports/benchmarks` returned no matches in this run, so the exact raw module workload ids are still absent while the compiled-pattern variants remain the only published `subn()` keyword-error benchmark rows on this owner path;
  - `reports/correctness/latest.py` currently reports `1543` total / `1543` passed / `0` unimplemented across `114` manifests; and
  - `reports/benchmarks/latest.py` currently reports `889` total / `889` measured / `0` known gaps overall, with `collection-replacement-boundary` at `81` selected / `81` measured / `0` known gaps.
