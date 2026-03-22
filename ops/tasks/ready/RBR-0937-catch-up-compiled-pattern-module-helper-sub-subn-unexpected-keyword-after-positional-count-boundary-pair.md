# RBR-0937: Catch up the compiled-pattern module-helper `sub()` / `subn()` unexpected-keyword-after-positional-count boundary pair

Status: ready
Owner: feature-implementation
Created: 2026-03-22

## Goal
- Extend the published Python-path `collection_replacement_boundary.py` benchmark surface with the exact compiled-pattern-first-argument module-helper `sub()` / `subn()` positional-count-plus-extra-keyword rejection pair that `RBR-0935` just published on the shared `module-workflow-surface` correctness path, while keeping this work on the existing compiled-pattern module-helper collection/replacement keyword owner route and limiting the run to the exact missing benchmark rows plus the matching shared benchmark assertions.

## Pattern Pair
- `re.sub(re.compile("abc"), "x", "abc", 1, missing=1)`
- `re.subn(re.compile(b"abc"), b"x", b"abc", 1, missing=1)`

## Deliverables
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly two compiled-pattern-first-argument module-helper keyword-error workloads:
  - add `module-sub-unexpected-keyword-after-positional-count-purged-str-compiled-pattern`; and
  - add `module-subn-unexpected-keyword-after-positional-count-purged-bytes-compiled-pattern`.
- Keep those two workloads pinned to the exact `RBR-0935` correctness anchors rather than widening the collection/replacement family:
  - `module-sub-unexpected-keyword-after-positional-count-purged-str-compiled-pattern` uses `operation == "module.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abc"`, `flags == 0`, `use_compiled_pattern == True`, `count == 1`, `kwargs == {"missing": 1}`, `expected_exception == {"type": "TypeError", "message_substring": "unexpected keyword argument 'missing'"}`, `text_model == "str"`, `cache_mode == "purged"`, and `timing_scope == "module-helper-call"`;
  - `module-subn-unexpected-keyword-after-positional-count-purged-bytes-compiled-pattern` uses `operation == "module.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abc"`, `flags == 0`, `use_compiled_pattern == True`, `count == 1`, `kwargs == {"missing": 1}`, `expected_exception == {"type": "TypeError", "message_substring": "unexpected keyword argument 'missing'"}`, `text_model == "bytes"`, `cache_mode == "purged"`, and `timing_scope == "module-helper-call"`;
  - anchor the two workloads to `workflow-module-sub-unexpected-keyword-after-positional-count-str-compiled-pattern` and `workflow-module-subn-unexpected-keyword-after-positional-count-bytes-compiled-pattern`;
  - insert `module-sub-unexpected-keyword-after-positional-count-purged-str-compiled-pattern` immediately after `module-sub-unexpected-keyword-purged-str-compiled-pattern` and immediately before `module-subn-literal-purged-bytes-compiled-pattern`; and
  - insert `module-subn-unexpected-keyword-after-positional-count-purged-bytes-compiled-pattern` immediately after `module-subn-unexpected-keyword-purged-bytes-compiled-pattern` and immediately before `pattern-split-maxsplit-indexlike-positional-warm-str`.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking another compiled-pattern module-helper collection/replacement benchmark suite:
  - extend the shared `collection-replacement-keyword` benchmark-to-correctness mapping by exactly two entries for the new workload ids above, with anchors `workflow-module-sub-unexpected-keyword-after-positional-count-str-compiled-pattern` and `workflow-module-subn-unexpected-keyword-after-positional-count-bytes-compiled-pattern`;
  - extend the existing compiled-pattern module-helper keyword contract coverage so the manifest round-trip, callback-time numeric-field materialization, CPython exception-matching checks, and internal workload probes now cover the positional-count-plus-extra-keyword pair alongside the already-landed compiled-pattern module-helper keyword rows;
  - update the compiled-pattern module-helper keyword measured-row expectation from `6` workloads to `8`;
  - update the collection-replacement manifest expectations from `79` measured workloads to `81`, still with `0` known gaps on that manifest;
  - update the module keyword replacement/split measured-row expectation from `31` workloads to `33`;
  - update the combined publication totals from `887` total / `887` measured / `0` known gaps across `30` manifests to `889` / `889` / `0` across the same `30` manifests; and
  - update `REPORT["summary"]["module_workloads"]` from `879` to `881`, while keeping `REPORT["summary"]["parser_workloads"]` at `8` and `REPORT["summary"]["regression_workloads"]` at `8`.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `selected_workload_count == 79`, `measured_workloads == 79`, and `known_gap_count == 0` to `81`, `81`, and `0`;
  - `REPORT["artifacts"]["manifests"]` keeps `collection-replacement-boundary` on the same tracked manifest path while moving its `workload_count` from `79` to `81`;
  - the combined tracked summary moves from `887` total / `887` measured / `0` known gaps with `879` module workloads to `889` / `889` / `0` with `881` module workloads; and
  - the two new compiled-pattern module-helper keyword-error workloads publish real `rebar` timings with `status == "measured"`, not placeholders.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'compiled-pattern-sub-unexpected-keyword-after-positional-count-str or compiled-pattern-subn-unexpected-keyword-after-positional-count-bytes'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_keyword_error or collection_replacement_manifest_keeps_module_keyword_replacement_and_split_rows_measured or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0937-compiled-pattern-module-helper-sub-subn-unexpected-keyword-after-positional-count-boundary-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only. Do not widen the correctness surface or change Rust/Python regex behavior beyond what is required to publish and time the exact compiled-pattern-first-argument module-helper pair above on the existing benchmark owner path.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another compiled-pattern module-helper benchmark manifest, another benchmark suite, or detached benchmark expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.
- Planning probes in this checkout already show that the current benchmark harness can normalize and measure the exact two workload shapes above, so do not widen this run into speculative `python/rebar_harness/benchmarks.py` changes unless a narrowly reproducible regression on this exact owner path appears while landing the two rows.

## Notes
- `RBR-0937` is the next available feature task id in the current checkout:
  - `RBR-0935` is the latest done feature task on this frontier;
  - `RBR-0936` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0935` / `RBR-0936` on the same shared `module-workflow-surface` / `collection-replacement-boundary` frontier so the newly published compiled-pattern module-helper positional-count keyword-error pair reaches the tracked Python-path benchmark surface before another compiled-pattern module-helper keyword family widens the queue.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'compiled-pattern-sub-unexpected-keyword-after-positional-count-str or compiled-pattern-subn-unexpected-keyword-after-positional-count-bytes'` is already green in this checkout (`4 passed, 1361 deselected`), so the compiled-pattern module-helper owner path exposes the exact bounded error pair that this task needs to benchmark;
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... re.sub(re.compile("abc"), "x", "abc", 1, missing=1) ... rebar.sub(rebar.compile("abc"), "x", "abc", 1, missing=1) ... re.subn(re.compile(b"abc"), b"x", b"abc", 1, missing=1) ... rebar.subn(rebar.compile(b"abc"), b"x", b"abc", 1, missing=1) ... PY` shows CPython and `rebar` already agree on the exact bounded `TypeError.args`: `("sub() got an unexpected keyword argument 'missing'",)` and `("subn() got an unexpected keyword argument 'missing'",)`;
  - a task-local `load_manifest(...)` plus `run_internal_workload_probe(...)` clone of the adjacent compiled-pattern module-helper unexpected-keyword workloads, with only `count` changed to `1` and the ids rewritten to the new `-after-positional-count-` spellings, returns `status == "measured"` for both synthetic `rebar` probes in this checkout, so the current benchmark harness already measures the exact bounded pair without another prerequisite;
  - `rg -n 'module-sub-unexpected-keyword-after-positional-count-purged-str-compiled-pattern|module-subn-unexpected-keyword-after-positional-count-purged-bytes-compiled-pattern' benchmarks/workloads tests/benchmarks reports/benchmarks` returned no matches in this run, so the exact benchmark workloads are still absent while `reports/benchmarks/latest.py` remains at `887` total / `887` measured / `0` known gaps overall and `collection-replacement-boundary` remains at `79` selected / `79` measured / `0` known gaps; and
  - `reports/correctness/latest.py` currently reports `1541` total / `1541` passed / `0` unimplemented across `114` manifests, so this run stays on benchmark catch-up instead of reopening correctness publication.
