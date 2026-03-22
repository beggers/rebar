# RBR-0973: Catch up the direct Pattern verbose-regression search sextet

Status: ready
Owner: feature-implementation
Created: 2026-03-22

## Goal
- Extend the published Python-path `pattern_boundary.py` benchmark surface with the exact direct-`Pattern` verbose-regression `search()` sextet that the current runtime already publishes on the shared `module-workflow-surface` correctness path, keeping this run on the existing `pattern-boundary` owner route instead of widening into another manifest, another helper family, or a native-path detour.

## Pattern Pair
- `re.compile("^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $", re.VERBOSE | re.MULTILINE)`
- `re.compile(b"^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $", re.VERBOSE | re.MULTILINE)`

## Helper Sextet
- `re.compile(..., re.VERBOSE | re.MULTILINE).search("prefix\nENV_VAR=ABCD\nsuffix")`
- `re.compile(..., re.VERBOSE | re.MULTILINE).search("prefix\nENV_VAR = 123\nsuffix")`
- `re.compile(..., re.VERBOSE | re.MULTILINE).search("prefix\nENV_VAR = 12345\nsuffix")`
- `re.compile(..., re.VERBOSE | re.MULTILINE).search(b"prefix\nENV_VAR=ABCD\nsuffix")`
- `re.compile(..., re.VERBOSE | re.MULTILINE).search(b"prefix\nENV_VAR = 123\nsuffix")`
- `re.compile(..., re.VERBOSE | re.MULTILINE).search(b"prefix\nENV_VAR = 12345\nsuffix")`

## Deliverables
- `benchmarks/workloads/pattern_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/pattern_boundary.py` remains the only benchmark manifest for this slice and grows by exactly six direct-`Pattern` verbose-regression `search()` workloads:
  - add `pattern-search-verbose-regression-warm-str`;
  - add `pattern-search-verbose-regression-digits-warm-str`;
  - add `pattern-search-verbose-regression-too-many-digits-purged-str`;
  - add `pattern-search-verbose-regression-warm-bytes`;
  - add `pattern-search-verbose-regression-digits-warm-bytes`; and
  - add `pattern-search-verbose-regression-too-many-digits-purged-bytes`.
- Keep those six workloads pinned to the already-published correctness anchors above rather than widening the `pattern-boundary` lane:
  - `pattern-search-verbose-regression-warm-str` uses `operation == "pattern.search"`, the exact verbose pattern above, `haystack == "prefix\nENV_VAR=ABCD\nsuffix"`, `flags == 72`, `text_model == "str"`, `cache_mode == "warm"`, and `timing_scope == "pattern-helper-call"`;
  - `pattern-search-verbose-regression-digits-warm-str` uses the same pattern with `haystack == "prefix\nENV_VAR = 123\nsuffix"`, `flags == 72`, `text_model == "str"`, `cache_mode == "warm"`, and `timing_scope == "pattern-helper-call"`;
  - `pattern-search-verbose-regression-too-many-digits-purged-str` uses the same pattern with `haystack == "prefix\nENV_VAR = 12345\nsuffix"`, `flags == 72`, `text_model == "str"`, `cache_mode == "purged"`, and `timing_scope == "pattern-helper-call"`;
  - `pattern-search-verbose-regression-warm-bytes` uses the same pattern with `haystack == "prefix\nENV_VAR=ABCD\nsuffix"`, `flags == 72`, `text_model == "bytes"`, `cache_mode == "warm"`, and `timing_scope == "pattern-helper-call"`;
  - `pattern-search-verbose-regression-digits-warm-bytes` uses the same pattern with `haystack == "prefix\nENV_VAR = 123\nsuffix"`, `flags == 72`, `text_model == "bytes"`, `cache_mode == "warm"`, and `timing_scope == "pattern-helper-call"`;
  - `pattern-search-verbose-regression-too-many-digits-purged-bytes` uses the same pattern with `haystack == "prefix\nENV_VAR = 12345\nsuffix"`, `flags == 72`, `text_model == "bytes"`, `cache_mode == "purged"`, and `timing_scope == "pattern-helper-call"`;
  - anchor the six workloads to `workflow-pattern-search-str-verbose-regression`, `workflow-pattern-search-str-verbose-regression-digits`, `workflow-pattern-search-str-verbose-regression-too-many-digits`, `workflow-pattern-search-bytes-verbose-regression`, `workflow-pattern-search-bytes-verbose-regression-digits`, and `workflow-pattern-search-bytes-verbose-regression-too-many-digits`;
  - insert the six-row verbose-regression block immediately after `pattern-search-bounded-wildcard-endpos-miss-purged-str` and immediately before `pattern-search-on-bytes-string-warm-str`, preserving the exact order listed above; and
  - do not widen into the direct-`Pattern` verbose-regression `fullmatch()` sextet, module-boundary compiled-pattern verbose rows, keyword/window carriers, positional rows, another benchmark manifest, or benchmark-harness churn in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared `pattern-boundary` owner route instead of forking another benchmark suite:
  - update `test_pattern_boundary_manifest_keeps_keyword_and_positional_window_rows_measured(...)` or an equivalent existing `pattern-boundary` assertion so the manifest moves from `37` measured workloads to `43`, preserving the existing wrong-text-model, bounded-wildcard, keyword-window, and positional-indexlike subsets while adding a new verbose-regression subset in this exact order:
    - `pattern-search-verbose-regression-warm-str`
    - `pattern-search-verbose-regression-digits-warm-str`
    - `pattern-search-verbose-regression-too-many-digits-purged-str`
    - `pattern-search-verbose-regression-warm-bytes`
    - `pattern-search-verbose-regression-digits-warm-bytes`
    - `pattern-search-verbose-regression-too-many-digits-purged-bytes`;
  - extend the standard benchmark anchor-contract definitions with exactly one new `pattern-boundary` verbose-regression owner-path definition that maps the six workload ids above to their six `workflow-pattern-search-*` anchors and verifies the shared callback-result parity on the existing owner route; and
  - keep the existing `pattern-boundary` wrong-text-model, bounded-wildcard, keyword-window, and positional-indexlike ownership checks honest while moving the zero-gap `pattern-boundary` manifest expectation from `37` selected / `37` measured to `43` / `43`.
- `reports/benchmarks/latest.py` is regenerated honestly on the tracked source-tree-shim path:
  - the combined report moves from `920` total / `920` measured / `0` known gaps across `30` manifests to `926` / `926` / `0` across the same `30` manifests;
  - `module_workloads` moves from `912` to `918`;
  - `parser_workloads` stays `8`;
  - `regression_workloads` stays `8`; and
  - `REPORT["manifests"]["pattern-boundary"]` plus the matching `REPORT["artifacts"]["manifests"]` entry move from `37` selected / `37` measured / `37` workload-count rows to `43` / `43` / `43`, with all six new workload ids publishing `status == "measured"`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-search-str-verbose-regression or pattern-search-str-verbose-regression-digits or pattern-search-str-verbose-regression-too-many-digits or pattern-search-bytes-verbose-regression or pattern-search-bytes-verbose-regression-digits or pattern-search-bytes-verbose-regression-too-many-digits'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'pattern_boundary_manifest_keeps_keyword_and_positional_window_rows_measured or standard_benchmark_anchor_contract or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/pattern_boundary.py --report .rebar/tmp/rbr-0973-pattern-search-verbose-regression-sextet.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only. Do not widen the correctness surface or change Rust/Python regex behavior beyond what is required to publish and time the exact six direct-`Pattern` verbose-regression `search()` workloads above on the existing `pattern-boundary` owner path.
- Reuse the existing `pattern_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner route. Do not create another benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.

## Notes
- `RBR-0973` is the next available feature task id in the current checkout:
  - `RBR-0971` is the latest done feature task on the drained direct-`Pattern` `pattern-boundary` frontier;
  - `RBR-0972` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` contains only `.gitkeep` in this checkout.
- Queue this directly after `RBR-0971` / `RBR-0972` on the same shared `pattern-boundary` owner family so the next already-published direct-`Pattern` verbose-regression search slice reaches the tracked Python-path benchmark surface before the adjacent direct-`Pattern` verbose-regression `fullmatch()` sextet, another owner family, or native-path benchmark work widens the queue.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-search-str-verbose-regression or pattern-search-str-verbose-regression-digits or pattern-search-str-verbose-regression-too-many-digits or pattern-search-bytes-verbose-regression or pattern-search-bytes-verbose-regression-digits or pattern-search-bytes-verbose-regression-too-many-digits'` currently passes (`30 passed`), so the exact bounded correctness/parity slice is already green in this checkout;
  - `PYTHONPATH=python python3 - <<'PY' ... Workload.from_dict(...) / workload_to_payload(...) / run_internal_workload_probe(...) synthetic pattern-search-verbose-regression-warm-str, pattern-search-verbose-regression-digits-warm-str, pattern-search-verbose-regression-too-many-digits-purged-str, pattern-search-verbose-regression-warm-bytes, pattern-search-verbose-regression-digits-warm-bytes, and pattern-search-verbose-regression-too-many-digits-purged-bytes ... PY` returns `status == "measured"` for both adapters on all six synthetic workloads through the current benchmark harness in this checkout; and
  - `rg -n 'pattern-search-verbose-regression-warm-str|pattern-search-verbose-regression-digits-warm-str|pattern-search-verbose-regression-too-many-digits-purged-str|pattern-search-verbose-regression-warm-bytes|pattern-search-verbose-regression-digits-warm-bytes|pattern-search-verbose-regression-too-many-digits-purged-bytes' benchmarks/workloads/pattern_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/benchmarks/latest.py` currently returns no matches, while `reports/benchmarks/latest.py` still reports `920` total / `920` measured / `0` known gaps overall with `pattern-boundary` fixed at `37` selected / `37` measured / `37` workload-count rows and `module_workloads == 912`.
