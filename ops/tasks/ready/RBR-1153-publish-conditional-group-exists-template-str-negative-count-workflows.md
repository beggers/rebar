# RBR-1153: Publish conditional group-exists template str negative-count workflows

Status: ready
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Reopen the shared `conditional-group-exists-replacement-template-workflows` correctness frontier with the exact `str count=-1` replacement-template rows that the live runtime and shared parity owner path already cover, publishing that bounded conditional replacement outcome before same-family benchmark catch-up or callable follow-ons widen the queue.

## Pattern Pair
- `rebar.sub(r"a(b)?c(?(1)d|e)", r"\1x", "abcdaceabcd", -1)`
- `rebar.compile(r"a(?P<word>b)?c(?(word)d|e)").subn(r"\g<word>x", "abcdaceabcd", -1)`

## Deliverables
- `tests/conformance/fixtures/conditional_group_exists_replacement_template_workflows.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- Extend `tests/conformance/fixtures/conditional_group_exists_replacement_template_workflows.py` with exactly the four adjacent `str count=-1` replacement-template rows already exercised on the shared parity owner path:
  - add the numbered module `sub()` row for `r"a(b)?c(?(1)d|e)"` with `r"\1x"`, `"abcdaceabcd"`, and `count == -1`;
  - add the named module `subn()` row for `r"a(?P<word>b)?c(?(word)d|e)"` with `r"\g<word>x"`, `"abcdaceabcd"`, and `count == -1`;
  - add the numbered compiled-pattern `sub()` row for `r"a(b)?c(?(1)d|e)"` with `r"\1x"`, `"abcdaceabcd"`, and `count == -1`; and
  - add the named compiled-pattern `subn()` row for `r"a(?P<word>b)?c(?(word)d|e)"` with `r"\g<word>x"`, `"abcdaceabcd"`, and `count == -1`.
- Keep the work on the existing conditional replacement-template correctness owner path instead of creating another manifest or detached publication table:
  - update `tests/python/test_fixture_backed_replacement_parity_suite.py` only as needed so the shared conditional replacement publication selectors and frontier assertions expect these four new `str` negative-count rows on `conditional-group-exists-replacement-template-workflows`, making the mixed-text publication frontier explicit rather than leaving the new rows parity-only;
  - update `tests/conformance/test_combined_correctness_scorecards.py` only as needed so the representative `conditional-group-exists-replacement-template-workflows` cases stay aligned with the widened `str` publication slice; and
  - preserve the already-published present/absent `str` and bytes rows plus the already-landed bytes negative-count rows and the surrounding grouped and conditional replacement families on the same owner path.
- Regenerate `reports/correctness/latest.py` honestly on the tracked combined correctness surface:
  - the tracked report gains the four new `str` negative-count rows for `collection.replacement.conditional_group_exists.template`;
  - the exact conditional replacement-template manifest moves from `20` to `24` passing cases with no new explicit failures or unimplemented rows;
  - the combined correctness summary moves from `1665/1665` passing cases to `1669/1669` passing cases while the manifest count stays at `114`; and
  - do not widen this run into benchmark publication, callable replacements, alternation-heavy conditionals, nested conditionals, quantified conditionals, or broader replacement-owner families.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'conditional_replacement_template_publication_keeps_mixed_text_frontier_explicit or conditional_replacement_template_negative_count_str_cases_keep_exact_frontier_explicit'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'conditional_group_exists_replacement_template_scorecards_keep_bytes_negative_count_follow_on_cases_in_sync or mixed_text_manifests_cover_both_representative_text_models'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_replacement_template_workflows.py --report .rebar/tmp/rbr-1153-conditional-template-str-negative-count.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or tracked ops state prose in this run.
- Reuse the existing `conditional_group_exists_replacement_template_workflows.py` manifest and shared replacement parity suite. Do not create another correctness manifest, another parity module, or a detached conditional replacement publication file.
- Keep the scope pinned to the exact four `str count=-1` rows above. Leave same-family benchmark catch-up, callable replacements, bytes follow-ons beyond the already-published rows, and other conditional replacement follow-ons for later tasks.

## Notes
- `RBR-1153` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this run; and
  - `rg -n 'RBR-1153|RBR-1154|RBR-1155' ops/tasks ops/state -g '*.md'` matched only historical notes inside completed task files, not a live reservation.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The newest done same-family frontier leaves this publication slice concrete after `RBR-1151`:
  - `ops/tasks/done/RBR-1151-implement-conditional-group-exists-template-str-negative-count-parity.md` closed by proving the bounded Rust-backed `str count=-1` behavior was already present on this branch and by expanding the shared parity owner path to the full four-row module/pattern numbered/named matrix;
  - `tests/python/test_fixture_backed_replacement_parity_suite.py` now carries `module-conditional-template-negative-count`, `module-named-conditional-template-negative-count`, `pattern-numbered-conditional-template-negative-count`, and `pattern-named-conditional-template-negative-count` as explicit direct parity rows;
  - `tests/conformance/fixtures/conditional_group_exists_replacement_template_workflows.py` and `reports/correctness/latest.py` still omit the four matching `str` publication ids while already publishing the adjacent bytes negative-count follow-on; and
  - `benchmarks/workloads/conditional_group_exists_boundary.py` still omits any `str` negative-count benchmark rows on this owner path, so correctness publication is the smallest surviving same-family slice and benchmark catch-up should stay behind it.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'conditional_replacement_template_publication_keeps_mixed_text_frontier_explicit or conditional_replacement_template_negative_count_str_cases_keep_exact_frontier_explicit'` returned `2 passed, 1513 deselected` in this run;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'conditional_group_exists_replacement_template_scorecards_keep_bytes_negative_count_follow_on_cases_in_sync or mixed_text_manifests_cover_both_representative_text_models'` returned `2 passed, 42 deselected, 26 subtests passed` in this run;
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_replacement_template_workflows.py --report .rebar/tmp/feature-planning-conditional-template-str-negative-count.py` returned `20` executed and passing cases in this run; and
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report .rebar/tmp/feature-planning-full-correctness.py` returned `1665` executed and passing cases in this run.
