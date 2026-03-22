# RBR-0896: Publish the module-workflow module `sub()`/`subn()` bool-count complement pair

Status: done
Owner: feature-implementation
Created: 2026-03-22

## Goal
- Reopen the existing `module-workflow-surface` correctness frontier after `RBR-0894` by publishing the adjacent raw module-level bool-count complement pair that is already covered by the shared keyword-coercion parity matrix, while leaving the Python-path benchmark frontier unchanged in this run because the shared collection/replacement benchmark owner already times the adjacent module `sub()` / `subn()` bool count carriers on the same route.

## Pattern Pair
- `re.sub("abc", "x", "abcabc", count=False)`
- `re.subn(b"abc", b"x", b"abcabc", count=True)`

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared module-workflow owner path without another fixture file, detached coercion manifest, or benchmark-side churn:
  - extend `MODULE_KEYWORD_CALL_CASES` by exactly two direct cases:
    - `module-sub-count-bool-false-str`
    - `module-subn-count-bool-true-bytes`
  - pin those direct cases to the exact existing bounded module bool-count anchors from the coercion matrix:
    - `module-sub-count-bool-false-str` uses `helper == "sub"`, `args == ("abc", "x", "abcabc")`, `kwargs == {"count": False}`, and `result_kind == "value"`;
    - `module-subn-count-bool-true-bytes` uses `helper == "subn"`, `args == (b"abc", b"x", b"abcabc")`, `kwargs == {"count": True}`, and `result_kind == "value"`;
  - extend the published module-keyword fixture expectations by exactly two rows:
    - `workflow-module-sub-count-bool-false-str`
    - `workflow-module-subn-count-bool-true-bytes`
  - insert `workflow-module-sub-count-bool-false-str` immediately after `workflow-module-sub-count-indexlike-str` and immediately before `workflow-module-sub-count-bool-true-str`;
  - insert `workflow-module-subn-count-bool-true-bytes` immediately after `workflow-module-subn-count-bool-false-bytes`;
  - update the shared published module-keyword helper totals from `12` rows to `14`, with the text-model split moving from `5` `str` / `7` `bytes` to `6` / `8`;
  - update the shared module-keyword helper breakdown from `search: 1`, `match: 1`, `fullmatch: 1`, `split: 3`, `sub: 3`, `subn: 3` to `search: 1`, `match: 1`, `fullmatch: 1`, `split: 3`, `sub: 4`, `subn: 4`;
  - update the shared `module-workflow-surface` bundle expectations from `148` total rows to `150`, with the text-model split moving from `85` `str` / `63` `bytes` to `86` / `64`;
  - keep `pattern_call` expectations unchanged at `55` rows;
  - keep `module_call` compile/search/match/fullmatch/split/findall/finditer/escape counts unchanged in this run; and
  - move the `module_call` helper totals from `81` rows with `sub: 13` / `subn: 11` to `83` rows with `sub: 14` / `subn: 12`.
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by exactly two new `module_call` rows:
  - add `workflow-module-sub-count-bool-false-str`;
  - add `workflow-module-subn-count-bool-true-bytes`;
  - keep both rows on the existing raw module keyword-helper route with no positional `args`, no `use_compiled_pattern`, and explicit bool-valued `kwargs["count"]`;
  - keep the `sub()` row on the `str` text model and the `subn()` row on the `bytes` text model to match the existing owner-path split;
  - categorize both rows under `["workflow", ..., "literal", ..., "count", "bool"]`; and
  - keep the notes explicit that these are the bool-count complement spellings adjacent to the already published `count=True` `sub()` row and `count=False` `subn()` row, not a broader coercion-matrix dump.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1522` total / `1522` passed / `0` `unimplemented` across `114` manifests to `1524` / `1524` / `0` across the same `114` manifests;
  - `module.workflow` moves from `148` / `148` / `0` to `150` / `150` / `0`;
  - `module.workflow.str` moves from `85` / `85` / `0` to `86` / `86` / `0`;
  - `module.workflow.bytes` moves from `63` / `63` / `0` to `64` / `64` / `0`;
  - `module.workflow.module_call` moves from `81` / `81` / `0` to `83` / `83` / `0`;
  - `module.workflow.pattern_call` stays `55` / `55` / `0`; and
  - the two new bool-count rows are visible in the tracked scorecard as representative `module-workflow-surface` module-call cases.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module-sub-count-bool-false-str or module-subn-count-bool-true-bytes or module_workflow_surface_publishes_module_keyword_helpers_from_direct_cases or workflow_keyword_numeric_coercion_matches_cpython'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0896-module-workflow-module-sub-subn-bool-count-complement-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or benchmark-side selector logic in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached coercion-publication file.
- Keep the Python-path benchmark frontier unchanged here. The shared collection/replacement benchmark owner already times the adjacent module bool-count helper carriers, so this run should publish the missing correctness spellings without forking another benchmark family.

## Notes
- `RBR-0896` is the next available feature task id in the current checkout:
  - `RBR-0894` is already occupied by the ready feature task in `ops/tasks/ready/`;
  - `RBR-0895` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0894` on the same `module-workflow-surface` owner path so the next surviving follow-on reopens correctness through one bounded bool-count complement pair instead of broadening into the whole coercion matrix in one run.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier while the publication path still lacks the exact pair:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'workflow_keyword_numeric_coercion_matches_cpython and (module-sub-count-keyword-coercion or module-subn-count-keyword-coercion)'` passed in this run (`32 passed, 1195 deselected`), so no Rust or Python regex-behavior prerequisite is missing for the two exact bool-count spellings;
  - direct publication probes in this run confirmed `workflow-module-sub-count-bool-false-str` and `workflow-module-subn-count-bool-true-bytes` are still absent from `tests/conformance/fixtures/module_workflow_surface.py`, `tests/python/test_module_workflow_parity_suite.py`, `reports/correctness/latest.py`, and `reports/benchmarks/latest.py`;
  - the current owner path already publishes the adjacent `workflow-module-sub-count-bool-true-str` and `workflow-module-subn-count-bool-false-bytes` rows plus the exact `sub()` / `subn()` keyword and `__index__` neighbors, keeping this follow-on bounded to the missing bool complements rather than a new helper family; and
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and `reports/benchmarks/latest.py` already carry the adjacent `module-sub-count-bool-keyword-warm-str` and `module-subn-count-bool-keyword-purged-bytes` workloads on the shared collection/replacement owner path, so this task can stay correctness-only without inventing another benchmark manifest first.
- 2026-03-22 feature-implementation completed the bounded publication slice on the existing owner path:
  - added `workflow-module-sub-count-bool-false-str` and `workflow-module-subn-count-bool-true-bytes` to `tests/conformance/fixtures/module_workflow_surface.py`;
  - aligned the direct-case/publication assertions in `tests/python/test_module_workflow_parity_suite.py` and the representative-case coverage in `tests/conformance/test_combined_correctness_scorecards.py`;
  - republished `reports/correctness/latest.py`, which now records `1524` total / `1524` passed / `0` unimplemented cases across `114` manifests, with `module.workflow` at `150` total, `module.workflow.str` at `86`, `module.workflow.bytes` at `64`, `module.workflow.module_call` at `83`, and `module.workflow.pattern_call` unchanged at `55`; and
  - verified with the task-local keyword-helper pytest selector (`165 passed, 1067 deselected`), the narrowed module-workflow harness report (`150/150`), the published scorecard refresh (`1524/1524`), and the full direct gates (`1275 passed, 1 skipped, 2188 subtests passed`).
