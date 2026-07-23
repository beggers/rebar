# rebar: a faster Python `re`

`rebar` is a from-scratch replacement for Python's regular-expression module. Use it with `import rebar as re`. Four independent engines were built and checked against stable CPython 3.14.6; matching never delegates to Python `re`, `_sre`, or an external regular-expression package.

## Current results

On **6,216 separate, unseen tasks**, Zig / `rebar` is **1.583× as fast overall** (95% range **1.581–1.584×**) and clearly faster on **5,333/6,216 tasks (85.8%)**. The broader test exposes **243** tasks more than 20% slower, concentrated in filenames, repeated alternatives, dense literal collection, Unicode-heavy lines, and case-insensitive number/unit matching. **1× means the same speed as Python `re`; higher is faster.**

![Overall speed compared with Python re](performance/v6/evidence/initial-overall.svg)

| Engine | Overall speed | Clearly faster | Large slowdowns |
| --- | ---: | ---: | ---: |
| Zig / `rebar` | **1.583×** | **5,333/6,216** | **243/6,216** |
| Native C | 1.283× | 4,577/6,216 | 653/6,216 |
| Rust | 0.134× | 229/6,216 | 5,892/6,216 |
| Python | 0.021× | 195/6,216 | 5,918/6,216 |

![Zig speed across the broader holdout](performance/v6/evidence/initial-zig-speed.svg)

The holdout covers everyday text and bytes, common calls, compilation, Unicode, captures, replacements, scanners, input slices, structured data, hits, misses, and short and long inputs. All **808,080** paired timing rows, memory observations, confidence ranges, individual results, and every slowdown are preserved in the [broader performance report](performance/v6/evidence/INITIAL.md).

## Compatibility

`rebar` passes the frozen **44,084-case** correctness suite, including **35,840** unseen text, bytes, Unicode, buffer, scanner, property, and invalid-input cases, all **144** runnable official CPython `re` tests, **109,848** established focused checks, **163,960** alternative/run/delimiter/API checks, and **156,484** direct-scan checks. Debug, address, and undefined-behavior checks and the zero-delegation audit are clean. Every engine also passes all **62,160/62,160** broader pre-timing comparisons.

![Large correctness holdout coverage and results](oracle/v3/evidence/qualified-correctness.svg)

![Broader performance holdout coverage](performance/v6/evidence/coverage.svg)

| Check | Current result |
| --- | --- |
| Frozen correctness | **PASS** — stdlib and all four engines pass all 44,084 cases |
| Official CPython tests | **PASS** — 144/144 runnable methods; zero failures, crashes, or timeouts |
| Focused Zig/API/safety | **PASS** — Unicode, large patterns, groups, repeats, flags, errors, spans, captures, buffers, and public calls |
| Performance holdout | **PASS** — 1.583× overall, 85.8% clearly faster; all 243 large slowdowns are listed and explained |
| Public import | **AVAILABLE** — `import rebar as re` selects the independent Zig engine |

## Detailed current graphs

The following views keep the **48 new kinds of workload** separate so it is easy to see where each engine helps or hurts. Temporary Python memory for Zig is at or below Python `re` on **5,714/6,216** holdout tasks, with a **0.54×** median ratio. The raw data also retains process-memory observations.

![Speed by workload and engine](performance/v6/evidence/initial-family-speed.svg)

![Temporary Python memory by workload and engine](performance/v6/evidence/initial-memory.svg)

![Wins and large slowdowns by workload and engine](performance/v6/evidence/initial-win-loss.svg)

![Overall rankings on practice, holdout, and all tasks](performance/v6/evidence/initial-rankings.svg)

## Reproduce

The [broader performance protocol](performance/v6/PROTOCOL.md) records coverage, equal weights, seeds, timing rules, and correctness gates. The immutable objective is [GOAL.md](GOAL.md), SHA-256 `e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62`; scope notes are in [AMENDMENTS.md](AMENDMENTS.md), and the chronological record is in the [experiment log](docs/EXPERIMENT-LOG.md).

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHON="$PY" sh tools/build_zig_probe.sh

PYTHONPATH=. "$PY" -c 'import rebar as re; print(re.findall(r"[A-Za-z]+", "a faster python re"))'
PYTHONPATH=. "$PY" tools/oracle_v3.py verify --module rebar --cohort holdout --output /tmp/rebar-correctness.json
PYTHONPATH=. "$PY" tools/cpython_re_oracle.py verify --module rebar --output /tmp/rebar-official.json
PYTHONPATH=. "$PY" tools/zig_dispatch_probe.py --module rebar --seeded-cases 16384 --output /tmp/rebar-dispatch.json
PYTHONPATH=. "$PY" tools/zig_executor_probe.py --module rebar --seeded-cases 8192 --output /tmp/rebar-executor.json
PYTHONPATH=. "$PY" tools/perf_v6.py verify --output /tmp/rebar-performance-check.json
gzip -dc performance/v6/evidence/initial-raw.jsonl.gz > /tmp/rebar-raw.jsonl
PYTHONPATH=. "$PY" tools/perf_v6_analyze_fast.py --self-test
PYTHONPATH=. "$PY" tools/perf_v6_analyze_fast.py --input /tmp/rebar-raw.jsonl --output /tmp/rebar-summary.json
PYTHONPATH=. "$PY" tools/performance_v6_charts.py --summary /tmp/rebar-summary.json --prefix /tmp/rebar
```
