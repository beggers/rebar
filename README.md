# rebar

`rebar` is a Rust-backed attempt at a bug-for-bug compatible replacement for Python's `re` module. The target is simple: match CPython's accepted syntax, public API behavior, parse trees, and diagnostics first, then compete on compile and match speed through a CPython-facing extension.

The status block below is the published frontier: what passes today, how much of it is benchmarked, and what still blocks broader parity or performance claims.

<!-- REBAR:STATUS_START -->
## Current State

_This block reports the implemented slice and measurement coverage, not estimated end-state parity._

| Signal | Value |
| --- | --- |
| Phase | Phase 3 is still widening one bounded Rust-backed regex slice at a time, landing correctness first and Python-path benchmark catch-up immediately behind it. |
| Delivery estimate | Published correctness is 1334/1334 cases across 111 manifests with 0 honest gaps; the benchmark publication is 747/747 measured workloads across 30 manifests with 0 known gaps, but it still runs through the source-tree shim on a bounded slice. |
| Current milestone | `RBR-0665` should catch the broader `{1,4}` nested grouped-alternation plus branch-local-backreference callable-replacement bytes pair up on the existing `nested-group-callable-replacement-boundary` benchmark surface, so that manifest can move from `52` total workloads / `52` measured workloads / `0` known gaps to `56` / `56` / `0`, and the combined source-tree benchmark report can move from `743` total workloads / `743` measured workloads / `0` known gaps to `747` / `747` / `0` across the same `30` manifests. |
| Work queue | `0` ready, `0` in progress, `666` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `1334` |
| Passing in published slice | `1334` |
| Explicit failures | `0` |
| Honest gaps (`unimplemented`) | `0` |
| Covered manifests | `111` |
| Source | [`reports/correctness/latest.py`](reports/correctness/latest.py) |

_These correctness counts cover only the published slice. Overall delivery estimate: Published correctness is 1334/1334 cases across 111 manifests with 0 honest gaps; the benchmark publication is 747/747 measured workloads across 30 manifests with 0 known gaps, but it still runs through the source-tree shim on a bounded slice._

### Benchmark Snapshot

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/home/ubuntu/rebar/.venv/bin/python`) |
| Published workloads | `747` |
| Workloads with real `rebar` timings | `747` |
| Known-gap workloads | `0` |
| Timing path | `source-tree-shim` |
| Source | [`reports/benchmarks/latest.py`](reports/benchmarks/latest.py) |

_Full-suite benchmark publication still runs through the source-tree shim; strict built-native smoke and full-suite modes remain available for ad hoc runs and tests via `--native-smoke` and `--native-full` when you pass an explicit `--report` path._

### Immediate Next Steps

- Seed the next bounded Rust-backed follow-on; the current publications are up to date at 1334/1334 correctness cases and 747/747 measured benchmark workloads, but no ready or in-progress task remains after the latest queue drain.

### Current Risks

- The main published benchmark report still measures the source-tree shim rather than the built-native extension path.
- The published benchmark surface is still bounded at 747 workloads, so zero known gaps does not yet imply broad performance coverage.
<!-- REBAR:STATUS_END -->

## What Exists Today

`rebar` already has the pieces that matter for the next phase: a Rust regex core, a CPython-facing extension boundary, and published correctness and benchmark scorecards. The current published correctness slice is still bounded but fully green, and the latest benchmark catch-up is landed; the next bounded follow-on still needs to be seeded.

The clearest benchmark signal worth trusting is still the tiny parser compile-proxy slice, where 8 parser workloads are 2.5818x faster on median than CPython. The broader module-facing publication still runs through the source-tree shim and sits at 0.0734x median, so it is methodology and coverage signal rather than a general speed claim.

## Where To Look

Start with the tracked scorecards in `reports/correctness/latest.py` and `reports/benchmarks/latest.py`.

To rerun the same repo-local parity and benchmark harnesses from a checkout, use:

```bash
PYTHONPATH=python python3 -m rebar_harness.correctness --report <path>
PYTHONPATH=python python3 -m rebar_harness.benchmarks --report <path>
```

For stricter built-native benchmark spot checks, run `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-smoke --report <path>` or `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-full --report <path>`. `ops/state/current_status.md` tracks the current frontier; `ops/README.md` is only for loop and queue operations.
