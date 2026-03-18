# RBR-0642: Collapse the detached Rust compile/match boundary suite onto the module-workflow owner

Status: ready
Owner: architecture-implementation
Created: 2026-03-18

## Goal
- Delete `tests/python/test_rust_compile_match_boundary.py` by moving its remaining source-tree `_native` boundary coverage onto `tests/python/test_module_workflow_parity_suite.py`, so compile/match/collection/replacement dispatch through the native bridge stops living on a detached legacy file beside the existing module-workflow owner.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`
- Delete `tests/python/test_rust_compile_match_boundary.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` becomes the sole owner for the bounded `_native` boundary coverage currently isolated in `tests/python/test_rust_compile_match_boundary.py`:
  - keep the current fake-native compile/search boundary assertions on the module-workflow owner file instead of another helper module, wrapper suite, or follow-on owner;
  - preserve the direct compile metadata and native error-routing observations that matter for this slice:
    - `rebar.compile("abc", rebar.IGNORECASE)` still reports the current fake-native flags path;
    - compiled `search("zabczz")` still proves the native boundary controls the `Match` span, `pos`, `endpos`, and `group(0)` payload;
    - native compile failures still surface as `re.error` with the current message shape; and
    - unsupported compiled-pattern `search()` still surfaces the current native placeholder message instead of silently falling back.
- The absorbed boundary coverage stays on the module-workflow owner for the collection/replacement helper slice it already owns:
  - preserve the current fake-native module/pattern helper observations for `split`, `findall`, `finditer`, `sub`, and `subn` across both `str` and `bytes`;
  - keep the current returned values explicit (`"native-split"`, `"native-findall"`, `"native-subn"`, and the existing bytes mirrors) rather than weakening the assertions to generic truthiness checks; and
  - keep the helper-dispatch trace explicit through the existing owner suite, using the current call sequence or equivalent file-local assertions that prove module and compiled-pattern helpers are consuming fake-native results instead of source-tree Python fallbacks.
- Unsupported fake-native results still keep the current public placeholder behavior explicit on the module-workflow owner:
  - `rebar.findall("unsupported", "unsupported")` still raises the current module placeholder message; and
  - `rebar.compile("unsupported").finditer("unsupported")` still raises the current `Pattern.finditer()` placeholder message.
- Keep `escape()` on the existing module-workflow owner surface without perpetuating the detached file's stale bytes-call expectation:
  - preserve the existing public `escape()` parity tables already owned by `tests/python/test_module_workflow_parity_suite.py`; and
  - if any absorbed fake-native `escape()` assertion remains, make it match the live routing currently observed in this checkout for `rebar.escape(b"a-b")` instead of preserving the detached suite's failing `("escape", b"a-b")` call expectation.
- `tests/python/test_rust_compile_match_boundary.py` is deleted outright:
  - do not leave an import-only wrapper, compatibility shell, or `*_support.py` helper behind; and
  - do not move this boundary slice into `tests/python/test_native_extension_smoke.py` or another non-owner suite.
- Keep scope structural only:
  - do not change `python/rebar/`, Rust code, correctness fixtures, benchmark files, reports, or tracked state prose; and
  - do not broaden this cleanup into `tests/python/test_native_extension_smoke.py`, `tests/python/test_public_surface_parity_suite.py`, or another owner shuffle in the same run.
- After the consolidation lands:
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from tests.python import test_module_workflow_parity_suite as mod

assert tuple(spec.expected_manifest_id for spec in mod.SELECTED_CASE_BUNDLE_SPECS) == (
    "module-workflow-surface",
    "match-behavior-smoke",
)
print("ok")
PY`
  - `bash -lc "! rg --files tests/python | rg 'test_rust_compile_match_boundary\\.py$'"`
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from tests.python import test_module_workflow_parity_suite as mod

assert tuple(spec.expected_manifest_id for spec in mod.SELECTED_CASE_BUNDLE_SPECS) == (
    "module-workflow-surface",
    "match-behavior-smoke",
)
print("ok")
PY`
  - `bash -lc "! rg --files tests/python | rg 'test_rust_compile_match_boundary\\.py$'"`

## Constraints
- Keep this cleanup structural only. Do not change native/runtime behavior, broaden regex support, or alter public placeholder messages beyond matching the live behavior already present in the checkout.
- Prefer the existing module-workflow owner and its file-local helpers over another cross-suite support layer or another detached boundary suite.
- Do not preserve the detached suite's stale internal bytes-escape assertion just to keep the old file unchanged; keep the live owner surface honest instead.

## Notes
- `RBR-0642` is the next available architecture task id in the current checkout:
  - `rg -n 'RBR-0642|RBR-0643|RBR-0644|RBR-0645' ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked` returned no reserved or active entry in that range; and
  - `find ops/tasks -maxdepth 2 -name 'RBR-0642*' -o -name 'RBR-0643*' -o -name 'RBR-0644*' -o -name 'RBR-0645*'` returned no matching task files.
- No blocked architecture task exists to reopen first, and rule 10 does not currently block another architecture task:
  - `ops/tasks/blocked/` is empty; and
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`, while the only ready task before this ticket is the feature-owned `RBR-0641`.
- JSON burn-down remains complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining duplication is concrete and bounded in the current checkout:
  - `wc -l tests/python/test_rust_compile_match_boundary.py tests/python/test_module_workflow_parity_suite.py` reports `226` lines for the detached boundary file versus `3189` lines for the existing owner;
  - `rg -n 'test_compile_match_and_escape_use_native_boundary_hooks|test_compile_surfaces_native_re_error|test_pattern_placeholder_comes_from_native_boundary|test_collection_and_replacement_helpers_use_native_boundary_hooks|test_module_and_pattern_placeholders_still_surface_for_unsupported_native_results|_FakeNativeBoundary' tests/python/test_rust_compile_match_boundary.py tests/python/test_module_workflow_parity_suite.py` currently matches only the detached file; and
  - `tests/python/test_module_workflow_parity_suite.py` already owns the adjacent compile/search/collection/replacement/escape/public-helper surface, so this boundary slice no longer needs its own standalone owner module.
- 2026-03-18 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py` passes (`471 passed in 0.35s`);
  - the manifest-order probe in Acceptance currently passes (`ok`);
  - `bash -lc "! rg --files tests/python | rg 'test_rust_compile_match_boundary\\.py$'"` currently fails exactly on this cleanup because the detached suite still exists; and
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_rust_compile_match_boundary.py tests/python/test_module_workflow_parity_suite.py` currently fails exactly inside the detached suite on a stale bytes-escape call expectation, while a direct probe from the same checkout shows `rebar.escape(b"a-b")` currently records `[('escape', 'a-b')]` through that file's `_FakeNativeBoundary`. The absorbed owner coverage should keep the live routing honest instead of carrying the stale detached expectation forward.
