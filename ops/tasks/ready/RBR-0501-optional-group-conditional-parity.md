# RBR-0501: Add bounded optional-group conditional parity

Status: ready
Owner: feature-implementation
Created: 2026-03-17

## Goal
- Convert the exact optional-group conditional pair already published on the correctness surface into real Rust-backed behavior without broadening into counted repeats, alternation-heavy arms, or benchmark catch-up.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_conditional_group_exists_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The exact cases published by `RBR-0500` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded compile, module `search()`, and compiled-`Pattern` `fullmatch()` workflows under test:
  - `a(b)?(?(1)c|d)e`
  - `a(?P<word>b)?(?(word)c|d)e`
- Any new parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one optional capturing group immediately feeding a same-pattern conditional with literal `c` and `d` arms inside fixed literal prefix/suffix text is enough, including the published present-capture search successes and absent-capture fullmatch successes, but counted repeats such as `{1,4}`, empty-arm conditionals, alternation-heavy arms, replacement workflows, nested conditionals, branch-local backreferences, and broader backtracking remain honest gaps until later tasks land.
- `tests/python/test_conditional_group_exists_parity_suite.py` extends the existing conditional parity surface to load `optional_group_conditional_workflows.py` and keeps the new pair anchored to CPython for match/span/group behavior through any direct bounded-window or no-match checks needed for this exact numbered/named slice.
- `reports/correctness/latest.py` is regenerated honestly. With the current checkout still lacking this exact pair, the combined report currently sits at `977` total / `971` passed / `6` unimplemented across `110` manifests; after this task it should move to `977` / `977` / `0`, and `match.optional_group_conditional` should publish `6` total / `6` passed / `0` unimplemented.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_conditional_group_exists_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/optional_group_conditional_workflows.py --report .rebar/tmp/rbr-0501-optional-group-conditional.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task scoped to the cases published by `RBR-0500`; do not touch `benchmarks/workloads/optional_group_boundary.py`, `tests/benchmarks/`, `reports/benchmarks/latest.py`, or broaden into counted-repeat follow-ons or other conditional families in this run.
- Implement any new regex behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact optional-group-before-conditional slice.

## Notes
- Build on `RBR-0500`.
- Keep the follow-on on the existing conditional parity path in `tests/python/test_conditional_group_exists_parity_suite.py` instead of creating a second one-off parity suite unless the current helper structure cannot express the exact pair cleanly.
- `benchmarks/workloads/optional_group_boundary.py` already carries the existing Python-path benchmark anchor `module-search-numbered-optional-group-conditional-cold-gap`; later benchmark catch-up should stay on that manifest instead of inventing another benchmark family for this same bounded slice.
- 2026-03-17 feature-planning probe: direct public-API checks in the current checkout still raise `NotImplementedError` for both target patterns at `rebar.compile(...)`, so this task is not stale.
