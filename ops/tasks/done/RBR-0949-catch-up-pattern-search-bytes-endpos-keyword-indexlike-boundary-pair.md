# RBR-0949: Catch up the `Pattern.search()` bytes `endpos` keyword/indexlike boundary pair

Status: done
Owner: feature-implementation
Created: 2026-03-22
Completed: 2026-03-22

## Goal
- Extend the published Python-path `pattern_boundary.py` benchmark surface with the exact bytes `Pattern.search()` `endpos` keyword/indexlike pair that the shared `module-workflow-surface` correctness path already publishes, while keeping this work on the existing pattern-window benchmark owner route and limiting the run to the exact missing workload rows plus the matching shared benchmark assertions.

## Pattern Pair
- `re.compile(b"abc").search(b"zabcabc", endpos=4)`
- `re.compile(b"abc").search(b"zabcabc", endpos=_INDEX_FOUR)`

## Deliverables
- `benchmarks/workloads/pattern_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/pattern_boundary.py` remains the only benchmark manifest for this slice and grows by exactly two bytes `Pattern.search()` window-keyword workloads:
  - add `pattern-search-endpos-keyword-purged-bytes`;
  - add `pattern-search-endpos-indexlike-keyword-purged-bytes`.
- Keep those two workloads pinned to the exact already-published correctness anchors rather than widening the pattern-window family:
  - `pattern-search-endpos-keyword-purged-bytes` uses `operation == "pattern.search"`, `pattern == "abc"`, `haystack == "zabcabc"`, `flags == 0`, `text_model == "bytes"`, `kwargs == {"endpos": 4}`, `cache_mode == "purged"`, and `timing_scope == "pattern-helper-call"`;
  - `pattern-search-endpos-indexlike-keyword-purged-bytes` uses `operation == "pattern.search"`, `pattern == "abc"`, `haystack == "zabcabc"`, `flags == 0`, `text_model == "bytes"`, `kwargs == {"endpos": {"type": "indexlike", "value": 4}}`, `cache_mode == "purged"`, and `timing_scope == "pattern-helper-call"`;
  - anchor the two workloads to `workflow-pattern-search-bytes-endpos-keyword` and `workflow-pattern-search-bytes-endpos-indexlike`;
  - insert `pattern-search-endpos-keyword-purged-bytes` immediately after `pattern-search-pos-keyword-warm-str` and immediately before `pattern-search-endpos-indexlike-keyword-purged-bytes`;
  - insert `pattern-search-endpos-indexlike-keyword-purged-bytes` immediately after `pattern-search-endpos-keyword-purged-bytes` and immediately before `pattern-match-pos-keyword-purged-str`; and
  - do not widen into `Pattern.search()` `pos=` neighbors, positional `endpos` carriers, `Pattern.match()` / `fullmatch()` / `findall()` / `finditer()` rows, another benchmark manifest, or benchmark-harness churn in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the existing shared pattern-window owner path instead of forking another pattern benchmark suite:
  - update `test_pattern_boundary_manifest_keeps_keyword_and_positional_window_rows_measured(...)` so `pattern-boundary` moves from `18` total measured workloads to `20`, the keyword-window subset moves from `6` rows to `8`, the positional-indexlike subset stays at `6`, and the keyword-window ids now include the new `pattern-search-endpos-keyword-purged-bytes` / `pattern-search-endpos-indexlike-keyword-purged-bytes` pair immediately after `pattern-search-pos-keyword-warm-str`;
  - extend the existing `pattern-window-keyword` standard anchor-contract definition by exactly two entries for the new workload ids above, with anchors `workflow-pattern-search-bytes-endpos-keyword` and `workflow-pattern-search-bytes-endpos-indexlike`;
  - extend `test_standard_benchmark_manifest_preserves_pattern_keyword_window_descriptors_until_helper_invocation(...)` so its synthetic keyword-window manifest grows from `6` workloads to `8`, preserving descriptor round-trip and result parity for the new bytes `Pattern.search()` `endpos` keyword/indexlike pair;
  - extend `test_pattern_helper_keyword_kwargs_materialize_at_callback_time(...)` or a narrowly adjacent helper-path assertion on the same owner route so the new bytes `Pattern.search()` rows prove callback-time materialization of `kwargs.endpos`, with the indexlike spelling still materializing through `__index__()`;
  - keep the work on the existing pattern-window owner path instead of creating a detached benchmark manifest, another test module, or a second id-only selector table;
  - update the `pattern-boundary` manifest expectations from `18` selected / `18` measured / `0` known gaps to `20` / `20` / `0`;
  - update the combined publication totals from `895` total / `895` measured / `0` known gaps across `30` manifests to `897` / `897` / `0` across the same `30` manifests; and
  - update `REPORT["summary"]["module_workloads"]` from `887` to `889`, while keeping `REPORT["summary"]["parser_workloads"]` at `8` and `REPORT["summary"]["regression_workloads"]` at `8`.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["pattern-boundary"]` moves from `selected_workload_count == 18`, `measured_workloads == 18`, `known_gap_count == 0`, and `workload_count == 18` to `20`, `20`, `0`, and `20`;
  - `REPORT["artifacts"]["manifests"]` keeps `pattern-boundary` on the same tracked manifest path while moving its `workload_count` from `18` to `20`;
  - the combined tracked summary moves from `895` total / `895` measured / `0` known gaps with `887` module workloads to `897` / `897` / `0` with `889` module workloads; and
  - the two new bytes `Pattern.search()` `endpos` workloads publish real `rebar` timings with `status == "measured"`, not placeholders.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-search-endpos-keyword-bytes or pattern-search-endpos-indexlike-bytes or module_workflow_surface_publishes_pattern_keyword_helpers_from_direct_cases'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'pattern_boundary_manifest_keeps_keyword_and_positional_window_rows_measured or pattern_window_keyword or standard_benchmark_manifest_preserves_pattern_keyword_window_descriptors_until_helper_invocation or pattern_helper_keyword_kwargs_materialize_at_callback_time'`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/pattern_boundary.py --report .rebar/tmp/rbr-0949-pattern-search-bytes-endpos-keyword-indexlike-boundary-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only. Do not widen the correctness surface, change Rust/Python regex behavior, or mint another benchmark family just to cover a larger pattern-window matrix.
- Reuse the existing `pattern_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another pattern-boundary manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.

## Notes
- `RBR-0949` is the next available feature task id in the current checkout:
  - `RBR-0947` is the latest done feature task on the drained collection/replacement keyword frontier;
  - `RBR-0948` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this after the drained collection/replacement keyword-error lane: that owner path is now fully benchmarked in the current bounded slice, so the next concrete Python-path catch-up reopens through the adjacent `pattern_boundary.py` window owner route instead of inventing another collection/replacement sibling.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-search-endpos-keyword-bytes or pattern-search-endpos-indexlike-bytes or module_workflow_surface_publishes_pattern_keyword_helpers_from_direct_cases'` currently passes (`5 passed`), so the exact bounded owner-path parity is already green in this checkout;
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... re.compile(b\"abc\").search(b\"zabcabc\", endpos=4) ... rebar.compile(b\"abc\").search(b\"zabcabc\", endpos=4) ... re.compile(b\"abc\").search(b\"zabcabc\", endpos=_INDEX_FOUR) ... rebar.compile(b\"abc\").search(b\"zabcabc\", endpos=_INDEX_FOUR) ... PY` shows CPython and `rebar` already agree on the bounded match span `(1, 4)` for both spellings;
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... run_internal_workload_probe(...) synthetic ids pattern-search-endpos-keyword-purged-bytes-synthetic / pattern-search-endpos-indexlike-keyword-purged-bytes-synthetic ... PY` returns `status == "measured"` for both `rebar` probes in this checkout, so the current benchmark harness already measures the exact two workload shapes without another prerequisite; and
  - `rg -n 'pattern-search-endpos-keyword-purged-bytes|pattern-search-endpos-indexlike-keyword-purged-bytes' benchmarks/workloads/pattern_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/benchmarks/latest.py` currently returns no exact workload-id matches, so the bounded pair is still absent from the tracked benchmark surface.

## Completion
- 2026-03-22: Added `pattern-search-endpos-keyword-purged-bytes` and `pattern-search-endpos-indexlike-keyword-purged-bytes` to `benchmarks/workloads/pattern_boundary.py` immediately after `pattern-search-pos-keyword-warm-str`, keeping the exact bytes `Pattern.search()` `endpos=` keyword/indexlike pair on the existing pattern-window owner route and immediately before `pattern-match-pos-keyword-purged-str`.
- Updated `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the shared `pattern-boundary` owner-path expectations now move from `18` to `20` measured rows, the keyword-window subset moves from `6` to `8`, the `pattern-window-keyword` anchor contract now includes the `workflow-pattern-search-bytes-endpos-keyword` / `workflow-pattern-search-bytes-endpos-indexlike` pair, and the synthetic keyword-window plus helper-materialization checks now cover the new bytes `Pattern.search()` `endpos` keyword/indexlike rows without forking another suite.
- Republished `reports/benchmarks/latest.py`. The tracked report remains in the diff and now reads `897` total / `897` measured / `0` known gaps across `30` manifests, with `REPORT["summary"]["module_workloads"] == 889`, `REPORT["summary"]["parser_workloads"] == 8`, and `REPORT["summary"]["regression_workloads"] == 8`. `REPORT["manifests"]["pattern-boundary"]` now reports `20` selected / `20` measured / `0` known gaps with `workload_count == 20`, the matching artifact manifest record also has `workload_count == 20`, and both new rows publish real `rebar` timings with `status == "measured"`.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-search-endpos-keyword-bytes or pattern-search-endpos-indexlike-bytes or module_workflow_surface_publishes_pattern_keyword_helpers_from_direct_cases'`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'pattern_boundary_manifest_keeps_keyword_and_positional_window_rows_measured or pattern_window_keyword or standard_benchmark_manifest_preserves_pattern_keyword_window_descriptors_until_helper_invocation or pattern_helper_keyword_kwargs_materialize_at_callback_time'`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/pattern_boundary.py --report .rebar/tmp/rbr-0949-pattern-search-bytes-endpos-keyword-indexlike-boundary-pair.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`.
