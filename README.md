# rebar: a faster Python `re`

`rebar` is a from-scratch replacement for Python's regular-expression module. Four independent engines were built and tested against stable CPython 3.14.6; the fastest compatible engine is now the public one. Use it with `import rebar as re`. No engine wraps or delegates matching to Python `re` or an external regular-expression package.

The immutable objective is [GOAL.md](GOAL.md), SHA-256 `e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62`. Scope notes are in [AMENDMENTS.md](AMENDMENTS.md); the chronological record and rejected experiments are in the [experiment log](docs/EXPERIMENT-LOG.md).

## Headline results

The final holdout contains **3,144 separate, unseen tasks** covering everyday text and bytes, common calls, compilation, Unicode, captures, replacements, scanners, windows, structured data, hits, misses, and short and long inputs. **1× means the same speed as Python `re`; higher is faster.**

`rebar` reaches **1.539× as fast overall** (95% range **1.517–1.561×**) and is clearly faster on **2,635/3,144 tasks (83.8%)**. It passes all frozen and upstream correctness checks. The 93 large slowdowns are retained and explained; the main ones are repeated failed starts, many alternatives, and short verbose or lookahead-heavy searches.

![Overall speed compared with Python re](candidates/evidence/zig-bound-overall.svg)

| Engine | Overall speed | Clearly faster | Large slowdowns |
| --- | ---: | ---: | ---: |
| Zig / `rebar` | **1.539×** | **2,635/3,144** | **93/3,144** |
| Native C | 1.351× | 2,482/3,144 | 226/3,144 |
| Rust | 0.149× | 167/3,144 | 2,948/3,144 |
| Python | 0.024× | 86/3,144 | 3,021/3,144 |

The [final Zig report](candidates/evidence/ZIG-BOUNDARY.md) contains all **163,488** final paired timing rows, confidence ranges, memory results, repeated runs, rejected designs, and [every large slowdown](candidates/evidence/zig-bound-regressions.md). The [initial four-engine comparison](performance/v5/evidence/INITIAL.md) retains all **408,720** original paired rows. Every timed case is checked against frozen CPython output immediately before and after timing.

![Zig speed across all balanced holdout families](candidates/evidence/zig-bound-v5-family.svg)

All four engines pass the frozen **44,084-case** correctness matrix, including **35,840** unseen text, bytes, Unicode, buffer, scanner, property, and invalid-input cases, plus all **144** runnable official CPython `re` tests. Zig also passes **109,848** focused checks, **190** direct public-surface comparisons, full Unicode membership, and address/undefined-behavior checks with zero unexplained failures, crashes, or timeouts.

![Large correctness holdout coverage and results](oracle/v3/evidence/qualified-correctness.svg)

![Expanded performance holdout coverage](performance/v5/evidence/coverage.svg)

## Detailed graphs

The family graph above combines related tasks so the main differences are easy to see. The views below retain every task and show temporary memory, compiled-program memory, and all wins and losses. Green means clearly faster, red means more than 20% slower, and grey means close or uncertain.

![Zig temporary memory across the expanded holdout](candidates/evidence/zig-bound-v5-memory.svg)

![Compiled Zig program memory across the expanded holdout](candidates/evidence/zig-bound-program-memory.svg)

![Zig wins and losses across the expanded holdout](candidates/evidence/zig-bound-v5-regressions.svg)

The original comparison views remain available for every engine:

![Speed by kind of holdout task](performance/v5/evidence/initial-family-speed.svg)

![Speed and confidence on every holdout task](performance/v5/evidence/initial-speed-cloud.svg)

![Memory on every holdout task](performance/v5/evidence/initial-memory-cloud.svg)

![Where each engine wins and loses](performance/v5/evidence/initial-regressions.svg)

![Overall results across all task sets](performance/v5/evidence/initial-rankings.svg)

## Status and reproduction

| Check | Result |
| --- | --- |
| Correctness matrix | **PASS** — stdlib, Zig, native C, Rust, and Python each pass all 44,084 cases |
| Official CPython tests | **PASS** — all four engines pass 144/144 runnable methods; zero failures, crashes, or timeouts |
| Focused Zig checks | **PASS** — 109,848 large-pattern, group, repeat, syntax, error, flag, Unicode, span, and capture checks; 190 direct API checks |
| Expanded performance holdout | **PASS** — `rebar` is 1.539× as fast, clearly faster on 83.8%; all 93 large slowdowns explained |
| Public import | **AVAILABLE / WINNER** — `import rebar as re` selects the independent Zig engine |

Compiled Zig programs use **18,600–47,580 bytes**, with a **23,308-byte median**, instead of the earlier fixed 423,960-byte layout. The frozen [performance protocol](performance/v5/PROTOCOL.md) records coverage, seeds, weights, timing rules, and the correctness gate. The [qualification report](oracle/v3/evidence/QUALIFIED.md) records the compatibility gaps found by the larger suite and their fixes.

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHON="$PY" sh tools/build_zig_probe.sh

PYTHONPATH=. "$PY" -c 'import rebar as re; print(re.findall(r"[A-Za-z]+", "a faster python re"))'
PYTHONPATH=. "$PY" tools/oracle_v3.py verify --module rebar
PYTHONPATH=. "$PY" tools/cpython_re_oracle.py verify --module rebar
PYTHONPATH=. "$PY" tools/zig_public_surface_probe.py --module rebar --output /tmp/rebar-surface.json
PYTHONPATH=. "$PY" tools/perf_v5.py verify --module rebar --output /tmp/rebar-performance-check.json
PYTHONPATH=. "$PY" tools/zig_perf_v5_pilot.py --raw /tmp/rebar-timing.jsonl --output /tmp/rebar-summary.json --chart /tmp/rebar-speed.svg --memory-chart /tmp/rebar-memory.svg --regression-chart /tmp/rebar-regressions.svg --trials 13 --bootstraps 2000
PYTHONPATH=. "$PY" tools/zig_match_surface_perf.py --raw /tmp/rebar-match-hit.jsonl --output /tmp/rebar-match-hit.json --trials 13 --bootstraps 2000
```
