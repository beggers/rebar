# RBR-0898: Publish the module-workflow compiled-pattern module `sub()`/`subn()` bool-count complement pair

Status: done
Owner: feature-implementation
Created: 2026-03-22
Completed: 2026-03-22

## Goal
- Reopen the existing `module-workflow-surface` correctness frontier after `RBR-0896` by publishing the adjacent compiled-pattern module-level bool-count complement pair that the current runtime already executes with CPython parity, while leaving the Python-path benchmark frontier unchanged in this run because the shared collection/replacement benchmark owner already times the adjacent compiled-pattern module `sub()` / `subn()` bool keyword carriers on the same route.

## Pattern Pair
- `re.sub(re.compile("abc"), "x", "abcabc", count=False)`
- `re.subn(re.compile(b"abc"), b"x", b"abcabc", count=True)`

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared compiled-pattern module-helper owner path without another fixture file, detached coercion manifest, or benchmark-side churn:
  - extend `COMPILED_PATTERN_MODULE_KEYWORD_CALL_CASES` by exactly two direct cases:
    - `compiled-pattern-sub-count-bool-false-str`
    - `compiled-pattern-subn-count-bool-true-bytes`
  - pin those direct cases to the exact existing bounded compiled-pattern module bool-count anchors:
    - `compiled-pattern-sub-count-bool-false-str` uses `helper == "sub"`, `pattern == "abc"`, `args == ("x", "abcabc")`, and `kwargs == {"count": False}`;
    - `compiled-pattern-subn-count-bool-true-bytes` uses `helper == "subn"`, `pattern == b"abc"`, `args == (b"x", b"abcabc")`, and `kwargs == {"count": True}`;
  - extend the published compiled-pattern module-helper expectations by exactly two rows:
    - `workflow-module-sub-count-bool-false-str-compiled-pattern`
    - `workflow-module-subn-count-bool-true-bytes-compiled-pattern`
  - insert `workflow-module-sub-count-bool-false-str-compiled-pattern` immediately after `workflow-module-sub-count-bool-true-str-compiled-pattern` and immediately before `workflow-module-sub-duplicate-count-keyword-str-compiled-pattern`;
  - insert `workflow-module-subn-count-bool-true-bytes-compiled-pattern` immediately after `workflow-module-subn-count-bool-false-bytes-compiled-pattern` and immediately before `workflow-module-subn-duplicate-count-keyword-bytes-compiled-pattern`;
  - update `PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES` from `56` rows to `58`, with the text-model split moving from `30` `str` / `26` `bytes` to `31` / `27`;
  - update the compiled-pattern module-helper breakdown from `compile: 20`, `search: 4`, `match: 3`, `fullmatch: 4`, `split: 7`, `findall: 2`, `finditer: 2`, `sub: 7`, `subn: 7` to `compile: 20`, `search: 4`, `match: 3`, `fullmatch: 4`, `split: 7`, `findall: 2`, `finditer: 2`, `sub: 8`, `subn: 8`;
  - update the shared `module-workflow-surface` bundle expectations from `150` total rows to `152`, with the text-model split moving from `86` `str` / `64` `bytes` to `87` / `65`;
  - keep `pattern_call` expectations unchanged at `55` rows;
  - keep the raw module-keyword and positional-indexlike helper slices unchanged in this run; and
  - move the `module_call` helper totals from `83` rows with `sub: 14` / `subn: 12` to `85` rows with `sub: 15` / `subn: 13`.
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by exactly two new compiled-pattern `module_call` rows:
  - add `workflow-module-sub-count-bool-false-str-compiled-pattern`;
  - add `workflow-module-subn-count-bool-true-bytes-compiled-pattern`;
  - keep both rows on the existing compiled-pattern module-helper route with `use_compiled_pattern == True`, no positional pattern argument, and explicit bool-valued `kwargs["count"]`;
  - keep the `sub()` row on the `str` text model and the `subn()` row on the `bytes` text model to match the existing owner-path split;
  - categorize both rows under `["workflow", ..., "literal", "keyword", ..., "count", "bool", ..., "compiled-pattern"]`; and
  - keep the notes explicit that these are the bool-count complement spellings adjacent to the already published compiled-pattern `count=True` `sub()` row and `count=False` `subn()` row, not a broader compiled-pattern keyword dump.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1524` total / `1524` passed / `0` `unimplemented` across `114` manifests to `1526` / `1526` / `0` across the same `114` manifests;
  - `module.workflow` moves from `150` / `150` / `0` to `152` / `152` / `0`;
  - `module.workflow.str` moves from `86` / `86` / `0` to `87` / `87` / `0`;
  - `module.workflow.bytes` moves from `64` / `64` / `0` to `65` / `65` / `0`;
  - `module.workflow.module_call` moves from `83` / `83` / `0` to `85` / `85` / `0`;
  - `module.workflow.pattern_call` stays `55` / `55` / `0`; and
  - the two new compiled-pattern bool-count rows are visible in the tracked scorecard as representative `module-workflow-surface` module-call cases.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'compiled-pattern-sub-count-bool-false-str or compiled-pattern-subn-count-bool-true-bytes or module_workflow_surface_publishes_compiled_pattern_module_helpers_from_direct_cases or compiled_pattern_module_keyword_argument_calls_match_cpython'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0898-module-workflow-compiled-pattern-module-sub-subn-bool-count-complement-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or benchmark-side selector logic in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached compiled-pattern publication file.
- Keep the Python-path benchmark frontier unchanged here. The shared collection/replacement benchmark owner already times the adjacent compiled-pattern bool-count helper carriers, so this run should publish the missing complement spellings without forking another benchmark family.
- Assume `RBR-0896` has already landed the raw module bool-count complement pair; if it has not, stop and finish `RBR-0896` first instead of mixing raw and compiled-pattern bool complements in one run.

## Notes
- `RBR-0898` is the next available feature task id in the current checkout:
  - `RBR-0896` is already occupied by the ready feature task in `ops/tasks/ready/`;
  - `RBR-0897` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0896` on the same `module-workflow-surface` owner path so the next surviving follow-on reopens correctness through one bounded compiled-pattern bool-count complement pair instead of broadening into the whole compiled-pattern keyword matrix in one run.
- 2026-03-22 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier while the publication path still lacks the exact pair:
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... rebar.sub(rebar.compile(\"abc\"), \"x\", \"abcabc\", count=False) ... rebar.subn(rebar.compile(b\"abc\"), b\"x\", b\"abcabc\", count=True) ... PY` matched stdlib `re` for both exact calls in this run;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'compiled_pattern_module_keyword_argument_calls_match_cpython and (sub-count-bool-true-str or subn-count-bool-false-bytes)'` passed in this run (`4 passed, 1228 deselected`), so no Rust or Python regex-behavior prerequisite is missing for the adjacent compiled-pattern bool keyword owner path;
  - direct publication probes in this run confirmed the published fixture/report pair still lacked `workflow-module-sub-count-bool-false-str-compiled-pattern` and `workflow-module-subn-count-bool-true-bytes-compiled-pattern`, while `compiled-pattern-sub-count-bool-false-str` and `compiled-pattern-subn-count-bool-true-bytes` were already present on the direct owner path in `tests/python/test_module_workflow_parity_suite.py`; and
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and `reports/benchmarks/latest.py` already carry the adjacent `module-sub-count-bool-keyword-warm-str-compiled-pattern` and `module-subn-count-bool-keyword-purged-bytes-compiled-pattern` workloads on the shared collection/replacement owner path, so this task can stay correctness-only without inventing another benchmark manifest first.

## Completion
- Added the two missing compiled-pattern `module_call` publication rows to `tests/conformance/fixtures/module_workflow_surface.py` in the required order: `workflow-module-sub-count-bool-false-str-compiled-pattern` and `workflow-module-subn-count-bool-true-bytes-compiled-pattern`.
- Updated `tests/python/test_module_workflow_parity_suite.py` so the published compiled-pattern module-helper assertions now cover the 58-row compiled-pattern subset, the 152-row `module-workflow-surface` bundle, and the 85-row `module_call` slice; the direct bool-count owner-path cases were already present when this run started, so this run only had to publish the missing fixture/report half of the pair.
- Updated `tests/conformance/test_combined_correctness_scorecards.py` so the combined tracked scorecard now treats both new compiled-pattern rows as representative `module-workflow-surface` module-call cases.
- Regenerated `reports/correctness/latest.py`; the tracked artifact now reports `1526` total / `1526` passed / `0` unimplemented across `114` manifests, with `module.workflow` at `152`, `module.workflow.str` at `87`, `module.workflow.bytes` at `65`, `module.workflow.module_call` at `85`, and `module.workflow.pattern_call` unchanged at `55`.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'compiled-pattern-sub-count-bool-false-str or compiled-pattern-subn-count-bool-true-bytes or module_workflow_surface_publishes_compiled_pattern_module_helpers_from_direct_cases or compiled_pattern_module_keyword_argument_calls_match_cpython'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0898-module-workflow-compiled-pattern-module-sub-subn-bool-count-complement-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`
