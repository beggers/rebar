# RBR-1006: Publish the raw `re.sub()` / `re.subn()` bytes no-match/repeated pair

Status: ready
Owner: feature-implementation
Created: 2026-03-23

## Goal
- Reopen the shared `collection-replacement-workflows` correctness frontier with the adjacent raw-module bytes `re.sub()` / `re.subn()` literal no-match/repeated pair that the current runtime already matches in direct parity tests, publishing the exact CPython-visible bytes module-helper outcomes before a later Python-path benchmark catch-up widens the same `collection_replacement_boundary.py` owner route.

## Pattern Pair
- `re.sub(b"abc", b"x", b"zzz")`
- `re.subn(b"abc", b"x", b"abcabc")`

## Deliverables
- `tests/conformance/fixtures/collection_replacement_workflows.py`
- `tests/python/test_fixture_backed_replacement_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/collection_replacement_workflows.py` remains the only correctness manifest for this slice and grows by exactly two new raw-module `module_call` rows:
  - add `module-sub-bytes-no-match`; and
  - add `module-subn-bytes-repeated`.
- Keep those two rows pinned to the exact module-helper workflows above rather than widening the collection frontier:
  - `module-sub-bytes-no-match` uses `helper == "sub"`, `text_model == "bytes"`, `args == [{"type": "bytes", "encoding": "latin-1", "value": "abc"}, {"type": "bytes", "encoding": "latin-1", "value": "x"}, {"type": "bytes", "encoding": "latin-1", "value": "zzz"}]`, and categories `["workflow", "sub", "literal", "bytes", "no-match"]`;
  - `module-subn-bytes-repeated` uses `helper == "subn"`, `text_model == "bytes"`, `args == [{"type": "bytes", "encoding": "latin-1", "value": "abc"}, {"type": "bytes", "encoding": "latin-1", "value": "x"}, {"type": "bytes", "encoding": "latin-1", "value": "abcabc"}]`, and categories `["workflow", "subn", "literal", "bytes", "repeated"]`;
  - insert `module-sub-bytes-no-match` immediately after `module-sub-str-repeated`;
  - insert `module-subn-bytes-repeated` immediately after `module-subn-bytes-count`; and
  - keep the raw-module literal replacement block ordered as `module-sub-str-repeated`, `module-sub-bytes-no-match`, `module-subn-bytes-count`, and `module-subn-bytes-repeated` immediately before the direct compiled-pattern replacement block, without widening into str module-helper follow-ons, grouped-template rows, callable replacement rows, another correctness manifest, or benchmark updates in this run.
- `tests/python/test_fixture_backed_replacement_parity_suite.py` keeps this work on the existing shared collection/replacement owner path instead of creating another manifest, another parity suite, or a detached raw-module replacement publication table:
  - add `PUBLISHED_DIRECT_LITERAL_MODULE_REPLACEMENT_CASE_IDS`, or a strictly equivalent existing owner-path selector, so the shared `collection-replacement-workflows` route now resolves the published raw-module literal replacement rows in order as `module-sub-str-repeated`, `module-sub-bytes-no-match`, `module-subn-bytes-count`, and `module-subn-bytes-repeated`;
  - add a focused published raw-module literal-replacement assertion path, or tighten an equivalent existing owner-path assertion, so the selected rows above are checked for order, helper, args, and text-model alignment on the same file;
  - keep the direct source-package module literal replacement parity coverage on the same file rather than introducing another replacement-only test module; and
  - keep the direct compiled-pattern replacement publication path, grouped-template rows, callable rows, and mixed-text-model replacement ownership checks honest while widening only this raw-module bytes pair.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined tracked summary moves from `1569` total / `1569` passed / `0` failed / `0` unimplemented across `114` manifests to `1571` / `1571` / `0` / `0` across the same `114` manifests;
  - `collection.replacement.workflow` moves from `32` total / `32` passed to `34` / `34`;
  - `collection.replacement.workflow.bytes` moves from `11` total / `11` passed to `13` / `13`;
  - `collection.replacement.workflow.str` stays `21` total / `21` passed;
  - `collection.replacement.workflow.module_call` moves from `12` total / `12` passed to `14` / `14`; and
  - `collection.replacement.workflow.pattern_call` stays `20` total / `20` passed.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_match_cpython and (bytes-no-match or bytes-repeated-match)'`
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/collection_replacement_workflows.py --report .rebar/tmp/rbr-1006-module-replacement-bytes-no-match-repeated-pair.py`
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or benchmark-side selector logic in this run.
- Reuse the existing `collection_replacement_workflows.py` manifest and `tests/python/test_fixture_backed_replacement_parity_suite.py` owner route. Do not create another correctness manifest, another parity suite, or a detached raw-module replacement publication file.
- Keep the scope pinned to the two raw-module bytes replacement rows above. Leave the matching Python-path benchmark catch-up on `benchmarks/workloads/collection_replacement_boundary.py`, str module-helper follow-ons, grouped-template rows, callable replacement rows, and deeper direct replacement expansion for later tasks.

## Notes
- `RBR-1006` is the next available feature task id in the current checkout:
  - `RBR-1004` is the latest done feature task on the drained direct compiled-pattern bytes replacement benchmark frontier;
  - `RBR-1005` is already occupied by an architecture cleanup task in `ops/tasks/done/`; and
  - no blocked feature task exists to reopen first because `ops/tasks/blocked/` is empty in this checkout.
- Queue this directly after the drained direct compiled-pattern bytes replacement benchmark catch-up because the next concrete unpublished owner-path gap on the same shared collection/replacement lane is the adjacent raw-module bytes no-match/repeated pair rather than str module-helper follow-ons, grouped-template rows, callable replacement rows, or another benchmark-only expansion.
- 2026-03-23 feature-planning probes confirm this follow-on is concrete from the landed runtime frontier and does not need another implementation prerequisite first:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'test_source_package_module_literal_replacement_helpers_match_cpython and (bytes-no-match or bytes-repeated-match)'` currently passes (`2 passed`), so the exact raw-module bytes parity slice is already green in this checkout;
  - `rg -n 'module-sub-bytes-no-match|module-subn-bytes-repeated|module-sub-bytes-no-match-purged-bytes|module-subn-bytes-repeated-purged-bytes' tests/conformance/fixtures/collection_replacement_workflows.py tests/python/test_fixture_backed_replacement_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py benchmarks/workloads/collection_replacement_boundary.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py reports/correctness/latest.py reports/benchmarks/latest.py` currently returns no matches, confirming the exact correctness and benchmark ids are still absent from the tracked owner-path surfaces; and
  - synthetic benchmark probes built through `rebar_harness.benchmarks.Workload.from_dict(...)`, `workload_to_payload(...)`, and `run_internal_workload_probe(...)` return `status == "measured"` for both adapters on both hypothetical workloads `module-sub-bytes-no-match-purged-bytes` and `module-subn-bytes-repeated-purged-bytes`, so the later benchmark catch-up can stay on the existing Python-path owner route instead of needing another implementation prerequisite first.
