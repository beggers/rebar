# RBR-0832: Catch up the module-workflow `Pattern` positional `__index__` window benchmark quintet

Status: ready
Owner: feature-implementation
Created: 2026-03-21

## Goal
- Extend the published Python-path pattern-boundary benchmark surface with the remaining five precompiled `Pattern` positional `__index__` search/window helper workflows that the shared `module-workflow-surface` correctness path already publishes, while keeping this catch-up on the existing `pattern_boundary.py` manifest instead of opening another positional-only benchmark family.

## Pattern Pair
- `"abc"`
- `b"abc"`

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/pattern_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `python/rebar_harness/benchmarks.py` keeps the tracked Python-path benchmark publication stable while extending the bounded pattern-helper argument surface to the remaining positional window cases:
  - keep the existing plain pattern-helper search/match/fullmatch/sub/subn workloads working unchanged;
  - extend the workload schema from `count` / `maxsplit`-only numeric helper arguments to optional `pos` / `endpos` descriptors without regressing the already-landed collection/replacement positional `__index__` path;
  - add explicit `pattern.findall` benchmark execution support on the shared precompiled-helper path instead of introducing a detached collection runner;
  - allow descriptor-backed `pos` and `endpos` values to stay unresolved until precompiled helper invocation so the benchmarked helper call times the real positional `__index__` boundary; and
  - do not broaden into raw-module positional windows, `Pattern.match(..., pos, endpos)` support, new benchmark manifests, or unrelated benchmark-schema churn in this run.
- `benchmarks/workloads/pattern_boundary.py` remains the only benchmark manifest for this slice and grows by exactly five new precompiled-`Pattern` workloads:
  - add `pattern-search-pos-indexlike-positional-warm-str`;
  - add `pattern-search-endpos-indexlike-positional-purged-bytes`;
  - add `pattern-fullmatch-window-indexlike-positional-purged-bytes`;
  - add `pattern-findall-window-indexlike-positional-warm-str`; and
  - add `pattern-finditer-window-indexlike-positional-purged-bytes`.
- Keep those five workloads pinned to the exact already-published module-workflow positional anchors rather than inventing a broader helper family:
  - `pattern-search-pos-indexlike-positional-warm-str` uses `operation == "pattern.search"`, `pattern == "abc"`, `haystack == "zabcabc"`, `text_model == "str"`, `cache_mode == "warm"`, `timing_scope == "pattern-helper-call"`, and descriptor-backed `pos == {"type": "indexlike", "value": 2}`;
  - `pattern-search-endpos-indexlike-positional-purged-bytes` uses `operation == "pattern.search"`, `pattern == "abc"`, `haystack == "zabcabc"`, `text_model == "bytes"`, `cache_mode == "purged"`, `timing_scope == "pattern-helper-call"`, plain integer `pos == 0`, and descriptor-backed `endpos == {"type": "indexlike", "value": 4}`;
  - `pattern-fullmatch-window-indexlike-positional-purged-bytes` uses `operation == "pattern.fullmatch"`, `pattern == "abc"`, `haystack == "zabc"`, `text_model == "bytes"`, `cache_mode == "purged"`, `timing_scope == "pattern-helper-call"`, descriptor-backed `pos == {"type": "indexlike", "value": 1}`, and descriptor-backed `endpos == {"type": "indexlike", "value": 4}`;
  - `pattern-findall-window-indexlike-positional-warm-str` uses `operation == "pattern.findall"`, `pattern == "abc"`, `haystack == "zabcabcabcz"`, `text_model == "str"`, `cache_mode == "warm"`, `timing_scope == "pattern-helper-call"`, descriptor-backed `pos == {"type": "indexlike", "value": 1}`, and descriptor-backed `endpos == {"type": "indexlike", "value": 7}`;
  - `pattern-finditer-window-indexlike-positional-purged-bytes` uses `operation == "pattern.finditer"`, `pattern == "abc"`, `haystack == "zabcabcabcz"`, `text_model == "bytes"`, `cache_mode == "purged"`, `timing_scope == "pattern-helper-call"`, descriptor-backed `pos == {"type": "indexlike", "value": 1}`, and descriptor-backed `endpos == {"type": "indexlike", "value": 7}`;
  - keep the text-model split explicit at two `str` rows and three `bytes` rows; and
  - do not broaden into the adjacent positional `Pattern.split()` / `sub()` / `subn()` trio, keyword-form duplicates, smoke-only variants, or another benchmark manifest in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking a positional-only benchmark suite:
  - update the pattern-boundary manifest expectations from `6` measured workloads to `11`, still with `0` known gaps on that manifest once `RBR-0830` has landed;
  - keep the manifest on the existing `post-parser-workflows` / combined-boundary path and anchor the five new workloads to the already-published correctness case ids `workflow-pattern-search-str-pos-indexlike-positional`, `workflow-pattern-search-bytes-endpos-indexlike-positional`, `workflow-pattern-fullmatch-bytes-window-indexlike-positional`, `workflow-pattern-findall-str-window-indexlike-positional`, and `workflow-pattern-finditer-bytes-window-indexlike-positional`;
  - update the combined publication totals from `780` total / `780` measured / `0` known gaps across `30` manifests to `785` / `785` / `0` across the same `30` manifests;
  - update `REPORT["summary"]["module_workloads"]` from `772` to `777`;
  - keep `REPORT["summary"]["regression_workloads"]` at `8`; and
  - keep the built-native smoke manifest set and every existing non-positional workload unchanged in this run.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["pattern-boundary"]` moves from `6` selected / `6` measured / `0` known gaps to `11` / `11` / `0`;
  - the five new positional `__index__` workloads publish real `rebar` timings with `status == "measured"`, not synthetic placeholders; and
  - the tracked report exposes those exact workload ids on the existing pattern-boundary benchmark surface.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/pattern_boundary.py --report .rebar/tmp/rbr-0832-pattern-boundary.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not widen the correctness surface, add raw-module positional window benchmark support, or change Rust/Python regex behavior just to support a larger benchmark family.
- Reuse the existing `pattern_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another positional-only benchmark manifest, another benchmark suite, or detached benchmark expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.

## Notes
- `RBR-0832` is the next available feature task id in the current checkout:
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done -maxdepth 1 -type f -printf '%f\n' | rg '^RBR-0830|^RBR-0831|^RBR-0832' | sort` returned only `RBR-0830` and `RBR-0831` in this run; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0830` on the same `module-workflow-surface` frontier so the pattern-boundary benchmark surface catches the remaining positional `Pattern` window/search quintet up before any broader positional helper expansion reopens the queue.
- 2026-03-21 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier:
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... re.compile(...).search/fullmatch/findall/finditer(..., _IndexLike(...)) ... PY` in this run showed CPython and `rebar` already agree on the exact bounded outputs for the targeted five precompiled `Pattern` workflows, so this remains a benchmark/publication task rather than a missing runtime-implementation prerequisite;
  - `python/rebar_harness/benchmarks.py` currently exposes only `count` / `maxsplit` numeric helper arguments, ignores positional `pos` / `endpos` windows on the pattern-helper path, and lacks `pattern.findall` benchmark execution support, so the existing benchmark path cannot yet publish these exact positional carriers faithfully;
  - `benchmarks/workloads/pattern_boundary.py` already owns the adjacent precompiled `Pattern` search/fullmatch helper surface, so this slice can stay on the existing manifest path instead of inventing another benchmark family; and
  - `reports/benchmarks/latest.py` currently reports `777` total / `777` measured / `0` known gaps overall, with `REPORT["summary"]["module_workloads"] == 769` and `REPORT["manifests"]["pattern-boundary"]` at `6` selected / `6` measured / `0` known gaps because `RBR-0830` is still ready in this run, so the acceptance counts above are intentionally written against the immediate post-`RBR-0830` state.
