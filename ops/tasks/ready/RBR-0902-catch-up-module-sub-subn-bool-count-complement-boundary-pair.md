# RBR-0902: Catch up the module `sub()`/`subn()` bool-count complement boundary pair

Status: ready
Owner: feature-implementation
Created: 2026-03-22

## Goal
- Extend the published Python-path `collection_replacement_boundary.py` benchmark surface with the exact raw module-level bool-count complement pair that `RBR-0896` already publishes on the shared `module-workflow-surface` correctness path, reusing the existing module keyword-carrier owner route instead of widening into compiled-pattern-first-argument rows, direct-`Pattern` helpers, or another benchmark family.

## Pattern Pair
- `re.sub("abc", "x", "abcabc", count=False)`
- `re.subn(b"abc", b"x", b"abcabc", count=True)`

## Deliverables
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly two raw-module bool-count complement workloads:
  - add `module-sub-count-bool-false-keyword-warm-str`; and
  - add `module-subn-count-bool-true-keyword-purged-bytes`.
- Keep those two workloads pinned to the exact `RBR-0896` correctness anchors rather than widening the collection/replacement family:
  - `module-sub-count-bool-false-keyword-warm-str` uses `operation == "module.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `text_model == "str"`, `cache_mode == "warm"`, `timing_scope == "module-helper-call"`, `flags == 0`, and `kwargs == {"count": False}`;
  - `module-subn-count-bool-true-keyword-purged-bytes` uses `operation == "module.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `text_model == "bytes"`, `cache_mode == "purged"`, `timing_scope == "module-helper-call"`, `flags == 0`, and `kwargs == {"count": True}`;
  - anchor the two workloads to `workflow-module-sub-count-bool-false-str` and `workflow-module-subn-count-bool-true-bytes`;
  - insert `module-sub-count-bool-false-keyword-warm-str` immediately after `module-sub-count-bool-keyword-warm-str` and immediately before `module-sub-count-indexlike-keyword-warm-str`;
  - insert `module-subn-count-bool-true-keyword-purged-bytes` immediately after `module-subn-count-bool-keyword-purged-bytes` and immediately before `module-subn-count-indexlike-keyword-purged-bytes`; and
  - do not widen into compiled-pattern-first-argument rows, keyword-error rows, direct-`Pattern` replacement workloads, positional-count neighbors, another benchmark manifest, or benchmark-harness churn in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking another raw-module collection/replacement benchmark suite:
  - extend the shared `collection-replacement-keyword` benchmark-to-correctness mapping by exactly two entries for the new workload ids above, with anchors `workflow-module-sub-count-bool-false-str` and `workflow-module-subn-count-bool-true-bytes`;
  - keep the raw module keyword-carrier coverage on the existing shared owner path, including the descriptor round-trip, callback-time keyword materialization, and source-tree combined anchor checks, instead of creating another benchmark suite or detached expectation table;
  - update the collection-replacement manifest expectations from `64` measured workloads to `66`, still with `0` known gaps on that manifest;
  - update the combined publication totals from `872` total / `872` measured / `0` known gaps across `30` manifests to `874` / `874` / `0` across the same `30` manifests;
  - update `REPORT["summary"]["module_workloads"]` from `864` to `866`;
  - keep `REPORT["summary"]["parser_workloads"]` at `8` and `REPORT["summary"]["regression_workloads"]` at `8`; and
  - keep the built-native smoke manifest set unchanged in this run.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `selected_workload_count == 64`, `measured_workloads == 64`, and `known_gap_count == 0` to `66`, `66`, and `0`;
  - `REPORT["artifacts"]["manifests"]` keeps `collection-replacement-boundary` on the same tracked manifest path while moving its `workload_count` from `64` to `66`;
  - the two new raw-module bool-count complement workloads publish real `rebar` timings with `status == "measured"`, not placeholders; and
  - the tracked report exposes those exact workload ids on the existing collection/replacement benchmark surface.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_keyword'`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0902-module-sub-subn-bool-count-complement-boundary-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not widen the correctness surface or change Rust/Python regex behavior just to support a larger collection/replacement family.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another raw-module collection/replacement benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.
- Assume `RBR-0900` has already landed the matching compiled-pattern benchmark catch-up immediately ahead of this slice; if it has not, stop and finish `RBR-0900` first instead of mixing the raw-module and compiled-pattern benchmark complements in one run.

## Notes
- `RBR-0902` is the next available feature task id in the current checkout:
  - `RBR-0900` is already occupied by the ready feature task in `ops/tasks/ready/`;
  - `RBR-0901` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0900` on the same shared module-workflow/collection-replacement frontier so the newly published raw-module bool-count complement pair reaches the tracked Python-path benchmark surface before another owner-path widening invents a different helper family.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier while the exact benchmark ids are still missing:
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... rebar.sub("abc", "x", "abcabc", count=False) ... rebar.subn(b"abc", b"x", b"abcabc", count=True) ... PY` matched stdlib `re` for both exact calls in this run;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'collection_replacement_keyword'` passed in this run (`30 passed, 525 deselected`), so the shared raw module keyword-carrier benchmark owner path is already green before widening the exact bool-count complement spellings;
  - `benchmarks/workloads/collection_replacement_boundary.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and `reports/benchmarks/latest.py` currently publish only `module-sub-count-bool-keyword-warm-str` anchored to `workflow-module-sub-count-bool-true-str` and `module-subn-count-bool-keyword-purged-bytes` anchored to `workflow-module-subn-count-bool-false-bytes`, not the exact `count=False` / `count=True` complement rows queued here; and
  - `RBR-0900` already covers the compiled-pattern-first-argument complement spellings on the same owner path, so this follow-on stays bounded to the remaining raw-module benchmark publication pair instead of reopening correctness or a second benchmark family.
