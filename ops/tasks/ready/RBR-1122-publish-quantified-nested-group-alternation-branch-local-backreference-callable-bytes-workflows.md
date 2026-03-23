# RBR-1122: Publish quantified nested-group alternation branch-local-backreference callable bytes workflows

Status: ready
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Catch the newly landed quantified nested-group alternation plus branch-local-backreference callable bytes runtime slice up on the existing correctness owner path by publishing the adjacent bounded bytes workflows that `RBR-1120` enabled, before any same-family benchmark catch-up or broader callable-replacement expansion reopens the frontier.

## Pattern Pair
- `rebar.sub(rb"a((b|c)+)\\2d", lambda m: m.group(1) + b"x", b"abbd")`
- `rebar.compile(rb"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d").subn(lambda m: b"<" + m.group("inner") + b">", b"zzaccdabbbdzz", 1)`

## Deliverables
- `tests/conformance/fixtures/quantified_nested_group_alternation_branch_local_backreference_callable_replacement_workflows.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- Extend `tests/conformance/fixtures/quantified_nested_group_alternation_branch_local_backreference_callable_replacement_workflows.py` on the existing owner path with only the adjacent bytes cases for the exact bounded quantified nested-group alternation plus same-branch backreference callable slice that now works in `rebar`:
  - numbered module `sub()` and `subn(count=1)` rows for `rb"a((b|c)+)\\2d"` that exercise `group(1)` and `group(2)` on the existing lower-bound and first-match-only `b`-branch haystacks;
  - numbered compiled-pattern `sub()` and `subn(count=1)` rows for `rb"a((b|c)+)\\2d"` on the existing mixed-branch and leading-`c` first-match-only slices;
  - named module `sub()` and `subn(count=1)` rows for `rb"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d"` that exercise `group("outer")` and `group("inner")` on the existing lower-bound and first-match-only bounded haystacks; and
  - named compiled-pattern `sub()` and `subn(count=1)` rows for `rb"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d"` on that same mixed-branch and first-match-only bounded slice.
- Keep the publication bounded to the existing quantified branch-local-backreference callable manifest:
  - do not widen into broader counted repeats, conditional follow-ons, benchmark workloads, or another correctness manifest in this run; and
  - keep the existing `str` rows on the same manifest green.
- Refresh `tests/conformance/test_combined_correctness_scorecards.py` only as needed so the combined correctness scorecard explicitly requires representative bytes ids for `quantified-nested-group-alternation-branch-local-backreference-callable-replacement-workflows`.
- Regenerate `reports/correctness/latest.py` so the published scorecard includes the new bytes callable rows and remains fully passing with no new honest gaps or explicit failures:
  - `REPORT["summary"]` moves from `1637` total / `1637` passed / `0` failed / `0` unimplemented to `1645` / `1645` / `0` / `0`;
  - `REPORT["fixtures"]["manifest_count"]` remains `114`;
  - the exact `quantified-nested-group-alternation-branch-local-backreference-callable-replacement-workflows` manifest grows from `8` published passing cases to `16`; and
  - `collection.replacement.quantified_nested_group_alternation_branch_local_backreference.callable` no longer reports only `text_models == ['str']`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'quantified_nested_group_alternation_branch_local_backreference and callable and bytes'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the work on the Python-facing correctness publication path. Do not widen this task into benchmark manifests, benchmark reports, README text, or tracked ops state prose.
- New runtime behavior is already the prerequisite here; do not spend this task on more Rust execution changes unless a narrow fixture publication blocker forces a tiny bridge fix.
- Preserve the same bounded quantified nested-group alternation plus branch-local-backreference callable semantics that `RBR-1120` landed; this task is for correctness publication, not broader callback semantics.

## Notes
- `RBR-1122` is the next available unreserved feature task id in this checkout:
  - the highest live task id across `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, and `ops/tasks/blocked/` is `1121`; and
  - `rg -n 'RBR-1122' ops/tasks ops/state -g '*.md'` returned only historical mentions inside done-task notes in this run.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- `RBR-1120` closed the exact runtime prerequisite and explicitly left same-family publication and benchmark catch-up for later planning passes, and the narrow same-family owner-path check in this run confirms publication, not another implementation prerequisite, is now the missing exact slice:
  - `tests/python/test_callable_replacement_parity_suite.py` already contains direct bytes parity coverage for the bounded numbered module/pattern and named module/pattern workflows on `rb"a((b|c)+)\\2d"` and `rb"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d"`;
  - `tests/conformance/fixtures/quantified_nested_group_alternation_branch_local_backreference_callable_replacement_workflows.py` still defaults to `text_model: "str"` and publishes only the eight exact `str` callable workflows for that manifest;
  - `tests/conformance/test_combined_correctness_scorecards.py` still requires only representative `str` ids for the quantified branch-local callable slice; and
  - `reports/correctness/latest.py` still shows `collection.replacement.quantified_nested_group_alternation_branch_local_backreference.callable` with `text_models == ['str']`, while `benchmarks/workloads/nested_group_callable_replacement_boundary.py` and `reports/benchmarks/latest.py` also still carry only the adjacent `str` workload quartet, leaving benchmark catch-up as the later same-family follow-on rather than this task.
- `ops/state/backlog.md` and the queue-frontier prose in `ops/state/current_status.md` already honestly describe the post-drain frontier for a single ready feature task: no ready feature follow-on currently survives in this checkout, so this one-task refill does not need tracked state-prose edits.
