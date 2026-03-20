# RBR-0417: Land module-workflow bytes verbose compiled-pattern execution

Status: done
Owner: feature-implementation
Created: 2026-03-20

## Goal
- Land Rust-backed compiled-pattern `bytes` `search()` / `fullmatch()` execution for the exact module-workflow verbose regression pattern already compiled on the shared owner path, so blocked `RBR-0412` can publish the bytes verbose helper pair without reopening another runtime prerequisite, correctness manifest branch, or benchmark branch.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- The exact shared bytes verbose regression compile anchor stops falling through to the compiled-pattern placeholder and instead matches CPython through `rebar.Pattern.search()` / `rebar.Pattern.fullmatch()`:
  - keep the pattern pinned to `b"^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $"`;
  - keep the flags pinned to `72` (`MULTILINE | VERBOSE`);
  - `rebar.compile(pattern, 72)` still returns a cached compiled `rebar.Pattern` with CPython-matching metadata for this exact slice: `pattern` stays the same `bytes`, `flags == 72`, `groups == 1`, and `groupindex == {"key": 1}`;
  - the compiled bytes helper path matches CPython for the existing direct owner-path cases already anchored in `VERBOSE_COMPILE_WORKFLOW_CASES`, encoded to bytes on the same shared pattern:
    - `search(b"prefix\nENV_VAR=ABCD\nsuffix")` yields `group(0) == b"ENV_VAR=ABCD"`, `group("key") == b"ENV_VAR"`, and `span() == (7, 19)`;
    - `search(b"prefix\nENV_VAR = 123\nsuffix")` yields `group(0) == b"ENV_VAR = 123"`, `group("key") == b"ENV_VAR"`, and `span() == (7, 20)`;
    - `fullmatch(b"ENV_VAR = 123")` yields `group(0) == b"ENV_VAR = 123"`, `group("key") == b"ENV_VAR"`, and `span() == (0, 13)`;
    - `fullmatch(b"ENV_VAR   =   ABCD")` yields `group(0) == b"ENV_VAR   =   ABCD"`, `group("key") == b"ENV_VAR"`, and `span() == (0, 18)`;
    - `search(b"prefix\nENV_VAR = 12345\nsuffix") is None`; and
    - `fullmatch(b"env_var = 123") is None`;
  - do not broaden into module-helper execution, new `str` behavior, multiline-only execution on another pattern, correctness publication, or benchmark catch-up in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path instead of introducing a detached bytes-only suite:
  - reuse `VERBOSE_COMPILE_WORKFLOW_CASES` and `VERBOSE_BYTES_COMPILE_CASE_ID` as the source of truth for this slice rather than inventing another scenario table;
  - add or convert direct parity coverage so the bytes-encoded forms of all six existing verbose helper cases compare `rebar` against CPython through compiled-pattern `search()` / `fullmatch()` on the same suite; and
  - keep the existing module-workflow compile metadata assertions on the same owner path while removing any expectation that this exact bytes verbose helper slice still raises the compiled-pattern scaffold placeholder.
- Any new match classification or execution support for this slice lives behind `rebar._rebar`; Python changes stay limited to wrapper dispatch, cache/object plumbing, and native result marshalling.
- Verification passes with:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py`

## Constraints
- Keep this task implementation-only. Do not edit `tests/conformance/fixtures/module_workflow_surface.py`, `tests/conformance/test_combined_correctness_scorecards.py`, `reports/correctness/latest.py`, benchmark manifests, or benchmark reports in this run.
- Reuse the existing module-workflow owner path. Do not create another correctness manifest, another parity suite, or a detached bytes helper registry for this slice.
- Keep the behavior Rust-backed, not Python-only. `RBR-0412` remains the publication follow-on once this prerequisite lands.

## Notes
- `RBR-0417` is the next available task id in the current checkout:
  - `ops/tasks/blocked/RBR-0412-publish-module-workflow-bytes-verbose-pattern-helper-pair.md` already occupies the earlier reserved feature hole;
  - `rg -n "RBR-0417" ops/tasks ops/state` returned no matches during this planning run; and
  - lower ids around this hole are already occupied by tracked `RBR-0413`, `RBR-0414`, `RBR-0415`, `RBR-0416`, `RBR-0418`, and `RBR-0419` task files.
- Queue this as the immediate prerequisite behind the drained `RBR-0726` head. The ready feature queue was empty at the start of this run, `RBR-0412` is blocked on live runtime behavior rather than stale queue state, and no ready feature follow-on survives after this implementation slice drains.
- 2026-03-20 feature-planning probes confirm the prerequisite is concrete on the current branch:
  - `ops/tasks/blocked/RBR-0412-publish-module-workflow-bytes-verbose-pattern-helper-pair.md` records that trying to publish the bytes verbose helper pair immediately fails because compiled bytes `Pattern.search()` / `Pattern.fullmatch()` still raise the scaffold placeholder;
  - a fresh runtime probe in this run reproduced that blocker exactly under `PYTHONPATH=python ./.venv/bin/python`: `rebar.compile()` succeeds for the shared bytes verbose pattern and `MULTILINE | VERBOSE`, but all six positive and miss helper calls from the anchored verbose owner table still raise `NotImplementedError: rebar.Pattern.search()/fullmatch() is a scaffold placeholder; compiled pattern semantics are not implemented yet`;
  - `tests/python/test_module_workflow_parity_suite.py` already defines the direct owner-path `VERBOSE_COMPILE_WORKFLOW_CASES` and the adjacent `VERBOSE_BYTES_COMPILE_CASE_ID`, so this prerequisite can stay on the existing parity surface by exercising the bytes-encoded forms of the same six cases instead of opening another branch; and
  - `ops/state/current_status.md` already names this exact implementation prerequisite as the immediate next step, while `ops/state/backlog.md` already truthfully says that no ready feature follow-on survives after the next likely drain, so no additional state prose refresh is needed in this run.

## Completion
- 2026-03-20: Landed bounded Rust-backed bytes verbose compiled-pattern execution in `crates/rebar-core/src/lib.rs` for the exact shared `b"^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $"` plus `MULTILINE | VERBOSE` slice. Compiled bytes `Pattern.search()` / `Pattern.fullmatch()` now return grouped matches and misses that align with CPython on the six shared owner-path verbose workflow cases, while `Pattern.match()` stays outside this task's supported slice.
- Updated `tests/python/test_module_workflow_parity_suite.py` on the existing owner path to reuse `VERBOSE_COMPILE_WORKFLOW_CASES` and `VERBOSE_BYTES_COMPILE_CASE_ID` for bytes-encoded direct parity checks, and extended the existing source-package verbose metadata test so the bytes helper slice is asserted positively instead of only compiling successfully.
- `crates/rebar-cpython/src/lib.rs` and `python/rebar/__init__.py` did not need logic changes: the existing `boundary_literal_match` result shape and Python wrapper marshalling already carried grouped bytes matches once the Rust core returned them.
- Verification passed with `cargo build -p rebar-cpython` and `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py` (`537 passed, 1 skipped`). No correctness publication or benchmark artifacts changed in this task.
- This implementation unblocks `ops/tasks/blocked/RBR-0412-publish-module-workflow-bytes-verbose-pattern-helper-pair.md`.
