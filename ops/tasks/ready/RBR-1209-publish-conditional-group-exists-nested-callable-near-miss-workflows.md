# RBR-1209: Publish conditional group-exists nested callable near-miss workflows

Status: ready
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Publish the already-supported nested conditional callable near-miss slice on the shared conditional callable replacement correctness owner path by adding the exact bounded no-match `sub()` and `subn()` workflows that the direct parity suite already covers for both `str` and `bytes`.

## Pattern Pair
- `rebar.sub(r"a(b)?c(?(1)(?(1)d|e)|f)", lambda m: m.group(1) + "x", "zzabcezz")`
- `rebar.compile(rb"a(?P<word>b)?c(?(word)(?(word)d|e)|f)").subn(lambda m: m.group("word") + b"x", b"zzacezz", 1)`

## Deliverables
- `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- Extend `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` with exactly the sixteen adjacent nested conditional callable near-miss workflows already encoded on the same owner path in `tests/python/test_callable_replacement_parity_suite.py`:
  - add the eight `str` workflows from `CONDITIONAL_GROUP_EXISTS_NESTED_NEAR_MISS_CASES` for the numbered and named nested conditional spellings `a(b)?c(?(1)(?(1)d|e)|f)` and `a(?P<word>b)?c(?(word)(?(word)d|e)|f)`;
  - cover module `sub()` no-match rows on `zzabcezz` that leave the input unchanged and module `subn()` no-match rows on `zzacezz` with `count=1` that return `(input, 0)`;
  - mirror those same numbered and named `sub()`/`subn()` no-match workflows through compiled-`Pattern` entrypoints; and
  - add the matching eight `bytes` workflows from `CONDITIONAL_GROUP_EXISTS_NESTED_BYTES_NEAR_MISS_CASES`, preserving the same numbered/named and module/pattern matrix on `b"zzabcezz"` and `b"zzacezz"`.
- Keep the work on the existing conditional callable replacement correctness owner path instead of creating another manifest or detached publication file:
  - update `tests/conformance/test_combined_correctness_scorecards.py` only as needed so the `conditional-group-exists-callable-replacement-workflows` manifest expectations, representative case ids, and mixed-text scorecard sync stay aligned with the widened nested callable near-miss slice;
  - reuse the existing direct parity tables as the publication anchor instead of inventing new callable helpers or another parity source; and
  - do not widen this run into Rust implementation work, benchmark publication, or broader conditional callable expansion beyond the bounded nested near-miss rows above.
- Regenerate `reports/correctness/latest.py` honestly on the tracked combined correctness surface:
  - the `conditional-group-exists-callable-replacement-workflows` manifest stays present on the shared owner path and gains the sixteen new nested callable near-miss cases without introducing failures or `unimplemented` outcomes; and
  - the tracked combined correctness summary moves from `1733` total cases / `1733` passes / `0` failures / `0` unimplemented across `114` manifests to `1749` total cases / `1749` passes / `0` failures / `0` unimplemented across the same `114` manifests.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists_nested and near_miss'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'conditional_group_exists_callable_scorecards'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the scope pinned to the exact sixteen nested callable near-miss workflows above. Leave the adjacent benchmark catch-up for this same near-miss slice for a separate planning pass.
- Reuse the existing `conditional_group_exists_callable_replacement_workflows.py` fixture and combined correctness scorecard owner path. Do not create another callable replacement manifest, another conformance module, or a detached nested near-miss publication file.
- Keep this as Python-surface publication work only; do not widen the run into benchmark manifests or Rust-boundary implementation changes.

## Notes
- `RBR-1209` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this planning run; and
  - `rg -n "RBR-1209|RBR-1210" ops/tasks ops/state -g '*.md'` matched no live reservation before this task was seeded.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- One narrow same-owner-path scan keeps this exact follow-on concrete after `RBR-1207`:
  - `tests/python/test_callable_replacement_parity_suite.py` already encodes the exact bounded nested callable near-miss rows in `CONDITIONAL_GROUP_EXISTS_NESTED_NEAR_MISS_CASES` and `CONDITIONAL_GROUP_EXISTS_NESTED_BYTES_NEAR_MISS_CASES`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists_nested and near_miss'` passed with `33 passed, 5041 deselected`, confirming the runtime slice already exists on the current branch; and
  - `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py`, `tests/conformance/test_combined_correctness_scorecards.py`, and `reports/correctness/latest.py` still omit those exact nested near-miss workflows, leaving them as the smallest still-missing accepted publication slice on the same owner path.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'conditional_group_exists_callable_scorecards'` returned `1 passed, 44 deselected`;
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report .rebar/tmp/feature-planning-correctness-current.py` returned `1733 total / 1733 passed / 0 failed / 0 unimplemented`; and
  - `python3` inspection of the tracked scorecards confirmed `reports/correctness/latest.py` still publishes `1733/1733` passing cases across `114` manifests while `reports/benchmarks/latest.py` publishes `1099/1099` measured workloads across `30` manifests, with `conditional-group-exists-boundary` currently at `168` workloads.
