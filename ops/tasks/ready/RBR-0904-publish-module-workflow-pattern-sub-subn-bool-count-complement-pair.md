# RBR-0904: Publish the module-workflow `Pattern.sub()`/`Pattern.subn()` bool-count complement pair

Status: ready
Owner: feature-implementation
Created: 2026-03-22

## Goal
- Reopen the existing `module-workflow-surface` correctness frontier after the raw-module bool-count benchmark catch-up by publishing the adjacent direct `Pattern.sub()` / `Pattern.subn()` bool-count complement pair that the current runtime already executes with CPython parity, while leaving the Python-path benchmark frontier unchanged in this run because the shared `collection_replacement_boundary.py` owner already times the adjacent direct `Pattern` replacement keyword carriers on the same route.

## Pattern Pair
- `re.compile(b"abc").sub(b"x", b"abcabc", count=True)`
- `re.compile("abc").subn("x", "abcabc", count=False)`

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared direct-`Pattern` keyword owner path without another fixture file, detached coercion manifest, or benchmark-side churn:
  - extend `PATTERN_KEYWORD_CALL_CASES` by exactly two direct cases:
    - `pattern-sub-count-bool-true-bytes`
    - `pattern-subn-count-bool-false-str`
  - pin those direct cases to the exact existing bounded direct-`Pattern` replacement owner path:
    - `pattern-sub-count-bool-true-bytes` uses `helper == "sub"`, `pattern == b"abc"`, `args == (b"x", b"abcabc")`, and `kwargs == {"count": True}`;
    - `pattern-subn-count-bool-false-str` uses `helper == "subn"`, `pattern == "abc"`, `args == ("x", "abcabc")`, and `kwargs == {"count": False}`;
  - extend the published direct-`Pattern` keyword fixture expectations by exactly two rows:
    - `workflow-pattern-sub-count-bool-true-bytes`
    - `workflow-pattern-subn-count-bool-false-str`
  - insert `workflow-pattern-sub-count-bool-true-bytes` immediately after `workflow-pattern-sub-count-bool-false-bytes` and immediately before `workflow-pattern-subn-count-keyword-str`;
  - insert `workflow-pattern-subn-count-bool-false-str` immediately after `workflow-pattern-subn-count-indexlike-str` and immediately before `workflow-pattern-subn-count-bool-true-str`;
  - update the shared published direct-`Pattern` keyword helper totals from `25` rows to `27`, with the text-model split moving from `14` `str` / `11` `bytes` to `15` / `12`;
  - update the shared direct-`Pattern` keyword helper breakdown from `search: 5`, `match: 3`, `fullmatch: 2`, `findall: 3`, `finditer: 3`, `split: 3`, `sub: 3`, `subn: 3` to `search: 5`, `match: 3`, `fullmatch: 2`, `findall: 3`, `finditer: 3`, `split: 3`, `sub: 4`, `subn: 4`;
  - update the shared `module-workflow-surface` bundle expectations from `152` total rows to `154`, with the text-model split moving from `87` `str` / `65` `bytes` to `88` / `66`;
  - keep `module_call` expectations unchanged at `85` rows; and
  - move the `pattern_call` helper totals from `55` rows with `sub: 3` / `subn: 3` to `57` rows with `sub: 4` / `subn: 4`.
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by exactly two new `pattern_call` rows:
  - add `workflow-pattern-sub-count-bool-true-bytes`;
  - add `workflow-pattern-subn-count-bool-false-str`;
  - keep both rows on the existing direct-`Pattern` keyword-helper route with no module-level wrapper call, no positional count argument, and explicit bool-valued `kwargs["count"]`;
  - keep the `sub()` row on the `bytes` text model and the `subn()` row on the `str` text model to match the existing direct-`Pattern` owner-path split;
  - categorize both rows under `["workflow", ..., "literal", "keyword", ..., "count", "bool"]`; and
  - keep the notes explicit that these are the bool-count complement spellings adjacent to the already published `count=False` direct-`Pattern.sub()` row and `count=True` direct-`Pattern.subn()` row, not a broader direct-`Pattern` replacement keyword dump.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1526` total / `1526` passed / `0` `unimplemented` across `114` manifests to `1528` / `1528` / `0` across the same `114` manifests;
  - `module.workflow` moves from `152` / `152` / `0` to `154` / `154` / `0`;
  - `module.workflow.str` moves from `87` / `87` / `0` to `88` / `88` / `0`;
  - `module.workflow.bytes` moves from `65` / `65` / `0` to `66` / `66` / `0`;
  - `module.workflow.module_call` stays `85` / `85` / `0`;
  - `module.workflow.pattern_call` moves from `55` / `55` / `0` to `57` / `57` / `0`; and
  - the two new direct-`Pattern` bool-count complement rows are visible in the tracked scorecard as representative `module-workflow-surface` pattern-call cases.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-sub-count-bool-true-bytes or pattern-subn-count-bool-false-str or module_workflow_surface_publishes_pattern_keyword_helpers_from_direct_cases'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0904-module-workflow-pattern-sub-subn-bool-count-complement-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or benchmark-side selector logic in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached direct-`Pattern` publication file.
- Keep the Python-path benchmark frontier unchanged here. The shared `collection_replacement_boundary.py` owner already times the adjacent direct-`Pattern` bool-count helper carriers, so this run should publish the missing correctness spellings without forking another benchmark family.
- Assume `RBR-0902` remains the next task to drain first; if the raw-module benchmark catch-up has not landed yet, do not mix that benchmark update into this correctness-publication slice.

## Notes
- `RBR-0904` is the next available feature task id in the current checkout:
  - `RBR-0902` is already occupied by the ready feature task in `ops/tasks/ready/`;
  - `RBR-0903` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0902` on the same shared `module-workflow-surface` / `collection-replacement-boundary` frontier so the next surviving follow-on reopens correctness through one bounded direct-`Pattern` bool-count complement pair instead of widening into the full direct-`Pattern` replacement keyword matrix in one run.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier while the publication path still lacks the exact pair:
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... rebar.compile(b"abc").sub(b"x", b"abcabc", count=True) ... rebar.compile("abc").subn("x", "abcabc", count=False) ... PY` matched stdlib `re` for both exact calls in this run;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern_sub_count_keyword_argument_calls_match_cpython or pattern-sub-count-bool-false-bytes or pattern-subn-count-bool-true-str'` passed in this run (`4 passed, 1233 deselected`), so no Rust or Python regex-behavior prerequisite is missing for the adjacent direct-`Pattern` replacement keyword owner path;
  - direct publication probes in this run confirmed `workflow-pattern-sub-count-bool-true-bytes` and `workflow-pattern-subn-count-bool-false-str` are still absent from `tests/conformance/fixtures/module_workflow_surface.py`, `tests/python/test_module_workflow_parity_suite.py`, and `reports/correctness/latest.py`; and
  - `benchmarks/workloads/collection_replacement_boundary.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and `reports/benchmarks/latest.py` already carry the adjacent `pattern-sub-count-bool-keyword-purged-bytes` and `pattern-subn-count-bool-keyword-warm-str` workloads on the shared collection/replacement owner path, so this task can stay correctness-only without inventing another benchmark manifest first.
