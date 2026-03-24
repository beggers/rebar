# RBR-1232: Publish conditional group-exists alternation callable None-count workflows

Status: done
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Publish the already-supported alternation-heavy two-arm conditional callable `count=None` slice on the shared conditional callable replacement correctness owner path by adding the exact bounded invalid-count workflows that the live direct parity path already matches against CPython for both `str` and `bytes`.

## Pattern Pair
- `rebar.sub(r"a(b)?c(?(1)(de|df)|(eg|eh))", lambda m: m.group(1) + "x", "zzabcdezz", None)`
- `rebar.compile(rb"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))").subn(lambda m: m.group("word") + b"x", b"zzacehzz", None)`

## Deliverables
- `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- Extend `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` with exactly the eight adjacent alternation-heavy conditional callable `count=None` workflows that sit immediately behind `RBR-1230` on the shared owner path:
  - add the four `str` workflows for `a(b)?c(?(1)(de|df)|(eg|eh))` and `a(?P<word>b)?c(?(word)(de|df)|(eg|eh))` by mirroring the already-published alternation-heavy negative-count quartet while passing `None`, keeping the bounded shape on module `sub`, module `subn`, compiled-`Pattern` `sub`, and compiled-`Pattern` `subn`;
  - add the matching four `bytes` workflows for `rb"a(b)?c(?(1)(de|df)|(eg|eh))"` and `rb"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))"` on the same numbered and named module/pattern matrix;
  - keep the replacement descriptors on the existing `callable_match_group` helper pinned to group `1` or `"word"` so CPython's invalid-`count` `TypeError` stays explicit without inventing another callable helper shape; and
  - keep the slice bounded to the alternation-heavy top-level conditional callable family only, leaving nested, quantified, or broader callable count-contract publication for later tasks.
- Keep the work on the existing conditional callable correctness owner path instead of creating another manifest or detached publication file:
  - update `tests/conformance/test_combined_correctness_scorecards.py` only as needed so the `conditional-group-exists-callable-replacement-workflows` manifest expectations, representative case ordering, and mixed-text scorecard sync stay aligned with the widened alternation-heavy `count=None` slice;
  - reuse the existing direct parity owner path in `tests/python/test_callable_replacement_parity_suite.py` as the runtime anchor instead of inventing new callable helpers or another parity source; and
  - do not widen this run into benchmark publication, Rust implementation work, or non-conditional callable-owner expansion.
- Regenerate `reports/correctness/latest.py` honestly on the tracked combined correctness surface:
  - the `collection.replacement.conditional_group_exists.callable` suite grows from `176` executed cases to `184` executed cases with all `184` passing and `0` unimplemented outcomes; and
  - the tracked combined correctness summary moves from `1829` total cases / `1829` passes / `0` failures / `0` unimplemented across `114` manifests to `1837` total cases / `1837` passes / `0` failures / `0` unimplemented across the same `114` manifests.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'none_count_matches_cpython_typeerror and conditional-group-exists'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'conditional_group_exists_callable_scorecards'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/rbr-1232-conditional-callable-alternation-none-count.py`

## Constraints
- Keep the scope pinned to the exact eight alternation-heavy conditional callable `count=None` workflows above. Leave any benchmark catch-up, nested follow-ons, quantified follow-ons, or broader callable argument-contract publication for a separate planning pass.
- Reuse the existing `conditional_group_exists_callable_replacement_workflows.py` fixture and combined correctness scorecard owner path. Do not create another callable replacement manifest, another conformance module, or a detached conditional callable contract file.
- Keep this as Python-surface publication work only; do not widen the run into benchmark manifests or Rust-boundary implementation changes.

## Notes
- `RBR-1232` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this planning run; and
  - `rg -n "RBR-1232|RBR-1233" ops/tasks ops/state -g '*.md'` matched only historical mentions inside completed task files, not a live reservation for either id.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- One narrow same-owner-path scan keeps this exact follow-on concrete behind `RBR-1230`:
  - `ops/tasks/done/RBR-1230-benchmark-conditional-group-exists-alternation-callable-negative-count-workloads.md` explicitly left the same-route alternation-heavy callable `count=None` publication for a separate planning pass;
  - `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` already publishes the alternation-heavy numbered and named callable present/absent rows plus the adjacent negative-count quartet for `str` and `bytes`, but it does not yet publish any alternation-heavy `count=None` rows on that owner path;
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` already keeps the surrounding `conditional-group-exists-boundary` none-count benchmark slice in sync on the same owner route, so the same alternation-heavy `count=None` benchmark catch-up remains the concrete post-drain follow-on once this correctness publication lands; and
  - a direct runtime probe over sixteen numbered and named module/pattern `str` and `bytes` alternation-heavy `count=None` calls returned `cases=16 mismatches=0`, confirming the underlying bounded behavior already exists on the current branch.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'none_count_matches_cpython_typeerror and conditional-group-exists'` returned `528 passed, 5534 deselected`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'conditional_group_exists_callable_scorecards'` returned `4 passed, 44 deselected`; and
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/feature-planning-conditional-callable-current.py` returned `176 executed / 176 passed`.

## Completion
- Added the eight bounded alternation-heavy conditional callable `count=None` workflows to `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` and kept the existing `callable_match_group` helper pinned to group `1` / `"word"` on the shared owner path.
- Synced the shared owner-path expectations in `tests/python/test_callable_replacement_parity_suite.py` and `tests/conformance/test_combined_correctness_scorecards.py`, including the widened none-count representative ordering and helper-count assertions.
- Republished `reports/correctness/latest.py`; the tracked artifact now shows `184` executed / `184` passed / `0` unimplemented cases for `conditional-group-exists-callable-replacement-workflows` and `1837` total / `1837` passed / `0` failed / `0` unimplemented cases across `114` manifests.
- Verification in this run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'none_count_matches_cpython_typeerror and conditional-group-exists'` returned `552 passed, 5574 deselected`.
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'conditional_group_exists_callable_scorecards'` returned `4 passed, 44 deselected`.
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/rbr-1232-conditional-callable-alternation-none-count.py` returned `184 executed / 184 passed / 0 unimplemented`.
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py` republished the combined tracked scorecard at `1837 executed / 1837 passed / 0 failed / 0 unimplemented`.
