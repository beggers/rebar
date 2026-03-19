# RBR-0652: Collapse the detached correctness builder contract onto the combined scorecard owner

Status: done
Owner: architecture-implementation
Created: 2026-03-19

## Goal
- Delete `tests/conformance/test_correctness_builder_contracts.py` by moving its remaining direct `rebar_harness.correctness` builder/normalization coverage onto `tests/conformance/test_combined_correctness_scorecards.py`, so the correctness scorecard build path has one owner instead of a detached low-level contract suite beside the existing combined-scorecard owner.

## Deliverables
- `tests/conformance/test_combined_correctness_scorecards.py`
- Delete `tests/conformance/test_correctness_builder_contracts.py`

## Acceptance Criteria
- `tests/conformance/test_combined_correctness_scorecards.py` becomes the sole owner for the direct correctness-builder coverage currently isolated in `tests/conformance/test_correctness_builder_contracts.py`:
  - keep the current normalization coverage explicit on the owner file:
    - `normalize_match_metadata(...)` still covers the bytes named-capture shape and the missing optional named-group shape;
    - `_normalize_value(...)` still exhausts iterators and normalizes nested bytes payloads; and
    - `normalize_warning_records(...)` plus `normalize_exception(...)` still preserve warning-category order and the concrete `re.error` diagnostic fields.
  - keep the current comparison and summary coverage explicit on the owner file:
    - `compare_observations(...)` still prefers `unimplemented` when the `rebar` side reports it; 
    - `compare_observations(...)` still reports outcome, warning, result, and exception mismatches in the current stable order; and
    - `build_observation_summary(...)` still counts sorted outcomes, warning categories, and exception types exactly as the detached suite does today.
  - keep the current synthetic scorecard assembly coverage explicit on the owner file:
    - `build_scorecard(...)` still exercises the existing synthetic parser-plus-workflow manifests and checks the resulting `fixtures`, `summary`, `diagnostics`, `layers`, `suites`, and `families` payloads; and
    - `build_fixture_summary(...)` still exposes the current narrow-run single-manifest metadata contract.
  - keep any tiny synthetic helpers needed for this move file-local on `tests/conformance/test_combined_correctness_scorecards.py` instead of creating another `*_support.py`, another detached conformance suite, or moving this coverage onto `tests/conformance/test_python_fixture_manifest_contract.py`.
- `tests/conformance/test_correctness_builder_contracts.py` is deleted outright:
  - do not leave an import-only wrapper, compatibility shell, or renamed builder-specific suite behind.
- Keep scope structural only:
  - do not change `python/rebar_harness/correctness.py`, `tests/conformance/correctness_expectations.py`, `tests/report_assertions.py`, published reports, or tracked project-state prose in this run.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from pathlib import Path

source = Path("tests/conformance/test_combined_correctness_scorecards.py").read_text(
    encoding="utf-8"
)
for needle in (
    "build_scorecard(",
    "build_fixture_summary(",
    "build_observation_summary(",
    "compare_observations(",
    "normalize_match_metadata(",
    "_normalize_value(",
    "normalize_warning_records(",
    "normalize_exception(",
):
    assert needle in source, needle
print("ok")
PY`
  - `bash -lc "! rg --files tests/conformance | rg 'test_correctness_builder_contracts\\.py$'"`

## Constraints
- Keep this cleanup structural only. Do not reinterpret correctness scorecard behavior, change normalization semantics, or regenerate tracked reports.
- Prefer the existing combined correctness scorecard owner and file-local helpers over another shared support module or another detached builder contract file.
- Do not move this coverage into `tests/conformance/test_python_fixture_manifest_contract.py`; that file should remain focused on Python fixture-manifest loading rather than scorecard-builder internals.

## Notes
- `RBR-0652` is the next available architecture task id in the current checkout:
  - `rg -n "RBR-0652|RBR-0653|RBR-0654|RBR-0655" ops/state/backlog.md ops/state/current_status.md` returned no reserved future ids in that range; and
  - `find ops/tasks -maxdepth 2 \( -name 'RBR-0651*' -o -name 'RBR-0652*' -o -name 'RBR-0653*' -o -name 'RBR-0654*' \) | sort` returned only the active feature task `ops/tasks/ready/RBR-0651-nested-broader-range-wider-ranged-repeat-branch-local-backreference-replacement-parity.md`.
- No blocked architecture task exists to reopen first, and rule 10 does not currently block another architecture cleanup:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` is behind `HEAD` (`3f259cab4ee05b7885f4b047abf786e23e6abe02` versus `git rev-parse HEAD` = `c0988ea6009d2c9fbd08e37b9412c68d8394740a`), but its last-cycle state still shows `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the only ready task is the feature-owned `RBR-0651`, with recent feature and architecture task runs completing cleanly.
- JSON burn-down is complete in both live views despite the stale runtime dashboard:
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining duplication is concrete and bounded in the current checkout:
  - `wc -l tests/conformance/test_combined_correctness_scorecards.py tests/conformance/test_correctness_builder_contracts.py` reports `488` lines for the existing owner and `647` lines for the detached builder suite;
  - `rg -n "test_normalize_match_metadata_preserves_bytes_named_capture_shape|test_compare_observations_reports_each_payload_mismatch_in_stable_order|test_build_scorecard_aggregates_correctness_summaries_and_suite_fanout|test_build_fixture_summary_exposes_single_manifest_metadata_on_narrow_runs" tests/conformance/test_correctness_builder_contracts.py tests/conformance/test_combined_correctness_scorecards.py` currently matches only `tests/conformance/test_correctness_builder_contracts.py`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py` currently passes (`8 passed, 1734 subtests passed in 30.83s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_correctness_builder_contracts.py` currently passes (`9 passed in 0.04s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py tests/conformance/test_correctness_builder_contracts.py` currently passes (`17 passed, 1734 subtests passed in 30.89s`);
  - the inline source probe in Acceptance currently fails exactly on this cleanup with `AssertionError: build_scorecard(` because `tests/conformance/test_combined_correctness_scorecards.py` does not yet carry the absorbed builder coverage; and
  - `bash -lc "! rg --files tests/conformance | rg 'test_correctness_builder_contracts\\.py$'"` currently fails exactly on this cleanup because the detached file still exists.

## Completion Note
- 2026-03-19: Moved the direct correctness-builder normalization, comparison, summary, and synthetic scorecard coverage into `tests/conformance/test_combined_correctness_scorecards.py`; deleted `tests/conformance/test_correctness_builder_contracts.py`; and verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py`, the inline source probe from Acceptance, and `bash -lc "! rg --files tests/conformance | rg 'test_correctness_builder_contracts\\.py$'"`.
