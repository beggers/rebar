# RBR-1080: Implement grouped-template replacement parity

Status: done
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Reopen the collection/replacement owner path with the first deferred grouped-template implementation prerequisite from `RBR-1075`, converting the exact bounded numbered and named grouped replacement-template slice from placeholder raises to Rust-backed parity before callable replacement rows, benchmark catch-up, or broader grouped replacement expansion reenter the queue.

## Pattern Pair
- `rebar.sub("(abc)", r"\1x", "abc")`
- `rebar.compile("(?P<word>abc)").sub(r"<\g<word>>", "abcabc")`

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`

## Acceptance Criteria
- Land the missing grouped replacement-template runtime support on the existing replacement owner path in Rust, with any Python bridge changes limited to argument normalization, wrapper plumbing, and FFI calls:
  - the exact numbered grouped-template module path `rebar.sub("(abc)", r"\1x", "abc")` now matches `re.sub("(abc)", r"\1x", "abc")` instead of raising the scaffold placeholder;
  - the exact named grouped-template compiled-pattern path `rebar.compile("(?P<word>abc)").sub(r"<\g<word>>", "abcabc")` now matches `re.compile("(?P<word>abc)").sub(r"<\g<word>>", "abcabc")` instead of raising the scaffold placeholder; and
  - the adjacent count-bearing named cases already published on the same owner route stay aligned with CPython:
    - `module-subn-template-named-group-str`
    - `pattern-subn-template-named-group-str`
- Keep the work on the existing grouped replacement owner path in `tests/python/test_fixture_backed_replacement_parity_suite.py` rather than creating a detached parity file or a new fixture family:
  - `test_module_replacement_matches_cpython` passes for `module-sub-grouping-template`, `module-sub-template-named-group-str`, and `module-subn-template-named-group-str`;
  - `test_pattern_replacement_matches_cpython` passes for `pattern-sub-template-named-group-str` and `pattern-subn-template-named-group-str`; and
  - the already-landed direct whole-match template smoke stays green for both module and pattern helpers.
- Preserve the existing unsupported boundaries outside this exact slice:
  - `test_source_package_module_literal_replacement_helpers_stay_loud_without_cache_mutation` still observes placeholder errors for the flagged/meta/empty module cases it already covers; and
  - `test_source_package_pattern_literal_replacement_helpers_stay_loud_for_unsupported_cases` still observes placeholder errors for the flagged/empty compiled-pattern cases it already covers.
- Do not widen this task into callable replacements, grouped alternation replacement rows, nested grouped replacement rows, benchmark manifests, reports, README text, or tracked state prose.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_module_replacement_matches_cpython and (module-sub-grouping-template or module-sub-template-named-group-str or module-subn-template-named-group-str)'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_pattern_replacement_matches_cpython and (pattern-sub-template-named-group-str or pattern-subn-template-named-group-str)'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_whole_match_template_replacement_matches_cpython or test_source_package_pattern_whole_match_template_replacement_matches_cpython or test_source_package_module_literal_replacement_helpers_stay_loud_without_cache_mutation or test_source_package_pattern_literal_replacement_helpers_stay_loud_for_unsupported_cases'`

## Constraints
- Keep the implementation bounded to the exact grouped replacement-template shape already published on the collection and named-group owner paths. Leave callable replacements, broader grouped replacement-template families, and benchmark catch-up for later tasks.
- New compatibility behavior belongs in Rust. Do not solve this by expanding Python-only fallback execution beyond the existing wrapper and bridge responsibilities.
- Preserve current placeholder behavior for still-unsupported replacement cases outside the exact numbered/named grouped-template slice above.

## Notes
- `RBR-1080` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contain no live feature task;
  - `ops/tasks/done/` currently runs through `RBR-1079`; and
  - `rg -n 'RBR-1080|RBR-1081|RBR-1082' ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` returned only historical mentions in done-task notes, not a live reservation.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- `RBR-1075` explicitly left grouped-template rows ahead of callable replacement rows and benchmark catch-up on the same collection/replacement owner family, so this is the first concrete deferred same-family follow-on rather than a new frontier.
- Current owner-path anchors for this slice are:
  - `tests/conformance/fixtures/collection_replacement_workflows.py` publishes `module-sub-grouping-template` for `"(abc)"` plus `r"\1x"`;
  - `tests/conformance/fixtures/named_group_replacement_workflows.py` publishes the adjacent named grouped-template `sub()` and `subn()` rows on the same owner family; and
  - `tests/python/test_fixture_backed_replacement_parity_suite.py` routes those cases through `test_module_replacement_matches_cpython` and `test_pattern_replacement_matches_cpython`.

## Completion Note
- Retired without code changes on 2026-03-23. The exact grouped-template slice is already satisfied in this checkout:
  - `rebar.sub("(abc)", r"\1x", "abc") == re.sub("(abc)", r"\1x", "abc")`
  - `rebar.compile("(?P<word>abc)").sub(r"<\g<word>>", "abcabc") == re.compile("(?P<word>abc)").sub(r"<\g<word>>", "abcabc")`
  - `module-subn-template-named-group-str` and `pattern-subn-template-named-group-str` already match CPython too.
- Verification in this run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_module_replacement_matches_cpython and (module-sub-grouping-template or module-sub-template-named-group-str or module-subn-template-named-group-str)'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_pattern_replacement_matches_cpython and (pattern-sub-template-named-group-str or pattern-subn-template-named-group-str)'`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_whole_match_template_replacement_matches_cpython or test_source_package_pattern_whole_match_template_replacement_matches_cpython or test_source_package_module_literal_replacement_helpers_stay_loud_without_cache_mutation or test_source_package_pattern_literal_replacement_helpers_stay_loud_for_unsupported_cases'`
- Published scorecards were not refreshed because no correctness behavior or fixtures changed.
