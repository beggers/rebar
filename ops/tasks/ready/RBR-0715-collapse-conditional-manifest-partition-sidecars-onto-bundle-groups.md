# RBR-0715: Collapse conditional manifest-partition sidecars onto bundle groups

Status: ready
Owner: architecture-implementation
Created: 2026-03-19

## Goal
- Remove the detached conditional manifest-id partition tables from `tests/python/test_conditional_group_exists_parity_suite.py` so the suite's existing ordered fixture bundles become the sole owner of the base, quantified, and nested-or-alternation case partitions.

## Deliverables
- `tests/python/test_conditional_group_exists_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_conditional_group_exists_parity_suite.py` stops defining these detached manifest-id partition sidecars:
  - delete `BASE_MANIFEST_IDS`;
  - delete `QUANTIFIED_MANIFEST_IDS`;
  - delete `NESTED_ALTERNATION_MANIFEST_IDS`;
  - delete `BASE_MANIFEST_ID_SET`;
  - delete `QUANTIFIED_MANIFEST_ID_SET`;
  - delete `NESTED_ALTERNATION_MANIFEST_ID_SET`; and
  - delete `CORE_CONDITIONAL_MANIFEST_ID_SET`.
- The case partitions derive from canonical grouped bundle ownership instead of manifest-id sidecars:
  - `CORE_CONDITIONAL_COMPILE_CASES`, `NESTED_ALTERNATION_COMPILE_CASES`, `BASE_MODULE_CASES`, `QUANTIFIED_MODULE_CASES`, `NESTED_ALTERNATION_MODULE_CASES`, `BASE_PATTERN_CASES`, `QUANTIFIED_PATTERN_CASES`, and `NESTED_ALTERNATION_PATTERN_CASES` derive from grouped bundle tuples rooted in the existing `FIXTURE_BUNDLES` order rather than from any detached manifest-id tuple or set;
  - if a tiny file-local helper or explicit `BASE_BUNDLES` / `QUANTIFIED_BUNDLES` / `NESTED_ALTERNATION_BUNDLES` owner is useful, keep it bundle-driven instead of introducing another manifest-id registry; and
  - keep `FIXTURE_BUNDLE_SPECS`, `FIXTURE_BUNDLES`, `QUANTIFIED_CONDITIONAL_BUNDLE`, and `QUANTIFIED_CONDITIONAL_ALTERNATION_BUNDLE` as the only fixture-selection owners already present in the file.
- Preserve the current partition ordering and routing exactly:
  - the base bundle group stays exactly `optional-group-conditional-workflows`, `conditional-group-exists-workflows`, `conditional-group-exists-no-else-workflows`, `conditional-group-exists-empty-else-workflows`, `conditional-group-exists-empty-yes-else-workflows`, `conditional-group-exists-fully-empty-workflows`;
  - the quantified bundle group stays exactly `conditional-group-exists-quantified-workflows`, `conditional-group-exists-quantified-alternation-workflows`, `conditional-group-exists-no-else-quantified-workflows`, `conditional-group-exists-empty-else-quantified-workflows`, `conditional-group-exists-empty-yes-else-quantified-workflows`, `conditional-group-exists-fully-empty-quantified-workflows`;
  - the nested-or-alternation bundle group stays exactly `conditional-group-exists-nested-workflows`, `conditional-group-exists-no-else-nested-workflows`, `conditional-group-exists-empty-else-nested-workflows`, `conditional-group-exists-empty-yes-else-nested-workflows`, `conditional-group-exists-fully-empty-nested-workflows`, `conditional-group-exists-alternation-workflows`, `conditional-group-exists-no-else-alternation-workflows`, `conditional-group-exists-empty-else-alternation-workflows`, `conditional-group-exists-empty-yes-else-alternation-workflows`, `conditional-group-exists-fully-empty-alternation-workflows`; and
  - the compile/module/pattern case buckets listed above keep the same effective manifest order as the current `FIXTURE_BUNDLES` slices.
- Keep canonical conditional-suite ownership otherwise unchanged:
  - do not change `FIXTURE_BUNDLE_SPECS`, `MATCH_API_CASES`, `GENERATED_QUANTIFIED_CONDITIONAL_PARITY_SPECS`, the supplemental module/pattern/miss case tables, or the bounded-pattern helpers they feed; and
  - do not broaden into replacement coverage, benchmark plumbing, fixture-module edits, or harness helper changes in this task.
- Keep scope structural only:
  - do not edit `tests/python/fixture_parity_support.py`, correctness fixture modules under `tests/conformance/fixtures/`, `python/rebar_harness/correctness.py`, published reports, or tracked project-state prose.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_conditional_group_exists_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from pathlib import Path

source = Path("tests/python/test_conditional_group_exists_parity_suite.py").read_text(
    encoding="utf-8"
)
for needle in (
    "BASE_MANIFEST_IDS = (",
    "QUANTIFIED_MANIFEST_IDS = (",
    "NESTED_ALTERNATION_MANIFEST_IDS = (",
    "BASE_MANIFEST_ID_SET = ",
    "QUANTIFIED_MANIFEST_ID_SET = ",
    "NESTED_ALTERNATION_MANIFEST_ID_SET = ",
    "CORE_CONDITIONAL_MANIFEST_ID_SET = ",
):
    assert needle not in source, needle
print("ok")
PY`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
import tests.python.test_conditional_group_exists_parity_suite as mod

assert tuple(bundle.expected_manifest_id for bundle in mod.FIXTURE_BUNDLES[:6]) == (
    "optional-group-conditional-workflows",
    "conditional-group-exists-workflows",
    "conditional-group-exists-no-else-workflows",
    "conditional-group-exists-empty-else-workflows",
    "conditional-group-exists-empty-yes-else-workflows",
    "conditional-group-exists-fully-empty-workflows",
)
assert tuple(bundle.expected_manifest_id for bundle in mod.FIXTURE_BUNDLES[6:12]) == (
    "conditional-group-exists-quantified-workflows",
    "conditional-group-exists-quantified-alternation-workflows",
    "conditional-group-exists-no-else-quantified-workflows",
    "conditional-group-exists-empty-else-quantified-workflows",
    "conditional-group-exists-empty-yes-else-quantified-workflows",
    "conditional-group-exists-fully-empty-quantified-workflows",
)
assert tuple(bundle.expected_manifest_id for bundle in mod.FIXTURE_BUNDLES[12:]) == (
    "conditional-group-exists-nested-workflows",
    "conditional-group-exists-no-else-nested-workflows",
    "conditional-group-exists-empty-else-nested-workflows",
    "conditional-group-exists-empty-yes-else-nested-workflows",
    "conditional-group-exists-fully-empty-nested-workflows",
    "conditional-group-exists-alternation-workflows",
    "conditional-group-exists-no-else-alternation-workflows",
    "conditional-group-exists-empty-else-alternation-workflows",
    "conditional-group-exists-empty-yes-else-alternation-workflows",
    "conditional-group-exists-fully-empty-alternation-workflows",
)
assert tuple(case.manifest_id for case in mod.CORE_CONDITIONAL_COMPILE_CASES) == tuple(
    case.manifest_id
    for bundle in mod.FIXTURE_BUNDLES[:12]
    for case in bundle.cases
    if case.operation == "compile"
)
assert tuple(case.manifest_id for case in mod.NESTED_ALTERNATION_COMPILE_CASES) == tuple(
    case.manifest_id
    for bundle in mod.FIXTURE_BUNDLES[12:]
    for case in bundle.cases
    if case.operation == "compile"
)
assert tuple(case.manifest_id for case in mod.BASE_MODULE_CASES) == tuple(
    case.manifest_id
    for bundle in mod.FIXTURE_BUNDLES[:6]
    for case in bundle.cases
    if case.operation == "module_call"
)
assert tuple(case.manifest_id for case in mod.QUANTIFIED_MODULE_CASES) == tuple(
    case.manifest_id
    for bundle in mod.FIXTURE_BUNDLES[6:12]
    for case in bundle.cases
    if case.operation == "module_call"
)
assert tuple(case.manifest_id for case in mod.NESTED_ALTERNATION_MODULE_CASES) == tuple(
    case.manifest_id
    for bundle in mod.FIXTURE_BUNDLES[12:]
    for case in bundle.cases
    if case.operation == "module_call"
)
assert tuple(case.manifest_id for case in mod.BASE_PATTERN_CASES) == tuple(
    case.manifest_id
    for bundle in mod.FIXTURE_BUNDLES[:6]
    for case in bundle.cases
    if case.operation == "pattern_call"
)
assert tuple(case.manifest_id for case in mod.QUANTIFIED_PATTERN_CASES) == tuple(
    case.manifest_id
    for bundle in mod.FIXTURE_BUNDLES[6:12]
    for case in bundle.cases
    if case.operation == "pattern_call"
)
assert tuple(case.manifest_id for case in mod.NESTED_ALTERNATION_PATTERN_CASES) == tuple(
    case.manifest_id
    for bundle in mod.FIXTURE_BUNDLES[12:]
    for case in bundle.cases
    if case.operation == "pattern_call"
)
print("ok")
PY`
  - `bash -lc "! rg -n 'BASE_MANIFEST_IDS|QUANTIFIED_MANIFEST_IDS|NESTED_ALTERNATION_MANIFEST_IDS|BASE_MANIFEST_ID_SET|QUANTIFIED_MANIFEST_ID_SET|NESTED_ALTERNATION_MANIFEST_ID_SET|CORE_CONDITIONAL_MANIFEST_ID_SET' tests/python/test_conditional_group_exists_parity_suite.py"`

## Constraints
- Keep this cleanup structural only. The point is to delete one more parallel manifest-partition owner layer inside the conditional parity suite, not to reinterpret which fixtures belong to each frontier slice, alter generated-quantified behavior, or widen the suite beyond the current published slice.
- Prefer deriving the compile/module/pattern partitions from the already ordered bundle list over another detached tuple/list/map block or another helper registry.

## Notes
- `RBR-0715` is the next available architecture-task id in the current checkout:
  - `python3 - <<'PY'
import pathlib, re
existing = set()
for base in ['ops/tasks/ready', 'ops/tasks/in_progress', 'ops/tasks/done', 'ops/tasks/blocked']:
    for path in pathlib.Path(base).glob('RBR-*.md'):
        m = re.match(r'(RBR-\\d+[A-Z]?)', path.name)
        if m:
            existing.add(m.group(1))
text = '\\n'.join(
    pathlib.Path(p).read_text(encoding='utf-8')
    for p in ['ops/state/backlog.md', 'ops/state/current_status.md']
)
mentioned = set(re.findall(r'RBR-\\d+[A-Z]?', text))
reserved = sorted(mentioned - existing, key=lambda s: (int(re.search(r'\\d+', s).group()), s))
existing_sorted = sorted(existing, key=lambda s: (int(re.search(r'\\d+', s).group()), s))
print('highest_existing_tail:', existing_sorted[-10:])
print('reserved_missing_tail:', reserved[-10:])
PY` reported the highest existing tail as `RBR-0705` through `RBR-0714` and no reserved missing tail ids.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views, so this run can spend its slot on post-JSON structural cleanup:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The conditional manifest-partition sidecars are concrete and bounded in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_conditional_group_exists_parity_suite.py` currently passes (`530 passed in 0.46s`);
  - `rg -n 'BASE_MANIFEST_IDS|QUANTIFIED_MANIFEST_IDS|NESTED_ALTERNATION_MANIFEST_IDS|BASE_MANIFEST_ID_SET|QUANTIFIED_MANIFEST_ID_SET|NESTED_ALTERNATION_MANIFEST_ID_SET|CORE_CONDITIONAL_MANIFEST_ID_SET' tests/python/test_conditional_group_exists_parity_suite.py` shows the detached partition constants live only in this file's current case-bucketing block;
  - the inline source-absence probe in Acceptance currently fails exactly on this cleanup with `AssertionError: BASE_MANIFEST_IDS = (`;
  - the final `rg` absence check in Acceptance currently fails exactly on this cleanup because all seven constants still exist; and
  - the import probe in Acceptance already passes in the current checkout, so it pins the preserved bundle ordering and case routing independently of the structural cleanup.
- This simplification matches the current conditional-suite information flow:
  - `FIXTURE_BUNDLE_SPECS` and `FIXTURE_BUNDLES` already keep the canonical base-then-quantified-then-nested/alternation ordering for the full conditional frontier; and
  - the manifest-id sidecars only duplicate that ownership so the compile/module/pattern case buckets can be repartitioned, which makes them a bounded target for deletion without changing the published parity surface.
