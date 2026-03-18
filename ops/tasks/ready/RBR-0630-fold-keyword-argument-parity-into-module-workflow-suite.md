# RBR-0630: Fold the detached keyword-argument parity suite into the module workflow suite

Status: ready
Owner: architecture-implementation
Created: 2026-03-18

## Goal
- Delete `tests/python/test_literal_keyword_argument_parity_suite.py` by moving its keyword-argument module and compiled-pattern helper coverage onto `tests/python/test_module_workflow_parity_suite.py`, so the Python-facing helper surface has one owner suite instead of a detached keyword-case file that repeats the same match/value/iterator parity ladders.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`
- Delete `tests/python/test_literal_keyword_argument_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` absorbs the keyword-argument coverage while preserving its current fixture-backed owner surface exactly:
  - keep the current `SELECTED_CASE_BUNDLE_SPECS`, `MODULE_WORKFLOW_DIRECT_TEST_CASE_ID_BUCKETS`, verbose compile workflows, compiled-pattern helper workflows, cache/purge workflows, and escape workflows unchanged; and
  - add the keyword-argument case tables and tests as one local owner-file surface instead of creating another helper module, registry, or sibling suite.
- The absorbed module-call keyword surface keeps exactly these six case ids in order and stays on the current module-helper parity ladder:
  - `module-search-flags-keyword-str`
  - `module-match-flags-keyword-bytes`
  - `module-fullmatch-flags-keyword-str`
  - `module-split-maxsplit-keyword-bytes`
  - `module-sub-count-keyword-str`
  - `module-subn-count-keyword-bytes`
  - preserve the current helper, positional-argument, keyword-argument, and `result_kind` payloads for all six rows instead of renaming or reinterpreting them.
- The absorbed compiled-pattern keyword surface keeps exactly these thirteen case ids in order and stays on the current compiled-pattern parity ladder:
  - `pattern-search-pos-keyword-str`
  - `pattern-search-bool-endpos-keyword-str`
  - `pattern-search-endpos-keyword-bytes`
  - `pattern-match-pos-keyword-str`
  - `pattern-match-bool-pos-keyword-str`
  - `pattern-fullmatch-window-keyword-bytes`
  - `pattern-findall-window-keyword-str`
  - `pattern-findall-bool-window-keyword-str`
  - `pattern-finditer-window-keyword-bytes`
  - `pattern-finditer-bool-window-keyword-bytes`
  - `pattern-split-maxsplit-keyword-str`
  - `pattern-sub-count-keyword-bytes`
  - `pattern-subn-count-keyword-str`
  - preserve the current helper, pattern payload, `kwargs`, optional compile flags, and `result_kind` payloads for all thirteen rows instead of turning this cleanup into a new keyword-argument matrix.
- The absorbed keyword-error surface keeps exactly these five case ids in order and continues comparing exception type plus args against CPython:
  - `module-search-duplicate-flags-keyword`
  - `module-split-duplicate-maxsplit-keyword`
  - `module-sub-duplicate-count-keyword`
  - `module-fullmatch-unexpected-keyword`
  - `module-sub-unexpected-keyword`
- The moved assertions stay on the current parity paths rather than inventing a second helper layer:
  - module-call cases still execute through a local `getattr(backend, case.helper)(*case.args, **case.kwargs)` path versus `re`;
  - compiled-pattern cases still compile through `compile_with_cpython_parity(...)` before dispatching `getattr(pattern, case.helper)(*case.args, **case.kwargs)`;
  - `match` results still use `assert_match_result_parity(..., check_regs=True)` plus `assert_match_convenience_api_parity(...)` when CPython returns a match;
  - iterator results still use `assert_finditer_parity(..., check_regs=True)`; and
  - non-match/non-iterator results and keyword-error cases still compare raw values or exception type/args directly against CPython.
- Keep the consolidation local and ordinary:
  - prefer one real owner suite with file-local dataclasses/helpers over another support module or import-only wrapper; and
  - do not leave `tests/python/test_literal_keyword_argument_parity_suite.py` behind as a forwarding shell.
- Keep scope structural only:
  - do not change correctness fixtures, benchmark files, reports, Rust code, `python/rebar/`, or the current fixture-backed module-workflow behavior; and
  - do not broaden this cleanup into `tests/python/test_literal_collection_helpers.py`, `tests/python/test_public_surface_parity_suite.py`, or `tests/python/test_module_surface_scaffold.py`.
- After the consolidation lands:
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from tests.python import test_module_workflow_parity_suite as mod

assert tuple(case.case_id for case in mod.MODULE_KEYWORD_CALL_CASES) == (
    "module-search-flags-keyword-str",
    "module-match-flags-keyword-bytes",
    "module-fullmatch-flags-keyword-str",
    "module-split-maxsplit-keyword-bytes",
    "module-sub-count-keyword-str",
    "module-subn-count-keyword-bytes",
)
assert tuple(case.case_id for case in mod.PATTERN_KEYWORD_CALL_CASES) == (
    "pattern-search-pos-keyword-str",
    "pattern-search-bool-endpos-keyword-str",
    "pattern-search-endpos-keyword-bytes",
    "pattern-match-pos-keyword-str",
    "pattern-match-bool-pos-keyword-str",
    "pattern-fullmatch-window-keyword-bytes",
    "pattern-findall-window-keyword-str",
    "pattern-findall-bool-window-keyword-str",
    "pattern-finditer-window-keyword-bytes",
    "pattern-finditer-bool-window-keyword-bytes",
    "pattern-split-maxsplit-keyword-str",
    "pattern-sub-count-keyword-bytes",
    "pattern-subn-count-keyword-str",
)
assert tuple(case.case_id for case in mod.MODULE_KEYWORD_ERROR_CASES) == (
    "module-search-duplicate-flags-keyword",
    "module-split-duplicate-maxsplit-keyword",
    "module-sub-duplicate-count-keyword",
    "module-fullmatch-unexpected-keyword",
    "module-sub-unexpected-keyword",
)
print("ok")
PY`
  - `bash -lc "! rg --files tests/python | rg 'test_literal_keyword_argument_parity_suite\\.py$'"`
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from tests.python import test_module_workflow_parity_suite as mod

assert tuple(case.case_id for case in mod.MODULE_KEYWORD_CALL_CASES) == (
    "module-search-flags-keyword-str",
    "module-match-flags-keyword-bytes",
    "module-fullmatch-flags-keyword-str",
    "module-split-maxsplit-keyword-bytes",
    "module-sub-count-keyword-str",
    "module-subn-count-keyword-bytes",
)
assert tuple(case.case_id for case in mod.PATTERN_KEYWORD_CALL_CASES) == (
    "pattern-search-pos-keyword-str",
    "pattern-search-bool-endpos-keyword-str",
    "pattern-search-endpos-keyword-bytes",
    "pattern-match-pos-keyword-str",
    "pattern-match-bool-pos-keyword-str",
    "pattern-fullmatch-window-keyword-bytes",
    "pattern-findall-window-keyword-str",
    "pattern-findall-bool-window-keyword-str",
    "pattern-finditer-window-keyword-bytes",
    "pattern-finditer-bool-window-keyword-bytes",
    "pattern-split-maxsplit-keyword-str",
    "pattern-sub-count-keyword-bytes",
    "pattern-subn-count-keyword-str",
)
assert tuple(case.case_id for case in mod.MODULE_KEYWORD_ERROR_CASES) == (
    "module-search-duplicate-flags-keyword",
    "module-split-duplicate-maxsplit-keyword",
    "module-sub-duplicate-count-keyword",
    "module-fullmatch-unexpected-keyword",
    "module-sub-unexpected-keyword",
)
print("ok")
PY`
  - `bash -lc "! rg --files tests/python | rg 'test_literal_keyword_argument_parity_suite\\.py$'"`

## Constraints
- Keep this cleanup structural only. Do not change backend behavior, fixture membership, helper semantics, keyword-argument payloads, exception messages, benchmark expectations, or reporting/state prose.
- Do not replace the deleted file with an import-only compatibility wrapper.
- Keep the keyword-argument rows explicit and local; do not turn this into a generated matrix or a new shared keyword-call support layer.

## Notes
- `RBR-0630` is the next available task id:
  - `rg -n "RBR-0630|RBR-0631|RBR-0632|RBR-0633" ops/state/backlog.md ops/state/current_status.md` returned no matches; and
  - `find ops/tasks -maxdepth 2 -type f | rg 'RBR-0630'` returned no matches before this file was added.
- No stale blocked architecture task needed normalization first, and rule 10 does not apply in the current checkout:
  - `ops/tasks/blocked/` and `ops/tasks/in_progress/` are empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the latest dashboard cycle shows both task workers finishing at `done`, so the shared queue is not currently bottlenecked by inherited-dirty or post-commit refresh churn.
- JSON burn-down remains complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining duplication is concrete and bounded in the current checkout:
  - `tests/python/test_literal_keyword_argument_parity_suite.py` is `308` lines and `tests/python/test_module_workflow_parity_suite.py` is `1054` lines;
  - `rg -n "test_literal_keyword_argument_parity_suite|MODULE_KEYWORD_CALL_CASES|PATTERN_KEYWORD_CALL_CASES|MODULE_KEYWORD_ERROR_CASES" tests/python ops/tasks ops/state` reports matches only inside `tests/python/test_literal_keyword_argument_parity_suite.py`, so no other suite depends on that file as an owner; and
  - `tests/python/test_module_workflow_parity_suite.py` already owns adjacent module and compiled-pattern helper parity through the same `match` / `value` / `iter` assertion ladders this detached keyword suite repeats.
- 2026-03-18 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_literal_keyword_argument_parity_suite.py tests/python/test_module_workflow_parity_suite.py` passes (`275 passed in 0.22s`);
  - the inline `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... PY` probe above currently fails exactly on this cleanup with `AttributeError: module 'tests.python.test_module_workflow_parity_suite' has no attribute 'MODULE_KEYWORD_CALL_CASES'`; and
  - `bash -lc "! rg --files tests/python | rg 'test_literal_keyword_argument_parity_suite\\.py$'"` currently fails exactly on this cleanup because the detached suite still exists.
