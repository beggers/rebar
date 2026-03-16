# RBR-0495: Publish the nested grouped-alternation wrapper-template pair on the correctness surface

Status: done
Owner: feature-implementation
Created: 2026-03-16

## Goal
- Extend the published correctness scorecard with the exact nested grouped-alternation wrapper-template pair already exposed as explicit source-tree benchmark gaps on `grouped-alternation-boundary`, while keeping the work on an ordinary Python fixture path before Rust-backed parity or benchmark catch-up revisit that companion benchmark pair.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/fixtures/nested_group_alternation_wrapper_replacement_workflows.py`
- `tests/conformance/correctness_expectations.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/nested_group_alternation_wrapper_replacement_workflows.py` publishes only the minimal two `str` wrapper-template workflow cases needed to make the exact benchmark-anchored gap pair visible on the correctness surface:
  - a numbered module-helper case for `rebar.sub("a((b|c))d", "<\\1>", "abdacd")`, which CPython reports as `"<b><c>"`;
  - a named compiled-pattern case for `rebar.compile("a(?P<outer>(b|c))d").subn("<\\g<outer>>", "abdacd", 1)`, which CPython reports as `("<b>acd", 1)`.
- Keep both new cases pinned to one new `nested-group-alternation-wrapper-replacement-workflows` correctness manifest. Do not broaden into the already-landed `\\1x` / `\\g<outer>x` slice, inner-capture template references like `\\2x`, callable replacements, quantified nested alternation, branch-local backreferences, or benchmark updates in this run.
- `python/rebar_harness/correctness.py`, `tests/conformance/correctness_expectations.py`, and `tests/conformance/test_combined_correctness_scorecards.py` register the new manifest on the published combined scorecard path so the exact wrapper-template pair stays visible instead of disappearing behind the existing benchmark-only gap rows.
- `reports/correctness/latest.py` is regenerated honestly. With the current checkout still lacking this exact wrapper-template slice on the published correctness surface, the combined report should move from `969` total cases / `969` passed / `0` unimplemented across `108` manifests to `971` / `969` / `2` across `109` manifests, and the new `collection.replacement.nested_group_alternation.wrapper` suite should publish `2` total / `0` passed / `2` unimplemented.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_correctness_fixture_inventory_contract.py tests/conformance/test_python_fixture_manifest_contract.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/nested_group_alternation_wrapper_replacement_workflows.py --report .rebar/tmp/rbr-0495-nested-group-alternation-wrapper-replacement.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not implement nested grouped-alternation wrapper-template runtime behavior, do not touch `tests/python/test_grouped_literal_replacement_template.py`, `benchmarks/workloads/grouped_alternation_boundary.py`, `benchmarks/workloads/grouped_alternation_replacement_boundary.py`, `tests/benchmarks/`, or `reports/benchmarks/latest.py`, and do not broaden into later parity or benchmark catch-up for this pair.
- Keep the work anchored to the exact existing benchmark gap pair. This task should make those two helpers visible as honest correctness debt, not rename or replace the benchmark rows that already track them.

## Notes
- `RBR-0493` should land immediately ahead of this task and clear the sibling `grouped-alternation-replacement-boundary` gap pair, leaving this companion wrapper-template pair on `grouped-alternation-boundary` as the concrete surviving follow-on in the ready queue.
- 2026-03-16 planning probe: the tracked benchmark manifest `benchmarks/workloads/grouped_alternation_boundary.py` already carries the exact gap rows `module-sub-template-nested-grouped-alternation-warm-gap` and `pattern-subn-template-named-nested-grouped-alternation-purged-gap`, pinned to patterns `"a((b|c))d"` and `"a(?P<outer>(b|c))d"` with haystack `"abdacd"` plus replacement templates `"<\\1>"` and `"<\\g<outer>>"`.
- 2026-03-16 planning probe: `reports/benchmarks/latest.py` currently reports `grouped-alternation-boundary` at `6` measured workloads / `2` known gaps, and both exact wrapper-template workload ids still publish `status == "unimplemented"`.
- 2026-03-16 planning probe: CPython reports `re.sub("a((b|c))d", "<\\1>", "abdacd") == "<b><c>"` and `re.compile("a(?P<outer>(b|c))d").subn("<\\g<outer>>", "abdacd", 1) == ("<b>acd", 1)` for this exact pair.
- `RBR-0491` intentionally left this wrapper-template pair out of scope while converting the adjacent `\\1x` / `\\g<outer>x` nested grouped-alternation replacement-template slice to Rust-backed parity.

## Retirement Note
- 2026-03-16 feature-planning: Retired this queued publication-as-gap task after verifying the exact wrapper-template pair already matches CPython through the public `rebar` API in the current checkout: `rebar.sub("a((b|c))d", "<\\1>", "abdacd") == "<b><c>"` and `rebar.compile("a(?P<outer>(b|c))d").subn("<\\g<outer>>", "abdacd", 1) == ("<b>acd", 1)`. The adjacent blocked benchmark note on `RBR-0493` also already observed the same pair timing as measured on the narrow `grouped_alternation_boundary.py` rerun, so the old `971 / 969 / 2` acceptance criteria were no longer honest. Replacement task `RBR-0497` republishes the same bounded pair on the correctness surface as passing cases instead of `unimplemented` debt.
