# RBR-0441: Add bounded quantified alternation-heavy conditional replacement parity

Status: ready
Owner: feature-implementation
Created: 2026-03-16

## Goal
- Convert the bounded quantified alternation-heavy two-arm conditional replacement cases published by `RBR-0439` into real Rust-backed behavior without widening into replacement templates, callable replacements, broader repeat ranges, deeper nesting, or other conditional-replacement families.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_conditional_group_exists_replacement_parity_suite.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The exact eight numbered and named cases already published in `tests/conformance/fixtures/conditional_group_exists_quantified_alternation_replacement_workflows.py` stop reporting `unimplemented` and match CPython through the public `rebar` API for bounded `module.sub()`, `module.subn()`, `Pattern.sub()`, and `Pattern.subn()` constant-replacement workflows.
- Any new parsing, span-collection, or replacement semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, replacement marshalling, and native result marshalling.
- The supported slice remains intentionally narrow: one optional numbered or named capture gating a two-arm conditional whose yes and else arms each contain a two-branch literal alternation repeated exactly twice in `a(b)?c(?(1)(de|df)|(eg|eh)){2}` and `a(?P<word>b)?c(?(word)(de|df)|(eg|eh)){2}` is enough, including the published present-capture and absent-capture constant-replacement workflows that keep the first and second alternation branches explicit across module and compiled-`Pattern` entrypoints, while replacement-template expansion, callable replacements, deeper nesting, broader repeat ranges, branch-local backreferences, and non-`{2}` variants remain out of scope.
- `tests/python/test_conditional_group_exists_replacement_parity_suite.py` absorbs `conditional_group_exists_quantified_alternation_replacement_workflows.py` into the shared conditional replacement parity surface, removes it from the suite's known-uncovered published-fixture frontier, and does not introduce another manifest-specific parity module.
- `reports/correctness/latest.py` flips the eight published quantified alternation-heavy conditional replacement cases from `unimplemented` to `pass` without regressing the adjacent two-arm, alternation-heavy, nested, quantified, replacement-template, or callable conditional replacement slices already covered on the same shared surface.
- Verification passes with `cargo build -p rebar-cpython`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_conditional_group_exists_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_quantified_alternation_replacement_workflows.py --report .rebar/tmp/rbr-0441-conditional-quantified-alternation-replacement-parity.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`.

## Constraints
- Keep this task scoped to the cases published by `RBR-0439`; do not broaden into replacement-template capture expansion, callable replacements, deeper nested conditionals, broader repeat ranges, branch-local-backreference-bearing arms, or stdlib delegation.
- Implement any new regex or replacement behavior in Rust, not in ad hoc Python helpers.
- Preserve the existing replacement and `Match` object contracts outside this exact quantified alternation-heavy conditional replacement slice.

## Notes
- Build on `RBR-0439`, `RBR-0196`, `RBR-0202`, and the existing shared conditional replacement parity surface.
- Keep later benchmark catch-up on the existing `benchmarks/workloads/conditional_group_exists_boundary.py` path instead of forking another benchmark family.
- The intended post-parity follow-on is `RBR-0443`, which should add the missing quantified alternation-heavy replacement `sub()` / `subn()` benchmark rows on that shared Python-path boundary.
