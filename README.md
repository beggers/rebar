# rebar

`rebar` is a Rust-backed attempt at a bug-for-bug compatible replacement for Python's `re` module. The target is simple: match CPython's accepted syntax, public API behavior, parse trees, and diagnostics first, then compete on compile and match speed through a CPython-facing extension.

The status block below is the published frontier: what passes today, how much of it is benchmarked, and what still blocks broader parity or performance claims.

<!-- REBAR:STATUS_START -->
## Current State

_This block reports the implemented slice and measurement coverage, not estimated end-state parity._

| Signal | Value |
| --- | --- |
| Phase | Phase 3 is still widening one bounded Rust-backed regex slice at a time, landing correctness first and Python-path benchmark catch-up immediately behind it. |
| Delivery estimate | Published correctness covers 1701 cases across 114 manifests, with all 1701 passing in the current slice; the benchmark publication covers 1067/1067 measured workloads across 30 manifests with 0 known gaps, but it still runs through the source-tree-shim path on a bounded slice. |
| Current milestone | The next surviving frontier is bytes nested conditional callable correctness publication on the shared callable owner path. |
| Work queue | `0` ready, `0` in progress, `1185` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `1701` |
| Passing in published slice | `1701` |
| Explicit failures | `0` |
| Honest gaps (`unimplemented`) | `0` |
| Covered manifests | `114` |
| Source | [`reports/correctness/latest.py`](reports/correctness/latest.py) |

_These correctness counts cover only the published slice. Overall delivery estimate: Published correctness covers 1701 cases across 114 manifests, with all 1701 passing in the current slice; the benchmark publication covers 1067/1067 measured workloads across 30 manifests with 0 known gaps, but it still runs through the source-tree-shim path on a bounded slice._

### Benchmark Snapshot

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/home/ubuntu/rebar/.venv/bin/python`) |
| Published workloads | `1067` |
| Workloads with real `rebar` timings | `1067` |
| Known-gap workloads | `0` |
| Timing path | `source-tree-shim` |
| Source | [`reports/benchmarks/latest.py`](reports/benchmarks/latest.py) |

_Full-suite benchmark publication still runs through the source-tree shim; strict built-native smoke and full-suite modes remain available for ad hoc runs and tests via `--native-smoke` and `--native-full` when you pass an explicit `--report` path._

### Immediate Next Steps

- The next surviving frontier is bytes nested conditional callable correctness publication on the shared callable owner path.

### Current Risks

- The main published benchmark report still measures the source-tree-shim path rather than the built-native extension path.
- The published benchmark surface is still bounded at 1067 workloads, so zero known gaps does not yet imply broad performance coverage.
<!-- REBAR:STATUS_END -->

## What Exists Today

`rebar` already has the pieces that matter for the next phase: a Rust regex core, a CPython-facing extension boundary, and published correctness and benchmark scorecards. The current published correctness slice is fully green but still intentionally bounded, and the main benchmark publication measures that same slice through the source-tree-shim path rather than the built-native extension path.

The clearest benchmark signal today is still the tiny parser family, which beats CPython on median. The much larger module-facing family remains slower through the shim, so the current benchmark publication is stronger as coverage and methodology proof than as a headline speed claim.

## Where To Look

Start with the tracked scorecards in `reports/correctness/latest.py` and `reports/benchmarks/latest.py`.

To rerun the same repo-local parity and benchmark harnesses from a checkout, use:

```bash
PYTHONPATH=python python3 -m rebar_harness.correctness --report <path>
PYTHONPATH=python python3 -m rebar_harness.benchmarks --report <path>
```

For stricter built-native benchmark spot checks, run `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-smoke --report <path>` or `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-full --report <path>`. `ops/state/current_status.md` tracks the current frontier; `ops/README.md` is only for loop and queue operations.
