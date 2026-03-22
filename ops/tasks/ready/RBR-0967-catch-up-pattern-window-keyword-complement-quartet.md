# RBR-0967: Catch up the direct Pattern window keyword complement quartet

Status: ready
Owner: feature-implementation
Created: 2026-03-22

## Goal
- Extend the published Python-path `pattern_boundary.py` benchmark surface with the remaining direct-`Pattern` window keyword complements for `search()`, `match()`, and `fullmatch()` that the current runtime already matches on the shared `module-workflow-surface` correctness path, keeping this run on the existing `pattern-boundary` owner route instead of widening into another manifest or another helper family.

## Pattern Pair
- `re.compile("abc")`
- `re.compile(b"abc")`

## Helper Quartet
- `re.compile("z").search("zabcabc", endpos=True)`
- `re.compile("abc").search("zabcabc", pos=_INDEX_TWO)`
- `re.compile("abc").match("zabcabc", pos=True)`
- `re.compile(b"abc").fullmatch(b"zabc", pos=_INDEX_ONE, endpos=_INDEX_FOUR)`

## Deliverables
- `benchmarks/workloads/pattern_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/pattern_boundary.py` remains the only benchmark manifest for this slice and grows by exactly four direct-`Pattern` keyword-window workloads:
  - add `pattern-search-bool-endpos-keyword-warm-str`;
  - add `pattern-search-pos-indexlike-keyword-warm-str`;
  - add `pattern-match-bool-pos-keyword-purged-str`; and
  - add `pattern-fullmatch-window-indexlike-keyword-purged-bytes`.
- Keep those four workloads pinned to the already-published correctness anchors above rather than widening the pattern-window lane:
  - `pattern-search-bool-endpos-keyword-warm-str` uses `operation == "pattern.search"`, `pattern == "z"`, `haystack == "zabcabc"`, `kwargs == {"endpos": True}`, `text_model == "str"`, `cache_mode == "warm"`, and `timing_scope == "pattern-helper-call"`;
  - `pattern-search-pos-indexlike-keyword-warm-str` uses `operation == "pattern.search"`, `pattern == "abc"`, `haystack == "zabcabc"`, `kwargs == {"pos": {"type": "indexlike", "value": 2}}`, `text_model == "str"`, `cache_mode == "warm"`, and `timing_scope == "pattern-helper-call"`;
  - `pattern-match-bool-pos-keyword-purged-str` uses `operation == "pattern.match"`, `pattern == "abc"`, `haystack == "zabcabc"`, `kwargs == {"pos": True}`, `text_model == "str"`, `cache_mode == "purged"`, and `timing_scope == "pattern-helper-call"`;
  - `pattern-fullmatch-window-indexlike-keyword-purged-bytes` uses `operation == "pattern.fullmatch"`, `pattern == "abc"`, `haystack == "zabc"`, `kwargs == {"pos": {"type": "indexlike", "value": 1}, "endpos": {"type": "indexlike", "value": 4}}`, `text_model == "bytes"`, `cache_mode == "purged"`, and `timing_scope == "pattern-helper-call"`;
  - anchor the four workloads to `workflow-pattern-search-str-bool-endpos-keyword`, `workflow-pattern-search-str-pos-indexlike`, `workflow-pattern-match-str-bool-pos-keyword`, and `workflow-pattern-fullmatch-bytes-window-indexlike`;
  - insert `pattern-search-bool-endpos-keyword-warm-str` immediately after `pattern-search-pos-keyword-warm-str` and immediately before `pattern-search-endpos-keyword-purged-bytes`;
  - insert `pattern-search-pos-indexlike-keyword-warm-str` immediately after `pattern-search-endpos-keyword-purged-bytes` and immediately before `pattern-search-endpos-indexlike-keyword-purged-bytes`;
  - insert `pattern-match-bool-pos-keyword-purged-str` immediately after `pattern-match-pos-keyword-purged-str` and immediately before `pattern-match-window-indexlike-purged-bytes`;
  - insert `pattern-fullmatch-window-indexlike-keyword-purged-bytes` immediately after `pattern-fullmatch-window-keyword-purged-bytes` and immediately before `pattern-findall-bool-window-keyword-warm-str`; and
  - do not widen into the remaining `findall()` / `finditer()` window-keyword complements, positional-indexlike rows, wrong-text-model rows, collection/replacement helpers, another benchmark manifest, or benchmark-harness churn in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared `pattern-boundary` and `pattern-window-keyword` owner routes instead of forking another benchmark suite:
  - update `test_pattern_boundary_manifest_keeps_keyword_and_positional_window_rows_measured(...)` so `pattern-boundary` moves from `23` total measured workloads to `27`, the wrong-text-model subset stays at `3`, the positional-indexlike subset stays at `6`, and the keyword-window subset moves from `8` rows to `12` in this exact order:
    - `pattern-search-pos-keyword-warm-str`
    - `pattern-search-bool-endpos-keyword-warm-str`
    - `pattern-search-endpos-keyword-purged-bytes`
    - `pattern-search-pos-indexlike-keyword-warm-str`
    - `pattern-search-endpos-indexlike-keyword-purged-bytes`
    - `pattern-match-pos-keyword-purged-str`
    - `pattern-match-bool-pos-keyword-purged-str`
    - `pattern-match-window-indexlike-purged-bytes`
    - `pattern-fullmatch-window-keyword-purged-bytes`
    - `pattern-fullmatch-window-indexlike-keyword-purged-bytes`
    - `pattern-findall-bool-window-keyword-warm-str`
    - `pattern-finditer-window-indexlike-purged-bytes`;
  - extend the existing `pattern-window-keyword` anchor-contract definition by exactly four entries for the new workload ids above, with anchors `workflow-pattern-search-str-bool-endpos-keyword`, `workflow-pattern-search-str-pos-indexlike`, `workflow-pattern-match-str-bool-pos-keyword`, and `workflow-pattern-fullmatch-bytes-window-indexlike`;
  - extend `test_standard_benchmark_manifest_preserves_pattern_keyword_window_descriptors_until_helper_invocation(...)` so its synthetic keyword-window manifest grows from `8` workloads to `12`, preserving descriptor round-trip for the new bool and `__index__` keyword carriers without pre-materializing them;
  - extend `test_pattern_helper_keyword_kwargs_materialize_at_callback_time(...)` plus the adjacent search-endpos helper-path materialization coverage so the new rows prove callback-time materialization of `kwargs.endpos == True`, `kwargs.pos` via `__index__()`, and the bounded `fullmatch()` dual-window `__index__` keyword pair; and
  - keep the existing benchmark contract on the same `pattern-boundary` owner path instead of creating another keyword-window helper registry or detached expectation layer.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - the combined tracked summary moves from `906` total / `906` measured / `0` known gaps with `898` module workloads to `910` / `910` / `0` with `902` module workloads;
  - `REPORT["manifests"]["pattern-boundary"]` moves from `selected_workload_count == 23`, `measured_workloads == 23`, and `known_gap_count == 0` to `27`, `27`, and `0`;
  - `REPORT["artifacts"]["manifests"]` keeps `pattern-boundary` on the same tracked manifest path while moving its `workload_count` from `23` to `27`; and
  - all four new keyword-window workloads publish real `rebar` timings with `status == "measured"`, not placeholders.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-search-bool-endpos-keyword-str or pattern-search-pos-indexlike-str or pattern-match-bool-pos-keyword-str or pattern-fullmatch-window-indexlike-bytes or module_workflow_surface_publishes_pattern_keyword_helpers_from_direct_cases'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'pattern_boundary_manifest_keeps_keyword_and_positional_window_rows_measured or standard_benchmark_manifest_preserves_pattern_keyword_window_descriptors_until_helper_invocation or pattern_helper_keyword_kwargs_materialize_at_callback_time or pattern_helper_keyword_kwargs_materialize_at_callback_time_for_search_endpos_rows'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/pattern_boundary.py --report .rebar/tmp/rbr-0967-pattern-window-keyword-complement-quartet.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only. Do not widen the correctness surface or change Rust/Python regex behavior beyond what is required to publish and time the exact four direct-`Pattern` window keyword workloads above on the existing `pattern-boundary` owner path.
- Reuse the existing `pattern_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner routes. Do not create another benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.

## Notes
- `RBR-0967` is the next available feature task id in the current checkout:
  - `RBR-0965` is the latest done feature task on the drained direct-`Pattern` window wrong-text-model frontier;
  - `RBR-0966` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in the current checkout.
- Queue this directly after `RBR-0965` / `RBR-0966` on the same shared `pattern-boundary` owner family so the remaining `search()` / `match()` / `fullmatch()` keyword-window complements reach the tracked Python-path benchmark surface before the later `findall()` / `finditer()` keyword-window complements or another owner family widens the queue.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-search-bool-endpos-keyword-str or pattern-search-pos-indexlike-str or pattern-match-bool-pos-keyword-str or pattern-fullmatch-window-indexlike-bytes or module_workflow_surface_publishes_pattern_keyword_helpers_from_direct_cases'` currently passes (`15 passed`), so the exact bounded correctness/parity slice is already green in this checkout;
  - `PYTHONPATH=python:. ./.venv/bin/python - <<'PY' ... pattern-search-bool-endpos-keyword-probe-str / pattern-search-pos-indexlike-keyword-probe-str / pattern-match-bool-pos-keyword-probe-str / pattern-fullmatch-window-indexlike-keyword-probe-bytes ... PY` returns `status == "measured"` for all four synthetic `rebar` probes through `run_internal_workload_probe(...)`, so the current benchmark harness already measures the exact bounded quartet without another prerequisite;
  - `rg -n 'pattern-search-bool-endpos-keyword-warm-str|pattern-search-pos-indexlike-keyword-warm-str|pattern-match-bool-pos-keyword-purged-str|pattern-fullmatch-window-indexlike-keyword-purged-bytes' benchmarks/workloads/pattern_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/benchmarks/latest.py` currently returns no matches, so the exact four workload ids are still absent from the tracked benchmark surface; and
  - live tracked reports currently read `1556` total / `1556` passed / `0` unimplemented across `114` manifests in `reports/correctness/latest.py`, plus `906` total / `906` measured / `0` known gaps overall with `pattern-boundary` at `23` selected / `23` measured / `0` known gaps and `module_workloads == 898` in `reports/benchmarks/latest.py`.
