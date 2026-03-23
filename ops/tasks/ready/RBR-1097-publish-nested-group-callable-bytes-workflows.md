# RBR-1097: Publish nested-group callable bytes workflows

Status: ready
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Catch the newly landed nested-group callable bytes runtime slice up on the existing correctness owner path by publishing the exact bounded bytes workflows that `RBR-1095` enabled, before any same-family benchmark catch-up or broader callable-replacement expansion reopens the frontier.

## Pattern Pair
- `rebar.sub(rb"a((b))d", lambda m: b"<" + m.group(1) + b">", b"abdabd")`
- `rebar.compile(rb"a(?P<outer>(?P<inner>b))d").subn(lambda m: b"<" + m.group("inner") + b">", b"abdabd", 1)`

## Deliverables
- `tests/conformance/fixtures/nested_group_callable_replacement_workflows.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- Extend `tests/conformance/fixtures/nested_group_callable_replacement_workflows.py` on the existing owner path with only the adjacent bytes cases for the bounded nested-group callable slice that now works in `rebar`:
  - numbered module `sub()` and `subn(count=1)` rows for `rb"a((b))d"` that exercise `group(1)` and `group(2)`;
  - numbered compiled-pattern `sub()` and `subn(count=1)` rows for `rb"a((b))d"` on the same bounded callback shape;
  - named module `sub()` and `subn(count=1)` rows for `rb"a(?P<outer>(?P<inner>b))d"` that exercise `group("outer")` and `group("inner")`; and
  - named compiled-pattern `sub()` and `subn(count=1)` rows for `rb"a(?P<outer>(?P<inner>b))d"` on that same bounded callback shape.
- Keep the publication bounded to the existing nested-group callable manifest:
  - do not widen into alternation, quantified nested groups, callable replacement on other owner paths, or benchmark workloads in this run; and
  - keep the existing `str` rows on the same manifest green.
- Refresh `tests/conformance/test_combined_correctness_scorecards.py` only as needed so the combined correctness scorecard explicitly requires representative bytes ids for `nested-group-callable-replacement-workflows`.
- Regenerate `reports/correctness/latest.py` so the published scorecard includes the new bytes callable rows and remains fully passing with no new honest gaps or explicit failures.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the work on the Python-facing correctness publication path. Do not widen this task into benchmark manifests, benchmark reports, README text, or tracked state prose.
- New runtime behavior is already the prerequisite here; do not spend this task on more Rust execution changes unless a narrow fixture publication blocker forces a tiny bridge fix.
- Preserve the same bounded callable semantics that `RBR-1095` landed; this task is for correctness publication, not broader callback semantics.

## Notes
- `RBR-1097` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contain no live feature task file; and
  - `rg -n 'RBR-1097|RBR-1098|RBR-1099' ops/tasks ops/state -g '*.md'` returned only historical mentions inside done-task notes in this run.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The narrow same-family check in this run shows publication, not implementation, is the next bounded slice:
  - the public-path bytes probes for `rebar.sub(rb"a((b))d", ...)` and `rebar.compile(rb"a(?P<outer>(?P<inner>b))d").subn(...)` now match `re` on this checkout;
  - `tests/conformance/fixtures/nested_group_callable_replacement_workflows.py` still publishes only the `str` rows for this manifest today; and
  - the existing benchmark owner path in `benchmarks/workloads/nested_group_callable_replacement_boundary.py` also still stops at the `str` rows, so correctness catch-up remains the next same-family follow-on before any benchmark task.
