# RBR-0828: Catch up the module-workflow module positional `__index__` benchmark trio

Status: ready
Owner: feature-implementation
Created: 2026-03-21

## Goal
- Extend the published Python-path collection/replacement benchmark surface with the exact raw module `split()` / `sub()` / `subn()` positional `__index__` trio that the shared `module-workflow-surface` correctness path already publishes, while keeping this catch-up on the existing `collection_replacement_boundary.py` manifest instead of opening a second positional-only benchmark family.

## Pattern Pair
- `"abc"`
- `b"abc"`

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `python/rebar_harness/benchmarks.py` keeps the existing benchmark publication path stable while allowing the raw module helper surface to time exact positional `__index__` carriers:
  - keep plain integer `count` / `maxsplit` workloads working unchanged for every existing manifest;
  - allow `count` and `maxsplit` workload values to stay descriptor-backed until helper invocation instead of coercing them eagerly with `int(...)`;
  - materialize the exact `{"type": "indexlike", "value": 2}` carrier for this slice at call time so the benchmarked helper call stays faithful to the positional `__index__` boundary; and
  - do not broaden into generic bound-`Pattern` positional window support, new pattern helper operations, or unrelated benchmark-schema churn in this run.
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly three new raw-module workloads:
  - add `module-split-maxsplit-indexlike-positional-purged-bytes`;
  - add `module-sub-count-indexlike-positional-warm-str`; and
  - add `module-subn-count-indexlike-positional-purged-bytes`.
- Keep those three workloads pinned to the exact already-published module-workflow positional anchors rather than inventing a broader replacement family:
  - `module-split-maxsplit-indexlike-positional-purged-bytes` uses `operation == "module.split"`, `pattern == "abc"`, `haystack == "zabcabcabc"`, `text_model == "bytes"`, `cache_mode == "purged"`, `timing_scope == "module-helper-call"`, and descriptor-backed `maxsplit == {"type": "indexlike", "value": 2}`;
  - `module-sub-count-indexlike-positional-warm-str` uses `operation == "module.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabcabc"`, `text_model == "str"`, `cache_mode == "warm"`, `timing_scope == "module-helper-call"`, and descriptor-backed `count == {"type": "indexlike", "value": 2}`;
  - `module-subn-count-indexlike-positional-purged-bytes` uses `operation == "module.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabcabc"`, `text_model == "bytes"`, `cache_mode == "purged"`, `timing_scope == "module-helper-call"`, and descriptor-backed `count == {"type": "indexlike", "value": 2}`;
  - keep the text-model split explicit at one `str` row and two `bytes` rows; and
  - do not broaden into bound-`Pattern` positional rows, keyword-form duplicates, non-positional `bool` carriers, smoke-only variants, or another benchmark manifest in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking a positional-only benchmark suite:
  - update the collection/replacement manifest expectations from `10` measured workloads to `13`, still with `0` known gaps on that manifest;
  - keep the manifest on the existing `post-parser-workflows` / combined-boundary path and anchor the three new workloads to the already-published correctness case ids `workflow-module-split-maxsplit-indexlike-positional-bytes`, `workflow-module-sub-count-indexlike-positional-str`, and `workflow-module-subn-count-indexlike-positional-bytes`;
  - update the combined publication totals from `774` total / `774` measured / `0` known gaps across `30` manifests to `777` / `777` / `0` across the same `30` manifests;
  - update `REPORT["summary"]["module_workloads"]` from `766` to `769`;
  - keep `REPORT["summary"]["regression_workloads"]` at `8`; and
  - keep the built-native smoke manifest set and every existing non-positional workload unchanged in this run.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `10` selected / `10` measured / `0` known gaps to `13` / `13` / `0`;
  - the three new positional `__index__` workloads publish real `rebar` timings with `status == "measured"`, not synthetic placeholders; and
  - the tracked report exposes those exact workload ids on the existing collection/replacement benchmark surface.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0828-collection-replacement-boundary.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not widen the correctness surface, add bound-`Pattern` positional benchmark support, or change Rust/Python regex behavior just to support a larger benchmark family.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another positional-only benchmark manifest, another benchmark suite, or detached benchmark expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.

## Notes
- `RBR-0828` is the next available feature task id in the current checkout:
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done -maxdepth 1 -type f -printf '%f\n' | rg '^RBR-0828|^RBR-0829|^RBR-0830'` returned no matches in this run; and
  - `RBR-0827` is already occupied by an architecture cleanup task in `ops/tasks/done/`.
- Queue this directly after `RBR-0826` on the same `module-workflow-surface` frontier. `RBR-0826` still owns the adjacent bound-`Pattern` positional correctness publication slice, while this follow-on catches the already-published raw module trio up on the shared Python-path benchmark surface.
- 2026-03-21 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... re.split(..., _IndexLike(2)) / re.sub(..., _IndexLike(2)) / re.subn(..., _IndexLike(2)) ... PY` in this run showed CPython and `rebar` already agree on the exact bounded outputs for `split`, `sub`, and `subn` over the shared `"abc"` / `b"abc"` anchors, so this remains a benchmark/publication task rather than a missing runtime-implementation prerequisite;
  - `python/rebar_harness/benchmarks.py` currently coerces `count` and `maxsplit` through `int(...)`, so the existing benchmark path cannot yet publish an exact positional `__index__` carrier faithfully even though the raw module helper behavior is live;
  - `benchmarks/workloads/collection_replacement_boundary.py` already owns the adjacent raw-module `split` / `sub` collection-replacement surface, so this slice can stay on the existing manifest path instead of inventing another benchmark family;
  - `reports/benchmarks/latest.py` currently reports `774` total / `774` measured / `0` known gaps overall, with `REPORT["summary"]["module_workloads"] == 766`, `REPORT["summary"]["regression_workloads"] == 8`, and `REPORT["manifests"]["collection-replacement-boundary"]` at `10` selected / `10` measured / `0` known gaps; and
  - no blocked feature task exists to reopen first.
