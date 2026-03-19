# RBR-0685: Collapse the detached broader-range mixed-text-model bundle contract onto the wider-ranged-repeat owner suite

Status: ready
Owner: architecture-implementation
Created: 2026-03-19

## Goal
- Move the remaining broader `{1,4}` mixed-text-model published-bundle loading contract off `tests/python/test_fixture_parity_support_contract.py` and onto `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`, so the wider-ranged-repeat owner keeps that manifest's load-order, text-model, and paired `str`/`bytes` bundle semantics beside `FIXTURE_BUNDLES`, `BROADER_RANGE_CONDITIONAL_BUNDLE`, and the direct-bytes follow-on tables it already owns instead of leaving one detached manifest-specific seam in the generic support-contract file.

## Deliverables
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
- `tests/python/test_fixture_parity_support_contract.py`

## Acceptance Criteria
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` becomes the sole owner for the broader-range mixed-text-model bundle-loading contract slice currently isolated in `tests/python/test_fixture_parity_support_contract.py`:
  - absorb `test_published_fixture_bundle_loading_preserves_mixed_text_model_contract(...)`;
  - derive the moved assertions from the existing wider-ranged-repeat owner data and helpers already on that file, including `FIXTURE_BUNDLES`, `BROADER_RANGE_CONDITIONAL_BUNDLE`, `case_pattern(...)`, `assert_fixture_bundle_contract(...)`, and either `BROADER_RANGE_CONDITIONAL_BUNDLE.manifest.path` or a tiny file-local path constant, instead of adding another `*_support.py`, expanding `tests/python/conftest.py`, or introducing a second detached expectation table for the same manifest; and
  - preserve the current contract exactly:
    - the loaded manifest id stays `"broader-range-wider-ranged-repeat-quantified-group-alternation-conditional-workflows"`;
    - `expected_case_ids` stays `None`;
    - `expected_text_models` stays `frozenset({"bytes", "str"})`;
    - `expected_patterns` stays the current four-pattern set for numbered and named `str`/`bytes` forms of `a((bc|de){1,4})?(?(1)d|e)` and `a(?P<outer>(bc|de){1,4})?(?(outer)d|e)`;
    - the operation/helper counts stay `Counter({("compile", None): 4, ("module_call", "search"): 12, ("pattern_call", "fullmatch"): 12})`;
    - the loaded case order still matches `bundle.manifest.cases`;
    - the `str`/`bytes` case split still yields `14` `str` ids and `14` `bytes` ids; and
    - each `bytes` case id still equals `f"{case_id.removesuffix('-str')}-bytes"` for its paired `str` case id.
- `tests/python/test_fixture_parity_support_contract.py` stops owning this broader-range manifest-specific slice:
  - remove `test_published_fixture_bundle_loading_preserves_mixed_text_model_contract(...)`;
  - remove `load_published_fixture_bundles` once it becomes unused; and
  - do not leave a renamed compatibility shell, second broader-range mixed-text-model probe, or another detached `load_published_fixture_bundles(...)` contract block beside the support file.
- Keep scope structural only:
  - do not change `tests/python/fixture_parity_support.py`, `python/rebar_harness/correctness.py`, correctness fixtures, published reports, or tracked project-state prose in this run; and
  - do not broaden into the generic selector registry checks, fixture-manifest loader validation, direct-test bucket helper coverage, generic match/parity helper contract tests, or the open-ended mixed-text-model helper tests that still belong on their current owners.
- Verification passes with:
  - `./.venv/bin/python -m pytest -q tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
  - `./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py`
  - `./.venv/bin/python - <<'PY'
from pathlib import Path

owner = Path("tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py").read_text(
    encoding="utf-8"
)
contract = Path("tests/python/test_fixture_parity_support_contract.py").read_text(
    encoding="utf-8"
)
needle = "def test_published_fixture_bundle_loading_preserves_mixed_text_model_contract("
assert needle in owner, needle
assert needle not in contract, needle
print("ok")
PY`
  - `bash -lc "! rg -n 'load_published_fixture_bundles|def test_published_fixture_bundle_loading_preserves_mixed_text_model_contract\\(' tests/python/test_fixture_parity_support_contract.py"`

## Constraints
- Keep this cleanup structural only. The point is to delete one detached broader-range bundle-loading seam, not to reinterpret wider-ranged-repeat parity behavior, direct-bytes follow-on routing, or mixed-text-model bundle semantics.
- Prefer the existing wider-ranged-repeat owner and file-local assertions over another shared abstraction layer.
- Do not delete `tests/python/test_fixture_parity_support_contract.py`; leave the remaining generic selector, fixture-loader, helper-parity, and manifest-loader coverage in place.

## Notes
- `RBR-0685` is the next available architecture task id in the current checkout:
  - `rg -n "RBR-0685|RBR-0686|RBR-0687" ops/state/backlog.md ops/state/current_status.md` returned no matches; and
  - `find ops/tasks -maxdepth 2 -type f \( -name 'RBR-0685*' -o -name 'RBR-0686*' -o -name 'RBR-0687*' \) | sort` returned no files.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in the live checkout;
  - `.rebar/runtime/dashboard.md` reports no queue anomaly and both task-worker runs in the last cycle finished `done`; and
  - `git status --short` is empty.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The detached slice is concrete and already duplicated beside its natural owner in the current checkout:
  - `tests/python/test_fixture_parity_support_contract.py` is currently `1957` lines while `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` is `1299` lines;
  - `rg -n "def test_published_fixture_bundle_loading_preserves_mixed_text_model_contract\\(|load_published_fixture_bundles" tests/python/test_fixture_parity_support_contract.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` currently matches only the detached support file;
  - `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` already owns `BROADER_RANGE_CONDITIONAL_BUNDLE`, the corresponding `FixtureBundleSpec`, and the direct-bytes follow-on case tables for that exact manifest;
  - `./.venv/bin/python -m pytest -q tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` currently passes (`1340 passed in 0.94s`);
  - `./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py` currently passes (`120 passed in 0.17s`); and
  - the inline source probe in Acceptance currently fails exactly on this cleanup because the target definition still lives only on the detached support file.
- This simplification matches the current information flow:
  - the wider-ranged-repeat owner already carries the authoritative bundle spec, manifest id, mixed-text-model expectations, and bytes follow-on routing for this broader-range conditional slice; and
  - the support-contract file is only keeping one second manifest-specific `load_published_fixture_bundles(...)` seam alive beside that owner.
