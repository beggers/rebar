# RBR-1195: Publish conditional group-exists quantified callable bytes workflows

Status: done
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Reopen the shared `conditional-group-exists-callable-replacement-workflows` correctness frontier with the exact quantified conditional callable `bytes` rows that `RBR-1193` already made Rust-backed on the shared parity owner path, publishing that bounded slice before the adjacent Python-path benchmark catch-up or broader callable-helper expansion widen this family again.

## Pattern Pair
- `rebar.sub(rb"a(b)?c(?(1)d|e){2}", lambda m: m.group(1) + b"x", b"zzabcddzz")`
- `rebar.compile(rb"a(?P<word>b)?c(?(word)d|e){2}").subn(lambda m: m.group("word") + b"x", b"zzaceezz", 1)`

## Deliverables
- `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- Extend `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` with exactly the eight adjacent quantified conditional callable `bytes` rows already exercised on the shared direct parity owner path for `rb"a(b)?c(?(1)d|e){2}"` and `rb"a(?P<word>b)?c(?(word)d|e){2}"`:
  - add numbered module `sub()` and `subn()` rows using `lambda m: m.group(1) + b"x"`, with the present-arm success case on `b"zzabcddzz"` and the absent-capture `TypeError` case on `b"zzaceezz"`;
  - add numbered compiled-pattern `sub()` and `subn()` rows for the same present-arm success and absent-capture `TypeError` workflows;
  - add named module `sub()` and `subn()` rows using `lambda m: m.group("word") + b"x"`, with the matching present-arm success and absent-capture `TypeError` workflows; and
  - add named compiled-pattern `sub()` and `subn()` rows for the same named workflows.
- Keep the work on the existing conditional callable correctness owner path instead of creating another manifest or detached publication table:
  - update `tests/python/test_callable_replacement_parity_suite.py` only as needed so the shared callable manifest expectations and representative publication assertions stay aligned with the widened quantified conditional callable mixed-text slice on `conditional-group-exists-callable-replacement-workflows`;
  - update `tests/conformance/test_combined_correctness_scorecards.py` only as needed so the representative `conditional-group-exists-callable-replacement-workflows` scorecard expectations stay aligned with the widened quantified callable publication slice; and
  - preserve the already-published two-arm, alternation-heavy, nested, and quantified conditional callable `str` rows plus the surrounding replacement-owner families on the same owner path.
- Regenerate `reports/correctness/latest.py` honestly on the tracked combined correctness surface:
  - the tracked report gains the eight new quantified conditional callable `bytes` rows for `collection.replacement.conditional_group_exists.callable`;
  - the exact callable manifest moves from `64` passing cases to `72` passing cases with no new explicit failures or unimplemented rows;
  - the combined correctness summary moves from `1717/1717` passing cases to `1725/1725` passing cases while the manifest count stays at `114`; and
  - do not widen this run into benchmark publication or broader callable-helper expansion beyond `match.group(...) + b"x"`.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists and bytes and callable_replacement and quantified'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/rbr-1195-conditional-quantified-callable-bytes.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or tracked ops state prose in this run.
- Reuse the existing `conditional_group_exists_callable_replacement_workflows.py` manifest and shared callable parity suite. Do not create another correctness manifest, another callable parity module, or a detached conditional callable publication file.
- Keep the scope pinned to the exact eight quantified conditional callable `bytes` rows above. Leave the same-family Python-path benchmark catch-up and broader callable-helper expansion for later tasks.

## Notes
- `RBR-1195` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contain no active feature task in this run; and
  - `rg -n "RBR-1195|RBR-1196|quantified callable bytes|quantified-callable-bytes|conditional group-exists quantified callable bytes" ops/tasks ops/state -g '*.md'` matched only stale completion-note mentions, not a live reservation for this id.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The newest done same-family frontier leaves this exact correctness-publication slice concrete after `RBR-1193`:
  - `ops/tasks/done/RBR-1193-implement-conditional-group-exists-quantified-callable-bytes-parity.md` completed the bounded quantified conditional callable `bytes` parity slice and explicitly left correctness publication, benchmark catch-up, and broader callable-helper expansion for later on this owner path;
  - `tests/python/test_callable_replacement_parity_suite.py` already covers the exact numbered and named module/pattern quantified conditional callable `bytes` `sub()` and `subn()` success and absent-capture `TypeError` workflows on the shared direct parity surface;
  - `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` and `reports/correctness/latest.py` still stop at the quantified conditional callable `str` publication rows for this spelling, leaving the bounded mixed-text publication slice missing on the tracked correctness surface; and
  - the adjacent benchmark owner path in `benchmarks/workloads/conditional_group_exists_boundary.py` still stops at quantified conditional callable `str` workloads for this spelling, which keeps benchmark catch-up as the concrete post-publication survivor rather than another broader same-family synthesis pass.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists and bytes and callable_replacement and quantified'` returned `50 passed, 4775 deselected`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py` returned `45 passed, 2344 subtests passed`;
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/feature-planning-conditional-quantified-callable-bytes-current.py` returned `64 executed / 64 passed`; and
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py` returned `1717 executed / 1717 passed`.

## Completion
- Extended `/home/ubuntu/rebar/tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` with the exact eight quantified conditional callable `bytes` publication rows for numbered and named module/pattern `sub()` and `subn()` workflows, keeping them on the shared conditional callable owner path.
- Updated `/home/ubuntu/rebar/tests/python/test_callable_replacement_parity_suite.py` so the callable manifest contract now expects those eight additional quantified `bytes` rows, the matching `bytes` compile-pattern anchors, and the widened per-helper counts.
- Updated `/home/ubuntu/rebar/tests/conformance/test_combined_correctness_scorecards.py` so the shared representative scorecard expectations now include the quantified `bytes` publication rows and keep the bytes/str representative ordering assertions aligned.
- Republished `/home/ubuntu/rebar/reports/correctness/latest.py`; the tracked artifact now shows `collection.replacement.conditional_group_exists.callable` at `72` executed / `72` passed, `collection.replacement.conditional_group_exists.callable.bytes` at `36` executed / `36` passed, and the combined summary at `1725` executed / `1725` passed across `114` manifests.
- Verification in this run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists and bytes and callable_replacement and quantified'` -> `50 passed, 4951 deselected`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py` -> `45 passed, 2348 subtests passed`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/rbr-1195-conditional-quantified-callable-bytes.py` -> `72 executed / 72 passed`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py` -> `1725 executed / 1725 passed`
