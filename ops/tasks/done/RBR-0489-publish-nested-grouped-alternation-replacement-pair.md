# RBR-0489: Publish the nested grouped-alternation replacement-template pair on the correctness surface

Status: done
Owner: feature-implementation
Created: 2026-03-16

## Goal
- Extend the published correctness scorecard with the exact nested grouped-alternation replacement-template pair already exposed as explicit source-tree benchmark gaps on `grouped-alternation-replacement-boundary`, while keeping the work on an ordinary Python fixture path before Rust-backed parity or benchmark catch-up revisit those broader nested replacement shapes.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/nested_group_alternation_replacement_workflows.py`
- `tests/conformance/correctness_expectations.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/nested_group_alternation_replacement_workflows.py` publishes only the minimal two `str` replacement-template workflow cases needed to make the exact benchmark-anchored gap pair visible on the correctness surface:
  - a numbered module-helper case for `rebar.sub("a((b|c))d", "\\1x", "abdacd")`, which CPython reports as `"bxcx"`;
  - a named compiled-pattern case for `rebar.compile("a(?P<outer>(b|c))d").subn("\\g<outer>x", "acdabd", 1)`, which CPython reports as `("cxabd", 1)`.
- Keep both new cases pinned to one new `nested-group-alternation-replacement-workflows` correctness manifest. Do not broaden into callable replacements, `"<\\1>"` / `"<\\g<outer>>"` wrapper templates, inner named captures, quantified nested alternation, branch-local backreferences, or benchmark updates in this run.
- `python/rebar_harness/correctness.py`, `tests/conformance/correctness_expectations.py`, and `tests/conformance/test_combined_correctness_scorecards.py` register the new manifest on the published combined scorecard path so the exact nested replacement pair stays visible instead of disappearing behind the existing benchmark-only gap rows.
- `reports/correctness/latest.py` is regenerated honestly. With the current checkout still lacking this exact nested replacement-template slice, the combined report should move from `967` total cases / `967` passed / `0` unimplemented across `107` manifests to `969` / `967` / `2` across `108` manifests, and the new `collection.replacement.nested_group_alternation` suite should publish `2` total / `0` passed / `2` unimplemented.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_correctness_fixture_inventory_contract.py tests/conformance/test_python_fixture_manifest_contract.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_group_alternation_replacement_workflows.py --report .rebar/tmp/rbr-0489-nested-group-alternation-replacement.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not implement nested grouped-alternation replacement-template runtime behavior, do not touch `tests/python/test_grouped_literal_replacement_template.py`, `benchmarks/workloads/grouped_alternation_boundary.py`, `benchmarks/workloads/grouped_alternation_replacement_boundary.py`, `tests/benchmarks/`, or `reports/benchmarks/latest.py`, and do not broaden into the companion `"<\\1>"` / `"<\\g<outer>>"` benchmark pair on `grouped-alternation-boundary`.
- Keep the work anchored to the exact existing benchmark gap pair. This task should make those two helpers visible as honest correctness debt, not rename or replace the benchmark rows that already track them.

## Notes
- `RBR-0487` should land immediately ahead of this task and clear the unrelated nested-group benchmark pair from `nested-group-boundary`, leaving this nested grouped-alternation replacement publication slice as the concrete surviving follow-on in the ready queue.
- 2026-03-16 planning probe: the tracked benchmark manifest `benchmarks/workloads/grouped_alternation_replacement_boundary.py` already carries the exact gap rows `module-sub-template-nested-grouped-alternation-cold-gap` and `pattern-subn-template-named-nested-grouped-alternation-replacement-purged-gap`, pinned to patterns `"a((b|c))d"` and `"a(?P<outer>(b|c))d"` with haystacks `"abdacd"` and `"acdabd"` plus replacement templates `"\\1x"` and `"\\g<outer>x"`.
- 2026-03-16 planning probe: in the current checkout, CPython reports `re.sub("a((b|c))d", "\\1x", "abdacd") == "bxcx"` and `re.compile("a(?P<outer>(b|c))d").subn("\\g<outer>x", "acdabd", 1) == ("cxabd", 1)`.
- 2026-03-16 planning probe: in the current checkout, `rebar.sub("a((b|c))d", "\\1x", "abdacd")` and `rebar.compile("a(?P<outer>(b|c))d").subn("\\g<outer>x", "acdabd", 1)` still raise scaffold `NotImplementedError`s through the public Python path.
- The immediate follow-on after this publication should stay on the same exact pair: first Rust-backed parity on the grouped replacement pytest path, then source-tree benchmark catch-up against the already-existing `grouped-alternation-replacement-boundary` gap rows.

## Completion Note
- 2026-03-16 feature-implementation: Added `tests/conformance/fixtures/nested_group_alternation_replacement_workflows.py` with the bounded numbered module `sub()` and named compiled-pattern `subn()` replacement-template cases for `a((b|c))d` and `a(?P<outer>(b|c))d`, registered the new manifest on the published combined correctness path, and regenerated `reports/correctness/latest.py`. Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_correctness_fixture_inventory_contract.py tests/conformance/test_python_fixture_manifest_contract.py tests/conformance/test_combined_correctness_scorecards.py` (`11 passed, 2260 subtests passed in 25.12s`), `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_group_alternation_replacement_workflows.py --report .rebar/tmp/rbr-0489-nested-group-alternation-replacement.py` (`2` total, `0` passed, `2` unimplemented), and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`. The tracked report now reads `969` total cases across `108` manifests with `967` passed and `2` unimplemented, and `collection.replacement.nested_group_alternation` publishes `2` total / `0` passed / `2` unimplemented on `nested-group-alternation-replacement-workflows`.
