# RBR-0914: Match direct `Pattern.sub()` / `Pattern.subn()` unexpected-keyword `TypeError`s

Status: ready
Owner: feature-implementation
Created: 2026-03-22

## Goal
- Land the missing CPython-compatible unexpected-keyword `TypeError` behavior for the exact direct `Pattern.sub()` / `Pattern.subn()` pair adjacent to `RBR-0912`, so the next correctness-publication slice can reuse the existing direct bound-pattern replacement owner path instead of publishing against mismatched diagnostics.

## Pattern Pair
- `re.compile("abc").sub("x", "abc", missing=1)`
- `re.compile(b"abc").subn(b"x", b"abc", missing=1)`

## Deliverables
- `python/rebar/__init__.py`
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `python/rebar/__init__.py` stops leaking rebar-specific unexpected-keyword binder text for this exact direct bound-pattern replacement slice, so direct `Pattern.sub()` / `Pattern.subn()` calls match CPython instead of surfacing `Pattern.sub()` / `Pattern.subn()`-prefixed diagnostics:
  - `rebar.compile("abc").sub("x", "abc", missing=1)` raises `TypeError` with `args == ("'missing' is an invalid keyword argument for sub()",)`;
  - `rebar.compile(b"abc").subn(b"x", b"abc", missing=1)` raises `TypeError` with `args == ("'missing' is an invalid keyword argument for subn()",)`;
  - keep the already-landed direct `Pattern.sub()` / `Pattern.subn()` literal success paths unchanged for the default, integer, `__index__`, and bool `count=` carriers on the shared owner path; and
  - do not widen into direct `Pattern.split()` duplicate-`maxsplit=` parity, raw-module helper diagnostics, compiled-pattern-first-argument module helpers, correctness-publication files, or benchmark/report regeneration in this run.
- `tests/python/test_module_workflow_parity_suite.py` covers the exact direct bound-pattern unexpected-keyword pair on the existing module-workflow parity owner path instead of creating a detached regression harness:
  - add focused direct parity cases `pattern-sub-unexpected-keyword-str` and `pattern-subn-unexpected-keyword-bytes` for the exact calls above;
  - reuse the shared bound-pattern error invocation path that already carries keyword arguments for the duplicate-`count=` slice instead of introducing another one-off helper;
  - assert exception type and `args` match CPython for both new direct cases; and
  - keep the compiled-pattern module-helper unexpected-keyword cases and all published module-workflow fixture inventories unchanged in this run.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-sub-unexpected-keyword-str or pattern-subn-unexpected-keyword-bytes'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'bound_pattern_helper_type_errors_match_cpython'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'compiled-pattern-sub-unexpected-keyword-str or compiled-pattern-subn-unexpected-keyword-bytes'`

## Constraints
- Keep this task implementation-parity only. Do not publish the direct `Pattern` unexpected-keyword cases into `tests/conformance/fixtures/module_workflow_surface.py`, `tests/conformance/test_combined_correctness_scorecards.py`, `reports/correctness/latest.py`, benchmark manifests, or `reports/benchmarks/latest.py` in this run.
- Reuse the existing direct bound-pattern owner path in `tests/python/test_module_workflow_parity_suite.py`. Do not create another parity suite, a one-off probe script, or a detached argument-binding helper module.
- Keep the scope pinned to the unexpected-keyword replacement pair above. Leave direct bound-pattern `split()` duplicate-`maxsplit=` parity and any correctness/benchmark publication follow-ons for later tasks.

## Notes
- `RBR-0914` is the next available feature task id in the current checkout:
  - `RBR-0912` is already occupied by the latest done feature task on this frontier;
  - `RBR-0913` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0912` on the same direct bound-pattern replacement frontier so the next surviving follow-on fixes the underlying `Pattern.sub()` / `Pattern.subn()` unexpected-keyword parity gap before correctness publication or benchmark catch-up tries to expose it.
- 2026-03-22 feature-planning probes confirm this is an implementation prerequisite, not a publication-only slice:
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... re.compile("abc").sub("x", "abc", missing=1) ... re.compile(b"abc").subn(b"x", b"abc", missing=1) ... PY` showed CPython and `rebar` still disagree on the exact errors in this run: CPython raises `("'missing' is an invalid keyword argument for sub()",)` / `("'missing' is an invalid keyword argument for subn()",)`, while `rebar` currently raises `("Pattern.sub() got an unexpected keyword argument 'missing'",)` / `("Pattern.subn() got an unexpected keyword argument 'missing'",)`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'compiled-pattern-sub-unexpected-keyword-str or compiled-pattern-subn-unexpected-keyword-bytes'` passed in this run (`4 passed, 1307 deselected`), so the adjacent compiled-pattern-first-argument owner path is already green and does not need to be reopened here;
  - direct publication probes in this run confirmed there are still no `pattern-sub-unexpected-keyword-...`, `pattern-subn-unexpected-keyword-...`, `workflow-pattern-sub-unexpected-keyword-...`, or `workflow-pattern-subn-unexpected-keyword-...` cases in the live correctness or benchmark publications, so publication and benchmark follow-ons should wait until this behavior matches CPython first; and
  - `python/rebar/__init__.py` still defines `Pattern.sub()` / `Pattern.subn()` with fixed Python signatures, which is why Python-level argument binding still leaks the wrong unexpected-keyword diagnostics before the shared replacement logic runs.
