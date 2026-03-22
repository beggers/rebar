# RBR-0912: Catch up the direct `Pattern.sub()` / `Pattern.subn()` duplicate-`count=` keyword boundary pair

Status: ready
Owner: feature-implementation
Created: 2026-03-22

## Goal
- Extend the published Python-path `collection_replacement_boundary.py` benchmark surface with the exact direct `Pattern.sub()` / `Pattern.subn()` duplicate-`count=` keyword rejection pair that `RBR-0910` publishes on the shared `module-workflow-surface` correctness path, reusing the existing direct-`Pattern` collection/replacement keyword owner route instead of widening correctness again, inventing another benchmark family, or reopening adjacent unexpected-keyword publication work first.

## Pattern Pair
- `re.compile("abc").sub("x", "abc", 1, count=1)`
- `re.compile(b"abc").subn(b"x", b"abc", 1, count=1)`

## Deliverables
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly two direct-`Pattern` duplicate-`count=` keyword error workloads:
  - add `pattern-sub-duplicate-count-keyword-warm-str`; and
  - add `pattern-subn-duplicate-count-keyword-warm-bytes`.
- Keep those two workloads pinned to the exact `RBR-0910` correctness anchors rather than widening the collection/replacement family:
  - `pattern-sub-duplicate-count-keyword-warm-str` uses `operation == "pattern.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abc"`, `flags == 0`, `count == 1`, `kwargs == {"count": 1}`, `expected_exception == {"type": "TypeError", "message_substring": "sub() takes at most 3 arguments (4 given)"}`, `text_model == "str"`, `cache_mode == "warm"`, and `timing_scope == "pattern-helper-call"`;
  - `pattern-subn-duplicate-count-keyword-warm-bytes` uses `operation == "pattern.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abc"`, `flags == 0`, `count == 1`, `kwargs == {"count": 1}`, `expected_exception == {"type": "TypeError", "message_substring": "subn() takes at most 3 arguments (4 given)"}`, `text_model == "bytes"`, `cache_mode == "warm"`, and `timing_scope == "pattern-helper-call"`;
  - anchor the two workloads to `workflow-pattern-sub-duplicate-count-keyword-str` and `workflow-pattern-subn-duplicate-count-keyword-bytes`;
  - insert `pattern-sub-duplicate-count-keyword-warm-str` immediately after `pattern-sub-count-indexlike-keyword-purged-bytes` and immediately before `pattern-subn-count-indexlike-positional-warm-str`;
  - insert `pattern-subn-duplicate-count-keyword-warm-bytes` immediately after `pattern-subn-count-indexlike-keyword-warm-str`; and
  - do not widen into raw-module rows, compiled-pattern-first-argument rows, positional-count neighbors, direct `Pattern.split()` duplicate-`maxsplit=` rows, direct unexpected-keyword rows, another benchmark manifest, or benchmark-harness churn in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking another direct-`Pattern` collection/replacement benchmark suite:
  - extend the shared `collection-replacement-keyword` benchmark-to-correctness mapping by exactly two entries for the new workload ids above, with anchors `workflow-pattern-sub-duplicate-count-keyword-str` and `workflow-pattern-subn-duplicate-count-keyword-bytes`;
  - keep the direct-`Pattern` keyword replacement/split coverage on the existing shared owner path, including the descriptor round-trip, callback-time keyword materialization, and source-tree combined anchor checks, instead of creating another benchmark suite or detached expectation table;
  - update the pattern keyword replacement/split measured-row expectation from `11` workloads to `13`;
  - update the collection-replacement manifest expectations from `68` measured workloads to `70`, still with `0` known gaps on that manifest;
  - update the combined publication totals from `876` total / `876` measured / `0` known gaps across `30` manifests to `878` / `878` / `0` across the same `30` manifests;
  - update `REPORT["summary"]["module_workloads"]` from `868` to `870`;
  - keep `REPORT["summary"]["parser_workloads"]` at `8` and `REPORT["summary"]["regression_workloads"]` at `8`; and
  - keep the built-native smoke manifest set unchanged in this run.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `selected_workload_count == 68`, `measured_workloads == 68`, and `known_gap_count == 0` to `70`, `70`, and `0`;
  - `REPORT["artifacts"]["manifests"]` keeps `collection-replacement-boundary` on the same tracked manifest path while moving its `workload_count` from `68` to `70`;
  - the two new direct-`Pattern` duplicate-`count=` keyword workloads publish real `rebar` timings with `status == "measured"`, not placeholders; and
  - the tracked report exposes those exact workload ids on the existing collection/replacement benchmark surface.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-sub-duplicate-count-keyword-str or pattern-subn-duplicate-count-keyword-bytes'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_keyword or collection_replacement_manifest_keeps_pattern_keyword_replacement_and_split_rows_measured or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0912-pattern-sub-subn-duplicate-count-keyword-boundary-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not widen the correctness surface or change Rust/Python regex behavior just to support a larger collection/replacement family.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another direct-`Pattern` collection/replacement benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.
- Assume `RBR-0910` has already landed the matching correctness anchors; if it has not, stop and finish `RBR-0910` first instead of widening this task.

## Notes
- `RBR-0912` is the next available feature task id in the current checkout:
  - `RBR-0910` is already occupied by the ready feature task in `ops/tasks/ready/`;
  - `RBR-0911` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0910` on the same shared `module-workflow-surface` / `collection-replacement-boundary` frontier so the newly published direct-`Pattern` duplicate-`count=` keyword pair reaches the tracked Python-path benchmark surface before adjacent direct bound-pattern unexpected-keyword or `split()` duplicate-`maxsplit=` publication follow-ons widen the replacement-keyword error slice.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier while the exact benchmark ids are still missing:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-sub-duplicate-count-keyword-str or pattern-subn-duplicate-count-keyword-bytes'` currently passes in this checkout, so the direct-`Pattern` owner path already exposes the exact error pair that this task needs to benchmark;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_keyword'` currently passes in this checkout, so the shared direct-`Pattern` collection/replacement keyword benchmark owner path is already green before widening the exact duplicate-`count=` spellings;
  - `benchmarks/workloads/collection_replacement_boundary.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and `reports/benchmarks/latest.py` currently contain no `pattern-sub-duplicate-count-keyword-...` or `pattern-subn-duplicate-count-keyword-...` workload ids in this run; and
  - `reports/benchmarks/latest.py` currently reports `876` total / `876` measured / `0` known gaps overall, with `REPORT["manifests"]["collection-replacement-boundary"]` still at `68` selected workloads / `68` measured / `0` known gaps and the direct pattern keyword replacement/split subset still at `11` measured rows.
