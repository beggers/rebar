# RBR-0921: Match direct `Pattern.split()` duplicate-`maxsplit=` / unexpected-keyword `TypeError`s

Status: ready
Owner: feature-implementation
Created: 2026-03-22

## Goal
- Land the missing CPython-compatible duplicate-`maxsplit=` and unexpected-keyword `TypeError` behavior for the exact direct `Pattern.split()` pair adjacent to the landed `sub()` / `subn()` keyword-error slice, so the next correctness-publication step can reuse the existing direct bound-pattern split owner path instead of publishing against mismatched diagnostics.

## Pattern Pair
- `re.compile("abc").split("abcabc", 1, maxsplit=1)`
- `re.compile(b"abc").split(b"abcabc", missing=1)`

## Deliverables
- `python/rebar/__init__.py`
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `python/rebar/__init__.py` stops leaking rebar-specific direct bound-pattern `split()` binder text for this exact slice, so direct `Pattern.split()` calls match CPython instead of surfacing `Pattern.split() got ...` diagnostics:
  - `rebar.compile("abc").split("abcabc", 1, maxsplit=1)` raises `TypeError` with `args == ("split() takes at most 2 arguments (3 given)",)`;
  - `rebar.compile(b"abc").split(b"abcabc", missing=1)` raises `TypeError` with `args == ("'missing' is an invalid keyword argument for split()",)`;
  - keep the already-landed direct `Pattern.split()` literal success paths unchanged for the default, integer, `__index__`, and bool `maxsplit=` carriers on the shared owner path; and
  - do not widen into direct `Pattern.sub()` / `Pattern.subn()` keyword handling, raw-module helper diagnostics, compiled-pattern-first-argument module helpers, correctness-publication files, or benchmark/report regeneration in this run.
- `tests/python/test_module_workflow_parity_suite.py` covers the exact direct bound-pattern split keyword-error pair on the existing module-workflow parity owner path instead of creating a detached regression harness:
  - add focused direct parity cases `pattern-split-duplicate-maxsplit-keyword-str` and `pattern-split-unexpected-keyword-bytes` for the exact calls above;
  - reuse the shared bound-pattern error invocation path that already carries keyword arguments for adjacent `Pattern.sub()` / `Pattern.subn()` keyword-error cases instead of introducing another one-off helper;
  - assert exception type and `args` match CPython for both new direct cases; and
  - keep the compiled-pattern module-helper split keyword-error cases and all published module-workflow fixture inventories unchanged in this run.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-split-duplicate-maxsplit-keyword-str or pattern-split-unexpected-keyword-bytes'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'bound_pattern_helper_type_errors_match_cpython'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'compiled-pattern-split-duplicate-maxsplit-keyword-str or compiled-pattern-split-unexpected-keyword-bytes'`

## Constraints
- Keep this task implementation-parity only. Do not publish the direct `Pattern.split()` cases into `tests/conformance/fixtures/module_workflow_surface.py`, `tests/conformance/test_combined_correctness_scorecards.py`, `reports/correctness/latest.py`, benchmark manifests, or `reports/benchmarks/latest.py` in this run.
- Reuse the existing direct bound-pattern owner path in `tests/python/test_module_workflow_parity_suite.py`. Do not create another parity suite, a one-off probe script, or a detached argument-binding helper module.
- Keep the scope pinned to the duplicate-`maxsplit=` / unexpected-keyword `split()` pair above. Leave direct bound-pattern split correctness publication and Python-path benchmark catch-up for follow-on tasks.

## Notes
- `RBR-0921` is the next available feature task id in the current checkout:
  - `RBR-0919` is already occupied by the latest done feature task on this frontier;
  - `RBR-0920` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0919` on the same shared direct bound-pattern collection/replacement frontier so the next surviving follow-on can publish and then benchmark the exact direct `Pattern.split()` keyword-error pair instead of widening into another helper family first.
- 2026-03-22 feature-planning probes confirm this is an implementation prerequisite, not a publication-only slice:
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... re.compile("abc").split("abcabc", 1, maxsplit=1) ... re.compile(b"abc").split(b"abcabc", missing=1) ... PY` showed CPython and `rebar` still disagree on the exact direct errors in this run: CPython raises `("split() takes at most 2 arguments (3 given)",)` and `("'missing' is an invalid keyword argument for split()",)`, while `rebar` currently raises `("Pattern.split() got multiple values for argument 'maxsplit'",)` and `("Pattern.split() got an unexpected keyword argument 'missing'",)`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'compiled-pattern-split-duplicate-maxsplit-keyword-str or compiled-pattern-split-unexpected-keyword-bytes'` currently passes in this checkout (`4 passed, 1335 deselected`), so the adjacent compiled-pattern-first-argument owner path is already green and does not need to be reopened here; and
  - `rg -n "pattern-split-duplicate-maxsplit|pattern-split-unexpected-keyword|workflow-pattern-split-duplicate-maxsplit|workflow-pattern-split-unexpected-keyword" tests/python/test_module_workflow_parity_suite.py tests/conformance/fixtures/module_workflow_surface.py reports/correctness/latest.py benchmarks/workloads/collection_replacement_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/benchmarks/latest.py` returned only compiled-pattern/module-helper rows in this run, so direct `Pattern.split()` publication and benchmark rows are still absent and should wait until this exact parity gap is closed.
