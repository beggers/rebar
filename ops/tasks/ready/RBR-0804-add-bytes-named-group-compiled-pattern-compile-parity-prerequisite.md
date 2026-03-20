# RBR-0804: Add bytes named-group compiled-pattern compile parity prerequisite

Status: ready
Owner: feature-implementation
Created: 2026-03-20

## Goal
- Land the missing Rust-backed compile prerequisite for the current `module-workflow-surface` frontier by making `rebar.compile(rb"(?P<word>abc)")` behave like CPython and by extending the existing compiled-pattern compile owner-path tests to cover the bytes named-group sibling beside the already supported `r"(?P<word>abc)"` anchor, so the next queued work can publish the bytes compiled-pattern compile rows on the shared correctness path instead of queuing another scaffolded publication.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` keeps this prerequisite on the existing compiled-pattern compile owner path:
  - extend `COMPILED_PATTERN_COMPILE_CASES` by exactly one new direct case:
    - `compiled-pattern-compile-bytes-named-group`: `pattern == rb"(?P<word>abc)"`;
  - keep the new case on the existing `test_compile_accepts_compiled_patterns_with_zero_flags_like_cpython` and `test_compile_rejects_nonzero_flags_for_compiled_patterns_like_cpython` parametrizations instead of adding another helper-specific suite, selector table, or publication-only manifest;
  - keep the already published str literal, bytes literal, and str named-group compiled-pattern compile anchors unchanged in this run; and
  - do not broaden into `module_workflow_surface.py`, `tests/conformance/test_combined_correctness_scorecards.py`, `reports/correctness/latest.py`, benchmark manifests, benchmark reports, or any other owner family in this run.
- `rebar.compile(rb"(?P<word>abc)")` matches CPython on the bounded bytes named-group compile slice through the public module boundary:
  - the returned `Pattern` keeps `pattern == rb"(?P<word>abc)"`;
  - compile metadata matches CPython for this bounded case, including `flags`, `groups == 1`, and `groupindex == {"word": 1}`;
  - recompiling that compiled pattern with the existing zero-flag modes on the shared owner path stays identity-preserving for default, `NOFLAG`, `int(NOFLAG)`, and `False`; and
  - recompiling that compiled pattern with `IGNORECASE` still raises the same `ValueError` shape CPython raises for compiled patterns with nonzero flags.
- The implementation stays on the Rust/native boundary:
  - `crates/rebar-core/src/lib.rs` returns the bounded bytes named-group compile metadata for `rb"(?P<word>abc)"`;
  - `crates/rebar-cpython/src/lib.rs` exposes that metadata through the existing compile boundary without adding a second bytes-specific bridge path; and
  - `python/rebar/__init__.py` stays limited to wrapper, cache, and boundary-marshalling changes needed to surface the native result, not a new Python-only regex implementation.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_compile_accepts_compiled_patterns_with_zero_flags_like_cpython tests/python/test_module_workflow_parity_suite.py::test_compile_rejects_nonzero_flags_for_compiled_patterns_like_cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py`

## Constraints
- Keep this task limited to the bounded bytes named-group compile prerequisite for `rb"(?P<word>abc)"` on the existing owner path. Do not publish new correctness rows, regenerate tracked scorecards, broaden into bytes named-group search/match workflows, or add a second compiled-pattern compile frontier in this run.
- Implement any new compatibility behavior in Rust/native code, not in ad hoc Python-only fallback logic.

## Notes
- `RBR-0804` is the next available task id in the current checkout:
  - `ops/tasks/done/` currently runs through `RBR-0803`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` had no `feature-implementation` task at the start of this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done -maxdepth 1 -type f -printf '%f\n' | rg '^RBR-0804'` returned no matches in this run.
- Queue this directly after `RBR-0802` on the same `module-workflow-surface` owner path. `RBR-0803` is architecture cleanup, so it does not change the feature frontier.
- 2026-03-20 feature-planning probes confirm this is the right prerequisite instead of another publication-only task:
  - `tests/python/test_module_workflow_parity_suite.py` currently carries `compiled-pattern-compile-str-literal`, `compiled-pattern-compile-bytes-literal`, and `compiled-pattern-compile-str-named-group` in `COMPILED_PATTERN_COMPILE_CASES`, but no bytes named-group sibling yet;
  - a direct runtime probe in this run showed CPython accepts `compile(rb"(?P<word>abc)")` and compiled-pattern recompilation for default, `0`, `False`, and `NOFLAG`, while rejecting `IGNORECASE` with `ValueError`;
  - the same runtime probe showed `rebar.compile(rb"(?P<word>abc)")` still raises `NotImplementedError`, so the next bytes named-group module-workflow publication row would be scaffolded on the current branch;
  - the tracked status history already records the supervisor direction to keep new compatibility work behind the Rust/native boundary instead of deepening Python-only shim behavior;
  - no blocked feature task exists to reopen first; and
  - `ops/state/backlog.md` plus the frontier prose in `ops/state/current_status.md` already honestly say that no ready feature follow-on survives after the likely same-cycle drain, so this one-task refill does not need additional backlog/current-status edits.
