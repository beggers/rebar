# RBR-1104: Publish quantified nested-group callable bytes workflows

Status: done
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Catch the newly landed quantified nested-group callable bytes runtime slice up on the existing correctness owner path by publishing the exact bounded bytes workflows that `RBR-1102` enabled, before any same-family benchmark catch-up or broader callable-replacement expansion reopens the frontier.

## Pattern Pair
- `rebar.sub(rb"a((bc)+)d", lambda m: b"<" + m.group(1) + b">", b"zzabcdzz")`
- `rebar.compile(rb"a(?P<outer>(?P<inner>bc)+)d").subn(lambda m: b"<" + m.group("inner") + b">", b"zzabcbcdabcbcdzz", 1)`

## Deliverables
- `tests/conformance/fixtures/quantified_nested_group_callable_replacement_workflows.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- Extend `tests/conformance/fixtures/quantified_nested_group_callable_replacement_workflows.py` on the existing owner path with only the adjacent bytes cases for the bounded quantified nested-group callable slice that now works in `rebar`:
  - numbered module `sub()` and `subn(count=1)` rows for `rb"a((bc)+)d"` that exercise `group(1)` and `group(2)`;
  - numbered compiled-pattern `sub()` and `subn(count=1)` rows for `rb"a((bc)+)d"` on the same bounded repeated-inner-capture slice;
  - named module `sub()` and `subn(count=1)` rows for `rb"a(?P<outer>(?P<inner>bc)+)d"` that exercise `group("outer")` and `group("inner")`; and
  - named compiled-pattern `sub()` and `subn(count=1)` rows for `rb"a(?P<outer>(?P<inner>bc)+)d"` on that same bounded first-match-only slice.
- Keep the publication bounded to the existing quantified nested-group callable manifest:
  - do not widen into alternation inside the repeated site, branch-local backreferences, broader counted repeats, benchmark workloads, or another correctness manifest in this run; and
  - keep the existing `str` rows on the same manifest green.
- Refresh `tests/conformance/test_combined_correctness_scorecards.py` only as needed so the combined correctness scorecard explicitly requires representative bytes ids for `quantified-nested-group-callable-replacement-workflows`.
- Regenerate `reports/correctness/latest.py` so the published scorecard includes the new bytes callable rows and remains fully passing with no new honest gaps or explicit failures:
  - `REPORT["summary"]` moves from `1613` total / `1613` passed / `0` failed / `0` unimplemented to `1621` / `1621` / `0` / `0`;
  - `REPORT["fixtures"]["manifest_count"]` remains `114`;
  - `REPORT["manifests"]["quantified-nested-group-callable-replacement-workflows"]["summary"]` moves from `8` total / `8` passed / `0` failed / `0` unimplemented to `16` / `16` / `0` / `0`; and
  - the regenerated artifact publishes adjacent bytes ids for `collection.replacement.quantified_nested_group.callable` so that suite no longer reports only `text_models == ['str']`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'quantified_nested_group and callable and bytes'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the work on the Python-facing correctness publication path. Do not widen this task into benchmark manifests, benchmark reports, README text, or tracked ops state prose.
- New runtime behavior is already the prerequisite here; do not spend this task on more Rust execution changes unless a narrow fixture publication blocker forces a tiny bridge fix.
- Preserve the same bounded quantified nested-group callable semantics that `RBR-1102` landed; this task is for correctness publication, not broader callback semantics.

## Notes
- `RBR-1104` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contain no live feature task file before this task is added; and
  - `rg -n 'RBR-1104|RBR-1105|RBR-1106' ops/tasks ops/state -g '*.md'` returned no reserved future feature id in this run.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The narrow same-family check in this run shows publication, not another implementation prerequisite, is the next bounded slice:
  - `RBR-1102` already landed direct bytes callable parity coverage in `tests/python/test_callable_replacement_parity_suite.py` for the bounded quantified nested-group module and compiled-pattern paths;
  - `tests/conformance/fixtures/quantified_nested_group_callable_replacement_workflows.py` still publishes only the eight `str` cases for `quantified-nested-group-callable-replacement-workflows`;
  - `reports/correctness/latest.py` still reports `collection.replacement.quantified_nested_group.callable` with `text_models == ['str']`; and
  - the adjacent benchmark owner path in `benchmarks/workloads/nested_group_callable_replacement_boundary.py` already contains the same quantified nested-group family, so correctness catch-up is the next same-family follow-on before any benchmark task.

## Completion
- Added the adjacent eight bytes callable cases to `tests/conformance/fixtures/quantified_nested_group_callable_replacement_workflows.py` without widening beyond the existing quantified nested-group callable manifest, and updated the combined scorecard expectations plus callable-manifest parity contract to treat the manifest as mixed text.
- Regenerated `reports/correctness/latest.py` and verified the tracked artifact now reports `1621` total / `1621` passed / `0` failed / `0` unimplemented cases across `114` manifests, with `quantified-nested-group-callable-replacement-workflows` at `16` total / `16` passed and `collection.replacement.quantified_nested_group.callable` publishing `['bytes', 'str']` text models.
- Verification:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'quantified_nested_group and callable and bytes'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'quantified-nested-group-callable-replacement-workflows and (test_callable_replacement_cases_stay_aligned_with_published_fixture or test_mixed_text_callable_manifest_partitions_track_pending_or_landed_bytes_cases)'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`
