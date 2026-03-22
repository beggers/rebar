# RBR-0894: Catch up the bound `Pattern.match()` bytes window `__index__` boundary pair

Status: ready
Owner: feature-implementation
Created: 2026-03-22

## Goal
- Extend the published Python-path `pattern_boundary.py` benchmark surface with the exact bytes bound-`Pattern.match()` window `__index__` keyword and positional pair that `RBR-0892` publishes on the shared `module-workflow-surface` correctness path, reusing the existing pattern-boundary window-owner route instead of widening the correctness surface again, inventing another benchmark family, or reopening unrelated helper carriers.

## Pattern Pair
- `re.compile(b"abc").match(b"zabc", pos=_INDEX_ONE, endpos=_INDEX_FOUR)`
- `re.compile(b"abc").match(b"zabc", _INDEX_ONE, _INDEX_FOUR)`

## Deliverables
- `benchmarks/workloads/pattern_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/pattern_boundary.py` remains the only benchmark manifest for this slice and grows by exactly two new bytes bound-`Pattern.match()` window `__index__` workloads:
  - add `pattern-match-window-indexlike-purged-bytes`; and
  - add `pattern-match-window-indexlike-positional-purged-bytes`.
- Keep those two workloads pinned to the exact already-published `module-workflow-surface` correctness anchors rather than inventing a broader helper family:
  - `pattern-match-window-indexlike-purged-bytes` uses `operation == "pattern.match"`, `pattern == "abc"`, `haystack == "zabc"`, `text_model == "bytes"`, `cache_mode == "purged"`, `timing_scope == "pattern-helper-call"`, `flags == 0`, and `kwargs == {"pos": {"type": "indexlike", "value": 1}, "endpos": {"type": "indexlike", "value": 4}}`;
  - `pattern-match-window-indexlike-positional-purged-bytes` uses `operation == "pattern.match"`, `pattern == "abc"`, `haystack == "zabc"`, `text_model == "bytes"`, `cache_mode == "purged"`, `timing_scope == "pattern-helper-call"`, `flags == 0`, `pos == {"type": "indexlike", "value": 1}`, and `endpos == {"type": "indexlike", "value": 4}`;
  - anchor the two workloads to `workflow-pattern-match-bytes-window-indexlike` and `workflow-pattern-match-bytes-window-indexlike-positional`;
  - insert the keyword workload immediately after `pattern-match-pos-keyword-purged-str` and immediately before `pattern-fullmatch-window-keyword-purged-bytes`;
  - insert the positional workload immediately after `pattern-search-endpos-indexlike-positional-purged-bytes` and immediately before `pattern-fullmatch-window-indexlike-positional-purged-bytes`; and
  - do not widen into str `Pattern.match()` rows, bool window carriers, `Pattern.fullmatch()` / `Pattern.finditer()` neighbors that already publish on this owner path, another benchmark manifest, or benchmark-harness churn in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking another pattern-helper benchmark suite:
  - update `test_pattern_boundary_manifest_keeps_keyword_and_positional_window_rows_measured` so the keyword workload ids grow from `5` to `6` and the positional workload ids grow from `5` to `6`, inserting the two new `Pattern.match()` bytes window `__index__` rows at the exact positions listed above;
  - update the same manifest expectations from `16` measured workloads to `18`, still with `0` known gaps on that manifest;
  - update the shared `pattern-window-keyword` anchor contract to map `pattern-match-window-indexlike-purged-bytes` to `workflow-pattern-match-bytes-window-indexlike`;
  - update the shared `pattern-window-positional-indexlike` anchor contract to map `pattern-match-window-indexlike-positional-purged-bytes` to `workflow-pattern-match-bytes-window-indexlike-positional`;
  - keep the manifest on the existing combined-boundary owner path instead of creating another pattern-window benchmark suite;
  - update the combined publication totals from `868` total / `868` measured / `0` known gaps across `30` manifests to `870` / `870` / `0` across the same `30` manifests;
  - update `REPORT["summary"]["module_workloads"]` from `860` to `862`;
  - keep `REPORT["summary"]["parser_workloads"]` at `8` and `REPORT["summary"]["regression_workloads"]` at `8`; and
  - keep the built-native smoke manifest set unchanged in this run.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["pattern-boundary"]` moves from `selected_workload_count == 16`, `measured_workloads == 16`, and `known_gap_count == 0` to `18`, `18`, and `0`;
  - `REPORT["artifacts"]["manifests"]` keeps `pattern-boundary` on the same tracked manifest path while moving its `workload_count` from `16` to `18`;
  - the two new bound-`Pattern.match()` bytes window `__index__` workloads publish real `rebar` timings with `status == "measured"`, not placeholders; and
  - the tracked report exposes those exact workload ids on the existing `pattern-boundary` benchmark surface.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/pattern_boundary.py --report .rebar/tmp/rbr-0894-pattern-match-bytes-window-indexlike-boundary-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not widen the correctness surface or change Rust/Python regex behavior just to support a larger pattern-window family.
- Reuse the existing `pattern_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another pattern-helper benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.
- Assume `RBR-0892` has already landed the matching correctness anchors; if it has not, stop and finish `RBR-0892` first instead of widening this task.

## Notes
- `RBR-0894` is the next available feature task id in the current checkout:
  - `RBR-0892` is already occupied by the ready feature task in `ops/tasks/ready/`;
  - `RBR-0893` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0892` on the same `module-workflow-surface` frontier so the newly published bytes bound-`Pattern.match()` window `__index__` pair reaches the shared Python-path `pattern_boundary.py` benchmark surface before another correctness-only owner-path neighbor reopens the queue.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier but still absent from the benchmark surface:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-match-window-indexlike-bytes or pattern-match-window-indexlike-positional-bytes'` passed in this run (`16 passed, 1207 deselected`), so no Rust or Python regex-behavior prerequisite is missing for the exact bytes keyword/positional pair;
  - `benchmarks/workloads/pattern_boundary.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and `reports/benchmarks/latest.py` currently publish the adjacent `pattern-match-pos-keyword-purged-str`, `pattern-fullmatch-window-keyword-purged-bytes`, `pattern-finditer-window-indexlike-purged-bytes`, `pattern-fullmatch-window-indexlike-positional-purged-bytes`, and `pattern-finditer-window-indexlike-positional-purged-bytes` rows, but no exact `pattern-match-window-indexlike-purged-bytes` or `pattern-match-window-indexlike-positional-purged-bytes` workloads;
  - `reports/benchmarks/latest.py` currently reports `REPORT["summary"]["total_workloads"] == 868`, `REPORT["summary"]["measured_workloads"] == 868`, `REPORT["summary"]["known_gap_count"] == 0`, and `REPORT["summary"]["module_workloads"] == 860`, with `REPORT["manifests"]["pattern-boundary"]` at `16` selected / `16` measured / `0` known gaps; and
  - the shared source-tree benchmark contract already carries the `pattern-window-keyword` and `pattern-window-positional-indexlike` anchor families on the `pattern-boundary` manifest, so this follow-on remains a publication-only benchmark catch-up slice rather than a missing harness prerequisite.
