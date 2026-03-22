# RBR-0906: Catch up the direct `Pattern.sub()`/`Pattern.subn()` bool-count complement boundary pair

Status: ready
Owner: feature-implementation
Created: 2026-03-22

## Goal
- Extend the published Python-path `collection_replacement_boundary.py` benchmark surface with the exact direct `Pattern.sub()` / `Pattern.subn()` bool-count complement pair that `RBR-0904` publishes on the shared `module-workflow-surface` correctness path, reusing the existing direct-`Pattern` keyword-carrier owner route instead of widening the correctness surface again, inventing another benchmark family, or reopening unrelated collection/replacement helpers.

## Pattern Pair
- `re.compile(b"abc").sub(b"x", b"abcabc", count=True)`
- `re.compile("abc").subn("x", "abcabc", count=False)`

## Deliverables
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly two direct-`Pattern` bool-count complement workloads:
  - add `pattern-sub-count-bool-true-keyword-purged-bytes`; and
  - add `pattern-subn-count-bool-false-keyword-warm-str`.
- Keep those two workloads pinned to the exact `RBR-0904` correctness anchors rather than widening the collection/replacement family:
  - `pattern-sub-count-bool-true-keyword-purged-bytes` uses `operation == "pattern.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `text_model == "bytes"`, `cache_mode == "purged"`, `timing_scope == "pattern-helper-call"`, `flags == 0`, and `kwargs == {"count": True}`;
  - `pattern-subn-count-bool-false-keyword-warm-str` uses `operation == "pattern.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `text_model == "str"`, `cache_mode == "warm"`, `timing_scope == "pattern-helper-call"`, `flags == 0`, and `kwargs == {"count": False}`;
  - anchor the two workloads to `workflow-pattern-sub-count-bool-true-bytes` and `workflow-pattern-subn-count-bool-false-str`;
  - insert `pattern-sub-count-bool-true-keyword-purged-bytes` immediately after `pattern-sub-count-bool-keyword-purged-bytes` and immediately before `pattern-sub-count-indexlike-keyword-purged-bytes`;
  - insert `pattern-subn-count-bool-false-keyword-warm-str` immediately after `pattern-subn-count-bool-keyword-warm-str` and immediately before `pattern-subn-count-indexlike-keyword-warm-str`; and
  - do not widen into raw-module rows, compiled-pattern-first-argument rows, positional-count neighbors, keyword-error rows, split rows, another benchmark manifest, or benchmark-harness churn in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking another direct-`Pattern` collection/replacement benchmark suite:
  - extend the shared `collection-replacement-keyword` benchmark-to-correctness mapping by exactly two entries for the new workload ids above, with anchors `workflow-pattern-sub-count-bool-true-bytes` and `workflow-pattern-subn-count-bool-false-str`;
  - keep the direct-`Pattern` keyword-carrier coverage on the existing shared owner path, including the descriptor round-trip, callback-time keyword materialization, and source-tree combined anchor checks, instead of creating another benchmark suite or detached expectation table;
  - update the pattern keyword replacement/split measured-row expectation from `9` workloads to `11`;
  - update the collection-replacement manifest expectations from `66` measured workloads to `68`, still with `0` known gaps on that manifest;
  - update the combined publication totals from `874` total / `874` measured / `0` known gaps across `30` manifests to `876` / `876` / `0` across the same `30` manifests;
  - update `REPORT["summary"]["module_workloads"]` from `866` to `868`;
  - keep `REPORT["summary"]["parser_workloads"]` at `8` and `REPORT["summary"]["regression_workloads"]` at `8`; and
  - keep the built-native smoke manifest set unchanged in this run.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `selected_workload_count == 66`, `measured_workloads == 66`, and `known_gap_count == 0` to `68`, `68`, and `0`;
  - `REPORT["artifacts"]["manifests"]` keeps `collection-replacement-boundary` on the same tracked manifest path while moving its `workload_count` from `66` to `68`;
  - the two new direct-`Pattern` bool-count complement workloads publish real `rebar` timings with `status == "measured"`, not placeholders; and
  - the tracked report exposes those exact workload ids on the existing collection/replacement benchmark surface.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_keyword'`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0906-pattern-sub-subn-bool-count-complement-boundary-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not widen the correctness surface or change Rust/Python regex behavior just to support a larger collection/replacement family.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another direct-`Pattern` collection/replacement benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.
- Assume `RBR-0904` has already landed the matching correctness anchors; if it has not, stop and finish `RBR-0904` first instead of widening this task.

## Notes
- `RBR-0906` is the next available feature task id in the current checkout:
  - `RBR-0904` is already occupied by the ready feature task in `ops/tasks/ready/`;
  - `RBR-0905` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0904` on the same shared `module-workflow-surface` / `collection-replacement-boundary` frontier so the newly published direct-`Pattern` bool-count complement pair reaches the tracked Python-path benchmark surface before another owner-path widening invents a different helper family.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier while the exact benchmark ids are still missing:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-sub-count-bool-true-bytes or pattern-subn-count-bool-false-str or test_pattern_keyword_direct_cases_keep_bool_count_complements_balanced_for_follow_on'` passed in this run (`5 passed, 1237 deselected`), so the direct-`Pattern` owner path already exposes the exact complement calls that this task needs to benchmark;
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... rebar.compile(b"abc").sub(b"x", b"abcabc", count=True) ... rebar.compile("abc").subn("x", "abcabc", count=False) ... PY` matched stdlib `re` for both exact calls in this run;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_keyword'` passed in this run (`30 passed, 525 deselected`), so the shared direct-`Pattern` keyword-carrier benchmark owner path is already green before widening the exact bool-count complement spellings; and
  - `benchmarks/workloads/collection_replacement_boundary.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and `reports/benchmarks/latest.py` currently publish only `pattern-sub-count-bool-keyword-purged-bytes` anchored to `workflow-pattern-sub-count-bool-false-bytes` and `pattern-subn-count-bool-keyword-warm-str` anchored to `workflow-pattern-subn-count-bool-true-str`, not the exact `count=True` / `count=False` complement rows queued here.
