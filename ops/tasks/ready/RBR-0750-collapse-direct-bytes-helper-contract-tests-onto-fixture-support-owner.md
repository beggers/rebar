# RBR-0750: Collapse direct-bytes helper contract tests onto fixture support owner

Status: ready
Owner: architecture-implementation
Created: 2026-03-20

## Goal
- Remove the generic direct-bytes follow-on helper contract coverage from `tests/python/test_open_ended_quantified_group_parity_suite.py` so that file keeps only open-ended-owner assertions, while the shared helper contracts live under the canonical support-contract owner in `tests/python/test_fixture_parity_support_contract.py`.
- Make `tests/python/test_fixture_parity_support_contract.py` the single contract owner for the generic direct-bytes helper APIs already shared across multiple parity suites: `assert_direct_bytes_follow_on_bundle_routing(...)`, `assert_mixed_text_model_bundles_have_direct_bytes_follow_on_routing(...)`, `partition_direct_bytes_follow_on_case_buckets(...)`, and `published_bytes_texts_by_pattern(...)`.

## Deliverables
- `tests/python/test_open_ended_quantified_group_parity_suite.py`
- `tests/python/test_fixture_parity_support_contract.py`

## Acceptance Criteria
- `tests/python/test_open_ended_quantified_group_parity_suite.py` stops defining the generic helper-contract tests that currently live there:
  - `test_assert_direct_bytes_follow_on_bundle_routing_accepts_mixed_manifest_buckets`
  - `test_assert_direct_bytes_follow_on_bundle_routing_rejects_bytes_left_in_generic_bucket`
  - `test_assert_direct_bytes_follow_on_bundle_routing_rejects_unexpected_str_rows`
  - `test_assert_direct_bytes_follow_on_bundle_routing_rejects_missing_str_rows`
  - `test_assert_direct_bytes_follow_on_bundle_routing_rejects_str_only_manifest_bundle`
  - `test_mixed_text_model_manifest_helper_accepts_exact_direct_follow_on_coverage`
  - `test_mixed_text_model_manifest_helper_reports_missing_direct_follow_on_bundle`
  - `test_mixed_text_model_manifest_helper_reports_unexpected_direct_follow_on_bundle`
  - `test_mixed_text_model_manifest_helper_reports_direct_follow_on_order_drift`
  - `test_partition_direct_bytes_follow_on_case_buckets_drops_only_follow_on_bytes_rows`
  - `test_partition_direct_bytes_follow_on_case_buckets_preserves_unrelated_bytes_rows`
  - `test_published_bytes_texts_by_pattern_separates_search_and_fullmatch_rows`
  - `test_published_bytes_texts_by_pattern_deduplicates_texts_and_handles_compiled_module_rows`
- `tests/python/test_open_ended_quantified_group_parity_suite.py` keeps the owner-local direct-bytes surface assertions, but they derive from already-loaded owner data instead of generic support-contract helpers:
  - the suite still verifies the exact ordered `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` pairings for the open-ended owner; and
  - any remaining mixed-text-model assertion in that file should read `spec.bundle` / `DIRECT_BYTES_FOLLOW_ON_CASE_SURFACES` directly rather than reloading bundles through `load_published_fixture_bundles(...)` or routing through `assert_mixed_text_model_bundles_have_direct_bytes_follow_on_routing(...)`.
- `tests/python/test_open_ended_quantified_group_parity_suite.py` no longer imports either of these shared-contract-only helpers:
  - `load_published_fixture_bundles`
  - `assert_mixed_text_model_bundles_have_direct_bytes_follow_on_routing`
- `tests/python/test_fixture_parity_support_contract.py` gains the shared contract coverage that replaces the deleted open-ended copies:
  - success and drift/error-path coverage for `assert_direct_bytes_follow_on_bundle_routing(...)`
  - success and drift/error-path coverage for `assert_mixed_text_model_bundles_have_direct_bytes_follow_on_routing(...)`
  - success-path coverage for `partition_direct_bytes_follow_on_case_buckets(...)`, including preserving unrelated bytes rows outside the selected direct-follow-on manifest set
  - success-path coverage for `published_bytes_texts_by_pattern(...)`, including the compiled-module row handling and text deduplication currently asserted in the open-ended suite
- The moved shared-contract tests must not import direct-bytes surface registries from `tests/python/test_open_ended_quantified_group_parity_suite.py`. Use `tests.python.fixture_parity_support`, `CORRECTNESS_FIXTURES_ROOT`, and/or small local synthetic fixtures directly from the contract owner instead of routing helper coverage through a parity-owner module.
- Keep parity behavior unchanged:
  - do not edit `tests/python/fixture_parity_support.py`, any correctness fixture modules under `tests/conformance/fixtures/`, benchmark files, reports, `python/rebar/`, `crates/`, README copy, or tracked project-state prose in this run.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_fixture_parity_support_contract.py`
  - `bash -lc "! rg -n \"def test_assert_direct_bytes_follow_on_bundle_routing_|def test_mixed_text_model_manifest_helper_|def test_partition_direct_bytes_follow_on_case_buckets_|def test_published_bytes_texts_by_pattern_\" tests/python/test_open_ended_quantified_group_parity_suite.py"`

## Constraints
- Keep this cleanup structural only. The point is to put generic helper-contract coverage under the one shared owner and trim one parity owner back to owner-specific checks, not to reinterpret direct-bytes routing, alter published fixture payloads, or broaden the open-ended parity frontier.
- Prefer moving or lightly rewriting the existing helper-contract tests over inventing another abstraction layer.

## Notes
- `RBR-0750` is the next available task id in the current checkout:
  - `python3 - <<'PY'
import pathlib, re
existing = set()
for base in ['ops/tasks/ready', 'ops/tasks/in_progress', 'ops/tasks/done', 'ops/tasks/blocked']:
    for path in pathlib.Path(base).glob('RBR-*.md'):
        m = re.match(r'(RBR-\d+[A-Z]?)', path.name)
        if m:
            existing.add(m.group(1))
text = '\n'.join(
    pathlib.Path(p).read_text(encoding='utf-8')
    for p in ['ops/state/backlog.md', 'ops/state/current_status.md']
)
reserved = set(re.findall(r'RBR-\d+[A-Z]?', text)) - existing
existing_sorted = sorted(existing, key=lambda s: (int(re.search(r'\d+', s).group()), s))
reserved_sorted = sorted(reserved, key=lambda s: (int(re.search(r'\d+', s).group()), s))
print('highest_existing_tail', existing_sorted[-10:])
print('reserved_tail', reserved_sorted[-10:])
for n in range(int(re.search(r'\d+', existing_sorted[-1]).group()), int(re.search(r'\d+', existing_sorted[-1]).group()) + 120):
    rid = f'RBR-{n:04d}'
    if rid not in existing and rid not in reserved:
        print('next_free', rid)
        break
PY` reported the existing tail through `RBR-0749`, no reserved missing tail ids, and `next_free RBR-0750`.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added; and
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`.
- JSON burn-down is complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication is concrete in the current checkout:
  - `tests/python/test_open_ended_quantified_group_parity_suite.py` still carries thirteen generic helper-contract tests for shared direct-bytes support helpers, even though `tests/python/test_fixture_parity_support_contract.py` already exists as the dedicated support-contract owner;
  - `rg -n "def test_assert_direct_bytes_follow_on_bundle_routing_|def test_mixed_text_model_manifest_helper_|def test_partition_direct_bytes_follow_on_case_buckets_|def test_published_bytes_texts_by_pattern_" tests/python/test_open_ended_quantified_group_parity_suite.py` currently shows those helper-contract tests only in the open-ended parity owner; and
  - the shared helpers under test are already used across multiple parity owners, including `tests/python/test_quantified_alternation_parity_suite.py`, `tests/python/test_branch_local_backreference_parity_suite.py`, `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`, and `tests/python/test_open_ended_quantified_group_parity_suite.py`.
- The baseline verification is green in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_fixture_parity_support_contract.py` passed (`4131 passed in 2.84s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py -k 'direct_bytes_follow_on_bundle_routing or partition_direct_bytes_follow_on_case_buckets or mixed_text_model_manifest_helper or published_bytes_texts_by_pattern or direct_bytes_follow_on_case_surfaces_resolve_to_expected_published_mixed_fixtures'` passed (`22 passed, 3901 deselected in 0.23s`); and
  - the final `rg` absence check in Acceptance currently fails exactly on this cleanup because those generic helper-contract tests still live in the open-ended parity owner.
