# RBR-1189: Publish conditional group-exists quantified callable workflows

Status: ready
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Reopen the shared `conditional-group-exists-callable-replacement-workflows` correctness frontier with the exact quantified conditional callable `str` rows that `RBR-1187` already made Rust-backed on the shared parity owner path, publishing that bounded slice before the adjacent Python-path benchmark catch-up, bytes mirrors, or broader callable-helper expansion widen this family again.

## Pattern Pair
- `rebar.sub(r"a(b)?c(?(1)d|e){2}", lambda m: m.group(1) + "x", "zzabcddzz")`
- `rebar.compile(r"a(?P<word>b)?c(?(word)d|e){2}").subn(lambda m: m.group("word") + "x", "zzaceezz", 1)`

## Deliverables
- `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- Extend `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` with exactly the eight adjacent quantified conditional callable `str` rows already exercised on the shared direct parity owner path for `a(b)?c(?(1)d|e){2}` and `a(?P<word>b)?c(?(word)d|e){2}`:
  - add numbered module `sub()` and `subn()` rows using `lambda m: m.group(1) + "x"`, with the present-arm success case on `"zzabcddzz"` and the absent-capture `TypeError` case on `"zzaceezz"`;
  - add numbered compiled-pattern `sub()` and `subn()` rows for the same present-arm success and absent-capture `TypeError` workflows;
  - add named module `sub()` and `subn()` rows using `lambda m: m.group("word") + "x"`, with the matching present-arm success and absent-capture `TypeError` workflows; and
  - add named compiled-pattern `sub()` and `subn()` rows for the same named workflows.
- Keep the work on the existing conditional callable correctness owner path instead of creating another manifest or detached publication table:
  - update `tests/python/test_callable_replacement_parity_suite.py` only as needed so the shared callable manifest expectations and representative publication assertions stay aligned with the widened quantified conditional callable slice on `conditional-group-exists-callable-replacement-workflows`;
  - update `tests/conformance/test_combined_correctness_scorecards.py` only as needed so the representative `conditional-group-exists-callable-replacement-workflows` scorecard expectations stay aligned with the widened quantified callable publication slice; and
  - preserve the already-published two-arm, alternation-heavy, and nested conditional callable `str` and `bytes` rows plus the surrounding replacement-owner families on the same owner path.
- Regenerate `reports/correctness/latest.py` honestly on the tracked combined correctness surface:
  - the tracked report gains the eight new quantified conditional callable `str` rows for `collection.replacement.conditional_group_exists.callable`;
  - the exact callable manifest moves from `56` passing cases to `64` passing cases with no new explicit failures or unimplemented rows;
  - the combined correctness summary moves from `1709/1709` passing cases to `1717/1717` passing cases while the manifest count stays at `114`; and
  - do not widen this run into benchmark publication, bytes mirrors, or broader callable-helper expansion beyond `match.group(...) + "x"`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'quantified and conditional_group_exists and callable_replacement'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/rbr-1189-conditional-quantified-callable.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or tracked ops state prose in this run.
- Reuse the existing `conditional_group_exists_callable_replacement_workflows.py` manifest and shared callable parity suite. Do not create another correctness manifest, another callable parity module, or a detached conditional callable publication file.
- Keep the scope pinned to the exact eight quantified conditional callable `str` rows above. Leave the same-family Python-path benchmark catch-up, bytes mirrors, and broader callable-helper expansion for later tasks.

## Notes
- `RBR-1189` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contain no active feature task in this run; and
  - `rg -n "RBR-1189|RBR-1190|quantified callable" ops/tasks ops/state -g '*.md'` matched only stale completion-note mentions, not a live reservation for this id.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The newest done same-family frontier leaves this exact correctness-publication slice concrete after `RBR-1187`:
  - `ops/tasks/done/RBR-1187-implement-conditional-group-exists-quantified-callable-parity.md` completed the bounded quantified conditional callable `str` parity slice and explicitly left correctness publication, bytes mirrors, benchmark catch-up, and broader callable-helper expansion for later on this owner path;
  - `tests/python/test_callable_replacement_parity_suite.py` already covers the exact numbered and named module/pattern quantified conditional callable `sub()` and `subn()` success and absent-capture `TypeError` workflows on the shared direct parity surface;
  - `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` and `reports/correctness/latest.py` still stop at the two-arm, alternation-heavy, and nested conditional callable publication rows, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/feature-planning-conditional-quantified-callable-current.py` returned `56 executed / 56 passed`; and
  - the adjacent benchmark owner path in `benchmarks/workloads/conditional_group_exists_boundary.py` already anchors the same exact quantified accepted patterns and haystacks on the existing Python-path benchmark surface, but it still stops at constant-replacement rows for this quantified slice, which leaves benchmark catch-up as the concrete post-publication survivor rather than another broad same-family synthesis pass.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'quantified and conditional_group_exists and callable_replacement'` returned `48 passed, 4625 deselected`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py` returned `45 passed, 2340 subtests passed`;
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/feature-planning-conditional-quantified-callable-current.py` returned `56 executed / 56 passed`; and
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py` returned `1709 executed / 1709 passed`.
