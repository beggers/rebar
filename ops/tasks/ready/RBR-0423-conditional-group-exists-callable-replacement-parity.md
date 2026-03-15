# RBR-0423: Add bounded two-arm conditional callable-replacement parity

Status: ready
Owner: feature-implementation
Created: 2026-03-15

## Goal
- Convert the bounded two-arm conditional callable-replacement cases published by `RBR-0421` into real Rust-backed behavior without widening into alternation-heavy arms, nested or quantified conditionals, replacement-template variants, or broader callback helpers.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The exact eight numbered and named cases already published in `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` stop reporting `unimplemented` and match CPython through the public `rebar` API for the bounded `module.sub()`, `module.subn()`, `Pattern.sub()`, and `Pattern.subn()` callable-replacement workflows under test.
- Any new parsing or execution semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, callable marshalling, and native result marshalling.
- The supported slice remains intentionally narrow: one optional numbered or named capture gating the two-arm conditional yes/no branch in `a(b)?c(?(1)d|e)` and `a(?P<word>b)?c(?(word)d|e)` is enough, including one present-capture callback result path and one absent-capture callback-exception path for both module and compiled-`Pattern` entrypoints, while alternation-heavy arms, nested conditionals, quantified conditionals, replacement-template behavior, broader callback helpers, and benchmark catch-up stay out of scope.
- `tests/python/test_callable_replacement_parity_suite.py` keeps this manifest on the shared callable parity surface, drops `conditional-group-exists-callable-replacement-workflows` from the pending-manifest skip set once live `rebar` behavior stops being `unimplemented`, and continues to cover both callback result parity and callback exception parity without growing another manifest-specific parity module.
- `reports/correctness/latest.py` flips the eight published two-arm conditional callable-replacement cases from `unimplemented` to `pass` without regressing the adjacent two-arm conditional replacement-template slice, the already-landed broader conditional callable-replacement slices, or the surrounding callable `Match` and exception surfaces.
- Verification passes with `cargo build -p rebar-cpython`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/rbr-0423-conditional-callable.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`.

## Constraints
- Keep this task scoped to the cases published by `RBR-0421`; do not broaden into alternation-heavy conditional arms, nested or quantified conditional callable replacements, replacement-template variants, or stdlib delegation.
- Implement any new regex or callback behavior in Rust, not in ad hoc Python helpers.
- Preserve the existing `Pattern` / `Match` callback contracts outside this exact two-arm conditional slice.

## Notes
- Build on `RBR-0421`, `RBR-0193`, and the existing shared callable-replacement parity surface.
- Keep later benchmark catch-up on the existing `benchmarks/workloads/conditional_group_exists_boundary.py` path instead of forking another benchmark family.
- The adjacent post-parity benchmark anchor is the existing `pattern-subn-callable-named-conditional-group-exists-replacement-purged-gap` row in `benchmarks/workloads/conditional_group_exists_boundary.py`.
