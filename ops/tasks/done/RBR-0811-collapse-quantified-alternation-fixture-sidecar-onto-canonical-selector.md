# RBR-0811: Collapse the quantified-alternation fixture sidecar onto the canonical selector

Status: done
Owner: architecture-implementation
Created: 2026-03-21

## Goal
- Delete the file-local quantified-alternation fixture filename sidecar in `tests/python/test_quantified_alternation_parity_suite.py`.
- Keep the quantified-alternation parity suite anchored to the correctness harness's canonical selector by loading its fixture paths through `select_correctness_fixture_paths(QUANTIFIED_ALTERNATION_FIXTURE_SELECTOR)` instead of hand-maintaining the same manifest list in the test module.

## Deliverables
- `tests/python/test_quantified_alternation_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_quantified_alternation_parity_suite.py` no longer defines or references:
  - `QUANTIFIED_ALTERNATION_FIXTURE_NAMES`; or
  - the `CORRECTNESS_FIXTURES_ROOT / fixture_name` tuple-comprehension sidecar used only to rebuild that selector.
- `FIXTURE_BUNDLES` loads from the correctness harness selector instead of the handwritten filename tuple:
  - import and use `QUANTIFIED_ALTERNATION_FIXTURE_SELECTOR` plus `select_correctness_fixture_paths` from `rebar_harness.correctness`;
  - keep `pattern_extractor=case_pattern`; and
  - do not add another local filename table, manifest-id keyed selector map, or replacement helper just to restate the same published slice.
- Preserve the existing explicit quantified-alternation bundle anchors and parity coverage behavior:
  - keep `QUANTIFIED_ALTERNATION_BOUNDED_BUNDLE`, `QUANTIFIED_ALTERNATION_BROADER_RANGE_BUNDLE`, `QUANTIFIED_ALTERNATION_CONDITIONAL_BUNDLE`, `QUANTIFIED_ALTERNATION_OPEN_ENDED_BUNDLE`, `QUANTIFIED_ALTERNATION_NESTED_BRANCH_BUNDLE`, and `BACKTRACKING_HEAVY_BUNDLE` resolved by manifest id through `published_fixture_bundle_by_manifest_id(...)`;
  - keep the generated compile-parity specs and direct-bytes follow-on specs pinned to the same manifest ids they use today; and
  - do not broaden into `python/rebar_harness/correctness.py`, fixture manifests under `tests/conformance/fixtures/`, reports, README copy, or tracked project-state prose.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py`
  - `bash -lc "! rg -n 'QUANTIFIED_ALTERNATION_FIXTURE_NAMES|CORRECTNESS_FIXTURES_ROOT / fixture_name' tests/python/test_quantified_alternation_parity_suite.py"`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from rebar_harness.correctness import (
    QUANTIFIED_ALTERNATION_FIXTURE_SELECTOR,
    select_correctness_fixture_paths,
)
import tests.python.test_quantified_alternation_parity_suite as mod

assert tuple(bundle.manifest.path for bundle in mod.FIXTURE_BUNDLES) == (
    select_correctness_fixture_paths(QUANTIFIED_ALTERNATION_FIXTURE_SELECTOR)
)
assert tuple(
    bundle.manifest.manifest_id
    for bundle in (
        mod.QUANTIFIED_ALTERNATION_BOUNDED_BUNDLE,
        mod.QUANTIFIED_ALTERNATION_BROADER_RANGE_BUNDLE,
        mod.QUANTIFIED_ALTERNATION_CONDITIONAL_BUNDLE,
        mod.QUANTIFIED_ALTERNATION_OPEN_ENDED_BUNDLE,
        mod.QUANTIFIED_ALTERNATION_NESTED_BRANCH_BUNDLE,
        mod.BACKTRACKING_HEAVY_BUNDLE,
    )
) == (
    "quantified-alternation-workflows",
    "quantified-alternation-broader-range-workflows",
    "quantified-alternation-conditional-workflows",
    "quantified-alternation-open-ended-workflows",
    "quantified-alternation-nested-branch-workflows",
    "quantified-alternation-backtracking-heavy-workflows",
)
print("ok")
PY`

## Constraints
- Keep this cleanup limited to `tests/python/test_quantified_alternation_parity_suite.py`.
- Prefer deleting the handwritten selector mirror over adding another helper, another registry, or another compatibility shim.

## Notes
- `RBR-0811` is free in the current checkout:
  - `rg -n "RBR-0811|RBR-0812|RBR-0813|RBR-0814" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done` returned only the historical mention embedded in the completed `RBR-0809` notes and no reserved or live-queue conflict.
- No blocked architecture task exists to reopen first, and rule 10 does not apply here:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the most recent cycle completed both architecture and feature work cleanly, so there is no inherited-dirty or post-task refresh bottleneck to yield to.
- JSON burn-down is complete in both tracked and live views, so this stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete in the live checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py` currently passes (`778 passed in 0.99s`);
  - `rg -n 'QUANTIFIED_ALTERNATION_FIXTURE_NAMES|CORRECTNESS_FIXTURES_ROOT / fixture_name' tests/python/test_quantified_alternation_parity_suite.py` currently reports exactly the local filename tuple plus the tuple-comprehension load site; and
  - a live probe shows the suite is mirroring the harness-owned selector rather than defining an independent slice: `select_correctness_fixture_paths(QUANTIFIED_ALTERNATION_FIXTURE_SELECTOR)` resolves the same nine manifest filenames already loaded by the suite, but through the canonical correctness-harness path instead of the local sidecar.
- The selector currently returns a different raw path order than the local tuple, but this suite resolves its important anchors by manifest id:
  - the generated parity specs already assert against the six explicit bundle constants rather than the raw `FIXTURE_BUNDLES` tuple order; and
  - the direct-bytes follow-on coverage also keys off explicit manifest-id lookups, so this cleanup should stay limited to deleting the duplicated selector metadata instead of changing fixture contents or broadening test scope.
- 2026-03-21: Replaced the local quantified-alternation filename sidecar in `tests/python/test_quantified_alternation_parity_suite.py` with `select_correctness_fixture_paths(QUANTIFIED_ALTERNATION_FIXTURE_SELECTOR)`, kept the explicit manifest-id bundle anchors unchanged, and left the generated compile-parity plus direct-bytes follow-on coverage pinned to the same manifest ids as before. Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py` (`778 passed in 1.04s`), `bash -lc "! rg -n 'QUANTIFIED_ALTERNATION_FIXTURE_NAMES|CORRECTNESS_FIXTURES_ROOT / fixture_name' tests/python/test_quantified_alternation_parity_suite.py"` (passed with no matches), and the task's selector-path assertion snippet (`ok`).
