# RBR-1191: Benchmark conditional group-exists quantified callable str workloads

Status: ready
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Catch the newly published quantified conditional callable `str` slice up on the existing Python-path benchmark surface by measuring the exact eight bounded module and compiled-`Pattern` `sub()`/`subn()` workflows that the live runtime and correctness owner path already cover, before quantified `bytes` mirrors or broader callable-helper expansion widen this family again.

## Pattern Pair
- `rebar.sub(r"a(b)?c(?(1)d|e){2}", lambda m: m.group(1) + "x", "zzabcddzz")`
- `rebar.compile(r"a(?P<word>b)?c(?(word)d|e){2}").subn(lambda m: m.group("word") + "x", "zzaceezz", 1)`

## Deliverables
- `benchmarks/workloads/conditional_group_exists_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- Extend `benchmarks/workloads/conditional_group_exists_boundary.py` with exactly the eight adjacent quantified conditional callable `str` workloads already exercised on the shared direct parity and correctness owner paths for `a(b)?c(?(1)d|e){2}` and `a(?P<word>b)?c(?(word)d|e){2}`:
  - add numbered module `sub()` and `subn()` rows using the existing `callable_match_group` helper for the present-arm success case on `"zzabcddzz"` and the absent-capture `TypeError` companion on `"zzaceezz"` with `count=1`;
  - add numbered compiled-pattern `sub()` and `subn()` rows for the same present-arm success and absent-capture `TypeError` workflows;
  - add named module `sub()` and `subn()` rows using the same helper pinned to group `"word"` for the matching present-arm success and absent-capture `TypeError` workflows; and
  - add named compiled-pattern `sub()` and `subn()` rows for the same named workflows.
- Keep the work on the existing conditional benchmark owner path instead of creating another manifest or detached callable benchmark family:
  - update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` only as needed so the shared `conditional-group-exists-boundary` manifest expectations, representative measured-row checks, and callable slice round-trip coverage stay aligned with the widened quantified callable `str` slice;
  - preserve the already-measured two-arm, alternation-heavy, and nested conditional callable rows plus the surrounding conditional replacement-owner families on the same manifest; and
  - do not widen this run into quantified `bytes` mirrors, correctness publication, Rust implementation work, or broader callable-helper expansion beyond `callable_match_group`.
- Regenerate `reports/benchmarks/latest.py` honestly on the tracked combined benchmark surface:
  - the `conditional-group-exists-boundary` manifest grows from `136` workloads to `144` workloads with all `144` measured and `0` known gaps;
  - the tracked combined benchmark summary moves from `1067/1067` measured workloads to `1075/1075` measured workloads while the manifest count stays at `30`; and
  - do not widen this run into built-native-only reporting or another benchmark family.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists and callable'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/rbr-1191-conditional-group-exists-boundary.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep the scope pinned to the exact eight quantified conditional callable `str` workloads above. Leave quantified `bytes` mirrors and broader callable-helper expansion for later tasks.
- Reuse the existing `conditional_group_exists_boundary.py` manifest and benchmark-suite owner path. Do not create another benchmark manifest, another callable benchmark module, or a detached quantified publication file.
- Keep benchmark comparisons running through the Python-facing `rebar` path so the published comparison against stdlib `re` stays faithful at the module boundary.

## Notes
- `RBR-1191` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contained no active feature task in this run; and
  - `rg -n "RBR-1191|RBR-1192|quantified conditional callable|quantified-callable" ops/tasks ops/state -g '*.md'` matched only stale completion-note mentions and current frontier prose, not a live reservation for this id.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The newest done same-family frontier leaves this exact benchmark catch-up slice concrete after `RBR-1189`:
  - `ops/tasks/done/RBR-1189-publish-conditional-group-exists-quantified-callable-workflows.md` completed the bounded quantified conditional callable `str` correctness-publication slice and explicitly left benchmark catch-up, quantified `bytes` mirrors, and broader callable-helper expansion for later on this owner path;
  - `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py`, `tests/python/test_callable_replacement_parity_suite.py`, and `reports/correctness/latest.py` now cover the exact eight quantified conditional callable `str` publication/parity rows on the shared owner path;
  - `benchmarks/workloads/conditional_group_exists_boundary.py` still stops at quantified constant-replacement `sub()`/`subn()` rows plus quantified `Pattern.fullmatch()` probes for `a(b)?c(?(1)d|e){2}` and `a(?P<word>b)?c(?(word)d|e){2}`, leaving the adjacent quantified callable benchmark rows as the smallest still-missing publication slice on the same owner path; and
  - the narrow same-family bytes follow-on is still runtime-missing after this benchmark slice: `PYTHONPATH=python python3` probes on the exact `bytes` pattern pair returned CPython success or bounded `TypeError` results while `rebar.sub(...)`, `rebar.subn(...)`, and `rebar.compile(...).sub()/subn()` still raise scaffold `NotImplementedError`, which keeps quantified `bytes` parity as the concrete post-drain survivor rather than bytes publication or benchmark catch-up.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists and callable'` returned `7 passed, 587 deselected, 84 subtests passed`;
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/feature-planning-conditional-group-exists-boundary-current.py` returned `136 measured workloads / 0 known gaps`; and
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py` returned `1067 measured workloads / 0 known gaps`.
