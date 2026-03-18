# rebar

`rebar` is a Rust-backed attempt at a bug-for-bug compatible replacement for Python's `re` module. The target is simple: match CPython's accepted syntax, public API behavior, parse trees, and diagnostics first, then compete on compile and match speed through a CPython-facing extension.

The status block below is the published frontier: what passes today, how much of it is benchmarked, and what still blocks broader parity or performance claims.

<!-- REBAR:STATUS_START -->
## Current State

_This block reports the implemented slice and measurement coverage, not estimated end-state parity._

| Signal | Value |
| --- | --- |
| Phase | Phase 3 is still widening one bounded Rust-backed regex slice at a time, landing correctness first and Python-path benchmark catch-up immediately behind it. |
| Delivery estimate | The published correctness report now covers 1190 cases across 111 manifests, with 1190 passing, 0 explicit failures, and 0 honest gaps; the main benchmark report covers 674 workloads across 30 manifests with 674 real `rebar` timings and 0 explicit known gaps through the source-tree shim, so the published slice is still bounded and not yet a near-full parity or native-path performance signal. |
| Current milestone | `RBR-0576` should catch the bounded quantified-alternation bytes pair for `rb"a(b|c){1,2}d"` and `rb"a(?P<word>b|c){1,2}d"` up on the existing Python-facing benchmark surface, mirroring the six adjacent bounded `str` rows so the same mixed `str`/`bytes` slice reaches zero-gap measurement before another quantified-alternation bytes family broadens the frontier. |
| Work queue | `1` ready, `0` in progress, `575` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `1190` |
| Passing in published slice | `1190` |
| Explicit failures | `0` |
| Honest gaps (`unimplemented`) | `0` |
| Covered manifests | `111` |
| Source | [`reports/correctness/latest.py`](reports/correctness/latest.py) |

_These correctness counts cover only the published slice. Overall delivery estimate: The published correctness report now covers 1190 cases across 111 manifests, with 1190 passing, 0 explicit failures, and 0 honest gaps; the main benchmark report covers 674 workloads across 30 manifests with 674 real `rebar` timings and 0 explicit known gaps through the source-tree shim, so the published slice is still bounded and not yet a near-full parity or native-path performance signal._

### Benchmark Snapshot

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/home/ubuntu/rebar/.venv/bin/python`) |
| Published workloads | `674` |
| Workloads with real `rebar` timings | `674` |
| Known-gap workloads | `0` |
| Timing path | `source-tree-shim` |
| Source | [`reports/benchmarks/latest.py`](reports/benchmarks/latest.py) |

_Full-suite benchmark publication still runs through the source-tree shim; strict built-native smoke and full-suite modes remain available for ad hoc runs and tests via `--native-smoke` and `--native-full` when you pass an explicit `--report` path._

### Immediate Next Steps

- `RBR-0576` should catch the bounded quantified-alternation bytes pair for `rb"a(b|c){1,2}d"` and `rb"a(?P<word>b|c){1,2}d"` up on the existing Python-facing benchmark surface, mirroring the six adjacent bounded `str` rows so the same mixed `str`/`bytes` slice reaches zero-gap measurement before another quantified-alternation bytes family broadens the frontier.

### Current Risks

- The main published benchmark report still measures the source-tree shim rather than the built-native extension path.
- The published benchmark surface is still bounded at 674 workloads even though the report no longer carries explicit known-gap rows.
<!-- REBAR:STATUS_END -->

## What Exists Today

`rebar` already has the pieces that matter for the next phase: a Rust regex core, a CPython-facing extension boundary, and published correctness and benchmark scorecards. The current published correctness slice is fully green but still bounded: 1190 of 1190 cases across 111 manifests pass. The ready queue is now at `RBR-0576`, which catches the bounded quantified-alternation bytes pair up on the benchmark surface so the same mixed `str`/`bytes` slice reaches zero-gap measurement.

The benchmark story is similarly early. The clearest trustworthy positive signal today is still the tiny parser compile-proxy slice, where 8 workloads are about 2.9x faster on median than CPython. The broader 674-workload publication still goes through the source-tree shim and is slower overall, so that is signal rather than a general speed claim.

## Where To Look

Start with the tracked scorecards in `reports/correctness/latest.py` and `reports/benchmarks/latest.py`.

To rerun the same repo-local parity and benchmark harnesses from a checkout, use:

```bash
PYTHONPATH=python python3 -m rebar_harness.correctness --report <path>
PYTHONPATH=python python3 -m rebar_harness.benchmarks --report <path>
```

For stricter built-native benchmark spot checks, run `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-smoke --report <path>` or `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-full --report <path>`. `ops/state/current_status.md` tracks the current frontier; `ops/README.md` is only for loop and queue operations.
