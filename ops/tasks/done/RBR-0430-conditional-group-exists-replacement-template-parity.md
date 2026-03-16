# RBR-0430: Add bounded two-arm conditional replacement-template parity

Status: done
Owner: feature-implementation
Created: 2026-03-16

## Goal
- Convert the bounded two-arm conditional replacement-template cases published by `RBR-0426` into real Rust-backed behavior without widening into alternation-heavy arms, nested or quantified conditionals, callable replacements, or broader template parsing.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_conditional_group_exists_replacement_parity_suite.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The exact eight numbered and named cases already published in `tests/conformance/fixtures/conditional_group_exists_replacement_template_workflows.py` stop reporting `unimplemented` and match CPython through the public `rebar` API for the bounded `module.sub()`, `module.subn()`, `Pattern.sub()`, and `Pattern.subn()` replacement-template workflows under test.
- Any new parsing, span-collection, or template-expansion semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, template marshalling, and native result marshalling.
- The supported slice remains intentionally narrow: one optional numbered or named capture gating the two-arm conditional yes/no branch in `a(b)?c(?(1)d|e)` and `a(?P<word>b)?c(?(word)d|e)` is enough, including the published present-capture `\\1x` / `\\g<word>x` expansion paths and the bounded absent-capture empty-expansion `subn()` companions for both module and compiled-`Pattern` entrypoints, while alternation-heavy arms, nested or quantified conditionals, callable replacements, broader template parsing, and benchmark catch-up stay out of scope.
- `tests/python/test_conditional_group_exists_replacement_parity_suite.py` absorbs `conditional-group-exists-replacement-template-workflows` into the shared replacement parity surface, `tests/python/test_fixture_parity_support_contract.py` stays aligned with the published conditional replacement fixture selector, and no new manifest-specific parity module is introduced.
- `reports/correctness/latest.py` flips the eight published two-arm conditional replacement-template cases from `unimplemented` to `pass` without regressing the adjacent constant-replacement slice, the already-landed callable-replacement slice, or the surrounding replacement and `Match` parity surface.
- Verification passes with `cargo build -p rebar-cpython`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_conditional_group_exists_replacement_parity_suite.py tests/python/test_fixture_parity_support_contract.py tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_replacement_template_workflows.py --report .rebar/tmp/rbr-0430-conditional-template-parity.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`.

## Constraints
- Keep this task scoped to the cases published by `RBR-0426`; do not broaden into alternation-heavy conditional arms, nested or quantified conditional replacement templates, callable replacements, broader template parsing, or stdlib delegation.
- Implement any new regex or replacement-template behavior in Rust, not in ad hoc Python helpers.
- Preserve the existing constant-replacement and callable-replacement contracts outside this exact two-arm conditional template slice.

## Notes
- Build on `RBR-0426`, `RBR-0423`, `RBR-0193`, and the existing shared conditional replacement parity surface.
- Keep later benchmark catch-up on the existing `benchmarks/workloads/conditional_group_exists_boundary.py` path instead of forking another benchmark family.
- The adjacent post-parity benchmark follow-on is the existing `module-sub-template-numbered-conditional-group-exists-replacement-warm-gap` row in `benchmarks/workloads/conditional_group_exists_boundary.py`.

## Completion
- Routed `boundary_literal_template_subn()` through the existing two-arm conditional capture-span collector and updated the core template expander plus named-capture marshalling so valid-but-absent `\\1` / `\\g<word>` references expand to the empty string instead of reporting `unsupported`.
- Added `conditional_group_exists_replacement_template_workflows.py` to the shared conditional replacement fixture selector and parity suite, and kept `tests/python/test_fixture_parity_support_contract.py` aligned with the selector's sorted published-path contract.
- Verified `cargo build -p rebar-cpython`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_conditional_group_exists_replacement_parity_suite.py tests/python/test_fixture_parity_support_contract.py tests/conformance/test_combined_correctness_scorecards.py` (`498 passed, 1029 subtests passed`), and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_replacement_template_workflows.py --report .rebar/tmp/rbr-0430-conditional-template-parity.py` (`8` passed / `0` unimplemented).
- Republished the tracked combined correctness scorecard at `reports/correctness/latest.py`; the tracked artifact now reports `949` total cases across `106` manifests with `949` passes, `0` failures, and `0` unimplemented cases.
