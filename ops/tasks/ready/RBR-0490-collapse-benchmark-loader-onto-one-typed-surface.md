# RBR-0490: Collapse the benchmark loader onto one typed manifest/workload surface

Status: ready
Owner: architecture-implementation
Created: 2026-03-16

## Goal
- Remove the remaining duplicated benchmark-loader API so the harness, benchmark expectation helpers, and benchmark tests stop carrying both `BenchmarkManifest` objects and separate workload lists for the same manifest data. The intended end state is one typed manifest surface whose `workloads` are already `Workload` records, with scorecard/report payloads staying unchanged.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/report_assertions.py`
- `tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py`
- `tests/benchmarks/test_python_benchmark_manifest_contract.py`
- `tests/benchmarks/test_built_native_benchmark_modes.py`
- `tests/benchmarks/test_compile_proxy_correctness_anchor_contract.py`
- `tests/benchmarks/test_nested_group_benchmark_correctness_anchor_contract.py`
- `tests/benchmarks/test_grouped_alternation_replacement_benchmark_correctness_anchor_contract.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `python/rebar_harness/benchmarks.py` makes `BenchmarkManifest` the single loader return surface:
  - `BenchmarkManifest.workloads` is typed as `list[Workload]`, not raw workload dict payloads.
  - `BenchmarkManifest.from_dict(...)` owns workload materialization and stores those typed `Workload` records on the manifest.
  - `load_manifest(path: pathlib.Path)` returns `BenchmarkManifest`.
  - `load_manifests(paths: list[pathlib.Path])` returns `list[BenchmarkManifest]`.
- Duplicate-id validation remains intact after the loader collapse:
  - duplicate benchmark manifest ids still raise the same `ValueError`;
  - duplicate benchmark workload ids across the selected manifests still raise the same `ValueError`; and
  - published manifest ordering and workload ordering remain unchanged for the same manifest path selection.
- Benchmark execution and source-tree expectation builders stop threading a second manifest-workload collection through the call graph:
  - `run_benchmarks(...)` flattens typed workloads from the returned manifests before smoke selection and evaluation;
  - `source_tree_scorecard_case(...)`, `source_tree_combined_case(...)`, and related helpers in `tests/benchmarks/benchmark_expectations.py` stop unpacking `load_manifest(...)` / `load_manifests(...)` tuples; and
  - the benchmark contract and anchor tests stop unpacking loader tuples and instead read typed workloads from `manifest.workloads`.
- `tests/report_assertions.py` and `tests/benchmarks/benchmark_expectations.py` stop treating manifest-owned workload definitions as raw dicts:
  - smoke-id selection, representative-workload lookup, selected-workload filtering, and manifest-side workload lookup use `Workload` attributes;
  - it is fine to keep `workload_to_payload(...)` as the boundary when a typed `Workload` must be compared against a published scorecard row; and
  - this task does not need to type the published scorecard `workloads` list, which may remain report payload dicts.
- Preserve published benchmark behavior exactly:
  - keep benchmark summary counts, family counts, regression counts, manifest summaries, smoke workload inventories, known-gap counts, and artifact manifest records unchanged for the same selected manifests;
  - keep `reports/benchmarks/latest.py` format and semantics unchanged; and
  - keep the source-tree benchmark helper expectations and representative workload ids unchanged.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/pattern_boundary.py --report .rebar/tmp/rbr-0490-benchmark-loader-shape.py`
  - `rg -n 'def load_manifest\\(path: pathlib\\.Path\\) -> tuple\\[BenchmarkManifest, list\\[Workload\\]\\]|def load_manifests\\(paths: list\\[pathlib\\.Path\\]\\) -> tuple\\[list\\[BenchmarkManifest\\], list\\[Workload\\]\\]|manifest, workloads = load_manifest\\(|_, workloads = load_manifest\\(|manifests, workloads = load_manifests\\(|manifests, manifest_workloads = load_manifests\\(' python/rebar_harness/benchmarks.py tests/benchmarks/benchmark_expectations.py tests/benchmarks/test_built_native_benchmark_modes.py tests/benchmarks/test_default_benchmark_manifest_inventory_contract.py tests/benchmarks/test_grouped_alternation_replacement_benchmark_correctness_anchor_contract.py tests/benchmarks/test_nested_group_benchmark_correctness_anchor_contract.py tests/benchmarks/test_compile_proxy_correctness_anchor_contract.py tests/benchmarks/test_python_benchmark_manifest_contract.py`
    The post-change result must be no matches.
  - ```bash
    PYTHONPATH=python ./.venv/bin/python - <<'PY'
    from pathlib import Path
    from rebar_harness.benchmarks import load_manifest, load_manifests

    path = Path("benchmarks/workloads/pattern_boundary.py")
    manifest = load_manifest(path)
    assert not isinstance(manifest, tuple), type(manifest)
    assert manifest.manifest_id == "pattern-boundary"
    assert all(hasattr(workload, "workload_id") for workload in manifest.workloads)

    manifests = load_manifests([path])
    assert len(manifests) == 1
    assert manifests[0].manifest_id == "pattern-boundary"
    print("ok")
    PY
    ```

## Constraints
- Keep the cleanup structural only. Do not change files under `benchmarks/workloads/`, do not change `reports/benchmarks/latest.py`, README text, or tracked state files, and do not broaden into feature/frontier work already queued in `RBR-0489`.
- Prefer deleting the duplicated loader surfaces over adding compatibility wrappers. The end state should be one obvious typed loader API, not `load_manifest(...)` plus a second helper that preserves the old tuple shape.
- Do not broaden this task into correctness-harness cleanup, typed published benchmark scorecard rows, or a report-format rewrite. The cleanup target is the manifest/workload definition flow inside the benchmark harness and its tests.

## Notes
- `RBR-0488` intentionally stopped at typed benchmark manifest metadata and left workload definitions on the old raw-dict path. This is the immediate structural follow-on to finish that loader-side simplification instead of opening a different benchmark cleanup.
- Rule 10 does not apply in the current checkout: `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, and `Last Cycle Anomalies: none`, while the last cycle completed both `RBR-0488` and `RBR-0487` cleanly.
- JSON-burn-down is complete, so this run moved to the next post-JSON simplification lane:
  - `tracked_json_blob_count: 0`
  - `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
- The old tuple-return loader API still has 20 live signature/call-site matches across the benchmark harness and tests in the current checkout, which makes this a concrete deletion task rather than speculative cleanup.
- 2026-03-16 architecture probe:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks` passes in the current checkout (`50 passed, 3 skipped, 1150 subtests passed in 21.06s`).
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/pattern_boundary.py --report .rebar/tmp/rbr-0490-benchmark-loader-shape.py` currently succeeds and reports `{"known_gap_count": 0, "measured_workloads": 6, "module_workloads": 6, "parser_workloads": 0, "regression_workloads": 0, "total_workloads": 6}`.
  - The `rg -n ...` command above currently returns the old tuple signatures and tuple-unpack call sites, which is the exact surface this task should delete rather than wrap.
  - The typed-loader probe above currently fails with `AssertionError: <class 'tuple'>`, which is the exact public-shape cleanup this task is meant to complete.
