# RBR-1151: Implement conditional group-exists template str negative-count parity

Status: ready
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Reopen the shared conditional replacement-template owner path with the bounded `str count=-1` follow-on that the newest done benchmark task left deferred, converting the exact four numbered and named module and compiled-`Pattern` negative-count workflows to Rust-backed parity before correctness publication or benchmark catch-up widens this family again.

## Pattern Pair
- `rebar.sub(r"a(b)?c(?(1)d|e)", r"\1x", "abcdaceabcd", -1)`
- `rebar.compile(r"a(?P<word>b)?c(?(word)d|e)").subn(r"\g<word>x", "abcdaceabcd", -1)`

## Deliverables
- `crates/rebar-core/src/lib.rs`
- `crates/rebar-cpython/src/lib.rs`
- `python/rebar/__init__.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`

## Acceptance Criteria
- Land the missing bounded `str count=-1` replacement-template parity for the shared two-arm conditional owner path in Rust, with Python changes limited to wrapper plumbing, argument normalization, and FFI calls:
  - `rebar.sub(r"a(b)?c(?(1)d|e)", r"\1x", "abcdaceabcd", -1)` matches CPython's exact no-substitution result instead of remaining scaffolded on the module helper path;
  - `rebar.subn(r"a(?P<word>b)?c(?(word)d|e)", r"\g<word>x", "abcdaceabcd", -1)` matches CPython's exact zero-replacement tuple on the named module helper path;
  - `rebar.compile(r"a(b)?c(?(1)d|e)").sub(r"\1x", "abcdaceabcd", -1)` matches CPython on the numbered compiled-pattern helper path; and
  - `rebar.compile(r"a(?P<word>b)?c(?(word)d|e)").subn(r"\g<word>x", "abcdaceabcd", -1)` matches CPython on the named compiled-pattern helper path.
- Keep the work on the existing shared replacement parity owner path in `tests/python/test_fixture_backed_replacement_parity_suite.py` instead of creating another parity module, correctness fixture, or benchmark manifest:
  - expand the negative-count supplemental/direct parity coverage so the shared conditional replacement-template route requires the full four-row `str` numbered and named module and compiled-pattern matrix rather than only the current representative rows;
  - preserve the already-landed bytes negative-count cases plus the existing present and absent `str` and bytes publication assertions on `conditional-group-exists-replacement-template-workflows`; and
  - do not widen this run into correctness publication, benchmark manifests, benchmark reports, callable replacements, alternation-heavy conditionals, nested conditionals, quantified conditionals, or other replacement families.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'negative_replacement_counts_short_circuit_like_cpython and conditional-template-negative-count'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'conditional_replacement_template_publication_keeps_mixed_text_frontier_explicit'`

## Constraints
- Keep the implementation bounded to the exact `str count=-1` two-arm conditional replacement-template slice above. Leave correctness publication, benchmark catch-up, bytes follow-ons, callable replacements, and broader conditional replacement work for later tasks.
- New compatibility behavior belongs in Rust. Do not solve this by delegating the new `str` negative-count behavior to stdlib `re` or by expanding Python-only fallback execution beyond wrapper and bridge responsibilities.
- Scope this prerequisite to the full mirrored owner-path slice that the next correctness publication will need: numbered and named, plus module and compiled-pattern entrypoints, on the same bounded `count=-1` template family.

## Notes
- `RBR-1151` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this run; and
  - `rg -n 'RBR-1151|RBR-1152|RBR-1153' ops/tasks ops/state -g '*.md'` matched only historical notes inside completed task files, not a live reservation.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The narrow same-family owner-path check in this run shows that the newest done frontier leaves a concrete `str` follow-on, but publication would outrun a still-unconfirmed runtime boundary:
  - `ops/tasks/done/RBR-1149-benchmark-conditional-group-exists-template-bytes-negative-count-workloads.md` explicitly leaves same-family `str` negative-count publication or benchmark work for later after the bytes catch-up lands;
  - `tests/conformance/fixtures/conditional_group_exists_replacement_template_workflows.py` and `reports/correctness/latest.py` still omit the four `str` negative-count publication ids for this owner path;
  - `tests/python/test_fixture_backed_replacement_parity_suite.py` currently carries only the representative `module-conditional-template-negative-count` and `pattern-named-conditional-template-negative-count` direct parity cases, so the full mirrored `str` matrix the next publication would need is not yet explicit on the parity route; and
  - exact source-package probes for the four literal `str count=-1` workflows above still raise scaffold `NotImplementedError` on the current branch, so the next bounded slice here is the implementation prerequisite rather than a publication-only or benchmark-only task.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'negative_replacement_counts_short_circuit_like_cpython and conditional-template-negative-count'` returned `4 passed, 1506 deselected` under collection and `2 passed, 1508 deselected` per exact case-id filter in this run; and
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'conditional_replacement_template_publication_keeps_mixed_text_frontier_explicit'` returned `1 passed, 1509 deselected` in this run.
