# RBR-0969: Catch up the direct Pattern `findall()` / `finditer()` window keyword quartet

Status: done
Owner: feature-implementation
Created: 2026-03-22

## Goal
- Extend the published Python-path `pattern_boundary.py` benchmark surface with the exact remaining direct-`Pattern` `findall()` / `finditer()` window keyword quartet that the current runtime already publishes on the shared `module-workflow-surface` correctness path, keeping this run on the existing `pattern-boundary` / `pattern-window-keyword` owner route instead of widening into another manifest or another helper family.

## Pattern Pair
- `re.compile("abc")`
- `re.compile(b"abc")`

## Helper Quartet
- `re.compile("abc").findall("zabcabcz", pos=1, endpos=7)`
- `re.compile("abc").findall("zabcabcabcz", pos=_INDEX_ONE, endpos=_INDEX_SEVEN)`
- `re.compile(b"abc").finditer(b"zabcabcz", pos=1, endpos=7)`
- `re.compile(b"abc").finditer(b"zabcabcz", pos=True, endpos=7)`

## Deliverables
- `benchmarks/workloads/pattern_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/pattern_boundary.py` remains the only benchmark manifest for this slice and grows by exactly four direct-`Pattern` keyword-window workloads:
  - add `pattern-findall-window-keyword-warm-str`;
  - add `pattern-findall-window-indexlike-keyword-warm-str`;
  - add `pattern-finditer-window-keyword-purged-bytes`; and
  - add `pattern-finditer-bool-window-keyword-purged-bytes`.
- Keep those four workloads pinned to the already-published correctness anchors above rather than widening the `pattern-boundary` lane:
  - `pattern-findall-window-keyword-warm-str` uses `operation == "pattern.findall"`, `pattern == "abc"`, `haystack == "zabcabcz"`, `kwargs == {"pos": 1, "endpos": 7}`, `text_model == "str"`, `cache_mode == "warm"`, and `timing_scope == "pattern-helper-call"`;
  - `pattern-findall-window-indexlike-keyword-warm-str` uses `operation == "pattern.findall"`, `pattern == "abc"`, `haystack == "zabcabcabcz"`, `kwargs == {"pos": {"type": "indexlike", "value": 1}, "endpos": {"type": "indexlike", "value": 7}}`, `text_model == "str"`, `cache_mode == "warm"`, and `timing_scope == "pattern-helper-call"`;
  - `pattern-finditer-window-keyword-purged-bytes` uses `operation == "pattern.finditer"`, `pattern == "abc"`, `haystack == "zabcabcz"`, `kwargs == {"pos": 1, "endpos": 7}`, `text_model == "bytes"`, `cache_mode == "purged"`, and `timing_scope == "pattern-helper-call"`;
  - `pattern-finditer-bool-window-keyword-purged-bytes` uses `operation == "pattern.finditer"`, `pattern == "abc"`, `haystack == "zabcabcz"`, `kwargs == {"pos": True, "endpos": 7}`, `text_model == "bytes"`, `cache_mode == "purged"`, and `timing_scope == "pattern-helper-call"`;
  - anchor the four workloads to `workflow-pattern-findall-str-window-keyword`, `workflow-pattern-findall-str-window-indexlike`, `workflow-pattern-finditer-bytes-window-keyword`, and `workflow-pattern-finditer-bytes-bool-window-keyword`;
  - insert `pattern-findall-window-keyword-warm-str` immediately after `pattern-fullmatch-window-indexlike-keyword-purged-bytes`;
  - insert `pattern-findall-window-indexlike-keyword-warm-str` immediately after `pattern-findall-window-keyword-warm-str` and immediately before `pattern-findall-bool-window-keyword-warm-str`;
  - insert `pattern-finditer-window-keyword-purged-bytes` immediately after `pattern-findall-bool-window-keyword-warm-str` and immediately before `pattern-finditer-window-indexlike-purged-bytes`;
  - insert `pattern-finditer-bool-window-keyword-purged-bytes` immediately after `pattern-finditer-window-indexlike-purged-bytes` and immediately before `pattern-search-pos-indexlike-positional-warm-str`; and
  - do not widen into raw-module rows, positional-indexlike rows, wrong-text-model rows, collection/replacement helpers, another benchmark manifest, or benchmark-harness churn in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared `pattern-boundary` and `pattern-window-keyword` owner routes instead of forking another benchmark suite:
  - update `test_pattern_boundary_manifest_keeps_keyword_and_positional_window_rows_measured(...)` so `pattern-boundary` moves from `27` total measured workloads to `31`, the wrong-text-model subset stays at `3`, the positional-indexlike subset stays at `6`, and the keyword-window subset moves from `12` rows to `16` in this exact order:
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
    - `pattern-findall-window-keyword-warm-str`
    - `pattern-findall-window-indexlike-keyword-warm-str`
    - `pattern-findall-bool-window-keyword-warm-str`
    - `pattern-finditer-window-keyword-purged-bytes`
    - `pattern-finditer-window-indexlike-purged-bytes`
    - `pattern-finditer-bool-window-keyword-purged-bytes`;
  - extend the existing `pattern-window-keyword` anchor-contract definition by exactly four entries for the new workload ids above, with anchors `workflow-pattern-findall-str-window-keyword`, `workflow-pattern-findall-str-window-indexlike`, `workflow-pattern-finditer-bytes-window-keyword`, and `workflow-pattern-finditer-bytes-bool-window-keyword`;
  - extend `test_standard_benchmark_manifest_preserves_pattern_keyword_window_descriptors_until_helper_invocation(...)` so its synthetic keyword-window manifest grows from `12` workloads to `16`, preserving descriptor round-trip for the new direct-`Pattern` `findall()` and `finditer()` keyword-window carriers without pre-materializing them;
  - extend `test_pattern_helper_keyword_kwargs_materialize_at_callback_time(...)` so callback-time keyword materialization and CPython result parity now cover the new `findall()` and `finditer()` keyword-window rows alongside the existing search/match/fullmatch cases; and
  - keep this work on the existing `pattern-boundary` and `pattern-window-keyword` owner paths instead of creating another contract helper family or detached manifest.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - the combined tracked summary moves from `910` total / `910` measured / `0` known gaps across `30` manifests to `914` / `914` / `0` across the same `30` manifests;
  - `REPORT["summary"]["module_workloads"]` moves from `902` to `906`, while `REPORT["summary"]["parser_workloads"]` stays `8` and `REPORT["summary"]["regression_workloads"]` stays `8`;
  - `REPORT["manifests"]["pattern-boundary"]` moves from `selected_workload_count == 27`, `measured_workloads == 27`, and `known_gap_count == 0` to `31`, `31`, and `0`;
  - `REPORT["artifacts"]["manifests"]` keeps `pattern-boundary` on the same tracked manifest path while moving its `workload_count` from `27` to `31`; and
  - the four new direct-`Pattern` `findall()` / `finditer()` keyword-window workloads publish real `rebar` timings with `status == "measured"`, not placeholders.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-findall-window-keyword-str or pattern-findall-window-indexlike-str or pattern-finditer-window-keyword-bytes or pattern-finditer-bool-window-keyword-bytes or module_workflow_surface_publishes_pattern_keyword_helpers_from_direct_cases'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'pattern_boundary_manifest_keeps_keyword_and_positional_window_rows_measured or standard_benchmark_manifest_preserves_pattern_keyword_window_descriptors_until_helper_invocation or pattern_helper_keyword_kwargs_materialize_at_callback_time'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/pattern_boundary.py --report .rebar/tmp/rbr-0969-pattern-findall-finditer-window-keyword-quartet.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only. Do not widen the correctness surface or change Rust/Python regex behavior beyond what is required to publish and time the exact four direct-`Pattern` `findall()` / `finditer()` keyword-window workloads above on the existing `pattern-boundary` owner path.
- Reuse the existing `pattern_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another benchmark manifest, another benchmark suite, or detached benchmark expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.
- Planning probes in this checkout already show that the current benchmark harness can normalize and measure the exact four workload shapes above, so do not widen this run into speculative `python/rebar_harness/benchmarks.py` changes unless a narrowly reproducible regression on this exact owner path appears while landing the four rows.

## Notes
- `RBR-0969` is the next available feature task id in the current checkout:
  - `RBR-0967` is the latest done feature task on this drained direct-`Pattern` window-keyword frontier;
  - `RBR-0968` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in the current checkout.
- Queue this directly after `RBR-0967` / `RBR-0968` on the same shared `pattern-boundary` owner family so the remaining direct-`Pattern` `findall()` / `finditer()` keyword-window complements reach the tracked Python-path benchmark surface before another pattern-helper family widens the queue.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-findall-window-keyword-str or pattern-findall-window-indexlike-str or pattern-finditer-window-keyword-bytes or pattern-finditer-bool-window-keyword-bytes or module_workflow_surface_publishes_pattern_keyword_helpers_from_direct_cases'` currently passes (`15 passed`), so the exact bounded correctness/parity slice is already green in this checkout;
  - `PYTHONPATH=python:. ./.venv/bin/python - <<'PY' ... Workload.from_dict(...) / workload_to_payload(...) / run_internal_workload_probe(...) synthetic pattern-findall-window-keyword-probe-str, pattern-findall-window-indexlike-probe-str, pattern-finditer-window-keyword-probe-bytes, and pattern-finditer-bool-window-keyword-probe-bytes ... PY` returns `status == "measured"` for all four synthetic `rebar` probes through the current benchmark harness in this checkout; and
  - `rg -n 'pattern-findall-window-keyword-warm-str|pattern-findall-window-indexlike-keyword-warm-str|pattern-finditer-window-keyword-purged-bytes|pattern-finditer-bool-window-keyword-purged-bytes' benchmarks/workloads/pattern_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/benchmarks/latest.py` currently returns no matches, while `reports/benchmarks/latest.py` still reports `910` total / `910` measured / `0` known gaps overall with `pattern-boundary` fixed at `27` measured workloads and `module_workloads == 902`.
- 2026-03-22 feature-implementation: Added the four bounded direct-`Pattern` `findall()` / `finditer()` keyword-window workloads to `benchmarks/workloads/pattern_boundary.py` on the existing `pattern-boundary` route, extended the shared `pattern-boundary` and `pattern-window-keyword` benchmark assertions plus descriptor/materialization coverage in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and regenerated `reports/benchmarks/latest.py` on the tracked source-tree-shim path. `reports/correctness/latest.py` was unchanged because this benchmark-only task did not change correctness behavior or fixtures.
- Verification:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-findall-window-keyword-str or pattern-findall-window-indexlike-str or pattern-finditer-window-keyword-bytes or pattern-finditer-bool-window-keyword-bytes or module_workflow_surface_publishes_pattern_keyword_helpers_from_direct_cases'` passed (`15 passed`).
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'pattern_boundary_manifest_keeps_keyword_and_positional_window_rows_measured or standard_benchmark_manifest_preserves_pattern_keyword_window_descriptors_until_helper_invocation or pattern_helper_keyword_kwargs_materialize_at_callback_time'` passed (`12 passed, 670 deselected, 25 subtests passed`).
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'` passed (`1 passed, 681 deselected`).
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/pattern_boundary.py --report .rebar/tmp/rbr-0969-pattern-findall-finditer-window-keyword-quartet.py` passed with `31` total / `31` measured / `0` known gaps for `pattern-boundary`.
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py` regenerated the tracked report. The tracked `reports/benchmarks/latest.py` artifact now records `914` total / `914` measured / `0` known gaps with `906` module workloads, while `REPORT["manifests"]["pattern-boundary"]` and `REPORT["artifacts"]["manifests"]` now show `31` selected / `31` measured / `31` workload-count rows on `benchmarks/workloads/pattern_boundary.py`. The four new workload ids publish `status == "measured"`.
