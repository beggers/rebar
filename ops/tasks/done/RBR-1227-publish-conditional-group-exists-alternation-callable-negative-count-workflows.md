# RBR-1227: Publish conditional group-exists alternation callable negative-count workflows

Status: done
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Publish the already-supported alternation-heavy two-arm conditional callable `count=-1` slice on the shared conditional callable replacement correctness owner path by adding the exact bounded no-substitution workflows that the live direct parity path can already validate for both `str` and `bytes`.

## Pattern Pair
- `rebar.sub(r"a(b)?c(?(1)(de|df)|(eg|eh))", lambda m: m.group(1) + "x", "zzabcdezz", -1)`
- `rebar.compile(rb"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))").subn(lambda m: m.group("word") + b"x", b"zzacehzz", -1)`

## Deliverables
- `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- Extend `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` with exactly the eight adjacent alternation-heavy conditional callable `count=-1` workflows that sit immediately behind the ready top-level `count=None` benchmark catch-up on the same owner path:
  - add the four `str` workflows for `a(b)?c(?(1)(de|df)|(eg|eh))` and `a(?P<word>b)?c(?(word)(de|df)|(eg|eh))` by mirroring the already-published alternation-heavy present/absent rows while passing `count=-1`, keeping the bounded shape on module `sub`, module `subn`, compiled-`Pattern` `sub`, and compiled-`Pattern` `subn`;
  - add the matching four `bytes` workflows for `rb"a(b)?c(?(1)(de|df)|(eg|eh))"` and `rb"a(?P<word>b)?c(?(word)(de|df)|(eg|eh))"` on the same numbered/named module/pattern matrix;
  - keep the replacement descriptors on the existing `callable_match_group` helper pinned to group `1` or `"word"` so CPython's exact `count=-1` short-circuit stays explicit without inventing another callable helper shape; and
  - keep the slice bounded to the alternation-heavy top-level conditional callable family only, leaving any `count=None`, nested, quantified, or broader callable argument-contract publication for later tasks.
- Keep the work on the existing conditional callable correctness owner path instead of creating another manifest or detached publication file:
  - update `tests/conformance/test_combined_correctness_scorecards.py` only as needed so the `conditional-group-exists-callable-replacement-workflows` manifest expectations, representative case ordering, and mixed-text scorecard sync stay aligned with the widened alternation-heavy `count=-1` slice;
  - reuse the existing direct parity owner path in `tests/python/test_callable_replacement_parity_suite.py` as the runtime anchor instead of inventing new callable helpers or another parity source; and
  - do not widen this run into benchmark publication, Rust implementation work, or non-conditional callable-owner expansion.
- Regenerate `reports/correctness/latest.py` honestly on the tracked combined correctness surface:
  - the `collection.replacement.conditional_group_exists.callable` suite grows from `168` executed cases to `176` executed cases with all `176` passing and `0` unimplemented outcomes; and
  - the tracked combined correctness summary moves from `1821` total cases / `1821` passes / `0` failures / `0` unimplemented across `114` manifests to `1829` total cases / `1829` passes / `0` failures / `0` unimplemented across the same `114` manifests.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'negative_count_short_circuits_without_callback and conditional-group-exists-alternation'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'conditional_group_exists_callable_scorecards'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/rbr-1227-conditional-callable-alternation-negative-count.py`

## Constraints
- Keep the scope pinned to the exact eight alternation-heavy conditional callable `count=-1` workflows above. Leave any later same-route alternation-heavy `count=None`, nested, or quantified callable count-contract publication for a separate planning pass.
- Reuse the existing `conditional_group_exists_callable_replacement_workflows.py` fixture and combined correctness scorecard owner path. Do not create another callable replacement manifest, another conformance module, or a detached conditional callable contract file.
- Keep this as Python-surface publication work only; do not widen the run into benchmark manifests or Rust-boundary implementation changes.

## Notes
- `RBR-1227` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/` contained only `RBR-1225` as live feature work, while `ops/tasks/in_progress/` and `ops/tasks/blocked/` contained no active feature task in this planning run; and
  - `rg -n "RBR-1227|RBR-1228" ops/tasks ops/state -g '*.md'` matched only historical mentions inside completed task files, not a live reservation for this id.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- One narrow same-owner-path scan keeps this exact follow-on concrete behind `RBR-1225`:
  - `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` already publishes the alternation-heavy numbered and named callable present/absent rows for `str` and `bytes`, but it does not yet publish any alternation-heavy `count=-1` rows on that owner path;
  - `benchmarks/workloads/conditional_group_exists_boundary.py` already measures the top-level, nested, and quantified callable negative-count slices, but it does not yet publish alternation-heavy callable negative-count coverage, so correctness remains the next honest publication stop on this owner route;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'negative_count_short_circuits_without_callback and conditional-group-exists-alternation'` passed with `48 passed`, confirming the bounded direct parity shape already exists on the current branch; and
  - a direct runtime probe over numbered and named module/pattern `str` and `bytes` alternation-heavy `count=-1` calls returned matching stdlib `re` and `rebar` outcomes without invoking the callback, confirming the underlying bounded behavior already exists for this mirrored publication slice.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'negative_count_short_circuits_without_callback and conditional-group-exists-alternation'` returned `48 passed, 5924 deselected`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'conditional_group_exists_callable_scorecards'` returned `4 passed, 44 deselected`; and
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/rbr-1227-conditional-callable-alternation-negative-count.py` returned `168 executed / 168 passed`.

## Completion Notes
- Added the exact eight alternation-heavy conditional callable `count=-1` workflows on the shared `conditional-group-exists-callable-replacement-workflows` owner path for numbered/named module and compiled-`Pattern` `sub`/`subn` coverage across `str` and `bytes`.
- Updated the combined scorecard expectation and negative-count sync assertions so the representative-case matrix and helper/operation counts stay aligned with the widened alternation-negative-count slice.
- Republished `reports/correctness/latest.py`; the tracked combined report now shows `collection.replacement.conditional_group_exists.callable` at `176` executed / `176` passed / `0` unimplemented and the overall combined summary at `1829` executed / `1829` passed / `0` failed / `0` unimplemented across `114` manifests.
- Verification run results on this branch:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'negative_count_short_circuits_without_callback and conditional-group-exists-alternation'` returned `72 passed, 5988 deselected`.
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'conditional_group_exists_callable_scorecards'` returned `4 passed, 44 deselected` after the tracked report refresh.
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py --report .rebar/tmp/rbr-1227-conditional-callable-alternation-negative-count.py` returned `176 executed / 176 passed`.
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py` returned `1829 executed / 1829 passed`.
