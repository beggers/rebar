# RBR-0488: Collapse benchmark manifest documents onto typed records

Status: ready
Owner: architecture-implementation
Created: 2026-03-16

## Goal
- Replace the remaining raw dict-shaped benchmark manifest documents with an explicit typed record so the benchmark harness, source-tree expectation builders, and benchmark report assertions stop threading manifest-level metadata through `dict[str, Any]` while preserving workload rows and published scorecard behavior.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/report_assertions.py`
- `tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py`
- `tests/benchmarks/test_python_benchmark_manifest_contract.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `python/rebar_harness/benchmarks.py` exposes a local typed manifest record (for example `BenchmarkManifest`) and makes it the public return surface of `load_manifest(...)` and `load_manifests(...)`.
- That typed surface covers the manifest-level metadata currently read through string keys:
  - `path`
  - `manifest_id`
  - `schema_version`
  - `defaults`
  - `workloads`
  - `spec_refs`
  - `notes`
- The benchmark harness stops returning or threading raw manifest dicts through its manifest-level helper path while preserving current validation and duplicate-id behavior:
  - `load_manifest(...)`
  - `load_manifests(...)`
  - `manifest_notes(...)`
  - `_manifest_record_by_id(...)`
  - `build_manifest_summaries(...)`
  - `build_artifacts(...)`
  - `build_scorecard(...)`
  - `run_benchmarks(...)`
- `tests/benchmarks/benchmark_expectations.py` stops typing source-tree manifest collections as `dict[str, Any]` and uses the typed manifest record for stored manifest inventories and target-manifest references while preserving current behavior for:
  - `_source_tree_manifest_records(...)`
  - `SourceTreeBenchmarkCommonCase`
  - `SourceTreeScorecardCase`
  - `SourceTreeCombinedCase`
  - `_selected_workload_ids_by_manifest(...)`
  - `_build_source_tree_benchmark_common_case(...)`
  - `source_tree_scorecard_case(...)`
  - `expected_summary_for_manifests(...)`
  - `source_tree_combined_case(...)`
- `tests/report_assertions.py` benchmark helpers accept the typed manifest record for manifest-level assertions and workload lookup, but this task does not broaden into typed benchmark workload rows. It is fine for `manifest.workloads` and `find_workload_document(...)` to keep using the existing raw workload dict payloads.
- The benchmark contract tests stop indexing manifest return values through string keys and instead assert attribute-based manifest metadata:
  - `tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py`
  - `tests/benchmarks/test_python_benchmark_manifest_contract.py`
- Preserve current benchmark behavior and published scorecard shape exactly:
  - keep benchmark manifest ids, path ordering, workload ordering, smoke workload inventories, and manifest/workload counts unchanged;
  - keep benchmark manifest schema validation and duplicate manifest/workload id errors unchanged;
  - keep the benchmark artifact manifest records, manifest summaries, and scorecard summary counts unchanged for the same manifest selections; and
  - keep `source_tree_scorecard_case(...)` and `source_tree_combined_case(...)` returning the same manifest ids, representative workload ids, known-gap counts, and manifest-path mappings as today.
- Keep the cleanup structural only:
  - do not change files under `benchmarks/workloads/`;
  - do not change `reports/benchmarks/latest.py`, README text, or tracked state files beyond this task file; and
  - do not broaden this into typed benchmark workload definitions, correctness-harness work, or the ready feature task `RBR-0487`.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py tests/benchmarks/test_python_benchmark_manifest_contract.py`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/pattern_boundary.py --report .rebar/tmp/rbr-0488-benchmark-manifest-typing.py`
  - `rg -n 'def load_manifest\\(path: pathlib\\.Path\\) -> tuple\\[dict\\[str, Any\\], list\\[Workload\\]\\]|def load_manifests\\(paths: list\\[pathlib\\.Path\\]\\) -> tuple\\[list\\[dict\\[str, Any\\]\\], list\\[Workload\\]\\]|raw_manifests: list\\[dict\\[str, Any\\]\\]|manifest_documents: list\\[dict\\[str, Any\\]\\]|manifest_documents_by_id: dict\\[str, dict\\[str, Any\\]\\]|target_manifest: dict\\[str, Any\\]|expected_manifest_documents: list\\[dict\\[str, Any\\]\\]|manifest_document: dict\\[str, Any\\]|load_manifest\\(path\\)\\[0\\]\\[\"manifest_id\"\\]|manifest\\[\"defaults\"\\]|manifest\\[\"manifest_id\"\\]' python/rebar_harness/benchmarks.py tests/benchmarks/benchmark_expectations.py tests/report_assertions.py tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py tests/benchmarks/test_python_benchmark_manifest_contract.py`
    The post-change result must be no matches.
  - ```bash
    PYTHONPATH=python ./.venv/bin/python - <<'PY'
    from pathlib import Path
    from rebar_harness.benchmarks import load_manifest
    from tests.benchmarks.benchmark_expectations import source_tree_combined_case

    manifest, workloads = load_manifest(Path("benchmarks/workloads/pattern_boundary.py"))
    assert not isinstance(manifest, dict), type(manifest)
    assert manifest.manifest_id == "pattern-boundary"
    assert manifest.defaults["warmup_iterations"] == 2
    assert len(workloads) == len(manifest.workloads)

    case = source_tree_combined_case("pattern-boundary")
    assert not isinstance(case.target_manifest, dict), type(case.target_manifest)
    assert case.target_manifest.manifest_id == "pattern-boundary"
    assert len(case.target_manifest.workloads) == len(manifest.workloads)
    print("ok")
    PY
    ```

## Constraints
- Prefer one small local dataclass in `python/rebar_harness/benchmarks.py` over another renamed dict-normalization helper or a new support module. The intended end state is one explicit typed benchmark-manifest API, not a second helper that still routes everything through string keys.
- If a raw manifest dict is retained for one-time staging inside `load_manifest(...)`, keep it private to that loader boundary. Do not return raw manifest dicts or keep threading them through `build_scorecard(...)`, `tests/benchmarks/benchmark_expectations.py`, or `tests/report_assertions.py`.
- Do not broaden this task into typed benchmark workload rows, benchmark expectation-table reshaping, correctness-harness cleanup, or any benchmark frontier change already queued in `RBR-0487`.

## Notes
- `RBR-0487` is already queued as the ready-head feature task, and the current runtime dashboard is clean (`Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `Last Cycle Anomalies: none`), so rule 10 does not apply.
- No blocked architecture task is waiting to be reopened or normalized in the current checkout.
- JSON counts remain fully burned down in both tracked and live views:
  - `tracked_json_blob_count: 0`
  - `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
- `RBR-0488` is unused in `ops/state/backlog.md`, `ops/state/current_status.md`, and the current task queue, so it is the next available architecture id.
- The remaining benchmark-manifest coupling is concentrated in three layers:
  - `python/rebar_harness/benchmarks.py` still exposes `load_manifest(...) -> tuple[dict[str, Any], list[Workload]]`, threads `raw_manifests: list[dict[str, Any]]` through scorecard builders, and still computes artifact/manifest metadata through string-key lookups.
  - `tests/benchmarks/benchmark_expectations.py` still stores `manifest_documents`, `manifest_documents_by_id`, and `target_manifest` as raw manifest dicts and still derives source-tree manifest summaries from `manifest["manifest_id"]` / `manifest["workloads"]`.
  - `tests/report_assertions.py` and the benchmark manifest contract tests still type benchmark manifests as `dict[str, Any]` and still assert manifest metadata through `manifest["manifest_id"]` / `manifest["defaults"]`.
- Current file sizes underline why this is still a useful bounded simplification:
  - `python/rebar_harness/benchmarks.py`: `1748` lines
  - `tests/benchmarks/benchmark_expectations.py`: `2107` lines
  - `tests/report_assertions.py`: `670` lines
  - `tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py`: `137` lines
  - `tests/benchmarks/test_python_benchmark_manifest_contract.py`: `548` lines
  - `tests/benchmarks/test_source_tree_benchmark_scorecards.py`: `248` lines
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`: `609` lines
- 2026-03-16 intake verification:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py tests/benchmarks/test_python_benchmark_manifest_contract.py` passes in the current checkout (`11 passed, 652 subtests passed in 0.09s`).
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passes in the current checkout (`21 passed, 493 subtests passed in 20.60s`).
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/pattern_boundary.py --report .rebar/tmp/rbr-0488-benchmark-manifest-typing.py` currently succeeds and reports `{"known_gap_count": 0, "measured_workloads": 6, "module_workloads": 6, "parser_workloads": 0, "regression_workloads": 0, "total_workloads": 6}`.
  - The `rg -n ...` command above currently returns the raw-manifest signature and string-key matches called out in the deliverables, which is the exact coupling this task should delete rather than rename.
  - The typed-manifest probe above currently fails immediately with `AssertionError: <class 'dict'>`, which is the exact public-shape cleanup this task is meant to complete.
