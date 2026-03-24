# RBR-1236: Publish conditional group-exists nested callable None-count workflows

Status: ready
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Publish the already-supported nested two-arm conditional callable `count=None` slice on the shared conditional callable replacement correctness owner path by adding the exact bounded invalid-count workflows that the live runtime behavior already matches against CPython for both `str` and `bytes`.

## Pattern Pair
- `rebar.sub(r"a(b)?c(?(1)(?(1)d|e)|f)", lambda m: m.group(1) + "x", "zzabcdzz", None)`
- `rebar.compile(rb"a(?P<word>b)?c(?(word)(?(word)d|e)|f)").subn(lambda m: m.group("word") + b"x", b"zzacfzz", None)`

## Deliverables
- `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- Extend `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` with exactly the eight adjacent nested conditional callable `count=None` workflows that sit immediately behind the closed alternation-heavy `count=None` slice on the shared owner path:
  - add the four `str` workflows for `a(b)?c(?(1)(?(1)d|e)|f)` and `a(?P<word>b)?c(?(word)(?(word)d|e)|f)` by mirroring the already-published nested negative-count quartet while passing `None`, keeping the bounded shape on module `sub`, module `subn`, compiled-`Pattern` `sub`, and compiled-`Pattern` `subn`;
  - add the matching four `bytes` workflows for `rb"a(b)?c(?(1)(?(1)d|e)|f)"` and `rb"a(?P<word>b)?c(?(word)(?(word)d|e)|f)"` on the same numbered and named module/pattern matrix;
  - keep the replacement descriptors on the existing `callable_match_group` helper pinned to group `1` or `"word"` so CPython's invalid-count `TypeError` stays explicit without inventing another callable helper shape; and
  - keep the slice bounded to the nested top-level conditional callable family only, leaving quantified `count=None`, broader callable count-contract publication, and benchmark catch-up for later tasks.
- Keep the work on the existing conditional callable correctness owner path instead of creating another manifest or detached publication file:
  - update `tests/python/test_callable_replacement_parity_suite.py` only as needed so the shared callable owner-path stem lists, manifest expectations, and `count=None` parity coverage stay aligned with the widened nested slice;
  - update `tests/conformance/test_combined_correctness_scorecards.py` only as needed so the `conditional-group-exists-callable-replacement-workflows` manifest expectations, representative case ordering, and mixed-text scorecard sync stay aligned with the widened nested `count=None` slice; and
  - do not widen this run into benchmark publication, Rust implementation work, or non-conditional callable-owner expansion.
- Regenerate `reports/correctness/latest.py` honestly on the tracked combined correctness surface:
  - the `collection.replacement.conditional_group_exists.callable` suite grows from `184` executed cases to `192` executed cases with all `192` passing and `0` unimplemented outcomes; and
  - the tracked combined correctness summary moves from `1837` total cases / `1837` passes / `0` failures / `0` unimplemented across `114` manifests to `1845` total cases / `1845` passes / `0` failures / `0` unimplemented across the same `114` manifests.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'none_count_matches_cpython_typeerror'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'conditional_group_exists_callable_scorecards'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/rbr-1236-conditional-callable-nested-none-count.py`

## Constraints
- Keep the scope pinned to the exact eight nested conditional callable `count=None` workflows above. Leave benchmark catch-up, quantified `count=None`, or broader callable argument-contract publication for a separate planning pass.
- Reuse the existing `conditional_group_exists_callable_replacement_workflows.py` fixture and combined correctness scorecard owner path. Do not create another callable replacement manifest, another conformance module, or a detached conditional callable contract file.
- Keep this as Python-surface publication work only; do not widen the run into benchmark manifests or Rust-boundary implementation changes.

## Notes
- `RBR-1236` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this planning run; and
  - the highest filed task before this seed was `RBR-1235`.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- One narrow same-owner-path scan keeps this exact follow-on concrete after `RBR-1234`:
  - `ops/tasks/done/RBR-1234-benchmark-conditional-group-exists-alternation-callable-none-count-workloads.md` explicitly left nested, quantified, or broader callable count-contract publication for later tasks on the same owner route;
  - `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` already publishes the nested callable present, absent-exception, near-miss, and negative-count rows for `str` and `bytes`, but it does not yet publish any nested `count=None` rows on that owner path;
  - `benchmarks/workloads/conditional_group_exists_boundary.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` already carry the adjacent nested callable negative-count benchmark quartet, so the same-route nested callable `count=None` benchmark catch-up stays the concrete post-drain follow-on once this correctness publication lands; and
  - a direct runtime probe over four exact nested numbered and named module/pattern `str` and `bytes` `count=None` calls returned the same `TypeError: 'NoneType' object cannot be interpreted as an integer` in both `re` and `rebar`, confirming the underlying bounded behavior already exists on the current branch.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'none_count_matches_cpython_typeerror'` returned `1136 passed, 4990 deselected`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'conditional_group_exists_callable_scorecards'` returned `4 passed, 44 deselected`; and
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/feature-planning-conditional-callable-current.py` returned `184 executed / 184 passed / 0 unimplemented`.
