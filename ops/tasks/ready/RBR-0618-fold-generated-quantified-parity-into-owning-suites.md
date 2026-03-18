# RBR-0618: Fold the detached generated quantified parity suite into its owning suites

Status: ready
Owner: architecture-implementation
Created: 2026-03-18

## Goal
- Delete `tests/python/test_generated_quantified_parity_suite.py` by moving its generated text-matrix parity checks into the three parity suites that already own those six manifests, so generated quantified coverage no longer lives on a detached suite parallel to the manifest-owning suites.

## Deliverables
- `tests/python/test_quantified_alternation_parity_suite.py`
- `tests/python/test_conditional_group_exists_parity_suite.py`
- `tests/python/test_branch_local_backreference_parity_suite.py`
- Delete `tests/python/test_generated_quantified_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_quantified_alternation_parity_suite.py` absorbs the current generated text-matrix parity coverage for exactly these three manifests, and no others:
  - `quantified-alternation-workflows`
  - `quantified-alternation-broader-range-workflows`
  - `quantified-alternation-backtracking-heavy-workflows`
- `tests/python/test_branch_local_backreference_parity_suite.py` absorbs the current generated text-matrix parity coverage for exactly:
  - `quantified-nested-group-alternation-branch-local-backreference-workflows`
- `tests/python/test_conditional_group_exists_parity_suite.py` absorbs the current generated text-matrix parity coverage for exactly these two manifests, and no others:
  - `conditional-group-exists-quantified-workflows`
  - `conditional-group-exists-quantified-alternation-workflows`
- The owner-suite consolidation preserves the existing generated candidate frontier exactly:
  - keep `HELPERS == ("search", "match", "fullmatch")`;
  - keep `WRAPPER_PAIRS == (("", ""), ("zz", ""), ("", "zz"), ("zz", "zz"))`;
  - keep `BODY_ATOMS == ("b", "c", "e")` with the current quantified-alternation candidate depths: `range(4)` for bounded `{1,2}` and `range(5)` for broader-range `{1,3}`, backtracking-heavy `{1,2}`, and quantified nested-group alternation branch-local-backreference;
  - keep the current quantified-conditional candidate matrices built from the same present/absent capture choice and the same branch-product choices `("d", "e")` and `("de", "df", "eg", "eh")`;
  - keep the current expected candidate counts: `160`, `484`, `484`, `484`, `32`, and `128` for the six manifests above, in that order;
  - keep the current bytes-versus-str handling: the three quantified-alternation manifests plus the quantified nested-group alternation branch-local-backreference manifest keep mixed text-model candidate matrices, while the two quantified conditional manifests stay str-only; and
  - keep the current failure-preview truncation at twenty entries.
- The owner-suite consolidation preserves the generated parity assertions exactly:
  - keep the compile path through `compile_with_cpython_parity(...)`;
  - keep module and pattern helper loops over all generated candidate texts;
  - keep `assert_match_result_parity(...)` with `check_regs=True`;
  - keep the current convenience-API plus valid/invalid group-access parity checks only when CPython produces a match; and
  - keep the current failure prefixes for the six generated slices rather than rewriting or coalescing them into a new generic message surface.
- The generated coverage stays on the existing fixture-backed owner paths rather than another detached layer:
  - use the existing owner-suite fixture bundles / manifest ids already declared in those files;
  - do not add a new helper module, registry, or code-generation step to move the detached suite elsewhere; and
  - do not leave an import-only wrapper or compatibility shell at `tests/python/test_generated_quantified_parity_suite.py`.
- Keep scope structural only:
  - do not change correctness fixtures, `tests/python/fixture_parity_support.py`, benchmarks, reports, Rust code, or `python/rebar/`; and
  - do not broaden the generated frontier beyond the six manifests listed above.
- After the consolidation lands:
  - `bash -lc "! rg --files tests/python | rg 'test_generated_quantified_parity_suite\\.py$'"`
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py tests/python/test_conditional_group_exists_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py`
  - `bash -lc "! rg --files tests/python | rg 'test_generated_quantified_parity_suite\\.py$'"`

## Constraints
- Keep this cleanup structural only. Do not change backend behavior, fixture membership, manifest ids, selected compile-case anchors, candidate-text builders, helper routing, or the generated failure surface.
- Prefer local tables/helpers inside the three owner suites over a new cross-suite support module. The point is to remove the extra suite layer, not to hide it behind another layer.
- Keep the quantified conditional generated checks str-only; do not widen them into bytes follow-ons during this cleanup.

## Notes
- `RBR-0618` is the next available task id:
  - before this file was added, `ops/state/backlog.md` and `ops/state/current_status.md` did not reserve `RBR-0618` or a later concrete architecture follow-on; and
  - before this file was added, `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` did not already contain `RBR-0618`.
- No stale blocked architecture task needed normalization first, and rule 10 did not apply in the pre-edit checkout:
  - `ops/tasks/blocked/` was empty;
  - the dashboard snapshot in `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`;
  - `.rebar/runtime/dashboard.md` reports `HEAD: 2fb7cb3bcfbb27e2fa8e41ff3d09d88e487af789`, which matches the live clean checkout for this run; and
  - the latest runtime cycle finished both task workers at `done`, so the shared ready queue is not currently bottlenecked by inherited-dirty or post-commit refresh churn.
- JSON burn-down remains complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining duplication is concrete and bounded in the current checkout:
  - `tests/python/test_generated_quantified_parity_suite.py` is `367` lines;
  - `RBR-0594` already collapsed the earlier generated singleton modules into this one detached suite, so the remaining extra layer is now the standalone suite itself rather than per-family copies;
  - the detached suite repeats the same `FixtureBundleSpec` loading path, manifest-id keyed spec lookup, generated candidate builders, `_record_match_failure(...)` helper, compile-through-`compile_with_cpython_parity(...)` flow, helper loop, and twenty-entry failure preview while the owner suites already load the same manifests; and
  - those manifest owners are already explicit in the current checkout:
    - `tests/python/test_quantified_alternation_parity_suite.py` already covers `quantified-alternation-workflows`, `quantified-alternation-broader-range-workflows`, and `quantified-alternation-backtracking-heavy-workflows`;
    - `tests/python/test_conditional_group_exists_parity_suite.py` already covers `conditional-group-exists-quantified-workflows` and `conditional-group-exists-quantified-alternation-workflows`; and
    - `tests/python/test_branch_local_backreference_parity_suite.py` already covers `quantified-nested-group-alternation-branch-local-backreference-workflows`.
- 2026-03-18 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_generated_quantified_parity_suite.py` passes (`46 passed in 0.81s`);
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_quantified_alternation_parity_suite.py tests/python/test_conditional_group_exists_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py` passes (`1552 passed in 1.88s`); and
  - `bash -lc "! rg --files tests/python | rg 'test_generated_quantified_parity_suite\\.py$'"` currently fails exactly on this cleanup because the detached suite still exists.
