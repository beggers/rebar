# RBR-1147: Publish conditional group-exists template bytes negative-count workflows

Status: done
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Reopen the shared `conditional-group-exists-replacement-template-workflows` correctness frontier with the exact bytes `count=-1` replacement-template rows that the live runtime already matches against CPython on the shared parity owner path, publishing that bounded conditional replacement outcome before any same-family benchmark catch-up or broader conditional replacement follow-on widens the queue.

## Pattern Pair
- `rebar.sub(rb"a(b)?c(?(1)d|e)", rb"\\1x", b"abcdaceabcd", -1)`
- `rebar.compile(rb"a(?P<word>b)?c(?(word)d|e)").subn(rb"\\g<word>x", b"abcdaceabcd", -1)`

## Deliverables
- `tests/conformance/fixtures/conditional_group_exists_replacement_template_workflows.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- Extend `tests/conformance/fixtures/conditional_group_exists_replacement_template_workflows.py` with exactly the four adjacent bytes `count=-1` replacement-template rows already exercised on the shared parity owner path:
  - add the numbered module `sub()` bytes row for `rb"a(b)?c(?(1)d|e)"` with `rb"\\1x"`, `b"abcdaceabcd"`, and `count == -1`;
  - add the named module `subn()` bytes row for `rb"a(?P<word>b)?c(?(word)d|e)"` with `rb"\\g<word>x"`, `b"abcdaceabcd"`, and `count == -1`;
  - add the numbered compiled-pattern `sub()` bytes row for `rb"a(b)?c(?(1)d|e)"` with `rb"\\1x"`, `b"abcdaceabcd"`, and `count == -1`; and
  - add the named compiled-pattern `subn()` bytes row for `rb"a(?P<word>b)?c(?(word)d|e)"` with `rb"\\g<word>x"`, `b"abcdaceabcd"`, and `count == -1`.
- Keep the work on the existing conditional replacement-template correctness owner path instead of creating another manifest or detached publication table:
  - update `tests/python/test_fixture_backed_replacement_parity_suite.py` only as needed so the shared conditional replacement publication selectors and frontier assertions expect these four new bytes negative-count rows on `conditional-group-exists-replacement-template-workflows`;
  - update `tests/conformance/test_combined_correctness_scorecards.py` only as needed so the representative `conditional-group-exists-replacement-template-workflows` cases stay aligned with the widened bytes publication slice; and
  - preserve the already-published present/absent `str` and bytes rows plus the surrounding grouped and conditional replacement families on the same owner path.
- Regenerate `reports/correctness/latest.py` honestly on the tracked combined correctness surface:
  - the tracked report gains the four new bytes negative-count rows for `collection.replacement.conditional_group_exists.template`;
  - the exact conditional replacement-template manifest remains fully passing with no new explicit failures or unimplemented rows; and
  - do not widen this run into benchmark publication, callable replacements, alternation-heavy conditionals, nested conditionals, quantified conditionals, or broader replacement-owner families.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'conditional_replacement_template_negative_count_bytes_cases_keep_exact_frontier_explicit or conditional_replacement_template_publication_keeps_mixed_text_frontier_explicit'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py -k 'conditional_group_exists_replacement_template_workflows or collection_replacement_conditional_group_exists_template'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_replacement_template_workflows.py --report .rebar/tmp/rbr-1147-conditional-template-bytes-negative-count.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or tracked ops state prose in this run.
- Reuse the existing `conditional_group_exists_replacement_template_workflows.py` manifest and shared replacement parity suite. Do not create another correctness manifest, another parity module, or a detached conditional replacement publication file.
- Keep the scope pinned to the exact four bytes `count=-1` rows above. Leave any same-family benchmark catch-up, str negative-count publication, callable replacements, broader bytes helper execution, and other conditional replacement follow-ons for later tasks.

## Notes
- `RBR-1147` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contain no active feature task in this run; and
  - `rg -n 'RBR-1147|RBR-1148|RBR-1149' ops/tasks ops/state -g '*.md'` matched only historical notes inside completed task files, not a live reservation.
- Queue this directly after `RBR-1145` because the newest done same-family task leaves broader conditional replacement follow-ons unspecified, and the narrow owner-path scan shows this exact bytes negative-count publication slice is the smallest still-missing accepted surface on the shared conditional replacement-template route.
- 2026-03-24 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'conditional_replacement_template_negative_count_bytes_cases_keep_exact_frontier_explicit or module_numbered_conditional_bytes_template_negative_count or module_named_conditional_bytes_template_negative_count or pattern_numbered_conditional_bytes_template_negative_count or pattern_named_conditional_bytes_template_negative_count'` returned `1 passed, 1461 deselected`, keeping the exact bytes negative-count frontier explicit on the shared parity owner path;
  - a direct runtime probe in this run confirmed `rebar.sub(...)`, `rebar.subn(...)`, `rebar.compile(...).sub(...)`, and `rebar.compile(...).subn(...)` match CPython for the exact two bounded bytes `count=-1` conditional-template workflows above;
  - `rg -n 'module-numbered-conditional-bytes-template-negative-count|module-named-conditional-bytes-template-negative-count|pattern-numbered-conditional-bytes-template-negative-count|pattern-named-conditional-bytes-template-negative-count' tests/conformance/fixtures tests/conformance/test_combined_correctness_scorecards.py reports/correctness/latest.py` currently finds those ids only on the shared parity file, confirming the tracked correctness publication still omits this exact bytes slice; and
  - the adjacent benchmark owner-path scan shows no published `conditional-group-exists-boundary` negative-count workload for this slice yet, so benchmark catch-up should stay behind correctness publication.

## Completion
- Added the four bytes `count=-1` conditional replacement-template publication rows on the existing `conditional-group-exists-replacement-template-workflows` manifest and widened the shared parity/scorecard assertions to cover the now-asymmetric `str`/`bytes` frontier without changing any broader replacement family routing.
- Regenerated `reports/correctness/latest.py`; the tracked publication now reports 1665 total cases with 1665 passing overall, `collection.replacement.conditional_group_exists.template` at 20/20 passing, and the bytes sub-suite at 12/12 passing with the four new negative-count rows present in the tracked artifact.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'conditional_replacement_template_negative_count_bytes_cases_keep_exact_frontier_explicit or conditional_replacement_template_publication_keeps_mixed_text_frontier_explicit'`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/conditional_group_exists_replacement_template_workflows.py --report .rebar/tmp/rbr-1147-conditional-template-bytes-negative-count.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`.
