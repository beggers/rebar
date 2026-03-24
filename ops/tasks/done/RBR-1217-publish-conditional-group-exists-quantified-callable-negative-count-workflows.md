Status: done
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Publish the already-supported quantified conditional callable negative-count slice on the shared conditional callable replacement correctness owner path by adding the exact bounded `count=-1` `sub()` and `subn()` workflows that the direct parity suite already covers for both `str` and `bytes`.

## Pattern Pair
- `rebar.sub(r"a(b)?c(?(1)d|e){2}", lambda m: m.group(1) + "x", "zzabcddzz", -1)`
- `rebar.compile(rb"a(?P<word>b)?c(?(word)d|e){2}").subn(lambda m: m.group("word") + b"x", b"zzacedzz", -1)`

## Deliverables
- `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- Extend `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` with exactly the thirty-two adjacent quantified conditional callable negative-count workflows already encoded on the same owner path in `tests/python/test_callable_replacement_parity_suite.py`:
  - add the sixteen `str` workflows for `a(b)?c(?(1)d|e){2}` and `a(?P<word>b)?c(?(word)d|e){2}` across numbered and named module/compiled-`Pattern` `sub()` and `subn()` entrypoints with `count=-1`;
  - keep the bounded present-match rows on `"zzabcddzz"` and the bounded absent-capture rows on `"zzaceezz"` aligned with the direct parity tables while preserving the exact no-substitution / no-callback short-circuit outcome that CPython exposes when `count=-1`;
  - add the matching bounded no-match rows on `"zzabcdezz"` and `"zzacedzz"` so the quantified near-miss branch stays explicit on the shared correctness path even though the callback never runs; and
  - mirror the same sixteen workflows for `bytes` on `b"zzabcddzz"`, `b"zzaceezz"`, `b"zzabcdezz"`, and `b"zzacedzz"` without widening beyond the existing `callable_match_group` helper route.
- Keep the work on the existing conditional callable replacement correctness owner path instead of creating another manifest or detached publication file:
  - update `tests/conformance/test_combined_correctness_scorecards.py` only as needed so the `conditional-group-exists-callable-replacement-workflows` manifest expectations, representative case ordering, negative-count follow-on sync, and mixed-text scorecard coverage stay aligned with the widened quantified slice;
  - reuse the existing direct parity tables as the publication anchor instead of inventing new callable helpers or another parity source; and
  - do not widen this run into benchmark publication, Rust implementation work, or broader callable replacement expansion beyond the bounded quantified `count=-1` rows above.
- Regenerate `reports/correctness/latest.py` honestly on the tracked combined correctness surface:
  - the `conditional-group-exists-callable-replacement-workflows` manifest stays present on the shared owner path and gains the thirty-two quantified callable negative-count cases without introducing failures or `unimplemented` outcomes; and
  - the tracked combined correctness summary moves from `1765` total cases / `1765` passes / `0` failures / `0` unimplemented across `114` manifests to `1797` total cases / `1797` passes / `0` failures / `0` unimplemented across the same `114` manifests.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'test_module_callable_replacement_negative_count_short_circuits_without_callback and conditional-group-exists-quantified'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'conditional_group_exists_callable_scorecards and negative_count'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep the scope pinned to the exact thirty-two quantified conditional callable negative-count workflows above. Leave the adjacent benchmark catch-up for the same quantified `count=-1` slice to a separate planning pass.
- Reuse the existing `conditional_group_exists_callable_replacement_workflows.py` fixture and combined correctness scorecard owner path. Do not create another callable replacement manifest, another conformance module, or a detached quantified negative-count publication file.
- Keep this as Python-surface publication work only; do not widen the run into benchmark manifests or Rust-boundary implementation changes.

## Notes
- `RBR-1217` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this planning run; and
  - `rg -n "RBR-1217|RBR-1218|quantified callable negative-count" ops/tasks ops/state -g '*.md'` matched only historical mentions in planning state and completed task notes, not a live reservation for this id.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The newest done same-family frontier and one narrow owner-path scan keep this exact follow-on concrete after `RBR-1215`:
  - `ops/tasks/done/RBR-1215-benchmark-conditional-group-exists-quantified-callable-near-miss-workloads.md` explicitly leaves quantified callable negative-count publication as a concrete post-drain follow-on;
  - `tests/python/test_callable_replacement_parity_suite.py` already exercises the bounded quantified `count=-1` present, absent, and near-miss callable rows on the current branch;
  - `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py` and `tests/conformance/test_combined_correctness_scorecards.py` currently stop at the quantified callable present / absent / near-miss publication slice and omit the adjacent quantified negative-count rows; and
  - `benchmarks/workloads/conditional_group_exists_boundary.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` do not yet carry quantified callable negative-count rows, which keeps the same-pattern Python-path benchmark catch-up pinned as the post-drain surviving frontier after this correctness task lands.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'test_module_callable_replacement_negative_count_short_circuits_without_callback and conditional-group-exists-quantified'` returned `32 passed, 5394 deselected`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'conditional_group_exists_callable_scorecards and negative_count'` returned `1 passed, 46 deselected`; and
  - a direct import probe against `reports/correctness/latest.py` and `reports/benchmarks/latest.py` confirmed the current tracked summaries remain `1765/1765/0/0` across `114` manifests for correctness and `1131/1131/0` across `30` benchmark manifests before this new slice lands.

## Completion
- Added the thirty-two quantified conditional callable `count=-1` publication rows on the existing `conditional-group-exists-callable-replacement-workflows` owner path and kept the direct parity owner tables as the source anchor.
- Updated the callable scorecard expectations plus the parity-suite owner-path alignment checks needed to distinguish quantified negative-count rows from the pre-existing quantified present/absent/near-miss publication slice.
- Republished `reports/correctness/latest.py`; the tracked combined correctness report now shows `1797` total / `1797` passed / `0` failed / `0` unimplemented across `114` manifests, and the callable manifest slice reports `72` executed / `72` passed / `0` unimplemented.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'test_module_callable_replacement_negative_count_short_circuits_without_callback and conditional-group-exists-quantified'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k 'conditional_group_exists_quantified_negative_count'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'conditional_group_exists_callable_scorecards and negative_count'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'conditional_group_exists_callable_scorecards and quantified_no_match'`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`
