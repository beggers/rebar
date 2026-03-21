# RBR-0836: Catch up the module-workflow `Pattern` keyword replacement/split benchmark trio

Status: done
Owner: feature-implementation
Created: 2026-03-21

## Goal
- Extend the published Python-path collection/replacement benchmark surface with the exact precompiled `Pattern.split()` / `Pattern.sub()` / `Pattern.subn()` keyword `maxsplit` / `count` trio that the shared `module-workflow-surface` correctness path already publishes, while keeping this catch-up on the existing `collection_replacement_boundary.py` manifest instead of opening a second keyword-only benchmark family.

## Pattern Pair
- `"abc"`
- `b"abc"`

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/collection_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `python/rebar_harness/benchmarks.py` keeps the tracked Python-path benchmark publication stable while extending the post-`RBR-0834` precompiled-helper keyword path from window carriers to collection/replacement keyword carriers:
  - keep the post-`RBR-0834` keyword `pos` / `endpos` search/match/fullmatch/findall/finditer workloads working unchanged once they land;
  - keep every existing positional `count` / `maxsplit` workload working unchanged for both raw-module and precompiled-helper operations;
  - route exact keyword `maxsplit` / `count` descriptors through the shared precompiled-helper path for `Pattern.split()` / `Pattern.sub()` / `Pattern.subn()` instead of forcing those helper calls back through positional arguments;
  - allow keyword-backed `maxsplit` and `count` values to stay unresolved until precompiled helper invocation so the benchmarked helper call times the real keyword numeric coercion boundary; and
  - do not broaden into the remaining pattern keyword window quintet, keyword bool carriers, raw-module keyword duplicates, new benchmark manifests, or unrelated benchmark-schema churn in this run.
- `benchmarks/workloads/collection_replacement_boundary.py` remains the only benchmark manifest for this slice and grows by exactly three new precompiled-`Pattern` workloads:
  - add `pattern-split-maxsplit-keyword-warm-str`;
  - add `pattern-sub-count-keyword-purged-bytes`; and
  - add `pattern-subn-count-keyword-warm-str`.
- Keep those three workloads pinned to the exact already-published module-workflow keyword anchors rather than inventing a broader helper family:
  - `pattern-split-maxsplit-keyword-warm-str` uses `operation == "pattern.split"`, `pattern == "abc"`, `haystack == "zabczabc"`, `text_model == "str"`, `cache_mode == "warm"`, `timing_scope == "pattern-helper-call"`, and `kwargs == {"maxsplit": 1}`;
  - `pattern-sub-count-keyword-purged-bytes` uses `operation == "pattern.sub"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `text_model == "bytes"`, `cache_mode == "purged"`, `timing_scope == "pattern-helper-call"`, and `kwargs == {"count": 1}`;
  - `pattern-subn-count-keyword-warm-str` uses `operation == "pattern.subn"`, `pattern == "abc"`, `replacement == "x"`, `haystack == "abcabc"`, `text_model == "str"`, `cache_mode == "warm"`, `timing_scope == "pattern-helper-call"`, and `kwargs == {"count": 1}`;
  - keep the text-model split explicit at two `str` rows and one `bytes` row; and
  - do not broaden into keyword `__index__` or `bool` collection/replacement carriers, remaining keyword window rows, raw-module keyword rows, smoke-only variants, or another benchmark manifest in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared source-tree benchmark contract path instead of forking a keyword-only benchmark suite:
  - update the collection/replacement manifest expectations from `16` measured workloads to `19`, still with `0` known gaps on that manifest once `RBR-0834` has landed;
  - keep the manifest on the existing `post-parser-workflows` / combined-boundary path and anchor the three new workloads to the already-published correctness case ids `workflow-pattern-split-str-maxsplit-keyword`, `workflow-pattern-sub-count-keyword-bytes`, and `workflow-pattern-subn-count-keyword-str`;
  - update the combined publication totals from `790` total / `790` measured / `0` known gaps across `30` manifests to `793` / `793` / `0` across the same `30` manifests;
  - update `REPORT["summary"]["module_workloads"]` from `782` to `785`;
  - keep `REPORT["summary"]["regression_workloads"]` at `8`; and
  - keep the built-native smoke manifest set and every existing non-keyword workload unchanged in this run.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - `REPORT["manifests"]["collection-replacement-boundary"]` moves from `16` selected / `16` measured / `0` known gaps to `19` / `19` / `0`;
  - the three new keyword workloads publish real `rebar` timings with `status == "measured"`, not synthetic placeholders; and
  - the tracked report exposes those exact workload ids on the existing collection/replacement benchmark surface.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0836-collection-replacement-boundary.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not widen the correctness surface, add raw-module keyword collection/replacement benchmark support, or change Rust/Python regex behavior just to support a larger benchmark family.
- Reuse the existing `collection_replacement_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another keyword-only benchmark manifest, another benchmark suite, or detached benchmark expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.

## Notes
- `RBR-0836` is the next available feature task id in the current checkout:
  - `python3 - <<'PY'
import pathlib, re
existing = set()
for base in ['ops/tasks/ready', 'ops/tasks/in_progress', 'ops/tasks/done', 'ops/tasks/blocked']:
    for path in pathlib.Path(base).glob('RBR-*.md'):
        m = re.match(r'(RBR-\\d+[A-Z]?)', path.name)
        if m:
            existing.add(m.group(1))
text = '\\n'.join(
    pathlib.Path(p).read_text(encoding='utf-8')
    for p in ['ops/state/backlog.md', 'ops/state/current_status.md']
)
mentioned = set(re.findall(r'RBR-\\d+[A-Z]?', text))
reserved = sorted(mentioned - existing, key=lambda s: (int(re.search(r'\\d+', s).group()), s))
for n in range(1, 10000):
    rid = f'RBR-{n:04d}'
    if rid not in existing and rid not in reserved:
        print(rid)
        break
print('reserved_tail', reserved[-10:])
PY` returned `RBR-0836` with an empty reserved tail.
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0834` on the same `module-workflow-surface` frontier so the precompiled `Pattern` keyword replacement/split carriers catch up on the existing Python-path collection/replacement benchmark surface before broader helper duplication reopens the queue.
- 2026-03-21 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier:
  - a direct runtime probe in this run showed CPython and `rebar` already agree on the exact bounded outputs for `workflow-pattern-split-str-maxsplit-keyword`, `workflow-pattern-sub-count-keyword-bytes`, and `workflow-pattern-subn-count-keyword-str`, so this remains a benchmark/publication task rather than a missing runtime-implementation prerequisite;
  - `python/rebar_harness/benchmarks.py` currently invokes `Pattern.split()` / `Pattern.sub()` / `Pattern.subn()` through positional `maxsplit` / `count` arguments only and does not yet expose keyword-backed `maxsplit` / `count` descriptors on the precompiled helper path, so the existing benchmark path cannot yet publish these exact keyword carriers faithfully even though the runtime behavior is already live;
  - `benchmarks/workloads/collection_replacement_boundary.py` already owns the adjacent precompiled `Pattern` collection/replacement surface, so this slice can stay on the existing manifest path instead of inventing another benchmark family; and
  - `reports/benchmarks/latest.py` currently reports `785` total / `785` measured / `0` known gaps overall, with `REPORT["summary"]["module_workloads"] == 777` and `REPORT["manifests"]["collection-replacement-boundary"]` at `16` selected / `16` measured / `0` known gaps because `RBR-0834` is still ready in this run, so the acceptance counts above are intentionally written against the immediate post-`RBR-0834` state.

## Completion Note
- Extended `python/rebar_harness/benchmarks.py` so precompiled `Pattern` helper benchmarks now accept keyword `kwargs` carriers for `split(maxsplit=...)`, `sub(count=...)`, and `subn(count=...)`, while keeping keyword numeric descriptors unresolved until callback invocation and leaving the existing window-keyword plus positional collection/replacement paths intact.
- Added the three requested `collection_replacement_boundary.py` workloads, anchored them on the shared source-tree benchmark contract to `workflow-pattern-split-str-maxsplit-keyword`, `workflow-pattern-sub-count-keyword-bytes`, and `workflow-pattern-subn-count-keyword-str`, and expanded the zero-gap `collection-replacement-boundary` manifest from `16` to `19` selected/measured workloads.
- Regenerated the tracked `reports/benchmarks/latest.py`; the published report now shows `793` total workloads, `793` measured, `0` known gaps, `785` module workloads, and `collection-replacement-boundary` at `19` selected / `19` measured / `0` gaps, with all three new workload ids published as `measured`.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/collection_replacement_boundary.py --report .rebar/tmp/rbr-0836-collection-replacement-boundary.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`.
