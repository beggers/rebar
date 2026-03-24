# RBR-1185: Publish conditional group-exists nested callable bytes workflows

Status: done
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Reopen the shared `conditional-group-exists-callable-replacement-workflows` correctness frontier with the exact nested conditional callable `bytes` rows that `RBR-1182` already made Rust-backed on the shared parity owner path, publishing that bounded slice before benchmark catch-up, quantified conditional callable follow-ons, or broader callable-helper expansion widen this family again.

## Pattern Pair
- `rebar.sub(rb"a(b)?c(?(1)(?(1)d|e)|f)", lambda m: m.group(1) + b"x", b"zzabcdzz")`
- `rebar.compile(rb"a(?P<word>b)?c(?(word)(?(word)d|e)|f)").subn(lambda m: m.group("word") + b"x", b"zzacfzz", 1)`

## Deliverables
- `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- Extend `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` with exactly the eight adjacent nested conditional callable `bytes` rows already exercised on the shared direct parity owner path for `rb"a(b)?c(?(1)(?(1)d|e)|f)"` and `rb"a(?P<word>b)?c(?(word)(?(word)d|e)|f)"`:
  - add numbered module `sub()` and `subn()` rows using `lambda m: m.group(1) + b"x"`, with the present-arm success case on `b"zzabcdzz"` and the absent-capture `TypeError` case on `b"zzacfzz"`;
  - add numbered compiled-pattern `sub()` and `subn()` rows for the same present-arm success and absent-capture `TypeError` workflows;
  - add named module `sub()` and `subn()` rows using `lambda m: m.group("word") + b"x"`, with the matching present-arm success and absent-capture `TypeError` workflows; and
  - add named compiled-pattern `sub()` and `subn()` rows for the same named workflows.
- Keep the work on the existing conditional callable correctness owner path instead of creating another manifest or detached publication table:
  - update `tests/python/test_callable_replacement_parity_suite.py` only as needed so the shared callable manifest expectations and representative publication assertions stay aligned with the widened nested conditional mixed-text slice on `conditional-group-exists-callable-replacement-workflows`;
  - update `tests/conformance/test_combined_correctness_scorecards.py` only as needed so the representative `conditional-group-exists-callable-replacement-workflows` mixed-text scorecard expectations stay aligned with the widened nested callable publication slice; and
  - preserve the already-published simple two-arm, alternation-heavy, `count=-1`, and nested `str` callable rows plus the surrounding replacement-owner families on the same owner path.
- Regenerate `reports/correctness/latest.py` honestly on the tracked combined correctness surface:
  - the tracked report gains the eight new nested conditional callable `bytes` rows for `collection.replacement.conditional_group_exists.callable`;
  - the exact callable manifest moves from `48` passing cases to `56` passing cases with no new explicit failures or unimplemented rows;
  - the combined correctness summary moves from `1701/1701` passing cases to `1709/1709` passing cases while the manifest count stays at `114`; and
  - do not widen this run into benchmark publication, quantified conditional callable follow-ons, or broader callable-helper expansion beyond `match.group(...) + b"x"`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists and nested and bytes and callable_replacement'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/rbr-1185-conditional-nested-callable-bytes.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or tracked ops state prose in this run.
- Reuse the existing `conditional_group_exists_callable_replacement_workflows.py` manifest and shared callable parity suite. Do not create another correctness manifest, another callable parity module, or a detached conditional callable publication file.
- Keep the scope pinned to the exact eight nested conditional callable `bytes` rows above. Leave same-family benchmark catch-up, quantified conditional callable follow-ons, and broader callable helper expansion for later tasks.

## Notes
- `RBR-1185` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this run; and
  - `rg -n "RBR-1185|RBR-1186|nested-callable-bytes|conditional group-exists nested callable bytes" ops/tasks ops/state -g '*.md'` matched only stale frontier prose, not a live task reservation for either id.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The newest done same-family frontier leaves this exact correctness-publication slice concrete after `RBR-1182`:
  - `ops/tasks/done/RBR-1182-implement-conditional-group-exists-nested-callable-bytes-parity.md` completed the bounded nested conditional callable `bytes` parity slice and explicitly left correctness publication, benchmark catch-up, quantified conditional callable follow-ons, and broader callable-helper expansion for later on this owner path;
  - `tests/python/test_callable_replacement_parity_suite.py` already covers the exact numbered and named module/pattern nested conditional callable `bytes` `sub()` and `subn()` success and absent-capture `TypeError` workflows on the shared parity surface;
  - `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` and `reports/correctness/latest.py` still stop at the nested callable `str` publication rows for this spelling, so the published callable manifest remains short of the newly landed bytes parity slice; and
  - the adjacent benchmark owner path in `benchmarks/workloads/conditional_group_exists_boundary.py` still exposes only the nested conditional callable `str` benchmark slice for this spelling, which keeps benchmark catch-up as the exact post-publication survivor rather than a broader quantified follow-on.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists and nested and bytes and callable_replacement'` returned `32 passed, 4415 deselected`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py` returned `45 passed, 2336 subtests passed`;
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/rbr-1185-conditional-nested-callable-bytes.py` is expected to move from the currently validated `48 executed / 48 passed` to `56 executed / 56 passed` once this publication lands; and
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py` is expected to move from the current `1701 executed / 1701 passed` surface to `1709 executed / 1709 passed` once this publication lands.

## Completion
- Added the exact eight nested conditional callable `bytes` publication rows on the shared `conditional-group-exists-callable-replacement-workflows` owner path and updated the shared parity-suite and combined-scorecard expectations to include the widened mixed-text nested slice.
- Verified `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists and nested and bytes and callable_replacement'` -> `33 passed, 4575 deselected`.
- Verified `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py` -> `45 passed, 2340 subtests passed`.
- Verified `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/rbr-1185-conditional-nested-callable-bytes.py` -> `56 executed / 56 passed`.
- Regenerated `reports/correctness/latest.py`; the tracked report now shows `collection.replacement.conditional_group_exists.callable` at `56/56` and the combined published surface at `1709/1709` across `114` manifests.
