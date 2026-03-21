# RBR-0830: Catch up the module-workflow `Pattern` positional `__index__` replacement/split benchmark trio

Status: done
Owner: feature-implementation
Created: 2026-03-21

## Goal
- Extend the published Python-path collection/replacement benchmark surface with the exact precompiled `Pattern.split()` / `Pattern.sub()` / `Pattern.subn()` positional `__index__` trio that the shared `module-workflow-surface` correctness path already publishes, while keeping this catch-up on the existing `collection_replacement_boundary.py` manifest instead of opening a second positional-only benchmark family.

## Pattern Pair
- `"abc"`
- `b"abc"`

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `python/rebar_harness/benchmarks.py` keeps the tracked Python-path benchmark publication stable while extending the post-`RBR-0828` positional `__index__` carrier support to the precompiled `Pattern` helper trio:
  - keep the raw module `split()` / `sub()` / `subn()` positional benchmark rows from `RBR-0828` working unchanged once they land;
  - keep plain integer `count` / `maxsplit` workloads working unchanged for every existing manifest;
  - add explicit `pattern.split` benchmark execution support on the shared precompiled-helper path instead of introducing a detached helper runner;
  - allow descriptor-backed `count` and `maxsplit` values to stay unresolved until precompiled helper invocation so `Pattern.split(..., __index__)`, `Pattern.sub(..., __index__)`, and `Pattern.subn(..., __index__)` time the real positional boundary; and
  - do not broaden into positional `Pattern.search()` / `fullmatch()` / `findall()` / `finditer()` window support, new benchmark manifests, or unrelated benchmark-schema churn in this run.
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly three new precompiled-`Pattern` workloads:
  - add `pattern-split-maxsplit-indexlike-positional-warm-str`;
  - add `pattern-sub-count-indexlike-positional-purged-bytes`; and
  - add `pattern-subn-count-indexlike-positional-warm-str`.
- Keep those three workloads pinned to the exact already-published module-workflow positional anchors rather than inventing a broader pattern-only family:
  - `pattern-split-maxsplit-indexlike-positional-warm-str` uses `operation == "pattern.split"`, `pattern == "abc"`, `haystack == "zabcabcabc"`, `text_model == "str"`, `cache_mode == "warm"`, `timing_scope == "pattern-helper-call"`, and descriptor-backed `maxsplit == {"type": "indexlike", "value": 2}`;
  - `pattern-sub-count-indexlike-positional-purged-bytes` uses `operation == "pattern.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabcabc"`, `text_model == "bytes"`, `cache_mode == "purged"`, `timing_scope == "pattern-helper-call"`, and descriptor-backed `count == {"type": "indexlike", "value": 2}`;
  - `pattern-subn-count-indexlike-positional-warm-str` uses `operation == "pattern.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabcabc"`, `text_model == "str"`, `cache_mode == "warm"`, `timing_scope == "pattern-helper-call"`, and descriptor-backed `count == {"type": "indexlike", "value": 2}`;
  - keep the text-model split explicit at two `str` rows and one `bytes` row; and
  - do not broaden into positional `Pattern.finditer()` window rows, `Pattern.findall()` rows, raw module rows, keyword-form duplicates, non-positional `bool` carriers, smoke-only variants, or another benchmark manifest in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking a positional-only benchmark suite:
  - update the collection/replacement manifest expectations from `13` measured workloads to `16`, still with `0` known gaps on that manifest once `RBR-0828` has landed;
  - keep the manifest on the existing `post-parser-workflows` / combined-boundary path and anchor the three new workloads to the already-published correctness case ids `workflow-pattern-split-str-maxsplit-indexlike-positional`, `workflow-pattern-sub-count-indexlike-positional-bytes`, and `workflow-pattern-subn-count-indexlike-positional-str`;
  - update the combined publication totals from `777` total / `777` measured / `0` known gaps across `30` manifests to `780` / `780` / `0` across the same `30` manifests;
  - update `REPORT["summary"]["module_workloads"]` from `769` to `772`;
  - keep `REPORT["summary"]["regression_workloads"]` at `8`; and
  - keep the built-native smoke manifest set and every existing non-positional workload unchanged in this run.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `13` selected / `13` measured / `0` known gaps to `16` / `16` / `0`;
  - the three new positional `__index__` workloads publish real `rebar` timings with `status == "measured"`, not synthetic placeholders; and
  - the tracked report exposes those exact workload ids on the existing collection/replacement benchmark surface.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0830-collection-replacement-boundary.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not widen the correctness surface, add positional `Pattern.search()` / `fullmatch()` / `findall()` / `finditer()` benchmark support, or change Rust/Python regex behavior just to support a larger benchmark family.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another positional-only benchmark manifest, another benchmark suite, or detached benchmark expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.

## Notes
- `RBR-0830` is the next available feature task id in the current checkout:
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done -maxdepth 1 -type f -printf '%f\n' | rg '^RBR-0830|^RBR-0831|^RBR-0832'` returned no matches in this run; and
  - `RBR-0829` is already occupied by an architecture cleanup task in `ops/tasks/done/`.
- Queue this directly after `RBR-0828` on the same `module-workflow-surface` frontier so the collection/replacement benchmark surface catches the adjacent precompiled `Pattern` positional trio up before any later positional window benchmark expansion reopens the queue.
- 2026-03-21 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier:
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... re.compile(...).split/sub/subn(..., _IndexLike(2)) ... PY` in this run showed CPython and `rebar` already agree on the exact bounded outputs for the targeted precompiled `Pattern` trio, so this remains a benchmark/publication task rather than a missing runtime-implementation prerequisite;
  - `python/rebar_harness/benchmarks.py` currently lacks `pattern.split` benchmark support and still eagerly coerces `count` / `maxsplit` through `int(...)`, so the existing benchmark path cannot yet publish these exact positional `__index__` carriers faithfully;
  - `benchmarks/workloads/collection_replacement_boundary.py` already owns the adjacent precompiled `Pattern` collection/replacement surface, so this slice can stay on the existing manifest path instead of inventing another benchmark family;
  - the current checkout still reports `10` selected / `10` measured / `0` known gaps on `collection-replacement-boundary` and `774` / `774` / `0` overall because `RBR-0828` is still ready in this run, so the acceptance counts above are intentionally written against the immediate post-`RBR-0828` state; and
  - no blocked feature task exists to reopen first.

## Completion
- Added benchmark-runner support for `pattern.split` on the shared precompiled-helper path and switched `Pattern.sub()` / `Pattern.subn()` benchmark invocation to positional `count` arguments so the positional `__index__` boundary is timed directly.
- Extended `benchmarks/workloads/collection_replacement_boundary.py` with the exact three precompiled positional workloads requested by this task and anchored them to the existing correctness ids `workflow-pattern-split-str-maxsplit-indexlike-positional`, `workflow-pattern-sub-count-indexlike-positional-bytes`, and `workflow-pattern-subn-count-indexlike-positional-str`.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0830-collection-replacement-boundary.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`
- The tracked publication changed: `reports/benchmarks/latest.py` now reports `collection-replacement-boundary` at `16` selected / `16` measured / `0` known gaps, and the combined published summary at `780` total / `780` measured / `772` module / `8` parser / `8` regression workloads with `0` known gaps.
