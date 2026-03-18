# RBR-0632: Retire the module surface scaffold onto owner suites

Status: done
Owner: architecture-implementation
Created: 2026-03-18
Completed: 2026-03-18

## Goal
- Delete `tests/python/test_module_surface_scaffold.py` by moving its remaining source-package coverage onto the existing owner suites, so the Python-facing surface stops keeping one legacy catch-all scaffold module beside the fixture-backed public-surface, module-workflow, replacement, and native-smoke owners.

## Deliverables
- `tests/python/test_public_surface_parity_suite.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`
- `tests/python/test_native_extension_smoke.py`
- Delete `tests/python/test_module_surface_scaffold.py`

## Acceptance Criteria
- `tests/python/test_module_surface_scaffold.py` is deleted outright:
  - do not leave an import-only wrapper, compatibility shell, or new `tests/python/*scaffold*_support.py` helper behind; and
  - keep the end state on the existing owner suites rather than replacing one catch-all file with another indirection layer.
- `tests/python/test_public_surface_parity_suite.py` becomes the sole owner for the public/export contract assertions still duplicated in the scaffold file:
  - absorb the existing `__all__` subset check, primary flag value and alias checks, `RegexFlag` iteration parity, exported `Pattern` / `Match` / `error` metadata checks, non-instantiable constructor guards for `Pattern()` and `Match()`, and the loud `rebar.template("abc")` placeholder check;
  - keep these as direct local tests in the same suite instead of adding new fixture manifests or another helper module; and
  - keep the current fixture-backed surface unchanged by leaving `FIXTURE_BUNDLE_SPECS` ordered as `("public-api-surface", "exported-symbol-surface", "pattern-object-surface")`.
- `tests/python/test_module_workflow_parity_suite.py` becomes the owner for the compile/match/cache/purge/escape and match-object edge cases still living only in the scaffold file:
  - absorb the direct compile metadata checks for `"abc"`, `b"abc"`, `"^abc$"`, and the verbose regression pattern, including the current zero-flag compiled-pattern identity path, the nonzero compiled-pattern flag error, and the `compile(123)` `TypeError`;
  - absorb the bounded literal module/pattern `search()` / `match()` / `fullmatch()` hit and miss checks, the missing-group `IndexError` checks for `group` / `span` / `start` / `end`, and the string-vs-bytes mismatch `TypeError` checks;
  - absorb the current loud unsupported compile/match surface for flagged module search, nonliteral module search, and flagged bound `Pattern.search()` / `match()` / `fullmatch()` placeholder messages;
  - absorb the cache reuse, purge, unsupported-compile-no-cache-mutation, normalized-flag cache-identity, and explicit `escape()` parity table checks without introducing a new owner file; and
  - keep the fixture-backed module-workflow surface unchanged by leaving `SELECTED_CASE_BUNDLE_SPECS` ordered as `("module-workflow-surface", "match-behavior-smoke")`.
- `tests/python/test_fixture_backed_replacement_parity_suite.py` becomes the owner for the replacement-specific direct cases still trapped in the scaffold file:
  - absorb the current literal module/pattern `sub()` / `subn()` parity cases, the whole-match `\\g<0>x` module/pattern replacement cases, and the existing replacement string-vs-bytes mismatch `TypeError` checks;
  - absorb the current loud unsupported replacement cases for module template replacement, module `flags=...`, nonliteral and empty-pattern module replacement, flagged compiled-pattern replacement, empty compiled-pattern replacement, and compiled template replacement, keeping the current cache-empty assertions explicit where they already exist today; and
  - keep the fixture-backed replacement harness on the same three local owner surfaces by leaving `tuple(surface.spec.id for surface in REPLACEMENT_SURFACES)` equal to `("grouped-replacement-template", "open-ended-quantified-group-replacement", "conditional-group-exists-replacement")`.
- `tests/python/test_native_extension_smoke.py` gains the rebar-only source-tree shim metadata checks that do not belong on the stdlib parity path:
  - add a non-`maturin`-gated test that covers `TARGET_CPYTHON_SERIES == "3.12.x"`, `SCAFFOLD_STATUS == "scaffold-only"`, `NATIVE_MODULE_NAME == "rebar._rebar"`, `native_module_loaded()`, and the current `native_scaffold_status()` / `native_target_cpython_series()` behavior; and
  - keep the existing built-wheel smoke test intact rather than folding it into another file.
- Keep scope structural only:
  - do not change `python/rebar/`, Rust code, correctness fixtures, benchmark manifests, reports, README/state files, or `tests/python/conftest.py`; and
  - do not broaden this cleanup into `tests/python/test_literal_collection_helpers.py`, `tests/python/test_grouped_capture_parity_suite.py`, or another new support module.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_public_surface_parity_suite.py tests/python/test_module_workflow_parity_suite.py tests/python/test_fixture_backed_replacement_parity_suite.py tests/python/test_native_extension_smoke.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from tests.python import test_public_surface_parity_suite as public_mod
from tests.python import test_module_workflow_parity_suite as workflow_mod
from tests.python import test_fixture_backed_replacement_parity_suite as replacement_mod

assert tuple(spec.expected_manifest_id for spec in public_mod.FIXTURE_BUNDLE_SPECS) == (
    "public-api-surface",
    "exported-symbol-surface",
    "pattern-object-surface",
)
assert tuple(spec.expected_manifest_id for spec in workflow_mod.SELECTED_CASE_BUNDLE_SPECS) == (
    "module-workflow-surface",
    "match-behavior-smoke",
)
assert tuple(surface.spec.id for surface in replacement_mod.REPLACEMENT_SURFACES) == (
    "grouped-replacement-template",
    "open-ended-quantified-group-replacement",
    "conditional-group-exists-replacement",
)
print("ok")
PY`
  - `rg -n "TARGET_CPYTHON_SERIES|SCAFFOLD_STATUS|NATIVE_MODULE_NAME" tests/python/test_native_extension_smoke.py`
  - `bash -lc "! rg --files tests/python | rg 'test_module_surface_scaffold\\.py$'"`

## Constraints
- Keep this cleanup structural. The point is to move already-covered behavior onto the natural owners, not to reinterpret parity semantics, change placeholder messages, or widen fixture publication.
- Prefer direct local tests inside the existing owner suites over another helper registry or compatibility layer.
- If tiny local helpers improve readability, keep them inside the touched owner suite instead of creating a new cross-suite module.

## Notes
- `RBR-0632` is the next available task id:
  - `ops/state/backlog.md`, `ops/state/current_status.md`, `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contain no reserved or active `RBR-0632` entry in the current checkout.
- Rule 10 does not apply in the current runtime state:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the latest cycle finished both task workers cleanly, so the queue is not stalled on inherited-dirty or post-commit refresh churn.
- JSON burn-down remains complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining duplication is concrete in the current checkout:
  - `tests/python/test_module_surface_scaffold.py` is still `657` lines of mixed public-surface, module-workflow, replacement, and shim-metadata assertions;
  - the current owner suites already exist and already pass together with the scaffold file present: `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_surface_scaffold.py tests/python/test_public_surface_parity_suite.py tests/python/test_module_workflow_parity_suite.py tests/python/test_fixture_backed_replacement_parity_suite.py tests/python/test_literal_collection_helpers.py tests/python/test_native_extension_smoke.py` passed in the live checkout (`1466 passed, 1 skipped`);
  - `tests/python/test_native_extension_smoke.py` currently has no direct source-tree metadata assertion for `TARGET_CPYTHON_SERIES`, `SCAFFOLD_STATUS`, or `NATIVE_MODULE_NAME`, so that rebar-only contract still needs a new non-`maturin`-gated owner there; and
  - the current failing structural probes belong exactly to this cleanup:
    - `rg -n "TARGET_CPYTHON_SERIES|SCAFFOLD_STATUS|NATIVE_MODULE_NAME" tests/python/test_native_extension_smoke.py` currently exits nonzero because those assertions are still only in `tests/python/test_module_surface_scaffold.py`; and
    - `bash -lc "! rg --files tests/python | rg 'test_module_surface_scaffold\\.py$'"` currently fails because the legacy scaffold file still exists.

## Completion Note
- 2026-03-18: Moved the scaffold-owned direct source-package assertions into `tests/python/test_public_surface_parity_suite.py`, `tests/python/test_module_workflow_parity_suite.py`, `tests/python/test_fixture_backed_replacement_parity_suite.py`, and `tests/python/test_native_extension_smoke.py`, then deleted `tests/python/test_module_surface_scaffold.py`. Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_public_surface_parity_suite.py tests/python/test_module_workflow_parity_suite.py tests/python/test_fixture_backed_replacement_parity_suite.py tests/python/test_native_extension_smoke.py` (`1391 passed, 1 skipped in 1.03s`), the inline fixture-order probe (`ok`), `rg -n "TARGET_CPYTHON_SERIES|SCAFFOLD_STATUS|NATIVE_MODULE_NAME" tests/python/test_native_extension_smoke.py` (three source-tree metadata assertions present), `bash -lc "! rg --files tests/python | rg 'test_module_surface_scaffold\\.py$'"` (no matches), and `git diff --name-status -- tests/python/test_module_surface_scaffold.py` (`D`).
