Status: done
Owner: feature-implementation
Created: 2026-03-25

## Goal
- Publish the next bounded callable-replacement correctness slice on the shared Python owner path by lifting the quantified conditional no-match direct-parity bucket out of `tests/python/test_callable_replacement_parity_suite.py` and onto the tracked correctness surface without widening into nested, negative-count, or `count=None` follow-ons.

## Pattern Pair
- `a(b)?c(?(1)d|e){2}`
- `a(?P<word>b)?c(?(word)d|e){2}`

## Deliverables
- `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- Extend the published `conditional-group-exists-callable-replacement-workflows` correctness slice with one bounded quantified callable no-match expansion sourced from the existing direct-parity owner tables in `tests/python/test_callable_replacement_parity_suite.py`:
  - publish the exact numbered and named `sub()` / `subn()` module and compiled-pattern no-match rows for `a(b)?c(?(1)d|e){2}` and `a(?P<word>b)?c(?(word)d|e){2}` across both `str` and `bytes`;
  - keep the helper, `count`, text, and expected no-substitution results aligned with `CONDITIONAL_GROUP_EXISTS_QUANTIFIED_NEAR_MISS_CASES` and `CONDITIONAL_GROUP_EXISTS_QUANTIFIED_BYTES_NEAR_MISS_CASES` instead of inventing new literals or a second helper shape;
  - preserve the existing published quantified present/absent, negative-count, and `count=None` rows exactly; and
  - do not add a new manifest id, JSON sidecar, or non-Python intermediate representation.
- Refresh the published correctness scorecard expectations on the same owner route:
  - keep `tests/conformance/test_combined_correctness_scorecards.py` aligned with the widened quantified callable no-match slice; and
  - regenerate `reports/correctness/latest.py` so the tracked case and manifest totals match the landed fixture surface.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py -k 'conditional_group_exists_quantified'`

## Constraints
- Keep the scope pinned to quantified conditional callable no-match publication for `a(b)?c(?(1)d|e){2}` and `a(?P<word>b)?c(?(word)d|e){2}` only.
- Limit edits to `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py`, `tests/conformance/test_combined_correctness_scorecards.py`, and the regenerated `reports/correctness/latest.py` unless a small adjacent harness adjustment is strictly required to publish the widened fixture rows.
- Do not widen into nested conditional callable no-match rows, negative-count rows, `count=None` rows, benchmarks, runtime implementation work, or tracked ops/state prose.

## Notes
- `RBR-1268` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this planning run; and
  - `rg -n "RBR-1268|RBR-1269|RBR-1270" ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done ops/state/backlog.md ops/state/current_status.md -g '*.md'` found no reserved live follow-on ids outside historical mentions in older done-task files.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The tracked published scorecards remain fully green on the bounded published surface in this run:
  - `reports/correctness/latest.py` reports `1853` total / `1853` passed / `0` failed / `0` unimplemented cases across `114` manifests; and
  - `reports/benchmarks/latest.py` reports `1219` total / `1219` measured workloads with `0` known gaps across `30` manifests.
- One narrow same-owner-path check pins this exact task:
  - `tests/python/test_callable_replacement_parity_suite.py` already carries the exact quantified conditional no-match direct-parity bucket in `CONDITIONAL_GROUP_EXISTS_QUANTIFIED_NEAR_MISS_CASES` plus its bytes mirror, covering numbered and named module/pattern `sub()` / `subn()` rows with the bounded patterns `a(b)?c(?(1)d|e){2}` and `a(?P<word>b)?c(?(word)d|e){2}`;
  - the tracked correctness surface still publishes only the representative quantified callable no-match rows inside `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` and `tests/conformance/test_combined_correctness_scorecards.py`, so the exact direct-parity table remains unpublished on the scorecard surface; and
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py -k 'conditional_group_exists_quantified'` already passes on the current branch, confirming the bounded behavior exists and the missing work is publication catch-up rather than another implementation slice.
- No exact post-drain feature follow-on is pinned after this seed:
  - the stale callable wrong-return-type conditional frontier named in tracked state is already satisfied in `tests/python/test_callable_replacement_parity_suite.py`; and
  - one adjacent owner-path scan found no second unpublished manifest-shaped follow-on beyond this quantified direct-parity publication slice, so the planning-owned frontier stays at "no ready feature follow-on currently survives."

## Completion
- Landed the combined-scorecard publication catch-up for the quantified callable near-miss rows by widening the combined `conditional-group-exists-callable-replacement-workflows` representative-case selection to include the exact numbered and named module/pattern `sub()` and `subn()` no-match rows across both `str` and `bytes`.
- Kept `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` unchanged because it already carried the exact direct-parity rows with the expected helper, `count`, text, and no-substitution outcomes; the missing publication surface was the combined scorecard selection rather than fixture data.
- Regenerated `reports/correctness/latest.py`; the tracked publication changed, but the published totals stayed at `1853` total / `1853` passed / `0` failed / `0` unimplemented cases across `114` manifests.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py -k 'conditional_group_exists_quantified'` (`102` passed, `6375` deselected).
