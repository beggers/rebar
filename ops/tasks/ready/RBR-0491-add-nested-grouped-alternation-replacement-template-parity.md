# RBR-0491: Add nested grouped-alternation replacement-template parity on the shared grouped replacement pytest path

Status: ready
Owner: feature-implementation
Created: 2026-03-16

## Goal
- Convert the exact nested grouped-alternation replacement-template pair that `RBR-0489` publishes into real Rust-backed behavior without widening into wrapper-template variants, inner-capture template expansion, callable replacements, quantified nested alternation, or benchmark catch-up.

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_grouped_literal_replacement_template.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- The exact two cases published in `tests/conformance/fixtures/nested_group_alternation_replacement_workflows.py` by `RBR-0489` stop reporting `unimplemented` and match CPython through the public `rebar` API for the bounded replacement-template workflows:
  - `rebar.sub("a((b|c))d", "\\1x", "abdacd") == "bxcx"`
  - `rebar.compile("a(?P<outer>(b|c))d").subn("\\g<outer>x", "acdabd", 1) == ("cxabd", 1)`
- Any new capture-span collection or replacement-template expansion semantics live behind Rust-backed entrypoints in `rebar._rebar`; Python changes stay limited to surface wiring, wrapper construction, cache/object plumbing, template marshalling, and native result marshalling.
- `tests/python/test_grouped_literal_replacement_template.py` absorbs `nested_group_alternation_replacement_workflows.py` into the existing shared grouped replacement parity surface instead of introducing another manifest-specific parity module, and keeps the new manifest explicit by asserting:
  - manifest id `nested-group-alternation-replacement-workflows`
  - compile patterns `a((b|c))d` and `a(?P<outer>(b|c))d`
  - operation/helper counts `("module_call", "sub"): 1` and `("pattern_call", "subn"): 1`
- The supported slice remains intentionally narrow: one numbered module `sub()` path exposing the outer nested capture through `\\1x` and one named compiled-`Pattern` `subn()` first-match-only path exposing `outer` through `\\g<outer>x` are enough, while wrapper-template variants like `"<\\1>"` / `"<\\g<outer>>"`, inner-capture template references like `\\2` / `\\g<inner>`, module `subn()` / compiled-`Pattern` `sub()` complements, callable replacements, broader nested grouped execution, and benchmark updates remain out of scope.
- With `RBR-0489` landed first, `reports/correctness/latest.py` flips the new `nested-group-alternation-replacement-workflows` manifest from `2` total / `0` passed / `2` unimplemented to `2` / `2` / `0`, moving the combined published correctness report from `969` total cases / `967` passed / `2` unimplemented across `108` manifests to `969` / `969` / `0`.
- Verification passes with:
  - `cargo build -p rebar-cpython`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_grouped_literal_replacement_template.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_group_alternation_replacement_workflows.py --report .rebar/tmp/rbr-0491-nested-grouped-alternation-template-parity.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task scoped to the cases published by `RBR-0489`; do not broaden into grouped-alternation benchmark catch-up, the adjacent `grouped_alternation_boundary.py` wrapper-template pair, inner-capture template references, callable replacements, quantified nested alternation, or stdlib delegation.
- Implement any new regex or replacement-template behavior in Rust, not in ad hoc Python helpers.
- Keep the later benchmark catch-up on the existing `benchmarks/workloads/grouped_alternation_replacement_boundary.py` path instead of forking another benchmark family.

## Notes
- Build on `RBR-0489`, `RBR-0389`, `RBR-0393`, and the existing grouped replacement pytest surface in `tests/python/test_grouped_literal_replacement_template.py`.
- The current grouped replacement parity module already owns the adjacent grouped, nested-group, and quantified nested-group replacement-template fixtures, so it is the correct home for this follow-on instead of another one-off parity file.
- The adjacent benchmark follow-on stays concrete on the same exact pair because `tests/benchmarks/benchmark_expectations.py` still classifies `module-sub-template-nested-grouped-alternation-cold-gap` and `pattern-subn-template-named-nested-grouped-alternation-replacement-purged-gap` as the remaining known-gap rows on `grouped-alternation-replacement-boundary`.
