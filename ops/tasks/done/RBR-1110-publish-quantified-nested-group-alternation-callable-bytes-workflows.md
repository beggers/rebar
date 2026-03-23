# RBR-1110: Publish quantified nested-group alternation callable bytes workflows

Status: done
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Catch the newly landed quantified nested-group alternation callable bytes runtime slice up on the existing correctness owner path by publishing the exact bounded bytes workflows that `RBR-1108` enabled, before any same-family benchmark catch-up or broader callable-replacement expansion reopens the frontier.

## Pattern Pair
- `rebar.sub(rb"a((b|c)+)d", lambda m: m.group(1) + b"x", b"zzabdzz")`
- `rebar.compile(rb"a(?P<outer>(?P<inner>b|c)+)d").subn(lambda m: b"<" + m.group("inner") + b">", b"zzabccdzz", 1)`

## Deliverables
- `tests/conformance/fixtures/quantified_nested_group_alternation_callable_replacement_workflows.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- Extend `tests/conformance/fixtures/quantified_nested_group_alternation_callable_replacement_workflows.py` on the existing owner path with only the adjacent bytes cases for the bounded quantified nested-group alternation callable slice that now works in `rebar`:
  - numbered module `sub()` and `subn(count=1)` rows for `rb"a((b|c)+)d"` that exercise `group(1)` and `group(2)` on the existing lower-bound, mixed-branch, and first-match-only haystacks;
  - numbered compiled-pattern `sub()` and `subn(count=1)` rows for `rb"a((b|c)+)d"` on those same bounded repeated-branch and first-match-only slices;
  - named module `sub()` and `subn(count=1)` rows for `rb"a(?P<outer>(?P<inner>b|c)+)d"` that exercise `group("outer")` and `group("inner")`; and
  - named compiled-pattern `sub()` and `subn(count=1)` rows for `rb"a(?P<outer>(?P<inner>b|c)+)d"` on that same bounded mixed-branch and first-match-only slice.
- Keep the publication bounded to the existing quantified nested-group alternation callable manifest:
  - do not widen into branch-local backreferences, broader counted repeats, benchmark workloads, or another correctness manifest in this run; and
  - keep the existing `str` rows on the same manifest green.
- Refresh `tests/conformance/test_combined_correctness_scorecards.py` only as needed so the combined correctness scorecard explicitly requires representative bytes ids for `quantified-nested-group-alternation-callable-replacement-workflows`.
- Regenerate `reports/correctness/latest.py` so the published scorecard includes the new bytes callable rows and remains fully passing with no new honest gaps or explicit failures:
  - `REPORT["summary"]` moves from `1621` total / `1621` passed / `0` failed / `0` unimplemented to `1629` / `1629` / `0` / `0`;
  - `REPORT["fixtures"]["manifest_count"]` remains `114`;
  - `quantified-nested-group-alternation-callable-replacement-workflows` moves from `8` total / `8` passed / `0` failed / `0` unimplemented to `16` / `16` / `0` / `0`; and
  - `collection.replacement.quantified_nested_group_alternation.callable` no longer reports only `text_models == ['str']`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'quantified_nested_group_alternation and callable and bytes'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the work on the Python-facing correctness publication path. Do not widen this task into benchmark manifests, benchmark reports, README text, or tracked ops state prose.
- New runtime behavior is already the prerequisite here; do not spend this task on more Rust execution changes unless a narrow fixture publication blocker forces a tiny bridge fix.
- Preserve the same bounded quantified nested-group alternation callable semantics that `RBR-1108` landed; this task is for correctness publication, not broader callback semantics.

## Notes
- `RBR-1110` is the next available unreserved feature task id in this checkout:
  - the highest live task id across `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, and `ops/tasks/blocked/` is `1109`; and
  - `rg -n 'RBR-1110|RBR-1111|RBR-1112' ops/tasks ops/state -g '*.md'` returned only historical mentions inside done-task notes in this run.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The newest feature frontier note leaves same-family publication as the next concrete deferred slice, and the narrow owner-path check in this run confirms publication, not another implementation prerequisite, is now missing:
  - `ops/tasks/done/RBR-1108-implement-quantified-nested-group-alternation-callable-bytes-parity.md` explicitly leaves correctness publication and later benchmark catch-up for this bounded bytes slice to later tasks;
  - `tests/conformance/fixtures/quantified_nested_group_alternation_callable_replacement_workflows.py` still publishes only the eight `str` cases for `quantified-nested-group-alternation-callable-replacement-workflows`;
  - `tests/conformance/test_combined_correctness_scorecards.py` still requires only four representative `str` ids for that manifest, and `reports/correctness/latest.py` still reports `collection.replacement.quantified_nested_group_alternation.callable` with `text_models == ['str']`; and
  - direct public-path probes in this run showed the exact numbered and named bytes `sub()` / `subn(count=1)` calls above now match CPython, so the runtime prerequisite has already landed.
- `ops/state/backlog.md` and the queue-frontier prose in `ops/state/current_status.md` already honestly say that no ready feature follow-on currently survives after the likely same-cycle drain, so this one-task refill does not need tracked state-prose changes.

## Completion
- Extended `tests/conformance/fixtures/quantified_nested_group_alternation_callable_replacement_workflows.py` with the adjacent eight bytes callable rows only, keeping the existing `str` rows intact while publishing numbered and named module/pattern `sub()` and `subn(count=1)` workflows for the bounded `rb"a((b|c)+)d"` and `rb"a(?P<outer>(?P<inner>b|c)+)d"` slice.
- Refreshed the representative manifest expectations in `tests/conformance/test_combined_correctness_scorecards.py` and the adjacent callable fixture-shape contract in `tests/python/test_callable_replacement_parity_suite.py` so the widened published manifest now requires bytes ids and mixed `str`/`bytes` text-model coverage on the existing owner path.
- Regenerated `reports/correctness/latest.py`; the tracked publication now reports `1629` total / `1629` passed / `0` failed / `0` unimplemented cases, keeps `REPORT["fixtures"]["manifest_count"] == 114`, moves `quantified-nested-group-alternation-callable-replacement-workflows` to `16` total / `16` passed / `0` failed / `0` unimplemented, and shows `collection.replacement.quantified_nested_group_alternation.callable` with `text_models == ['bytes', 'str']`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'quantified_nested_group_alternation and callable and bytes'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`
