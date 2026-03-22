## RBR-0975: Catch up the direct Pattern verbose-regression fullmatch sextet

Status: ready
Owner: feature-implementation
Created: 2026-03-22

## Goal
- Extend the published Python-path `pattern_boundary.py` benchmark surface with the exact direct-`Pattern` verbose-regression `fullmatch()` sextet that the current runtime already publishes on the shared `module-workflow-surface` correctness path, keeping this run on the existing `pattern-boundary` owner route instead of widening into another manifest, another helper family, or a native-path detour.

## Pattern Pair
- `re.compile("^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $", re.VERBOSE | re.MULTILINE)`
- `re.compile(b"^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $", re.VERBOSE | re.MULTILINE)`

## Helper Sextet
- `re.compile(..., re.VERBOSE | re.MULTILINE).fullmatch("ENV_VAR = 123")`
- `re.compile(..., re.VERBOSE | re.MULTILINE).fullmatch("ENV_VAR   =   ABCD")`
- `re.compile(..., re.VERBOSE | re.MULTILINE).fullmatch("env_var = 123")`
- `re.compile(..., re.VERBOSE | re.MULTILINE).fullmatch(b"ENV_VAR = 123")`
- `re.compile(..., re.VERBOSE | re.MULTILINE).fullmatch(b"ENV_VAR   =   ABCD")`
- `re.compile(..., re.VERBOSE | re.MULTILINE).fullmatch(b"env_var = 123")`

## Deliverables
- `benchmarks/workloads/pattern_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/pattern_boundary.py` remains the only benchmark manifest for this slice and grows by exactly six direct-`Pattern` verbose-regression `fullmatch()` workloads:
  - add `pattern-fullmatch-verbose-regression-warm-str`;
  - add `pattern-fullmatch-verbose-regression-alpha-warm-str`;
  - add `pattern-fullmatch-verbose-regression-lowercase-key-purged-str`;
  - add `pattern-fullmatch-verbose-regression-warm-bytes`;
  - add `pattern-fullmatch-verbose-regression-alpha-warm-bytes`; and
  - add `pattern-fullmatch-verbose-regression-lowercase-key-purged-bytes`.
- Keep those six workloads pinned to the already-published correctness anchors above rather than widening the `pattern-boundary` lane:
  - `pattern-fullmatch-verbose-regression-warm-str` uses `operation == "pattern.fullmatch"`, the exact verbose pattern above, `haystack == "ENV_VAR = 123"`, `flags == 72`, `text_model == "str"`, `cache_mode == "warm"`, and `timing_scope == "pattern-helper-call"`;
  - `pattern-fullmatch-verbose-regression-alpha-warm-str` uses the same pattern with `haystack == "ENV_VAR   =   ABCD"`, `flags == 72`, `text_model == "str"`, `cache_mode == "warm"`, and `timing_scope == "pattern-helper-call"`;
  - `pattern-fullmatch-verbose-regression-lowercase-key-purged-str` uses the same pattern with `haystack == "env_var = 123"`, `flags == 72`, `text_model == "str"`, `cache_mode == "purged"`, and `timing_scope == "pattern-helper-call"`;
  - `pattern-fullmatch-verbose-regression-warm-bytes` uses the same pattern with `haystack == "ENV_VAR = 123"`, `flags == 72`, `text_model == "bytes"`, `cache_mode == "warm"`, and `timing_scope == "pattern-helper-call"`;
  - `pattern-fullmatch-verbose-regression-alpha-warm-bytes` uses the same pattern with `haystack == "ENV_VAR   =   ABCD"`, `flags == 72`, `text_model == "bytes"`, `cache_mode == "warm"`, and `timing_scope == "pattern-helper-call"`;
  - `pattern-fullmatch-verbose-regression-lowercase-key-purged-bytes` uses the same pattern with `haystack == "env_var = 123"`, `flags == 72`, `text_model == "bytes"`, `cache_mode == "purged"`, and `timing_scope == "pattern-helper-call"`;
  - anchor the six workloads to `workflow-pattern-fullmatch-str-verbose-regression`, `workflow-pattern-fullmatch-str-verbose-regression-alpha`, `workflow-pattern-fullmatch-str-verbose-regression-lowercase-key`, `workflow-pattern-fullmatch-bytes-verbose-regression`, `workflow-pattern-fullmatch-bytes-verbose-regression-alpha`, and `workflow-pattern-fullmatch-bytes-verbose-regression-lowercase-key`;
  - insert the six-row fullmatch verbose-regression block immediately after `pattern-search-verbose-regression-too-many-digits-purged-bytes` and immediately before `pattern-search-on-bytes-string-warm-str`, preserving the exact order listed above; and
  - do not widen into compiled-pattern module-boundary verbose rows, direct-`Pattern` keyword/window carriers, direct-`Pattern` positional rows, another benchmark manifest, or benchmark-harness churn in this run.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the shared `pattern-boundary` owner route instead of forking another benchmark suite:
  - update `test_pattern_boundary_manifest_keeps_keyword_and_positional_window_rows_measured(...)` or an equivalent existing `pattern-boundary` assertion so the manifest moves from `43` measured workloads to `49`, preserving the existing wrong-text-model, bounded-wildcard, verbose-search, keyword-window, and positional-indexlike subsets while adding a new fullmatch verbose-regression subset in this exact order:
    - `pattern-fullmatch-verbose-regression-warm-str`
    - `pattern-fullmatch-verbose-regression-alpha-warm-str`
    - `pattern-fullmatch-verbose-regression-lowercase-key-purged-str`
    - `pattern-fullmatch-verbose-regression-warm-bytes`
    - `pattern-fullmatch-verbose-regression-alpha-warm-bytes`
    - `pattern-fullmatch-verbose-regression-lowercase-key-purged-bytes`;
  - extend the standard benchmark anchor-contract definitions with exactly one new `pattern-boundary` fullmatch verbose-regression owner-path definition, or a strictly equivalent widening of the existing verbose-regression definition, that maps the six workload ids above to their six `workflow-pattern-fullmatch-*` anchors and verifies the shared callback-result parity on the existing owner route; and
  - keep the existing `pattern-boundary` wrong-text-model, bounded-wildcard, verbose-search, keyword-window, and positional-indexlike ownership checks honest while moving the zero-gap `pattern-boundary` manifest expectation from `43` selected / `43` measured to `49` / `49`.
- `reports/benchmarks/latest.py` is regenerated honestly on the tracked source-tree-shim path:
  - the combined report moves from `926` total / `926` measured / `0` known gaps across `30` manifests to `932` / `932` / `0` across the same `30` manifests;
  - `module_workloads` moves from `918` to `924`;
  - `parser_workloads` stays `8`;
  - `regression_workloads` stays `8`; and
  - `REPORT["manifests"]["pattern-boundary"]` plus the matching `REPORT["artifacts"]["manifests"]` entry move from `43` selected / `43` measured / `43` workload-count rows to `49` / `49` / `49`, with all six new workload ids publishing `status == "measured"`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-fullmatch-str-verbose-regression or pattern-fullmatch-str-verbose-regression-alpha or pattern-fullmatch-str-verbose-regression-lowercase-key or pattern-fullmatch-bytes-verbose-regression or pattern-fullmatch-bytes-verbose-regression-alpha or pattern-fullmatch-bytes-verbose-regression-lowercase-key'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'pattern_boundary_manifest_keeps_keyword_and_positional_window_rows_measured or standard_benchmark_anchor_contract or published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/pattern_boundary.py --report .rebar/tmp/rbr-0975-pattern-fullmatch-verbose-regression-sextet.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-path only. Do not widen the correctness surface or change Rust/Python regex behavior beyond what is required to publish and time the exact six direct-`Pattern` verbose-regression `fullmatch()` workloads above on the existing `pattern-boundary` owner path.
- Reuse the existing `pattern_boundary.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner route. Do not create another benchmark manifest, another benchmark suite, or detached expectation helpers in this run.
- Keep the benchmark comparison on the tracked Python-facing source-tree shim path.

## Notes
- `RBR-0975` is the next available feature task id in the current checkout:
  - `RBR-0973` is the latest done feature task on the drained direct-`Pattern` `pattern-boundary` frontier;
  - `RBR-0974` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` contains only `.gitkeep` in this checkout.
- Queue this directly after `RBR-0973` on the same shared `pattern-boundary` owner family so the next already-published direct-`Pattern` verbose-regression fullmatch slice reaches the tracked Python-path benchmark surface before another owner family or native-path benchmark work widens the queue.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-fullmatch-str-verbose-regression or pattern-fullmatch-str-verbose-regression-alpha or pattern-fullmatch-str-verbose-regression-lowercase-key or pattern-fullmatch-bytes-verbose-regression or pattern-fullmatch-bytes-verbose-regression-alpha or pattern-fullmatch-bytes-verbose-regression-lowercase-key'` currently passes (`30 passed`), so the exact bounded correctness/parity slice is already green in this checkout;
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... Workload.from_dict(...) / workload_to_payload(...) / run_internal_workload_probe(...) synthetic pattern-fullmatch-verbose-regression-warm-str, pattern-fullmatch-verbose-regression-alpha-warm-str, pattern-fullmatch-verbose-regression-lowercase-key-purged-str, pattern-fullmatch-verbose-regression-warm-bytes, pattern-fullmatch-verbose-regression-alpha-warm-bytes, and pattern-fullmatch-verbose-regression-lowercase-key-purged-bytes ... PY` returns `status == "measured"` for both adapters on all six synthetic workloads through the current benchmark harness in this checkout; and
  - `rg -n 'pattern-fullmatch-verbose-regression-warm-str|pattern-fullmatch-verbose-regression-alpha-warm-str|pattern-fullmatch-verbose-regression-lowercase-key-purged-str|pattern-fullmatch-verbose-regression-warm-bytes|pattern-fullmatch-verbose-regression-alpha-warm-bytes|pattern-fullmatch-verbose-regression-lowercase-key-purged-bytes' benchmarks/workloads/pattern_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/benchmarks/latest.py` currently returns no matches, while `reports/benchmarks/latest.py` still reports `926` total / `926` measured / `0` known gaps overall with `pattern-boundary` fixed at `43` selected / `43` measured / `43` workload-count rows and `module_workloads == 918`.
