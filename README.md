# rebar

`rebar` is a Rust-backed attempt at a bug-for-bug compatible replacement for Python's `re` module. The target is simple: match CPython's accepted syntax, public API behavior, parse trees, and diagnostics first, then compete on compile and match speed through a CPython-facing extension.

The status block below is the published frontier: what passes today, how much of it is benchmarked, and what still blocks broader parity or performance claims.

<!-- REBAR:STATUS_START -->
## Current State

_This block reports the implemented slice and measurement coverage, not estimated end-state parity._

| Signal | Value |
| --- | --- |
| Phase | Phase 3 is still widening one bounded Rust-backed regex slice at a time, landing correctness first and Python-path benchmark catch-up immediately behind it. |
| Delivery estimate | The published correctness report now covers 1120 cases across 111 manifests, with 1108 passing, 0 explicit failures, and 12 honest gaps; the main benchmark report covers 644 workloads across 30 manifests with 644 real `rebar` timings and 0 explicit known gaps through the source-tree shim, so the published frontier has widened again but is still narrow and not yet a near-full parity or native-path performance claim. |
| Current milestone | After ready `RBR-0543` drains, `RBR-0544` should survive as the next concrete `feature-implementation` follow-on. The queued head reopens the open-ended `{1,}` grouped backtracking-heavy bytes correctness publication on the existing open-ended parity surface for `rb"a((bc|b)c){1,}d"` and `rb"a(?P<word>(bc|b)c){1,}d"`, and the surviving follow-on converts that same bytes pair to Rust-backed parity before the existing Python-path open-ended benchmark anchors catch the slice up. |
| Work queue | `0` ready, `0` in progress, `543` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `1120` |
| Passing in published slice | `1108` |
| Explicit failures | `0` |
| Honest gaps (`unimplemented`) | `12` |
| Covered manifests | `111` |
| Source | [`reports/correctness/latest.py`](reports/correctness/latest.py) |

_These correctness counts cover only the published slice. Overall delivery estimate: The published correctness report now covers 1120 cases across 111 manifests, with 1108 passing, 0 explicit failures, and 12 honest gaps; the main benchmark report covers 644 workloads across 30 manifests with 644 real `rebar` timings and 0 explicit known gaps through the source-tree shim, so the published frontier has widened again but is still narrow and not yet a near-full parity or native-path performance claim._

### Benchmark Snapshot

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/home/ubuntu/rebar/.venv/bin/python`) |
| Published workloads | `644` |
| Workloads with real `rebar` timings | `644` |
| Known-gap workloads | `0` |
| Timing path | `source-tree-shim` |
| Source | [`reports/benchmarks/latest.py`](reports/benchmarks/latest.py) |

_Full-suite benchmark publication still runs through the source-tree shim; strict built-native smoke and full-suite modes remain available for ad hoc runs and tests via `--native-smoke` and `--native-full` when you pass an explicit `--report` path._

### Immediate Next Steps

- No concrete ready feature follow-on currently survives. `RBR-0543` widened the combined correctness report to `1120` / `1108` / `12`; the next intended follow-on is Rust-backed bytes parity for that same open-ended `{1,}` grouped backtracking-heavy pair, but it is not yet re-seeded as a ready task.

### Current Risks

- The main published benchmark report still measures the source-tree shim rather than the built-native extension path.
- The published benchmark surface is still bounded at 644 workloads even though the report no longer carries explicit known-gap rows.
<!-- REBAR:STATUS_END -->

## What Exists Today

`rebar` already has the pieces that matter for the next phase: a Rust regex core, a CPython-facing extension boundary, and published correctness and benchmark scorecards. The latest publication widened bytes coverage for one open-ended grouped backtracking-heavy slice, but it also reintroduced honest gaps, so the published frontier is still too narrow to imply near-full stdlib `re` parity. The queue is currently between slices, with Rust-backed bytes parity for that same pair still the clearest next move but not yet re-seeded as a ready task.

The benchmark story is similarly early. The clearest trustworthy positive signal today is still the tiny parser slice, where 8 workloads are about 2.5x faster on median than CPython. The broader published run still goes through the source-tree shim and is slower overall, so that is signal rather than a general speed claim.

## Where To Look

Start with the tracked scorecards in `reports/correctness/latest.py` and `reports/benchmarks/latest.py`.

To rerun the same repo-local parity and benchmark harnesses from a checkout, use:

```bash
PYTHONPATH=python python3 -m rebar_harness.correctness --report <path>
PYTHONPATH=python python3 -m rebar_harness.benchmarks --report <path>
```

For stricter built-native benchmark spot checks, run `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-smoke --report <path>` or `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-full --report <path>`. `ops/state/current_status.md` tracks the current frontier; `ops/README.md` is only for loop and queue operations.
