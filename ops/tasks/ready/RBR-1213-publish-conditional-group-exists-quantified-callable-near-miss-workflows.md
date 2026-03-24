Status: ready
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Publish the already-supported quantified conditional callable near-miss slice on the shared conditional callable replacement correctness owner path by adding the exact bounded no-match `sub()` and `subn()` workflows that the direct parity suite already covers for both `str` and `bytes`.

## Pattern Pair
- `rebar.sub(r"a(b)?c(?(1)d|e){2}", lambda m: m.group(1) + "x", "zzabcdezz")`
- `rebar.compile(rb"a(?P<word>b)?c(?(word)d|e){2}").subn(lambda m: m.group("word") + b"x", b"zzacedzz", 1)`

## Deliverables
- `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- Extend `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` with exactly the sixteen adjacent quantified conditional callable near-miss workflows already encoded on the same owner path in `tests/python/test_callable_replacement_parity_suite.py`:
  - add the eight `str` workflows from `CONDITIONAL_GROUP_EXISTS_QUANTIFIED_NEAR_MISS_CASES` for the numbered and named quantified conditional spellings `a(b)?c(?(1)d|e){2}` and `a(?P<word>b)?c(?(word)d|e){2}`;
  - cover module `sub()` no-match rows on `zzabcdezz` that leave the input unchanged and module `subn()` no-match rows on `zzacedzz` with `count=1` that return `(input, 0)`;
  - mirror those same numbered and named `sub()`/`subn()` no-match workflows through compiled-`Pattern` entrypoints; and
  - add the matching eight `bytes` workflows from `CONDITIONAL_GROUP_EXISTS_QUANTIFIED_BYTES_NEAR_MISS_CASES`, preserving the same numbered/named and module/pattern matrix on `b"zzabcdezz"` and `b"zzacedzz"`.
- Keep the work on the existing conditional callable replacement correctness owner path instead of creating another manifest or detached publication file:
  - update `tests/conformance/test_combined_correctness_scorecards.py` only as needed so the `conditional-group-exists-callable-replacement-workflows` manifest expectations, representative case ids, and mixed-text scorecard sync stay aligned with the widened quantified callable near-miss slice;
  - reuse the existing direct parity tables as the publication anchor instead of inventing new callable helpers or another parity source; and
  - do not widen this run into Rust implementation work, benchmark publication, or broader conditional callable expansion beyond the bounded quantified near-miss rows above.
- Regenerate `reports/correctness/latest.py` honestly on the tracked combined correctness surface:
  - the `conditional-group-exists-callable-replacement-workflows` manifest stays present on the shared owner path and gains the sixteen new quantified callable near-miss cases without introducing failures or `unimplemented` outcomes; and
  - the tracked combined correctness summary moves from `1749` total cases / `1749` passes / `0` failures / `0` unimplemented across `114` manifests to `1765` total cases / `1765` passes / `0` failures / `0` unimplemented across the same `114` manifests.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists_quantified and near_miss'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'conditional_group_exists_callable_scorecards'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the scope pinned to the exact sixteen quantified conditional callable near-miss workflows above. Leave any adjacent benchmark catch-up or negative-count follow-on for a separate planning pass.
- Reuse the existing `conditional_group_exists_callable_replacement_workflows.py` fixture and combined correctness scorecard owner path. Do not create another callable replacement manifest, another conformance module, or a detached quantified near-miss publication file.
- Keep this as Python-surface publication work only; do not widen the run into benchmark manifests or Rust-boundary implementation changes.

## Notes
- `RBR-1213` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this planning run; and
  - `rg -n "RBR-1213|RBR-1214|RBR-1215" ops/tasks ops/state -g '*.md'` matched only historical mentions inside completed task files, not a live reservation for this id.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- One narrow same-owner-path scan keeps this exact follow-on concrete after `RBR-1211`:
  - `tests/python/test_callable_replacement_parity_suite.py` already encodes the exact bounded quantified callable near-miss rows in `CONDITIONAL_GROUP_EXISTS_QUANTIFIED_NEAR_MISS_CASES` and `CONDITIONAL_GROUP_EXISTS_QUANTIFIED_BYTES_NEAR_MISS_CASES`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists_quantified and near_miss'` passed with `34 passed, 5216 deselected`, confirming the runtime slice already exists on the current branch; and
  - `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py`, `tests/conformance/test_combined_correctness_scorecards.py`, `benchmarks/workloads/conditional_group_exists_boundary.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` contain the quantified callable present/absent slice but still omit any quantified callable near-miss or quantified callable negative-count publication/benchmark rows, leaving the bounded quantified near-miss workflows as the smallest still-missing accepted publication slice on that same owner path.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'conditional_group_exists_callable_scorecards'` returned `3 passed, 43 deselected`;
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report .rebar/tmp/feature-planning-correctness-current.py` returned `1749 total / 1749 passed / 0 failed / 0 unimplemented`; and
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists_quantified_callable'` returned `5 passed, 435 deselected, 56 subtests passed`, confirming the adjacent benchmark owner path already recognizes the quantified callable family even though the near-miss slice itself remains unpublished.
