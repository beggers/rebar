# RBR-1173: Publish conditional group-exists alternation callable bytes workflows

Status: done
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Reopen the shared `conditional-group-exists-callable-replacement-workflows` correctness frontier with the exact bytes alternation-heavy callable rows that `RBR-1171` already made Rust-backed on the shared parity owner path, publishing that bounded conditional callable slice before any same-family benchmark catch-up, nested callable follow-ons, or quantified callable follow-ons widen this family again.

## Pattern Pair
- `rebar.sub(rb"a(b)?c(?(1)(de|df)|(eg|eh))", callable_match_group(1, suffix=b"x"), b"zzabcdezz")`
- `rebar.compile(rb"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))").subn(callable_match_group("word", suffix=b"x"), b"zzacehzz", 1)`

## Deliverables
- `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- Extend `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` with exactly the eight adjacent bytes alternation-heavy callable rows already exercised on the shared direct parity owner path for `rb"a(b)?c(?(1)(de|df)|(eg|eh))"` and `rb"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))"`:
  - add numbered module `sub()` and `subn()` rows using `callable_match_group(1, suffix=b"x")`, with the present-arm success cases on `b"zzabcdezz"` / `b"zzabcdfzz"` and the absent-capture `TypeError` cases on `b"zzacegzz"` / `b"zzacehzz"`;
  - add numbered compiled-pattern `sub()` and `subn()` rows for the same present-arm success and absent-capture `TypeError` workflows;
  - add named module `sub()` and `subn()` rows using `callable_match_group("word", suffix=b"x")`, with the matching present-arm success and absent-capture `TypeError` workflows; and
  - add named compiled-pattern `sub()` and `subn()` rows for the same named workflows.
- Keep the work on the existing conditional callable correctness owner path instead of creating another manifest or detached publication table:
  - update `tests/python/test_callable_replacement_parity_suite.py` only as needed so the shared callable manifest expectations and representative publication assertions stay aligned with the widened alternation-heavy bytes slice on `conditional-group-exists-callable-replacement-workflows`;
  - update `tests/conformance/test_combined_correctness_scorecards.py` only as needed so the representative `conditional-group-exists-callable-replacement-workflows` scorecard expectations stay aligned with the widened bytes publication slice; and
  - preserve the already-published simple two-arm present/absent plus `count=-1` `str`/bytes callable rows and the adjacent alternation-heavy `str` rows on the same owner path.
- Regenerate `reports/correctness/latest.py` honestly on the tracked combined correctness surface:
  - the tracked report gains the eight new bytes alternation-heavy callable rows for `collection.replacement.conditional_group_exists.callable`;
  - the exact callable manifest moves from `32` passing cases to `40` passing cases with no new explicit failures or unimplemented rows;
  - the combined correctness summary moves from `1685/1685` passing cases to `1693/1693` passing cases while the manifest count stays at `114`; and
  - do not widen this run into benchmark publication, callable-helper expansion beyond `callable_match_group`, nested conditional callable follow-ons, quantified conditional callable follow-ons, or broader replacement-owner families.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists and bytes and callable_replacement and alternation'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/rbr-1173-conditional-callable-alternation-bytes.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or tracked ops state prose in this run.
- Reuse the existing `conditional_group_exists_callable_replacement_workflows.py` manifest and shared callable parity suite. Do not create another correctness manifest, another callable parity module, or a detached conditional callable publication file.
- Keep the scope pinned to the exact eight bytes alternation-heavy callable rows above. Leave same-family benchmark catch-up, nested conditional callable follow-ons, quantified conditional callable follow-ons, and broader callable helper expansion for later tasks.

## Notes
- `RBR-1173` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this run; and
  - `rg -n 'RBR-1173|alternation callable bytes workflows|alternation-callable-bytes-workflows' ops/tasks ops/state -g '*.md'` matched only historical mentions inside completed task files and an architecture-task note, not a live reservation for this id.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The newest done same-family frontier leaves this exact correctness-publication slice concrete after `RBR-1171`:
  - `ops/tasks/done/RBR-1171-implement-conditional-group-exists-alternation-callable-bytes-parity.md` completed the missing Rust-backed bytes parity slice and explicitly left correctness publication, benchmark catch-up, nested callable follow-ons, and quantified callable follow-ons for later on this bounded conditional callable family;
  - `ops/tasks/done/RBR-1169-benchmark-conditional-group-exists-alternation-callable-str-workloads.md` had already closed the adjacent `str` benchmark catch-up, so the next smallest same-family slice is the bytes correctness publication rather than another benchmark-only row;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists and bytes and callable_replacement and alternation'` returned `33 passed, 4056 deselected` in this planning run, confirming the exact bytes alternation callable owner path already matches CPython on the shared parity surface; and
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/feature-planning-conditional-callable-check.py` returned `32 executed / 32 passed` in this planning run, confirming the current correctness publication still stops before these eight bytes alternation rows.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists and bytes and callable_replacement and alternation'` returned `33 passed, 4056 deselected`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py` returned `45 passed, 2324 subtests passed`;
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/rbr-1173-conditional-callable-alternation-bytes.py` is expected to move from the currently validated `32 executed / 32 passed` to `40 executed / 40 passed` once this publication lands; and
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py` is expected to move from the currently validated `1685 executed / 1685 passed` to `1693 executed / 1693 passed` once this publication lands.

## Completion
- Added the exact eight bytes alternation-heavy callable `sub()`/`subn()` publication rows to `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` and updated the shared callable parity/scorecard expectations on the existing owner path.
- Republished `reports/correctness/latest.py`; the tracked callable manifest now shows `40` executed / `40` passed for `collection.replacement.conditional_group_exists.callable`, and the tracked combined summary now shows `1693` executed / `1693` passed across `114` manifests.
- Verification completed:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists and bytes and callable_replacement and alternation'` -> `33 passed, 4216 deselected`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py` -> `45 passed, 2332 subtests passed`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/rbr-1173-conditional-callable-alternation-bytes.py` -> `40 executed / 40 passed`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py` -> `1693 executed / 1693 passed`
