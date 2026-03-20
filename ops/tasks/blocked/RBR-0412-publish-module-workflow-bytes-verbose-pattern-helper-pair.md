# RBR-0412: Publish the module-workflow bytes verbose pattern-helper pair

Status: blocked
Owner: feature-implementation
Created: 2026-03-20

## Goal
- Reopen the module-workflow correctness frontier with the positive `bytes` compiled-pattern `search()` / `fullmatch()` verbose regression helper pair, so the just-finished `str` verbose helper table rolls forward on the same owner path before bytes miss-path rows, multiline-only helper variants, or another module-workflow branch broadens this family.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only two new `pattern_call` rows:
  - add `workflow-pattern-search-bytes-verbose-regression` and `workflow-pattern-fullmatch-bytes-verbose-regression` beside the finished `str` verbose helper rows;
  - keep the exact shared verbose regression pattern anchored to the existing module-workflow compile family instead of inventing another pattern family:
    - `pattern == "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $"`;
    - `flags == 72` (`MULTILINE | VERBOSE`);
    - `text_model == "bytes"` for both new rows;
    - `helper == "search"` with `args == [{"type": "bytes", "encoding": "latin-1", "value": "prefix\\nENV_VAR=ABCD\\nsuffix"}]` for `workflow-pattern-search-bytes-verbose-regression`; and
    - `helper == "fullmatch"` with `args == [{"type": "bytes", "encoding": "latin-1", "value": "ENV_VAR = 123"}]` for `workflow-pattern-fullmatch-bytes-verbose-regression`;
  - keep these rows pinned to the existing positive verbose regression spellings already exercised on the owner path instead of adding a detached bytes-only scenario table; and
  - do not broaden into bytes miss-path rows, multiline-only helper variants, module-helper rows, cache-state variants, or another workflow family in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without forking another verbose-specific suite:
  - update the bundle-contract expectations, selected case-id inventory, and operation/helper counts so `module-workflow-surface` now publishes `23` total rows instead of `21`;
  - update the pattern-call breakdown so the shared owner path now expects `5` `search` rows, `1` `match` row, and `5` `fullmatch` rows on the published manifest;
  - keep the bytes helper pair tied to the existing verbose owner data:
    - reuse the existing verbose regression spellings from `VERBOSE_COMPILE_WORKFLOW_CASES` as the source of truth for the `str` payloads and assert that the new bytes rows carry the same payloads encoded to bytes;
    - keep the existing `VERBOSE_BYTES_COMPILE_CASE_ID` / module-workflow compile anchor on the same shared pattern instead of creating another bytes-specific compile case or parity module; and
    - do not add a detached bytes helper fixture, another parity suite, or benchmark assertions in this run.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1391` total / `1391` passed / `0` `unimplemented` across `114` manifests to `1393` / `1393` / `0` across the same `114` manifests;
  - `module.workflow` moves from `21` / `21` / `0` to `23` / `23` / `0`;
  - `module.workflow.bytes` moves from `6` / `6` / `0` to `8` / `8` / `0`; and
  - `module.workflow.pattern_call` moves from `9` / `9` / `0` to `11` / `11` / `0`, with both new bytes verbose helper rows visible in the tracked scorecard.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0412-module-workflow-bytes-verbose-helpers.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust or Python implementation code, benchmark manifests, benchmark reports, README text, or harness files in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached bytes-only helper table for this pair.
- Keep any later bytes miss-path follow-on or benchmark catch-up on the existing module-workflow / Python-path owner surfaces instead of inventing a second family.

## Notes
- `RBR-0412` is the next available feature task id in the current checkout even though the live task tail is higher:
  - `ops/tasks/done/RBR-0413-centralize-benchmark-manifest-selectors.md` explicitly notes that `RBR-0412` had been reserved for a feature-owned slice, but no tracked task file currently occupies that id;
  - `find ops/tasks -type f -name 'RBR-041*.md' | sort` currently shows `RBR-0410`, `RBR-0411`, `RBR-0413`, `RBR-0414`, `RBR-0415`, `RBR-0416`, `RBR-0418`, and `RBR-0419`, leaving `RBR-0412` open; and
  - `rg -n "RBR-0412" ops/tasks ops/state` currently finds only the historical note in `RBR-0413`, so this run fills the oldest unclaimed feature id rather than skipping another hole.
- Queue this directly after the drained `RBR-0726` head so the shared verbose compiled-pattern helper frontier keeps moving on the same module-workflow owner path instead of pausing for a different family.
- 2026-03-20 feature-planning probes confirm this follow-on is concrete from the tracked frontier:
  - `ops/tasks/done/RBR-0726-publish-module-workflow-verbose-miss-path-helper-pair.md` closed the last unpublished `str` verbose helper pair and left the feature queue empty;
  - `tests/conformance/fixtures/module_workflow_surface.py` now publishes all six `str` verbose helper rows plus only one `bytes` `pattern_call` row (`workflow-pattern-fullmatch-bytes`), so the smallest same-family bytes follow-on is the positive verbose helper pair on the existing manifest;
  - `tests/python/test_module_workflow_parity_suite.py` already keeps the verbose regression compile pattern, bytes compile anchor, and generic compiled-pattern parity assertions on the same owner path, so adding two bytes `pattern_call` rows extends existing coverage instead of opening a new branch;
  - `tests/conformance/test_combined_correctness_scorecards.py` currently names the finished `str` verbose helper rows as representative `module-workflow-surface` pattern-call coverage, but no bytes verbose helper companions from the same anchored pattern family; and
  - `reports/correctness/latest.py` currently reports `1391` total / `1391` passed / `0` `unimplemented` across `114` manifests, with `module.workflow` at `21` / `21` / `0`, `module.workflow.bytes` at `6` / `6` / `0`, and `module.workflow.pattern_call` at `9` / `9` / `0`, so this slice widens the tracked frontier through adjacent owner-path publication rather than another family.

## Blocker Note
- 2026-03-20: Attempted to add the two bytes verbose `pattern_call` rows on the existing module-workflow owner path, but the required parity gate immediately exposed a real implementation gap on the current branch.
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py` failed on the added `rebar` bytes verbose `Pattern.search()` row with `NotImplementedError: rebar.Pattern.search() is a scaffold placeholder; compiled pattern semantics are not implemented yet`.
- A direct runtime probe against the current checkout confirms the blocker without any fixture edits: compiling `b"^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $"` with `MULTILINE | VERBOSE` succeeds, but both `compiled.search(b"prefix\\nENV_VAR=ABCD\\nsuffix")` and `compiled.fullmatch(b"ENV_VAR = 123")` still raise the same placeholder `NotImplementedError`.
- The exploratory fixture/test edits were reverted, `reports/correctness/latest.py` was not republished, and the checkout was returned to green by rerunning the required published gate.
- Follow-up needed: land bytes verbose compiled-pattern execution support for this anchored regression pair before retrying the publication-only manifest/report task.
