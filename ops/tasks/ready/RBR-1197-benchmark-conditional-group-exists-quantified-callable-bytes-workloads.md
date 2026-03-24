# RBR-1197: Benchmark conditional group-exists quantified callable bytes workloads

Status: ready
Owner: feature-implementation
Created: 2026-03-24

## Goal
- Catch the newly published quantified conditional callable `bytes` slice up on the existing Python-path benchmark surface by measuring the exact eight bounded module and compiled-`Pattern` `sub()`/`subn()` workflows that the live runtime and correctness owner path already cover, before broader callable-helper expansion widens this family again.

## Pattern Pair
- `rebar.sub(rb"a(b)?c(?(1)d|e){2}", lambda m: m.group(1) + b"x", b"zzabcddzz")`
- `rebar.compile(rb"a(?P<word>b)?c(?(word)d|e){2}").subn(lambda m: m.group("word") + b"x", b"zzaceezz", 1)`

## Deliverables
- `benchmarks/workloads/conditional_group_exists_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- Extend `benchmarks/workloads/conditional_group_exists_boundary.py` with exactly the eight adjacent quantified conditional callable `bytes` workloads already exercised on the shared direct parity and correctness owner paths for `rb"a(b)?c(?(1)d|e){2}"` and `rb"a(?P<word>b)?c(?(word)d|e){2}"`:
  - add numbered module `sub()` and `subn()` rows using the existing `callable_match_group` helper for the present-arm success case on `b"zzabcddzz"` and the absent-capture `TypeError` companion on `b"zzaceezz"` with `count=1`;
  - add numbered compiled-pattern `sub()` and `subn()` rows for the same present-arm success and absent-capture `TypeError` workflows;
  - add named module `sub()` and `subn()` rows using the same helper pinned to group `"word"` for the matching present-arm success and absent-capture `TypeError` workflows; and
  - add named compiled-pattern `sub()` and `subn()` rows for the same named workflows.
- Keep the work on the existing conditional benchmark owner path instead of creating another manifest or detached callable benchmark family:
  - update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` only as needed so the shared `conditional-group-exists-boundary` manifest expectations, representative measured-row checks, and callable slice round-trip coverage stay aligned with the widened quantified callable mixed-text slice;
  - preserve the already-measured two-arm, alternation-heavy, nested, and quantified conditional callable `str` rows plus the surrounding conditional replacement-owner families on the same manifest; and
  - do not widen this run into correctness publication, Rust implementation work, or broader callable-helper expansion beyond `callable_match_group`.
- Regenerate `reports/benchmarks/latest.py` honestly on the tracked combined benchmark surface:
  - the `conditional-group-exists-boundary` manifest grows from `144` workloads to `152` workloads with all `152` measured and `0` known gaps;
  - the tracked combined benchmark summary moves from `1075/1075` measured workloads to `1083/1083` measured workloads while the manifest count stays at `30`; and
  - do not widen this run into built-native-only reporting or another benchmark family.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists and callable'`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/rbr-1197-conditional-group-exists-boundary.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep the scope pinned to the exact eight quantified conditional callable `bytes` workloads above. Leave broader callable-helper expansion for later tasks.
- Reuse the existing `conditional_group_exists_boundary.py` manifest and benchmark-suite owner path. Do not create another benchmark manifest, another callable benchmark module, or a detached quantified publication file.
- Keep benchmark comparisons running through the Python-facing `rebar` path so the published comparison against stdlib `re` stays faithful at the module boundary.

## Notes
- `RBR-1197` is the next available unreserved feature task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contain no active feature task in this run; and
  - `rg -n "RBR-1197|RBR-1198|quantified callable bytes benchmark|benchmark conditional group-exists quantified callable bytes|conditional-group-exists quantified callable bytes" ops/tasks ops/state -g '*.md'` matched only historical completion-note mentions, not a live reservation for this id.
- No blocked feature task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The newest done same-family frontier leaves this exact benchmark catch-up slice concrete after `RBR-1195`:
  - `ops/tasks/done/RBR-1195-publish-conditional-group-exists-quantified-callable-bytes-workflows.md` completed the bounded quantified conditional callable `bytes` correctness-publication slice and explicitly left the adjacent Python-path benchmark catch-up plus broader callable-helper expansion for later on this owner path;
  - `tests/conformance/fixtures/conditional_group_exists_callable_replacement_workflows.py`, `tests/python/test_callable_replacement_parity_suite.py`, and `reports/correctness/latest.py` now cover the exact eight quantified conditional callable `bytes` publication/parity rows on the shared owner path;
  - `benchmarks/workloads/conditional_group_exists_boundary.py` still stops at the quantified conditional callable `str` benchmark rows for this spelling, leaving the adjacent quantified `bytes` callable benchmark rows as the smallest still-missing publication slice on the same owner path; and
  - the same-family owner-path scan in this planning run did not pin a narrower exact post-benchmark follow-on beyond broad callable-helper expansion, so this queued task is the only concrete ready slice for now.
- Acceptance-command validation in this planning run:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'conditional_group_exists and callable'` returned `9 passed, 542 deselected, 108 subtests passed`;
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/feature-planning-conditional-group-exists-boundary-current.py` returned `144 measured workloads / 0 known gaps`; and
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py` returned `1075 measured workloads / 0 known gaps`.
