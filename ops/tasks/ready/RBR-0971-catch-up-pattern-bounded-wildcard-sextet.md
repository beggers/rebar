# RBR-0971: Catch up the direct Pattern bounded-wildcard sextet

Status: ready
Owner: feature-implementation
Created: 2026-03-22

## Goal
- Extend the published Python-path `pattern_boundary.py` benchmark surface with the exact remaining direct-`Pattern` bounded-wildcard helper sextet that the current runtime already publishes on the shared `module-workflow-surface` correctness path, keeping this run on the existing `pattern-boundary` owner route instead of widening into another manifest or another helper family.

## Pattern Pair
- `re.compile("a.c", re.IGNORECASE)`
- `re.compile("a.c")`

## Helper Sextet
- `re.compile("a.c", re.IGNORECASE).search("zaBczz", 1, 5)`
- `re.compile("a.c").match("zabcaxc", 1, 4)`
- `re.compile("a.c").fullmatch("zaxcz", 1, 4)`
- `re.compile("a.c").findall("zabcaxcz", 1, 7)`
- `re.compile("a.c").finditer("zabcaxcx", 1, 7)`
- `re.compile("a.c").search("zabc", 1, 3)`

## Deliverables
- `benchmarks/workloads/pattern_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/pattern_boundary.py` remains the only benchmark manifest for this slice and grows by exactly six direct-`Pattern` bounded-wildcard workloads:
  - add `pattern-search-bounded-wildcard-ignorecase-warm-str`;
  - add `pattern-match-bounded-wildcard-warm-str`;
  - add `pattern-fullmatch-bounded-wildcard-purged-str`;
  - add `pattern-findall-bounded-wildcard-warm-str`;
  - add `pattern-finditer-bounded-wildcard-purged-str`; and
  - add `pattern-search-bounded-wildcard-endpos-miss-purged-str`.
- Keep those six workloads pinned to the already-published correctness anchors above rather than widening the `pattern-boundary` lane:
  - `pattern-search-bounded-wildcard-ignorecase-warm-str` uses `operation == "pattern.search"`, `pattern == "a.c"`, `haystack == "zaBczz"`, `flags == 2`, `pos == 1`, `endpos == 5`, `text_model == "str"`, `cache_mode == "warm"`, and `timing_scope == "pattern-helper-call"`;
  - `pattern-match-bounded-wildcard-warm-str` uses `operation == "pattern.match"`, `pattern == "a.c"`, `haystack == "zabcaxc"`, `flags == 0`, `pos == 1`, `endpos == 4`, `text_model == "str"`, `cache_mode == "warm"`, and `timing_scope == "pattern-helper-call"`;
  - `pattern-fullmatch-bounded-wildcard-purged-str` uses `operation == "pattern.fullmatch"`, `pattern == "a.c"`, `haystack == "zaxcz"`, `flags == 0`, `pos == 1`, `endpos == 4`, `text_model == "str"`, `cache_mode == "purged"`, and `timing_scope == "pattern-helper-call"`;
  - `pattern-findall-bounded-wildcard-warm-str` uses `operation == "pattern.findall"`, `pattern == "a.c"`, `haystack == "zabcaxcz"`, `flags == 0`, `pos == 1`, `endpos == 7`, `text_model == "str"`, `cache_mode == "warm"`, and `timing_scope == "pattern-helper-call"`;
  - `pattern-finditer-bounded-wildcard-purged-str` uses `operation == "pattern.finditer"`, `pattern == "a.c"`, `haystack == "zabcaxcx"`, `flags == 0`, `pos == 1`, `endpos == 7`, `text_model == "str"`, `cache_mode == "purged"`, and `timing_scope == "pattern-helper-call"`;
  - `pattern-search-bounded-wildcard-endpos-miss-purged-str` uses `operation == "pattern.search"`, `pattern == "a.c"`, `haystack == "zabc"`, `flags == 0`, `pos == 1`, `endpos == 3`, `text_model == "str"`, `cache_mode == "purged"`, and `timing_scope == "pattern-helper-call"`;
  - anchor the six workloads to `workflow-pattern-search-str-bounded-wildcard-ignorecase`, `workflow-pattern-match-str-bounded-wildcard`, `workflow-pattern-fullmatch-str-bounded-wildcard`, `workflow-pattern-findall-str-bounded-wildcard`, `workflow-pattern-finditer-str-bounded-wildcard`, and `workflow-pattern-search-str-bounded-wildcard-endpos-miss`;
  - insert the six-row bounded-wildcard block immediately after `pattern-fullmatch-bytes-purged-hit` and immediately before `pattern-search-on-bytes-string-warm-str`, preserving the exact order listed above; and
  - do not widen into wrong-text-model rows, keyword-window carriers, positional-indexlike rows, bytes-path wildcard siblings, another benchmark manifest, or benchmark-harness churn in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared `pattern-boundary` owner route instead of forking another benchmark suite:
  - update `test_pattern_boundary_manifest_keeps_keyword_and_positional_window_rows_measured(...)` so `pattern-boundary` moves from `31` total measured workloads to `37`, preserving the existing wrong-text-model, keyword-window, and positional-indexlike subsets while adding a new bounded-wildcard subset in this exact order:
    - `pattern-search-bounded-wildcard-ignorecase-warm-str`
    - `pattern-match-bounded-wildcard-warm-str`
    - `pattern-fullmatch-bounded-wildcard-purged-str`
    - `pattern-findall-bounded-wildcard-warm-str`
    - `pattern-finditer-bounded-wildcard-purged-str`
    - `pattern-search-bounded-wildcard-endpos-miss-purged-str`;
  - extend the standard benchmark anchor-contract definitions with exactly one new `pattern-boundary` bounded-wildcard owner-path definition that maps the six workload ids above to their six `workflow-pattern-*` anchors and verifies the shared callback-result parity on the existing owner route; and
  - keep the existing `pattern-boundary` wrong-text-model, keyword-window, and positional-indexlike ownership checks honest while moving the zero-gap `pattern-boundary` manifest expectation from `31` selected / `31` measured to `37` / `37`.
- `reports/benchmarks/latest.py` is regenerated honestly on the tracked source-tree-shim path:
  - the combined report moves from `914` total / `914` measured / `0` known gaps across `30` manifests to `920` / `920` / `0` across the same `30` manifests;
  - `module_workloads` moves from `906` to `912`;
  - `parser_workloads` stays `8`;
  - `regression_workloads` stays `8`; and
  - `REPORT["manifests"]["pattern-boundary"]` plus the matching `REPORT["artifacts"]["manifests"]` entry move from `31` selected / `31` measured / `31` workload-count rows to `37` / `37` / `37`, with all six new workload ids publishing `status == "measured"`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-search-str-bounded-wildcard-ignorecase or pattern-match-str-bounded-wildcard or pattern-fullmatch-str-bounded-wildcard or pattern-findall-str-bounded-wildcard or pattern-finditer-str-bounded-wildcard or pattern-search-str-bounded-wildcard-endpos-miss'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'pattern_boundary_manifest_keeps_keyword_and_positional_window_rows_measured or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks or standard_benchmark_anchor_contract'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/pattern_boundary.py --report .rebar/tmp/rbr-0971-pattern-bounded-wildcard-sextet.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only. Do not widen the correctness surface or change Rust/Python regex behavior beyond what is required to publish and time the exact six direct-`Pattern` bounded-wildcard workloads above on the existing `pattern-boundary` owner path.
- Reuse the existing `pattern_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner route. Do not create another benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.

## Notes
- `RBR-0971` is the next available feature task id in the current checkout:
  - `RBR-0969` is the latest done feature task on the drained direct-`Pattern` keyword-window frontier;
  - `RBR-0970` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` contains only `.gitkeep` in this checkout.
- Queue this directly after `RBR-0969` on the same shared `pattern-boundary` owner family so the next already-published direct-`Pattern` helper slice reaches the tracked Python-path benchmark surface before a broader verbose-regression pack, another compiled-pattern module benchmark sibling, or another owner family widens the queue.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-search-str-bounded-wildcard-ignorecase or pattern-match-str-bounded-wildcard or pattern-fullmatch-str-bounded-wildcard or pattern-findall-str-bounded-wildcard or pattern-finditer-str-bounded-wildcard or pattern-search-str-bounded-wildcard-endpos-miss'` currently passes (`20 passed`), so the exact bounded correctness/parity slice is already green in this checkout;
  - `PYTHONPATH=python:. ./.venv/bin/python - <<'PY' ... workload_from_payload(...) / workload_to_payload(...) / run_internal_workload_probe(...) synthetic pattern-search-bounded-wildcard-ignorecase-probe, pattern-match-bounded-wildcard-probe, pattern-fullmatch-bounded-wildcard-probe, pattern-findall-bounded-wildcard-probe, pattern-finditer-bounded-wildcard-probe, and pattern-search-bounded-wildcard-endpos-miss-probe ... PY` returns `status == "measured"` for both adapters on all six synthetic workloads through the current benchmark harness in this checkout; and
  - `rg -n 'pattern-search-bounded-wildcard-ignorecase-warm-str|pattern-match-bounded-wildcard-warm-str|pattern-fullmatch-bounded-wildcard-purged-str|pattern-findall-bounded-wildcard-warm-str|pattern-finditer-bounded-wildcard-purged-str|pattern-search-bounded-wildcard-endpos-miss-purged-str' benchmarks/workloads/pattern_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/benchmarks/latest.py` currently returns no matches, while `reports/benchmarks/latest.py` still reports `914` total / `914` measured / `0` known gaps overall with `pattern-boundary` fixed at `31` selected / `31` measured / `31` workload-count rows and `module_workloads == 906`.
