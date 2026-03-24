Status: ready
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Publish the already-supported quantified two-arm conditional callable `count=None` slice on the shared conditional callable replacement correctness owner path by adding the exact bounded invalid-count workflows that the live runtime behavior already matches against CPython for both `str` and `bytes`.

## Pattern Pair
- `rebar.sub(r"a(b)?c(?(1)d|e){2}", lambda m: m.group(1) + "x", "zzabcddzz", None)`
- `rebar.compile(rb"a(?P<word>b)?c(?(word)d|e){2}").subn(lambda m: m.group("word") + b"x", b"zzaceezz", None)`

## Deliverables
- `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- Extend `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` with exactly the eight adjacent quantified conditional callable `count=None` workflows that sit immediately behind the closed nested `count=None` slice on the shared owner path:
  - add the four `str` workflows for `a(b)?c(?(1)d|e){2}` and `a(?P<word>b)?c(?(word)d|e){2}` by mirroring the already-published quantified negative-count quartet while passing `None`, keeping the bounded shape on module `sub`, module `subn`, compiled-`Pattern` `sub`, and compiled-`Pattern` `subn`;
  - add the matching four `bytes` workflows for `rb"a(b)?c(?(1)d|e){2}"` and `rb"a(?P<word>b)?c(?(word)d|e){2}"` on the same numbered and named module/pattern matrix;
  - keep the replacement descriptors on the existing `callable_match_group` helper pinned to group `1` or `"word"` so CPython's invalid-count `TypeError` stays explicit without inventing another callable helper shape; and
  - keep the slice bounded to the quantified two-arm conditional callable family only, leaving quantified `count=None` benchmark catch-up and broader callable count-contract publication for later tasks.
- Keep the work on the existing conditional callable correctness owner path instead of creating another manifest or detached publication file:
  - update `tests/python/test_callable_replacement_parity_suite.py` only as needed so the shared callable owner-path stem lists, manifest expectations, and `count=None` parity coverage stay aligned with the widened quantified slice;
  - update `tests/conformance/test_combined_correctness_scorecards.py` only as needed so the `conditional-group-exists-callable-replacement-workflows` manifest expectations, representative case ordering, and mixed-text scorecard sync stay aligned with the widened quantified `count=None` slice; and
  - do not widen this run into benchmark publication, Rust implementation work, or non-conditional callable-owner expansion.
- Regenerate `reports/correctness/latest.py` honestly on the tracked combined correctness surface:
  - the `collection.replacement.conditional_group_exists.callable` suite grows from `192` executed cases to `200` executed cases with all `200` passing and `0` unimplemented outcomes; and
  - the tracked combined correctness summary moves from `1845` total cases / `1845` passes / `0` failures / `0` unimplemented across `114` manifests to `1853` total cases / `1853` passes / `0` failures / `0` unimplemented across the same `114` manifests.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'none_count_matches_cpython_typeerror'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'conditional_group_exists_callable_scorecards'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/rbr-1240-conditional-callable-quantified-none-count.py`

## Constraints
- Keep the scope pinned to the exact eight quantified conditional callable `count=None` workflows above. Leave benchmark catch-up and broader callable count-contract expansion for separate planning passes.
- Reuse the existing `conditional_group_exists_callable_replacement_workflows.py` fixture and combined correctness scorecard owner path. Do not create another callable replacement manifest, another conformance module, or a detached conditional callable contract file.
- Keep this as Python-surface publication work only; do not widen the run into benchmark manifests or Rust-boundary implementation changes.

## Notes
- `RBR-1240` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this planning run; and
  - the highest filed task before this seed was `RBR-1239`.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- One narrow same-owner-path scan keeps this exact follow-on concrete after `RBR-1238`:
  - `ops/tasks/done/RBR-1238-benchmark-conditional-group-exists-nested-callable-none-count-workloads.md` explicitly leaves quantified `count=None` and broader callable count-contract work for later tasks on the same owner route;
  - `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` already publishes the quantified callable present, absent-exception, near-miss, and negative-count rows for `str` and `bytes`, but it does not yet publish any quantified `count=None` rows on that owner path;
  - `benchmarks/workloads/conditional_group_exists_boundary.py` already carries the adjacent quantified callable present, absent-exception, near-miss, and negative-count workloads, so the same-route quantified callable `count=None` benchmark catch-up stays the concrete post-drain follow-on once this correctness publication lands; and
  - a direct runtime probe over four exact quantified numbered and named module/pattern `str` and `bytes` `count=None` calls returned the same `TypeError: 'NoneType' object cannot be interpreted as an integer` in both `re` and `rebar`, confirming the underlying bounded behavior already exists on the current branch.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'none_count_matches_cpython_typeerror'` returned `1160 passed, 5030 deselected`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'conditional_group_exists_callable_scorecards'` returned `5 passed, 44 deselected`; and
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/feature-planning-conditional-callable-current.py` returned `192 executed / 192 passed / 0 unimplemented`.
