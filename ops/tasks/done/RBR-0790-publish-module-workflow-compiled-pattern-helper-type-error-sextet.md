# RBR-0790: Publish the module-workflow compiled-pattern helper type-error sextet

Status: done
Owner: feature-implementation
Created: 2026-03-20

## Goal
- Reopen the existing `module-workflow-surface` correctness frontier with the next adjacent compiled-pattern module helper type-error slice, publishing the exact mixed text-model `rebar.search`, `match`, `fullmatch`, `split`, `findall`, and `finditer` rejections for the existing `"abc"` and `b"abc"` compiled-pattern anchors before benchmark catch-up or another owner family reopens the queue.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only six new `module_call` rows:
  - add `workflow-module-search-str-compiled-pattern-on-bytes-string`;
  - add `workflow-module-match-bytes-compiled-pattern-on-str-string`;
  - add `workflow-module-fullmatch-str-compiled-pattern-on-bytes-string`;
  - add `workflow-module-split-str-compiled-pattern-on-bytes-string`;
  - add `workflow-module-findall-bytes-compiled-pattern-on-str-string`;
  - add `workflow-module-finditer-str-compiled-pattern-on-bytes-string`;
  - keep all six rows pinned to the exact direct parity anchors already defined on the shared owner path in `COMPILED_PATTERN_MODULE_HELPER_ERROR_CASES`:
    - `compiled-pattern-search-str-on-bytes-string`: `helper == "search"`, `pattern == "abc"`, and `args == (b"abc",)`;
    - `compiled-pattern-match-bytes-on-str-string`: `helper == "match"`, `pattern == b"abc"`, and `args == ("abc",)`;
    - `compiled-pattern-fullmatch-str-on-bytes-string`: `helper == "fullmatch"`, `pattern == "abc"`, and `args == (b"abc",)`;
    - `compiled-pattern-split-str-on-bytes-string`: `helper == "split"`, `pattern == "abc"`, and `args == (b"zabczz", 1)`;
    - `compiled-pattern-findall-bytes-on-str-string`: `helper == "findall"`, `pattern == b"abc"`, and `args == ("zabczz",)`;
    - `compiled-pattern-finditer-str-on-bytes-string`: `helper == "finditer"`, `pattern == "abc"`, and `args == (b"zabczz",)`;
  - keep the compiled-pattern routing explicit by setting `use_compiled_pattern` on all six rows;
  - keep the text-model split explicit: `workflow-module-search-str-compiled-pattern-on-bytes-string`, `workflow-module-fullmatch-str-compiled-pattern-on-bytes-string`, `workflow-module-split-str-compiled-pattern-on-bytes-string`, and `workflow-module-finditer-str-compiled-pattern-on-bytes-string` stay on `str`, while `workflow-module-match-bytes-compiled-pattern-on-str-string` and `workflow-module-findall-bytes-compiled-pattern-on-str-string` stay on `bytes`; and
  - do not broaden into compiled-pattern compile rows, benchmark manifests, benchmark reports, native-boundary scaffolding, or any new manifest in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another helper-error manifest, detached selector table, or second compiled-pattern owner path:
  - update the bundle-contract expectations so `module-workflow-surface` now publishes `105` total rows instead of `99`;
  - update the owner-path text-model split so the bundle now expects `66` `str` rows and `39` `bytes` rows;
  - keep `pattern_call` expectations unchanged at `42` rows with the current helper breakdown;
  - update the shared `module_call` helper breakdown so the owner path now expects `7` `search` rows, `5` `match` rows, `6` `fullmatch` rows, `9` `split` rows, `2` `findall` rows, `2` `finditer` rows, `10` `sub` rows, `8` `subn` rows, and `2` `escape` rows;
  - extend the published compiled-pattern owner-path assertions so `PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES` now contains thirty-two rows, inserting the six new fixture ids adjacent to the existing compiled-pattern helper groups:
    - insert `workflow-module-search-str-compiled-pattern-on-bytes-string` immediately after `workflow-module-search-str-compiled-pattern`;
    - insert `workflow-module-match-bytes-compiled-pattern-on-str-string` immediately after `workflow-module-match-str-compiled-pattern`;
    - insert `workflow-module-fullmatch-str-compiled-pattern-on-bytes-string` immediately after `workflow-module-fullmatch-str-bounded-wildcard-compiled-pattern`;
    - insert `workflow-module-split-str-compiled-pattern-on-bytes-string` immediately after `workflow-module-split-unexpected-keyword-bytes-compiled-pattern`;
    - insert `workflow-module-findall-bytes-compiled-pattern-on-str-string` immediately after `workflow-module-findall-bytes-compiled-pattern`;
    - insert `workflow-module-finditer-str-compiled-pattern-on-bytes-string` immediately after `workflow-module-finditer-str-compiled-pattern`;
  - extend the compiled-pattern direct-case alignment so the published direct-anchor sequence likewise inserts:
    - `compiled-pattern-search-str-on-bytes-string` immediately after `compiled-pattern-search-str`;
    - `compiled-pattern-match-bytes-on-str-string` immediately after `compiled-pattern-match-str`;
    - `compiled-pattern-fullmatch-str-on-bytes-string` immediately after `compiled-module-fullmatch-bounded-hit`;
    - `compiled-pattern-split-str-on-bytes-string` immediately after `compiled-pattern-split-unexpected-keyword-bytes`;
    - `compiled-pattern-findall-bytes-on-str-string` immediately after `compiled-pattern-findall-bytes`;
    - `compiled-pattern-finditer-str-on-bytes-string` immediately after `compiled-pattern-finditer-str`;
  - keep the shared compiled-pattern publication contract on the existing direct-case alignment path instead of inventing another helper-error selector; and
  - keep the already published compiled-pattern `sub` / `subn` wrong-text-model rows, raw-module keyword-error rows, pattern keyword rows, and benchmark-oriented assertions unchanged in this run.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1469` total / `1469` passed / `0` `unimplemented` across `114` manifests to `1475` / `1475` / `0` across the same `114` manifests;
  - `module.workflow` moves from `99` / `99` / `0` to `105` / `105` / `0`;
  - `module.workflow.str` moves from `62` / `62` / `0` to `66` / `66` / `0`;
  - `module.workflow.bytes` moves from `37` / `37` / `0` to `39` / `39` / `0`;
  - `module.workflow.module_call` moves from `45` / `45` / `0` to `51` / `51` / `0`;
  - `module.workflow.pattern_call` stays `42` / `42` / `0`; and
  - at least one of the new compiled-pattern mixed-text-model helper-error rows is visible in the tracked scorecard as a representative `module-workflow-surface` compiled-pattern module-call case.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0790-module-workflow-compiled-pattern-helper-type-error-sextet.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached compiled-pattern helper-error publication file.

## Notes
- `RBR-0790` is the next available task id in the current checkout:
  - `ops/tasks/done/` currently runs through `RBR-0789`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` had no `feature-implementation` task at the start of this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done -maxdepth 1 -type f -printf '%f\n' | rg '^RBR-0790|^RBR-0791|^RBR-0792'` returned no matches.
- Queue this directly after `RBR-0788` on the same `module-workflow-surface` owner path. `RBR-0789` is architecture cleanup, so it does not change the feature frontier.
- 2026-03-20 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `tests/python/test_module_workflow_parity_suite.py` already carries the exact adjacent direct parity anchors `compiled-pattern-search-str-on-bytes-string`, `compiled-pattern-match-bytes-on-str-string`, `compiled-pattern-fullmatch-str-on-bytes-string`, `compiled-pattern-split-str-on-bytes-string`, `compiled-pattern-findall-bytes-on-str-string`, and `compiled-pattern-finditer-str-on-bytes-string` in `COMPILED_PATTERN_MODULE_HELPER_ERROR_CASES`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_module_helpers_preserve_compiled_pattern_type_errors_like_cpython` passed in this run (`16 passed in 0.10s`);
  - direct publication probes in this run confirmed the six `workflow-module-*-compiled-pattern-on-*-string` ids above are still absent from `tests/conformance/fixtures/module_workflow_surface.py`, `tests/python/test_module_workflow_parity_suite.py`, `tests/conformance/test_combined_correctness_scorecards.py`, and `reports/correctness/latest.py`;
  - the current owner path already publishes the adjacent compiled-pattern `sub` / `subn` wrong-text-model rows, leaving this search/match/fullmatch/split/findall/finditer sextet as the smallest unpublished neighbor on the same owner file;
  - no blocked feature task exists to reopen first; and
  - `ops/state/backlog.md` and the frontier prose in `ops/state/current_status.md` already honestly say that no ready feature follow-on survives after the likely same-cycle drain, so this one-task refill does not need a backlog-frontier prose change.

## Completion Notes
- 2026-03-20: Published the six compiled-pattern mixed text-model helper TypeError rows on `tests/conformance/fixtures/module_workflow_surface.py`, extended the shared owner-path parity assertions to the 32-row compiled-pattern publication order, and refreshed the combined representative-case list in `tests/conformance/test_combined_correctness_scorecards.py`.
- Republished `reports/correctness/latest.py`; the tracked artifact now reports `1475` total / `1475` passed / `0` unimplemented across `114` manifests, with `module.workflow` at `105/105/0`, `module.workflow.str` at `66/66/0`, `module.workflow.bytes` at `39/39/0`, `module.workflow.module_call` at `51/51/0`, and `module.workflow.pattern_call` unchanged at `42/42/0`. The tracked report includes the new representative row `workflow-module-search-str-compiled-pattern-on-bytes-string`.
- Verification passed:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_module_helpers_preserve_compiled_pattern_type_errors_like_cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0790-module-workflow-compiled-pattern-helper-type-error-sextet.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`
