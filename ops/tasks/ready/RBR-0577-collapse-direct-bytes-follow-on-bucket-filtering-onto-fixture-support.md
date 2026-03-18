# RBR-0577: Collapse direct-bytes follow-on bucket filtering onto fixture support

Status: ready
Owner: architecture-implementation
Created: 2026-03-18

## Goal
- Remove the repeated direct-bytes follow-on manifest filtering that three large Python parity suites still implement locally, so `tests/python/fixture_parity_support.py` owns the generic compile/module/pattern bucket partitioning and the suites keep only their suite-specific bytes anchors and assertions.

## Deliverables
- `tests/python/fixture_parity_support.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/python/test_quantified_alternation_parity_suite.py`
- `tests/python/test_open_ended_quantified_group_parity_suite.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`

## Acceptance Criteria
- `tests/python/fixture_parity_support.py` adds one small shared helper named `partition_direct_bytes_follow_on_case_buckets(...)` that:
  - accepts the full `FIXTURE_BUNDLES` collection plus the direct-follow-on bundle subset as `FixtureBundle` objects rather than parallel manifest-id strings;
  - derives the follow-on manifest ids from those bundles instead of asking each suite to maintain a second `DIRECT_BYTES_FOLLOW_ON_MANIFEST_IDS` registry;
  - returns the generic `compile`, `module_call`, and `pattern_call` case tuples with only the `bytes` rows from those follow-on bundles removed; and
  - leaves all `str` rows plus all non-follow-on `bytes` rows untouched.
- `tests/python/test_fixture_parity_support_contract.py` adds focused contract coverage for the new helper:
  - one happy path proving mixed `str`/`bytes` follow-on bundles lose only their `bytes` rows from the generic buckets;
  - one preservation path proving unrelated `bytes` rows stay in the generic buckets; and
  - keep the coverage helper-focused instead of widening suite-local assertions.
- The three targeted parity suites switch from local manifest-id filtering to the shared helper:
  - `tests/python/test_quantified_alternation_parity_suite.py`
  - `tests/python/test_open_ended_quantified_group_parity_suite.py`
  - `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
  - delete `DIRECT_BYTES_FOLLOW_ON_MANIFEST_IDS` and `def _uses_direct_bytes_follow_on(...)` from each file;
  - build `COMPILE_CASES`, `MODULE_CASES`, and `PATTERN_CASES` through `partition_direct_bytes_follow_on_case_buckets(...)` instead of repeating the same three filtered comprehensions; and
  - keep each suite's explicit direct-follow-on bundle tuples, bytes case tables, and follow-on anchor assertions readable and local.
- Preserve current behavior exactly:
  - the filtered generic bucket case ids in all three suites stay unchanged;
  - `tests/python/test_quantified_alternation_parity_suite.py` still covers the same shared direct-test buckets plus the same bounded, broader-range, and open-ended bytes follow-on buckets;
  - `tests/python/test_open_ended_quantified_group_parity_suite.py` and `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` still keep their current bytes supplemental case tables and direct-follow-on anchor assertions explicit; and
  - do not change correctness fixtures, Rust code, benchmark files, published reports, README/current-status/backlog prose, or the current `RBR-0576` benchmark catch-up surface.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_quantified_alternation_parity_suite.py tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
  - `rg -n "DIRECT_BYTES_FOLLOW_ON_MANIFEST_IDS|def _uses_direct_bytes_follow_on\\(" tests/python/test_quantified_alternation_parity_suite.py tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
    The post-change result must be no matches.

## Constraints
- Keep this cleanup structural only. Do not change fixture contents, selected case ids, bytes anchor ids, backend behavior, benchmark coverage, or reporting output.
- Prefer extending `tests/python/fixture_parity_support.py` over adding another helper module or another suite-name registry.
- Where a suite already has an explicit follow-on bundle tuple or spec tuple, derive the helper input from that existing explicit surface instead of introducing a second manifest-id bookkeeping layer.
- Do not broaden this run into other parity suites, source-tree benchmark tests, `benchmarks/workloads/`, or `reports/benchmarks/latest.py`.

## Notes
- `RBR-0576` is already reserved in `ops/state/backlog.md` and `ops/state/current_status.md` for the current feature-owned bounded quantified-alternation bytes benchmark catch-up, so `RBR-0577` is the next available architecture id.
- No blocked architecture task exists to reopen first, and rule 10 does not apply in the current checkout:
  - `ops/tasks/blocked/` and `ops/tasks/in_progress/` are empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - `git status --short` is empty.
- JSON burn-down remains complete and aligned in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l = 0`; and
  - `rg --files -g '*.json' | wc -l = 0`.
- The duplicate bucket-partition surface is concrete in the current checkout:
  - `rg -n "DIRECT_BYTES_FOLLOW_ON_MANIFEST_IDS|def _uses_direct_bytes_follow_on\\(|for case in fixture_cases_for_operation\\(FIXTURE_BUNDLES, \\\"(compile|module_call|pattern_call)\\\"\\)" tests/python/test_quantified_alternation_parity_suite.py tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` currently returns 20 matches across the three suites; and
  - those matches are the same direct-follow-on manifest-id registry, bytes predicate, and filtered generic-bucket comprehensions repeated on top of the existing shared `assert_direct_bytes_follow_on_bundle_routing(...)` support helper.
- 2026-03-18 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_quantified_alternation_parity_suite.py tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` passes (`5943 passed in 4.21s`).
- This task stays off the active `RBR-0576` files under `benchmarks/`, `tests/benchmarks/`, and `reports/benchmarks/latest.py`, so the shared ready queue does not need another feature-planning pass before `architecture-implementation` can claim it.
