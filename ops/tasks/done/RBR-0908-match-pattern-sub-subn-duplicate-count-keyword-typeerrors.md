# RBR-0908: Match direct `Pattern.sub()` / `Pattern.subn()` duplicate `count=` keyword `TypeError`s

Status: done
Owner: feature-implementation
Created: 2026-03-22
Completed: 2026-03-22

## Goal
- Land the missing CPython-compatible duplicate-`count=` `TypeError` behavior for the exact direct `Pattern.sub()` / `Pattern.subn()` pair adjacent to `RBR-0906`, so the next correctness-publication slice can reuse the existing direct bound-pattern replacement owner path instead of publishing against mismatched diagnostics.

## Pattern Pair
- `re.compile("abc").sub("x", "abc", 1, count=1)`
- `re.compile(b"abc").subn(b"x", b"abc", 1, count=1)`

## Deliverables
- `python/rebar/__init__.py`
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `python/rebar/__init__.py` stops relying on Python's default method-signature binder for this exact duplicate-`count=` slice, so direct bound-pattern replacement calls match CPython instead of surfacing rebar-specific argument-binding text:
  - `rebar.compile("abc").sub("x", "abc", 1, count=1)` raises `TypeError` with `args == ("sub() takes at most 3 arguments (4 given)",)`;
  - `rebar.compile(b"abc").subn(b"x", b"abc", 1, count=1)` raises `TypeError` with `args == ("subn() takes at most 3 arguments (4 given)",)`;
  - keep the already-landed direct `Pattern.sub()` / `Pattern.subn()` literal success paths unchanged for the default, integer, `__index__`, and bool `count=` carriers on the shared owner path; and
  - do not widen into unexpected-keyword parity, `Pattern.split()` duplicate `maxsplit=` parity, raw-module helper diagnostics, compiled-pattern-first-argument module helpers, correctness-publication files, or benchmark/report regeneration in this run.
- `tests/python/test_module_workflow_parity_suite.py` covers the exact direct bound-pattern duplicate-`count=` pair on the existing module-workflow parity owner path instead of creating a detached regression harness:
  - add focused direct parity cases `pattern-sub-duplicate-count-keyword-str` and `pattern-subn-duplicate-count-keyword-bytes` for the exact calls above;
  - teach the shared bound-pattern error invocation path to carry keyword arguments for this slice while keeping the existing wrong-text-model error cases intact;
  - assert exception type and `args` match CPython for both new direct cases; and
  - keep the compiled-pattern module-helper duplicate keyword cases and all published module-workflow fixture inventories unchanged in this run.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-sub-duplicate-count-keyword-str or pattern-subn-duplicate-count-keyword-bytes'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'bound_pattern_helper_type_errors_match_cpython'`

## Constraints
- Keep this task implementation-parity only. Do not publish the direct `Pattern` duplicate-keyword cases into `tests/conformance/fixtures/module_workflow_surface.py`, `tests/conformance/test_combined_correctness_scorecards.py`, `reports/correctness/latest.py`, benchmark manifests, or `reports/benchmarks/latest.py` in this run.
- Reuse the existing direct bound-pattern owner path in `tests/python/test_module_workflow_parity_suite.py`. Do not create another parity suite, a one-off probe script, or a detached argument-binding helper module.
- Keep the scope pinned to the duplicate-`count=` replacement pair above. Leave direct bound-pattern unexpected-keyword parity and `split()` duplicate-`maxsplit=` parity for follow-on tasks.

## Notes
- `RBR-0908` is the next available feature task id in the current checkout:
  - `RBR-0906` is already occupied by the ready feature task in `ops/tasks/ready/`;
  - `RBR-0907` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first.
- Queue this directly after `RBR-0906` on the same direct bound-pattern replacement frontier so the next surviving follow-on fixes the underlying `Pattern.sub()` / `Pattern.subn()` duplicate-keyword parity gap before correctness publication or benchmark catch-up tries to expose it.
- 2026-03-22 feature-planning probes confirm this is an implementation prerequisite, not a publication-only slice:
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... re.compile("abc").sub("x", "abc", 1, count=1) ... re.compile(b"abc").subn(b"x", b"abc", 1, count=1) ... PY` showed CPython and `rebar` still disagree on the exact errors in this run: CPython raises `("sub() takes at most 3 arguments (4 given)",)` / `("subn() takes at most 3 arguments (4 given)",)`, while `rebar` currently raises `("Pattern.sub() got multiple values for argument 'count'",)` / `("Pattern.subn() got multiple values for argument 'count'",)`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'compiled-pattern-sub-duplicate-count-keyword-str or compiled-pattern-subn-duplicate-count-keyword-bytes or compiled-pattern-sub-unexpected-keyword-str or compiled-pattern-subn-unexpected-keyword-bytes'` passed in this run (`8 passed, 1234 deselected`), so the adjacent compiled-pattern-first-argument owner path is already green and does not need to be reopened here;
  - direct publication probes in this run confirmed there are still no `workflow-pattern-sub-duplicate-...` or `workflow-pattern-subn-duplicate-...` correctness rows and no direct bound-pattern duplicate-keyword benchmark rows, so publication and benchmark follow-ons should wait until this behavior matches CPython first; and
  - `python/rebar/__init__.py` currently defines `Pattern.sub()` / `Pattern.subn()` with fixed Python signatures, which is why Python-level argument binding leaks the wrong duplicate-keyword diagnostics before the shared replacement logic runs.

## Completion
- Patched `python/rebar/__init__.py` so direct bound `Pattern.sub()` / `Pattern.subn()` calls resolve `count` through a tiny manual argument shim before the replacement logic runs, producing CPython-matching duplicate-`count=` `TypeError.args` for the exact direct `sub()` / `subn()` pair while leaving the existing success-path replacement execution intact.
- Extended `tests/python/test_module_workflow_parity_suite.py` on the shared bound-pattern error owner path by teaching `PatternHelperErrorCase` and `_invoke_bound_pattern_helper(...)` to carry keyword arguments, then added `pattern-sub-duplicate-count-keyword-str` and `pattern-subn-duplicate-count-keyword-bytes`.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern-sub-duplicate-count-keyword-str or pattern-subn-duplicate-count-keyword-bytes'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'bound_pattern_helper_type_errors_match_cpython'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'compiled-pattern-sub-duplicate-count-keyword-str or compiled-pattern-subn-duplicate-count-keyword-bytes'`
- Published correctness and benchmark artifacts were intentionally left unchanged in this run; `reports/correctness/latest.py` and `reports/benchmarks/latest.py` were not regenerated.
