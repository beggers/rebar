# RBR-0772: Collapse literal-flag bundle-spec sidecar onto full-manifest owner

Status: done
Owner: architecture-implementation
Created: 2026-03-20
Completed: 2026-03-20

## Goal
- Remove the remaining full-manifest sidecar from `tests/python/test_literal_flag_parity_suite.py`; `TARGET_FIXTURE_CASE_IDS` and `SELECTED_CASE_BUNDLE_SPECS = (FixtureBundleSpec(...))` currently mirror the exact 13-row manifest order from `tests/conformance/fixtures/literal_flag_workflows.py` even though the suite already owns that full published manifest after `RBR-0640`.
- Make the published `literal_flag_workflows.py` owner manifest the single source of truth for the literal-flag parity suite's bundle contract and published frontier case ids.

## Deliverables
- `tests/python/test_literal_flag_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_literal_flag_parity_suite.py` stops defining or reading the detached full-manifest sidecar symbols:
  - `TARGET_FIXTURE_CASE_IDS`
  - `SELECTED_CASE_BUNDLE_SPECS`
  - the `FixtureBundleSpec(...)` / `load_fixture_bundles(...)` call
  - if they become unused after the cleanup, remove the `FixtureBundleSpec` and `load_fixture_bundles` imports from this file as well.
- `LITERAL_FLAG_FIXTURE_BUNDLE` loads `literal_flag_workflows.py` through the canonical full-manifest path instead of the selected-id sidecar:
  - define it through `load_published_fixture_bundles((CORRECTNESS_FIXTURES_ROOT / "literal_flag_workflows.py",))` or one equally direct file-local wrapper over that returned full bundle;
  - preserve manifest path `literal_flag_workflows.py` and manifest id `literal-flag-workflows`;
  - preserve case order exactly as the published manifest order.
- Derive the suite's published frontier directly from the loaded owner rows rather than from a handwritten case-id tuple:
  - `test_literal_flag_parity_suite_tracks_published_case_frontier()` uses the owner-bundle case ids or a tiny file-local helper over `LITERAL_FLAG_FIXTURE_BUNDLE.cases`;
  - `test_literal_flag_direct_test_buckets_cover_selected_frontier()` uses the same owner-derived case-id frontier;
  - preserve the exact owner-manifest order:
    - `flag-module-search-ignorecase-str-hit`
    - `flag-module-search-ignorecase-str-miss`
    - `flag-module-search-ignorecase-ascii-str-hit`
    - `flag-module-fullmatch-ignorecase-bytes-hit`
    - `flag-pattern-search-ignorecase-str-hit`
    - `flag-pattern-search-ignorecase-ascii-str-hit`
    - `flag-pattern-match-ignorecase-bytes-hit`
    - `flag-pattern-fullmatch-ignorecase-str-miss`
    - `flag-cache-hit-bytes-ignorecase`
    - `flag-cache-distinct-str-normalized`
    - `flag-unsupported-inline-flag-search`
    - `flag-unsupported-locale-bytes-search`
    - `flag-unsupported-nonliteral-ignorecase-search`
- Preserve the current full-manifest bundle contract after the cleanup, but derive it from loaded rows instead of mirrored sidecars:
  - `tuple(case.case_id for case in LITERAL_FLAG_FIXTURE_BUNDLE.cases)` stays equal to `tuple(case.case_id for case in LITERAL_FLAG_FIXTURE_BUNDLE.manifest.cases)`;
  - `expected_patterns` stays `frozenset(case_pattern(case) for case in LITERAL_FLAG_FIXTURE_BUNDLE.cases)`;
  - `expected_operation_helper_counts` stays `Counter((case.operation, case.helper) for case in LITERAL_FLAG_FIXTURE_BUNDLE.cases)`;
  - `expected_text_models` becomes `frozenset({"str", "bytes"})` through the owner-bundle load instead of being left unset.
- Keep the current literal-flag behavior coverage unchanged:
  - do not change `MODULE_IGNORECASE_CASES`, `PATTERN_IGNORECASE_CASES`, `NATIVE_MODULE_PARITY_CASES`, `NATIVE_PATTERN_PARITY_CASES`, `FAKE_BOUNDARY_CASES`, cache observations, placeholder coverage, or helper-call expectations outside this sidecar cleanup;
  - do not edit `tests/conformance/fixtures/literal_flag_workflows.py`, `tests/python/fixture_parity_support.py`, benchmark files, reports, README copy, or tracked project-state prose.
- Keep scope structural only:
  - prefer deleting the redundant tuple/spec layer over adding another shared abstraction or another registry;
  - if a helper is useful, keep it file-local to `tests/python/test_literal_flag_parity_suite.py`.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_literal_flag_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from collections import Counter
import tests.python.test_literal_flag_parity_suite as mod

assert mod.LITERAL_FLAG_FIXTURE_BUNDLE.manifest.path.name == "literal_flag_workflows.py"
assert mod.LITERAL_FLAG_FIXTURE_BUNDLE.manifest.manifest_id == "literal-flag-workflows"
assert tuple(case.case_id for case in mod.LITERAL_FLAG_FIXTURE_BUNDLE.cases) == (
    "flag-module-search-ignorecase-str-hit",
    "flag-module-search-ignorecase-str-miss",
    "flag-module-search-ignorecase-ascii-str-hit",
    "flag-module-fullmatch-ignorecase-bytes-hit",
    "flag-pattern-search-ignorecase-str-hit",
    "flag-pattern-search-ignorecase-ascii-str-hit",
    "flag-pattern-match-ignorecase-bytes-hit",
    "flag-pattern-fullmatch-ignorecase-str-miss",
    "flag-cache-hit-bytes-ignorecase",
    "flag-cache-distinct-str-normalized",
    "flag-unsupported-inline-flag-search",
    "flag-unsupported-locale-bytes-search",
    "flag-unsupported-nonliteral-ignorecase-search",
)
assert tuple(case.case_id for case in mod.LITERAL_FLAG_FIXTURE_BUNDLE.cases) == tuple(
    case.case_id for case in mod.LITERAL_FLAG_FIXTURE_BUNDLE.manifest.cases
)
assert mod.LITERAL_FLAG_FIXTURE_BUNDLE.expected_patterns == frozenset(
    mod.case_pattern(case) for case in mod.LITERAL_FLAG_FIXTURE_BUNDLE.cases
)
assert mod.LITERAL_FLAG_FIXTURE_BUNDLE.expected_operation_helper_counts == Counter(
    (case.operation, case.helper) for case in mod.LITERAL_FLAG_FIXTURE_BUNDLE.cases
)
assert mod.LITERAL_FLAG_FIXTURE_BUNDLE.expected_text_models == frozenset({"str", "bytes"})
print("ok")
PY`
  - `bash -lc "! rg -n '^(TARGET_FIXTURE_CASE_IDS|SELECTED_CASE_BUNDLE_SPECS) =|FixtureBundleSpec\\(|load_fixture_bundles\\(' tests/python/test_literal_flag_parity_suite.py"`

## Constraints
- Keep this cleanup limited to `tests/python/test_literal_flag_parity_suite.py`.
- Do not turn this into another literal-flag behavior expansion, a fixture-support rewrite, or a multi-suite parity refactor.

## Completion
- Replaced the literal-flag suite's detached `FixtureBundleSpec` / `load_fixture_bundles(...)` sidecar with the canonical full-manifest owner load via `load_published_fixture_bundles((CORRECTNESS_FIXTURES_ROOT / "literal_flag_workflows.py",))`.
- Switched the published-frontier assertions and direct-test bucket coverage check to a file-local owner-derived case-id helper built from `LITERAL_FLAG_FIXTURE_BUNDLE.cases`, while keeping the existing behavior buckets untouched.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_literal_flag_parity_suite.py` (`36 passed in 0.08s`), the acceptance owner-bundle probe (`ok`), and the grep absence check for `TARGET_FIXTURE_CASE_IDS`, `SELECTED_CASE_BUNDLE_SPECS`, `FixtureBundleSpec(`, and `load_fixture_bundles(`.

## Notes
- `RBR-0772` is the next available task id in the current checkout:
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
print('reserved_tail', reserved_sorted[-20:])
for n in range(int(re.search(r'\d+', existing_sorted[-1]).group()), int(re.search(r'\d+', existing_sorted[-1]).group()) + 200):
    rid = f'RBR-{n:04d}'
    if rid not in existing and rid not in reserved:
        print('next_free', rid)
        break
PY` reported the existing tail through `RBR-0771`, no reserved missing tail ids, and `next_free RBR-0772`.
- No blocked architecture task exists to reopen first, and rule 10 does not block another architecture cleanup:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`;
  - `ops/tasks/blocked/`, `ops/tasks/ready/`, and `ops/tasks/in_progress/` are empty in the current checkout; and
  - the last cycle completed both `RBR-0770` and `RBR-0771` cleanly, so there is no inherited-dirty or post-task refresh bottleneck to yield to.
- JSON burn-down remains complete and current in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- This cleanup is concrete and currently viable in the live checkout:
  - `tests/conformance/fixtures/literal_flag_workflows.py` currently publishes 13 rows, and `TARGET_FIXTURE_CASE_IDS` matches that exact manifest-order case-id sequence one-for-one;
  - `tests/python/test_literal_flag_parity_suite.py` is the literal-flag owner file that still carries this detached full-manifest sidecar;
  - the canonical full-manifest loader path is already viable for this owner:
    - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from collections import Counter
from rebar_harness.correctness import CORRECTNESS_FIXTURES_ROOT
from tests.python.fixture_parity_support import case_pattern, load_published_fixture_bundles

(bundle,) = load_published_fixture_bundles(
    (CORRECTNESS_FIXTURES_ROOT / 'literal_flag_workflows.py',)
)
assert bundle.manifest.path == CORRECTNESS_FIXTURES_ROOT / 'literal_flag_workflows.py'
assert bundle.manifest.manifest_id == 'literal-flag-workflows'
assert tuple(case.case_id for case in bundle.cases) == tuple(
    case.case_id for case in bundle.manifest.cases
)
assert bundle.expected_patterns == frozenset(case_pattern(case) for case in bundle.cases)
assert bundle.expected_operation_helper_counts == Counter(
    (case.operation, case.helper) for case in bundle.cases
)
assert bundle.expected_text_models == frozenset({'str', 'bytes'})
print('ok')
PY` passed (`ok`);
  - the current sidecar tuple is redundant in the live checkout:
    - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
from rebar_harness.correctness import CORRECTNESS_FIXTURES_ROOT, load_fixture_manifest
import tests.python.test_literal_flag_parity_suite as mod

manifest = load_fixture_manifest(CORRECTNESS_FIXTURES_ROOT / 'literal_flag_workflows.py')
assert tuple(case.case_id for case in manifest.cases) == mod.TARGET_FIXTURE_CASE_IDS
print('ok')
PY` passed (`ok`);
  - baseline verification is green:
    - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_literal_flag_parity_suite.py` passed (`36 passed in 0.07s`);
  - the future-state owner-bundle probe in Acceptance currently fails on this cleanup boundary because `LITERAL_FLAG_FIXTURE_BUNDLE.expected_text_models` is not yet derived from the full-manifest owner path; and
  - `bash -lc "! rg -n '^(TARGET_FIXTURE_CASE_IDS|SELECTED_CASE_BUNDLE_SPECS) =|FixtureBundleSpec\\(|load_fixture_bundles\\(' tests/python/test_literal_flag_parity_suite.py"` currently fails exactly on this cleanup boundary because the detached tuple/spec layer is still present.
