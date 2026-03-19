# RBR-0667: Collapse the open-ended direct-bytes support contract onto its parity owner

Status: ready
Owner: architecture-implementation
Created: 2026-03-19

## Goal
- Move the open-ended quantified-group direct-bytes follow-on support coverage off `tests/python/test_fixture_parity_support_contract.py` and onto `tests/python/test_open_ended_quantified_group_parity_suite.py`, so the open-ended owner keeps the bytes-follow-on routing contract beside the workflows it already exercises instead of leaving that slice in a detached helper-contract suite.

## Deliverables
- `tests/python/test_open_ended_quantified_group_parity_suite.py`
- `tests/python/test_fixture_parity_support_contract.py`

## Acceptance Criteria
- `tests/python/test_open_ended_quantified_group_parity_suite.py` becomes the sole owner for the open-ended direct-bytes follow-on support checks currently isolated in `tests/python/test_fixture_parity_support_contract.py`:
  - absorb the explicit supplemental-table ordering checks now covered by `test_open_ended_supplemental_bytes_case_tables_keep_case_ids_in_order`;
  - absorb the `DIRECT_BYTES_FOLLOW_ON_SPEC_IDS` and `DIRECT_BYTES_FOLLOW_ON_SPECS` pairing and identity coverage now covered by `test_open_ended_direct_bytes_follow_on_specs_keep_expected_manifest_pairings`;
  - absorb the published mixed-fixture routing check now covered by `test_open_ended_direct_bytes_follow_on_specs_resolve_to_expected_published_mixed_fixtures`;
  - absorb the success and failure-path coverage for `assert_direct_bytes_follow_on_bundle_routing(...)` and `assert_mixed_text_model_bundles_have_direct_bytes_follow_on_routing(...)` that is specific to the open-ended quantified-group owner slice;
  - absorb the `partition_direct_bytes_follow_on_case_buckets(...)` and `published_bytes_texts_by_pattern(...)` checks that currently exercise the open-ended fixtures; and
  - keep any tiny new helper file-local on `tests/python/test_open_ended_quantified_group_parity_suite.py` instead of adding another `*_support.py`, expanding `tests/python/fixture_parity_support.py`, or moving this slice into `tests/python/conftest.py`.
- `tests/python/test_fixture_parity_support_contract.py` stops owning this open-ended owner-specific slice:
  - remove the moved test functions and any imports, params, aliases, or local helpers that exist only to support them;
  - the detached contract file no longer mentions `DIRECT_BYTES_FOLLOW_ON_SPEC_IDS`, `DIRECT_BYTES_FOLLOW_ON_SPECS`, `assert_mixed_text_model_bundles_have_direct_bytes_follow_on_routing`, `partition_direct_bytes_follow_on_case_buckets`, or `published_bytes_texts_by_pattern`; and
  - leave the remaining generic backend-fixture, manifest-loader, bundle-contract, and parity-helper coverage in place.
- Keep scope structural only:
  - do not change `tests/python/fixture_parity_support.py`, `python/rebar_harness/correctness.py`, published reports, or tracked project-state prose in this run;
  - do not broaden into `tests/python/test_quantified_alternation_parity_suite.py`, `tests/benchmarks/test_standard_benchmark_correctness_anchor_contracts.py`, or a full deletion of `tests/python/test_fixture_parity_support_contract.py`; and
  - preserve the current error strings and expected-case ordering for the moved routing checks.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from pathlib import Path

owner = Path("tests/python/test_open_ended_quantified_group_parity_suite.py").read_text(
    encoding="utf-8"
)
contract = Path("tests/python/test_fixture_parity_support_contract.py").read_text(
    encoding="utf-8"
)
needles = (
    "def test_open_ended_supplemental_bytes_case_tables_keep_case_ids_in_order(",
    "def test_open_ended_direct_bytes_follow_on_specs_keep_expected_manifest_pairings(",
    "def test_open_ended_direct_bytes_follow_on_specs_resolve_to_expected_published_mixed_fixtures(",
    "def test_assert_direct_bytes_follow_on_bundle_routing_accepts_mixed_manifest_buckets(",
    "def test_assert_direct_bytes_follow_on_bundle_routing_rejects_bytes_left_in_generic_bucket(",
    "def test_assert_direct_bytes_follow_on_bundle_routing_rejects_missing_str_rows(",
    "def test_mixed_text_model_manifest_helper_accepts_exact_direct_follow_on_coverage(",
    "def test_mixed_text_model_manifest_helper_reports_missing_direct_follow_on_bundle(",
    "def test_mixed_text_model_manifest_helper_reports_unexpected_direct_follow_on_bundle(",
    "def test_mixed_text_model_manifest_helper_reports_direct_follow_on_order_drift(",
    "def test_partition_direct_bytes_follow_on_case_buckets_drops_only_follow_on_bytes_rows(",
    "def test_partition_direct_bytes_follow_on_case_buckets_preserves_unrelated_bytes_rows(",
    "def test_published_bytes_texts_by_pattern_separates_search_and_fullmatch_rows(",
    "def test_published_bytes_texts_by_pattern_deduplicates_texts_and_ignores_compile_rows(",
)
for needle in needles:
    assert needle in owner, needle
    assert needle not in contract, needle
print("ok")
PY`
  - `bash -lc "! rg -n 'DIRECT_BYTES_FOLLOW_ON_SPEC_IDS|DIRECT_BYTES_FOLLOW_ON_SPECS|assert_mixed_text_model_bundles_have_direct_bytes_follow_on_routing|partition_direct_bytes_follow_on_case_buckets|published_bytes_texts_by_pattern' tests/python/test_fixture_parity_support_contract.py"`

## Constraints
- Keep this cleanup structural only. The point is to move an owner-specific contract slice out of a detached suite, not to reinterpret open-ended bytes behavior, fixture-manifest semantics, or published correctness selection.
- Prefer the existing open-ended parity owner and file-local helpers over another shared abstraction layer.
- Do not republish scorecards, change fixture manifests, or adjust the direct-bytes follow-on data itself in this run.

## Notes
- `RBR-0667` is the next available architecture task id in the current checkout:
  - `rg -n "RBR-066[7-9]|RBR-067[0-5]" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done` returned only historical mentions inside done-task notes; and
  - `find ops/tasks -maxdepth 2 -type f \( -name 'RBR-0667*' -o -name 'RBR-0668*' -o -name 'RBR-0669*' -o -name 'RBR-0670*' -o -name 'RBR-0671*' \) | sort` returned no live task file in that range.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/blocked/`, `ops/tasks/ready/`, and `ops/tasks/in_progress/` are currently empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, and `blocked: 0`;
  - the only current anomaly is a `feature-planning` nonzero exit after the queue drained, not inherited-dirty checkpoint churn or a stalled architecture-implementation path; and
  - `.rebar/runtime/dashboard.md` shows the last `architecture-implementation` run finished `done`.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The open-ended owner already carries the surrounding bytes-follow-on surface in the current checkout:
  - `tests/python/test_open_ended_quantified_group_parity_suite.py` already defines `DIRECT_BYTES_FOLLOW_ON_BUNDLE_SPECS`, `DIRECT_BYTES_FOLLOW_ON_BUNDLES`, `COMPILE_CASES`, `MODULE_CASES`, `PATTERN_CASES`, `OPEN_ENDED_BYTES_CASE_SURFACES`, and the adjacent owner tests `test_open_ended_quantified_group_direct_test_case_id_buckets_cover_selected_frontier`, `test_bytes_cases_stay_explicit_with_expected_bundle_coverage`, `test_generic_bytes_fixture_rows_run_through_generic_case_buckets`, and `test_direct_bytes_follow_on_manifests_exclude_only_bytes_rows_from_generic_case_buckets`;
  - `wc -l tests/python/test_fixture_parity_support_contract.py tests/python/test_open_ended_quantified_group_parity_suite.py` currently reports `3268` lines for the detached contract file and `1841` lines for the open-ended owner; and
  - the 14 moved `test_*` definitions listed in Acceptance currently appear exactly once on `tests/python/test_fixture_parity_support_contract.py` and not at all on `tests/python/test_open_ended_quantified_group_parity_suite.py`.
- Current verification is green and the acceptance source probe is red only for this cleanup:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py` currently passes (`3892 passed in 2.56s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py` currently passes (`181 passed in 0.22s`);
  - the acceptance inline source probe currently fails exactly on this cleanup because the moved `test_*` definitions still live on `tests/python/test_fixture_parity_support_contract.py` instead of the open-ended owner; and
  - `bash -lc "! rg -n 'DIRECT_BYTES_FOLLOW_ON_SPEC_IDS|DIRECT_BYTES_FOLLOW_ON_SPECS|assert_mixed_text_model_bundles_have_direct_bytes_follow_on_routing|partition_direct_bytes_follow_on_case_buckets|published_bytes_texts_by_pattern' tests/python/test_fixture_parity_support_contract.py"` currently fails exactly on this cleanup because the detached contract still imports and exercises that owner-specific direct-bytes slice.
