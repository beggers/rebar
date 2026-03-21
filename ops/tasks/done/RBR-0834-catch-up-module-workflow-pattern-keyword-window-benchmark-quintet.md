# RBR-0834: Catch up the module-workflow `Pattern` keyword window benchmark quintet

Status: done
Owner: feature-implementation
Created: 2026-03-21

## Goal
- Extend the published Python-path pattern-boundary benchmark surface with the next five precompiled `Pattern` keyword-form `pos` / `endpos` helper workflows that the shared `module-workflow-surface` correctness path already publishes, while keeping this catch-up on the existing `pattern_boundary.py` manifest instead of opening another keyword-only benchmark family.

## Pattern Pair
- `"abc"`
- `b"abc"`

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/pattern_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `python/rebar_harness/benchmarks.py` keeps the tracked Python-path benchmark publication stable while extending the bounded pattern-helper argument surface to keyword-form `pos` / `endpos` carriers:
  - keep the existing plain pattern-helper search/match/fullmatch rows unchanged;
  - keep the post-`RBR-0832` positional-window and `pattern.findall` helper path working unchanged once it lands;
  - extend the workload schema from `count` / `maxsplit`-only numeric helper arguments to optional `kwargs` descriptors for `pos` / `endpos` on the precompiled helper path;
  - allow descriptor-backed `pos` and `endpos` values to stay unresolved until precompiled helper invocation so the benchmarked helper call times the real keyword-form numeric coercion boundary; and
  - do not broaden into raw-module keyword window rows, `Pattern.split()` / `sub()` / `subn()` keyword count/maxsplit catch-up, unexpected-keyword benchmark rows, new benchmark manifests, or unrelated benchmark-schema churn in this run.
- `benchmarks/workloads/pattern_boundary.py` remains the only benchmark manifest for this slice and grows by exactly five new precompiled-`Pattern` workloads:
  - add `pattern-search-pos-keyword-warm-str`;
  - add `pattern-match-pos-keyword-purged-str`;
  - add `pattern-fullmatch-window-keyword-purged-bytes`;
  - add `pattern-findall-bool-window-keyword-warm-str`; and
  - add `pattern-finditer-window-indexlike-purged-bytes`.
- Keep those five workloads pinned to the exact already-published module-workflow keyword anchors rather than inventing a broader helper family:
  - `pattern-search-pos-keyword-warm-str` uses `operation == "pattern.search"`, `pattern == "abc"`, `haystack == "zabcabc"`, `text_model == "str"`, `cache_mode == "warm"`, `timing_scope == "pattern-helper-call"`, and `kwargs == {"pos": 2}`;
  - `pattern-match-pos-keyword-purged-str` uses `operation == "pattern.match"`, `pattern == "abc"`, `haystack == "zabcabc"`, `text_model == "str"`, `cache_mode == "purged"`, `timing_scope == "pattern-helper-call"`, and `kwargs == {"pos": 1}`;
  - `pattern-fullmatch-window-keyword-purged-bytes` uses `operation == "pattern.fullmatch"`, `pattern == "abc"`, `haystack == "zabc"`, `text_model == "bytes"`, `cache_mode == "purged"`, `timing_scope == "pattern-helper-call"`, and `kwargs == {"pos": 1, "endpos": 4}`;
  - `pattern-findall-bool-window-keyword-warm-str` uses `operation == "pattern.findall"`, `pattern == "abc"`, `haystack == "zabcabcz"`, `text_model == "str"`, `cache_mode == "warm"`, `timing_scope == "pattern-helper-call"`, and `kwargs == {"pos": true, "endpos": 7}`;
  - `pattern-finditer-window-indexlike-purged-bytes` uses `operation == "pattern.finditer"`, `pattern == "abc"`, `haystack == "zabcabcabcz"`, `text_model == "bytes"`, `cache_mode == "purged"`, `timing_scope == "pattern-helper-call"`, and `kwargs == {"pos": {"type": "indexlike", "value": 1}, "endpos": {"type": "indexlike", "value": 7}}`;
  - keep the text-model split explicit at three `str` rows and two `bytes` rows; and
  - do not broaden into search endpos keyword/indexlike rows, match bool-pos rows, fullmatch indexlike-window rows, collection/replacement keyword carriers, smoke-only variants, or another benchmark manifest in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking a keyword-only benchmark suite:
  - update the pattern-boundary manifest expectations from `11` measured workloads to `16`, still with `0` known gaps on that manifest once `RBR-0832` has landed;
  - keep the manifest on the existing `post-parser-workflows` / combined-boundary path and anchor the five new workloads to the already-published correctness case ids `workflow-pattern-search-str-pos-keyword`, `workflow-pattern-match-str-pos-keyword`, `workflow-pattern-fullmatch-bytes-window-keyword`, `workflow-pattern-findall-str-bool-window-keyword`, and `workflow-pattern-finditer-bytes-window-indexlike`;
  - update the combined publication totals from `785` total / `785` measured / `0` known gaps across `30` manifests to `790` / `790` / `0` across the same `30` manifests;
  - update `REPORT["summary"]["module_workloads"]` from `777` to `782`;
  - keep `REPORT["summary"]["regression_workloads"]` at `8`; and
  - keep the built-native smoke manifest set and every existing non-keyword workload unchanged in this run.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["pattern-boundary"]` moves from `11` selected / `11` measured / `0` known gaps to `16` / `16` / `0`;
  - the five new keyword/window workloads publish real `rebar` timings with `status == "measured"`, not synthetic placeholders; and
  - the tracked report exposes those exact workload ids on the existing pattern-boundary benchmark surface.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/pattern_boundary.py --report .rebar/tmp/rbr-0834-pattern-boundary.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not widen the correctness surface, add raw-module keyword window benchmark support, or change Rust/Python regex behavior just to support a larger benchmark family.
- Reuse the existing `pattern_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another keyword-only benchmark manifest, another benchmark suite, or detached benchmark expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.

## Notes
- `RBR-0834` is the next available feature task id in the current checkout:
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done -maxdepth 1 -type f -printf '%f\n' | rg '^RBR-0832|^RBR-0833|^RBR-0834' | sort` returned `RBR-0832` and `RBR-0833` in this run; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0832` on the same `module-workflow-surface` frontier so the next precompiled `Pattern` keyword-form search/match/window slice catches up on the existing Python-path benchmark surface before collection/replacement keyword carriers or broader helper duplication reopens the queue.
- 2026-03-21 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier:
  - a normalized direct runtime probe in this run showed CPython and `rebar` already agree on the exact bounded outputs for `workflow-pattern-search-str-pos-keyword`, `workflow-pattern-match-str-pos-keyword`, `workflow-pattern-fullmatch-bytes-window-keyword`, `workflow-pattern-findall-str-bool-window-keyword`, and `workflow-pattern-finditer-bytes-window-indexlike`, so this remains a benchmark/publication task rather than a missing runtime-implementation prerequisite;
  - `python/rebar_harness/benchmarks.py` currently invokes precompiled `Pattern.search()` / `match()` / `fullmatch()` / `finditer()` without any keyword arguments and the `Workload` schema still only carries `count` / `maxsplit`, so the existing benchmark path cannot yet publish these exact keyword `pos` / `endpos` carriers faithfully; `RBR-0832` also still needs to land before the shared helper path can benchmark `pattern.findall`;
  - `benchmarks/workloads/pattern_boundary.py` already owns the adjacent precompiled `Pattern` search/match/fullmatch/findall/finditer surface, so this slice can stay on the existing manifest path instead of inventing another benchmark family; and
  - `reports/benchmarks/latest.py` currently reports `780` total / `780` measured / `0` known gaps overall, with `REPORT["summary"]["module_workloads"] == 772` and `REPORT["manifests"]["pattern-boundary"]` at `6` selected / `6` measured / `0` known gaps because `RBR-0832` is still ready in this run, so the acceptance counts above are intentionally written against the immediate post-`RBR-0832` state.

## Completion Note
- Added bounded `kwargs` support for precompiled `Pattern` benchmark helpers so `pos` / `endpos` keyword carriers stay as raw descriptors until callback invocation, while preserving the existing positional window rows and count/maxsplit handling.
- Landed the five requested `pattern_boundary.py` workloads, anchored them to the published module-workflow case ids on the shared source-tree benchmark contract, and expanded the zero-gap `pattern-boundary` manifest to `16` selected / `16` measured workloads.
- Regenerated `reports/benchmarks/latest.py`; the tracked publication now reports `790` total workloads, `790` measured, `0` known gaps, and `782` module workloads across the same `30` manifests.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/pattern_boundary.py --report .rebar/tmp/rbr-0834-pattern-boundary.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`.
