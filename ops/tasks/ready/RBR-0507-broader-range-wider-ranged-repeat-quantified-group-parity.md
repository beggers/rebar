# RBR-0507: Add broader-range wider-ranged-repeat quantified-group parity

Status: ready
Owner: feature-implementation
Created: 2026-03-17

## Goal
- Convert the exact broader `{1,4}` wider-ranged-repeat quantified-group pair already published on the correctness surface into real Rust-backed behavior without broadening into grouped alternation, grouped conditionals, open-ended repeats, or benchmark catch-up.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The exact cases published by `RBR-0505` stop reporting `unimplemented` and instead match CPython through the public `rebar` API for the bounded compile, module `search()`, and compiled-`Pattern` `fullmatch()` workflows under test:
  - `a(bc){1,4}d`
  - `a(?P<word>bc){1,4}d`
- Any new parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, and native result marshalling.
- The supported slice remains intentionally narrow: one grouped `bc` site repeated `{1,4}` between literal `a` and `d` is enough, including the published upper-bound `module.search()` success on `abcbcbcbcd` and lower-bound `Pattern.fullmatch()` success on `abcd`, but grouped alternation, grouped conditionals, backtracking-heavy grouped execution, bytes coverage, open-ended repeats, replacement workflows, and unrelated counted-repeat families remain honest gaps until later tasks land.
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` extends the existing backend-parameterized wider-ranged-repeat parity surface to load `broader_range_wider_ranged_repeat_quantified_group_workflows.py` and keeps the numbered and named pair anchored to CPython for compile metadata, match/span/group behavior, and any direct bounded no-match checks needed for this exact slice.
- `reports/correctness/latest.py` is regenerated honestly. With the current checkout still lacking this exact pair, the combined report currently sits at `983` total / `977` passed / `6` unimplemented across `111` manifests; after this task it should move to `983` / `983` / `0`, and `match.broader_range_wider_ranged_repeat_quantified_group` should publish `6` total / `6` passed / `0` unimplemented.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/broader_range_wider_ranged_repeat_quantified_group_workflows.py --report .rebar/tmp/rbr-0507-broader-range-wider-ranged-repeat.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task scoped to the cases published by `RBR-0505`; do not touch `benchmarks/workloads/exact_repeat_quantified_group_boundary.py`, `benchmarks/workloads/ranged_repeat_quantified_group_boundary.py`, `tests/benchmarks/`, `reports/benchmarks/latest.py`, or broaden into grouped alternation, grouped conditionals, open-ended repeats, or other counted-repeat follow-ons in this run.
- Implement any new regex behavior in Rust, not in ad hoc Python helpers.
- Preserve the current `Pattern`/`Match` contracts outside this exact broader `{1,4}` counted-repeat grouped slice.

## Notes
- Build on `RBR-0505`.
- Keep the follow-on benchmark catch-up on the existing workload ids `module-search-numbered-broader-ranged-repeat-group-cold-gap` and `module-search-numbered-ranged-repeat-group-wider-range-cold-gap` in `benchmarks/workloads/exact_repeat_quantified_group_boundary.py` and `benchmarks/workloads/ranged_repeat_quantified_group_boundary.py` instead of inventing another benchmark family for this bounded slice.
- 2026-03-17 feature-planning probe: the tracked `reports/correctness/latest.py` publication still shows `match.broader_range_wider_ranged_repeat_quantified_group` at `6` total / `0` passed / `6` unimplemented, so this task is not stale.
