# RBR-0788: Publish the module-workflow compiled-pattern keyword-error sextet

Status: done
Owner: feature-implementation
Created: 2026-03-20

## Goal
- Reopen the existing `module-workflow-surface` correctness frontier with the next adjacent compiled-pattern module keyword-error slice, publishing the exact duplicate-keyword and unexpected-keyword rejections for the existing `"abc"` and `b"abc"` compiled-pattern anchors before benchmark catch-up or another owner family reopens the queue.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only six new `module_call` rows:
  - add `workflow-module-split-duplicate-maxsplit-keyword-str-compiled-pattern`;
  - add `workflow-module-split-unexpected-keyword-bytes-compiled-pattern`;
  - add `workflow-module-sub-duplicate-count-keyword-str-compiled-pattern`;
  - add `workflow-module-sub-unexpected-keyword-str-compiled-pattern`;
  - add `workflow-module-subn-duplicate-count-keyword-bytes-compiled-pattern`;
  - add `workflow-module-subn-unexpected-keyword-bytes-compiled-pattern`;
  - keep all six rows pinned to the exact direct parity anchors already defined on the shared owner path in `COMPILED_PATTERN_MODULE_KEYWORD_ERROR_CASES`:
    - `compiled-pattern-split-duplicate-maxsplit-keyword-str`: `helper == "split"`, `pattern == "abc"`, `args == ("abc", 1)`, and `kwargs == {"maxsplit": 1}`;
    - `compiled-pattern-split-unexpected-keyword-bytes`: `helper == "split"`, `pattern == b"abc"`, `args == (b"abc",)`, and `kwargs == {"missing": 1}`;
    - `compiled-pattern-sub-duplicate-count-keyword-str`: `helper == "sub"`, `pattern == "abc"`, `args == ("x", "abc", 1)`, and `kwargs == {"count": 1}`;
    - `compiled-pattern-sub-unexpected-keyword-str`: `helper == "sub"`, `pattern == "abc"`, `args == ("x", "abc")`, and `kwargs == {"missing": 1}`;
    - `compiled-pattern-subn-duplicate-count-keyword-bytes`: `helper == "subn"`, `pattern == b"abc"`, `args == (b"x", b"abc", 1)`, and `kwargs == {"count": 1}`;
    - `compiled-pattern-subn-unexpected-keyword-bytes`: `helper == "subn"`, `pattern == b"abc"`, `args == (b"x", b"abc")`, and `kwargs == {"missing": 1}`;
  - keep the compiled-pattern routing explicit by setting `use_compiled_pattern` on all six rows;
  - keep the text-model split explicit: the `workflow-module-split-duplicate-maxsplit-keyword-str-compiled-pattern`, `workflow-module-sub-duplicate-count-keyword-str-compiled-pattern`, and `workflow-module-sub-unexpected-keyword-str-compiled-pattern` rows stay on `str`, while the `workflow-module-split-unexpected-keyword-bytes-compiled-pattern`, `workflow-module-subn-duplicate-count-keyword-bytes-compiled-pattern`, and `workflow-module-subn-unexpected-keyword-bytes-compiled-pattern` rows stay on `bytes`; and
  - do not broaden into benchmark manifests, benchmark reports, raw-module keyword-error rows, native-boundary scaffolding, or any new manifest in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another keyword-only manifest, detached selector table, or second compiled-pattern owner path:
  - update the bundle-contract expectations so `module-workflow-surface` now publishes `99` total rows instead of `93`;
  - update the owner-path text-model split so the bundle now expects `62` `str` rows and `37` `bytes` rows;
  - keep `pattern_call` expectations unchanged at `42` rows with the current helper breakdown;
  - update the shared `module_call` helper breakdown so the owner path now expects `6` `search` rows, `4` `match` rows, `5` `fullmatch` rows, `8` `split` rows, `1` `findall` row, `1` `finditer` row, `10` `sub` rows, `8` `subn` rows, and `2` `escape` rows;
  - extend the published compiled-pattern owner-path assertions so `PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES` now contains twenty-six rows, inserting the six new fixture ids adjacent to the existing compiled-pattern keyword rows so the published order becomes:
    - `workflow-module-search-str-compiled-pattern`
    - `workflow-module-match-str-compiled-pattern`
    - `workflow-module-search-str-bounded-wildcard-ignorecase-compiled-pattern`
    - `workflow-module-match-str-bounded-wildcard-compiled-pattern`
    - `workflow-module-fullmatch-str-bounded-wildcard-compiled-pattern`
    - `workflow-module-search-bytes-verbose-regression-compiled-pattern`
    - `workflow-module-fullmatch-bytes-verbose-regression-compiled-pattern`
    - `workflow-module-split-str-compiled-pattern`
    - `workflow-module-split-maxsplit-keyword-str-compiled-pattern`
    - `workflow-module-split-maxsplit-indexlike-bytes-compiled-pattern`
    - `workflow-module-split-duplicate-maxsplit-keyword-str-compiled-pattern`
    - `workflow-module-split-unexpected-keyword-bytes-compiled-pattern`
    - `workflow-module-findall-bytes-compiled-pattern`
    - `workflow-module-finditer-str-compiled-pattern`
    - `workflow-module-sub-str-compiled-pattern`
    - `workflow-module-sub-count-keyword-str-compiled-pattern`
    - `workflow-module-sub-count-indexlike-bytes-compiled-pattern`
    - `workflow-module-sub-duplicate-count-keyword-str-compiled-pattern`
    - `workflow-module-sub-unexpected-keyword-str-compiled-pattern`
    - `workflow-module-sub-str-compiled-pattern-on-bytes-string`
    - `workflow-module-subn-bytes-compiled-pattern`
    - `workflow-module-subn-count-keyword-bytes-compiled-pattern`
    - `workflow-module-subn-count-indexlike-str-compiled-pattern`
    - `workflow-module-subn-duplicate-count-keyword-bytes-compiled-pattern`
    - `workflow-module-subn-unexpected-keyword-bytes-compiled-pattern`
    - `workflow-module-subn-bytes-compiled-pattern-on-str-string`
  - extend the compiled-pattern direct-case alignment so the published direct-anchor sequence likewise becomes:
    - `compiled-pattern-search-str`
    - `compiled-pattern-match-str`
    - `compiled-module-search-ignorecase-bounded-hit`
    - `compiled-module-match-bounded-hit`
    - `compiled-module-fullmatch-bounded-hit`
    - `compiled-pattern-search-bytes-verbose-regression`
    - `compiled-pattern-fullmatch-bytes-verbose-regression`
    - `compiled-pattern-split-str-maxsplit`
    - `compiled-pattern-split-maxsplit-keyword-str`
    - `compiled-pattern-split-maxsplit-indexlike-bytes`
    - `compiled-pattern-split-duplicate-maxsplit-keyword-str`
    - `compiled-pattern-split-unexpected-keyword-bytes`
    - `compiled-pattern-findall-bytes`
    - `compiled-pattern-finditer-str`
    - `compiled-pattern-sub-str-count`
    - `compiled-pattern-sub-count-keyword-str`
    - `compiled-pattern-sub-count-indexlike-bytes`
    - `compiled-pattern-sub-duplicate-count-keyword-str`
    - `compiled-pattern-sub-unexpected-keyword-str`
    - `compiled-pattern-sub-str-on-bytes-string`
    - `compiled-pattern-subn-bytes-count`
    - `compiled-pattern-subn-count-keyword-bytes`
    - `compiled-pattern-subn-count-indexlike-str`
    - `compiled-pattern-subn-duplicate-count-keyword-bytes`
    - `compiled-pattern-subn-unexpected-keyword-bytes`
    - `compiled-pattern-subn-bytes-on-str-string`
  - extend the shared compiled-pattern publication contract so the six new rejection rows are matched through the existing normalized keyword-signature path instead of a detached keyword-error publication table; and
  - keep the published direct-test bucket coverage honest without restoring mirrored sidecars or inventing another owner path.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1463` total / `1463` passed / `0` `unimplemented` across `114` manifests to `1469` / `1469` / `0` across the same `114` manifests;
  - `module.workflow` moves from `93` / `93` / `0` to `99` / `99` / `0`;
  - `module.workflow.str` moves from `59` / `59` / `0` to `62` / `62` / `0`;
  - `module.workflow.bytes` moves from `34` / `34` / `0` to `37` / `37` / `0`;
  - `module.workflow.module_call` moves from `39` / `39` / `0` to `45` / `45` / `0`;
  - `module.workflow.pattern_call` stays `42` / `42` / `0`; and
  - at least one of the new compiled-pattern keyword-error rows is visible in the tracked scorecard as a representative `module-workflow-surface` compiled-pattern module-call case.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0788-module-workflow-compiled-pattern-keyword-error-sextet.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached compiled-pattern keyword-error publication file.

## Notes
- `RBR-0788` is the next available task id in the current checkout:
  - `ops/tasks/done/` currently runs through `RBR-0787`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` had no `feature-implementation` task at the start of this run; and
  - `rg -n '\\bRBR-0788\\b' ops/tasks ops/state/current_status.md ops/state/backlog.md` returned no active reservation for this id in this run.
- Queue this directly after `RBR-0786` on the same `module-workflow-surface` owner path. `RBR-0787` is architecture cleanup, so it does not change the feature frontier.
- 2026-03-20 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `tests/python/test_module_workflow_parity_suite.py` already carries the exact adjacent direct parity anchors `compiled-pattern-split-duplicate-maxsplit-keyword-str`, `compiled-pattern-sub-duplicate-count-keyword-str`, `compiled-pattern-subn-duplicate-count-keyword-bytes`, `compiled-pattern-split-unexpected-keyword-bytes`, `compiled-pattern-sub-unexpected-keyword-str`, and `compiled-pattern-subn-unexpected-keyword-bytes` in `COMPILED_PATTERN_MODULE_KEYWORD_ERROR_CASES`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_compiled_pattern_module_keyword_argument_calls_match_cpython tests/python/test_module_workflow_parity_suite.py::test_compiled_pattern_module_keyword_argument_errors_match_cpython` passed in this run (`24 passed`);
  - direct publication probes in this run confirmed the six `workflow-module-*-compiled-pattern` keyword-error ids above are still absent from `tests/conformance/fixtures/module_workflow_surface.py`, `tests/python/test_module_workflow_parity_suite.py`, `tests/conformance/test_combined_correctness_scorecards.py`, and `reports/correctness/latest.py`;
  - the current owner path already publishes the adjacent compiled-pattern keyword-call sextet plus the compiled-pattern wrong-text-model helper-error rows, leaving this compiled-pattern keyword-error sextet as the smallest unpublished neighbor on the same owner file;
  - no blocked feature task exists to reopen first; and
  - `ops/state/backlog.md` and the frontier prose in `ops/state/current_status.md` already honestly say that no ready feature follow-on survives after the likely same-cycle drain, so this one-task refill does not need a backlog-frontier prose change.

## Completion Notes
- 2026-03-20: Published the six compiled-pattern module keyword-error rows on `tests/conformance/fixtures/module_workflow_surface.py`, extended the shared owner-path parity assertions to the 26-row compiled-pattern publication order, and refreshed the combined representative-case list in `tests/conformance/test_combined_correctness_scorecards.py`.
- Republished `reports/correctness/latest.py`; the tracked artifact now reports `1469` total / `1469` passed / `0` unimplemented across `114` manifests, with `module.workflow` at `99/99/0`, `module.workflow.str` at `62/62/0`, `module.workflow.bytes` at `37/37/0`, `module.workflow.module_call` at `45/45/0`, and `module.workflow.pattern_call` unchanged at `42/42/0`.
- Verification passed:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0788-module-workflow-compiled-pattern-keyword-error-sextet.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`
