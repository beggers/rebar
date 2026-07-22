# rebar: building a faster Python `re`

`rebar` is an experiment to build a drop-in, faster replacement for Python's regular-expression module. The public import is `import rebar as re`. Three independent, from-scratch engines are checked against the latest stable CPython and compared on the same tasks; incorrect results are never timed.

The immutable objective is [GOAL.md](GOAL.md), SHA-256 `e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62`. Scope notes are in [AMENDMENTS.md](AMENDMENTS.md), and the complete chronological record is in the [experiment log](docs/EXPERIMENT-LOG.md).

## Headline results

The broader holdout contains **72 separate tasks** kept apart from tuning, including logs, URLs, configuration/text cleanup, byte inputs, Unicode, replacements, scanners, and windowed calls. **1× means the same speed as Python `re`; higher is faster.** The native C engine is **1.56× as fast overall** (1.55–1.57× measured range), clearly faster on **70/72** tasks, with **zero** tasks more than 20% slower. It meets every experiment target. Python and Rust are much slower on short calls.

![Overall speed compared with Python re](performance/v3/evidence/final-overall.svg)

| Engine | Overall speed | Clearly faster | Large slowdowns |
| --- | ---: | ---: | ---: |
| Native C | **1.56×** | **70/72** | **0/72** |
| Rust | 0.014× | 2/72 | 69/72 |
| Python | 0.012× | 3/72 | 69/72 |

The [final broader report](performance/v3/evidence/FINAL.md) retains all **7,488** correctness-gated timing rows, every task, memory observations, confidence ranges, and every slowdown. General native paths remove repeated state creation, character/class checks, boundary calls, and rescanning across common workloads while preserving compatibility. The pre-timing check passes **576/576** comparisons.

![Broader performance coverage and current status](performance/v3/evidence/coverage-final.svg)

All three engines now pass every runnable official CPython `re` test, including long inputs, deep lookbehind, mutable buffers, Unicode behavior, and the 403-pattern historical corpus. There are no failures, crashes, or timeouts.

![Official CPython re compatibility check](oracle/cpython-3.14.6/evidence/long-repeat-correctness.svg)

They also pass **66,033** focused differential checks, including **39,000** replacement checks covering `sub`, `subn`, match expansion, text/bytes/buffers, callbacks, empty inputs, and exact error behavior.

![Replacement compatibility before and after the fix](oracle/v2/evidence/replacement-correctness.svg)

## Detailed graphs

These show the broader holdout task by task. Green means clearly faster, red means more than 20% slower, and grey means close or uncertain. Each speed cell includes the measured range.

![Speed on every holdout task](performance/v3/evidence/final-speed.svg)

![Memory used on every holdout task](performance/v3/evidence/final-memory.svg)

![Where each engine is faster or slower](performance/v3/evidence/final-regressions.svg)

![Overall results across all task sets](performance/v3/evidence/final-rankings.svg)

The separate [from-scratch Zig trial](candidates/evidence/ZIG-PROBE.md) shows why the Python/native boundary matters: the compiled Zig matcher is faster than Python `re` on all six small tasks once repeated calls cross that boundary only once, but individual Python calls remain much slower. Zig is an architecture experiment, **not** a complete replacement candidate.

![Zig architecture speed compared with Python re](candidates/evidence/zig-probe-speed.svg)

## Correctness and current status

The baseline is [CPython 3.14.6](oracle/v1/BASELINE.md). Stdlib and all three engines pass the [expanded seeded matrix](oracle/v2/P0.md): **8,244/8,244 cases**, **45/45 obligations**. They also pass all **144** runnable [official CPython `re` methods](oracle/cpython-3.14.6/README.md), with two environment-dependent locale skips.

| Check | Status |
| --- | --- |
| Seeded correctness | **PASS** — stdlib, native C, Python, and Rust each pass all 8,244 expanded cases |
| Official CPython tests | **PASS** — all three engines pass 144/144 runnable methods; zero failures, crashes, or timeouts |
| Focused differential checks | **PASS** — 66,033 replacement, buffer, long-input, lookaround, structured, and collection checks |
| Original performance | **PASS** — native C reaches 1.56× on the original 16-task holdout |
| Expanded performance | **MEASURED / OPTIMIZATION NEEDED** — native C reaches 1.16× on 28 holdout tasks; all results are correctness-gated |
| Broader performance | **PASS** — native C reaches 1.56× on 72 holdout tasks, clearly faster on 70/72 with zero large slowdowns |
| Public import | **AVAILABLE / WINNER** — `import rebar as re` uses the correctness-qualified native C engine |

The [broader performance protocol](performance/v3/PROTOCOL.md) explains exactly what is timed, how comparisons are made, and how slowdowns are reported. Full results, raw data, rejected experiments, and older charts are linked from the [experiment log](docs/EXPERIMENT-LOG.md).

## Try it or reproduce the checks

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHON="$PY" sh tools/build_vm.sh
RUSTFLAGS='-D warnings' sh tools/build_rust.sh

PYTHONPATH=. "$PY" -c 'import rebar as re; print(re.findall(r"[A-Za-z]+", "a faster python re"))'
PYTHONPATH=. "$PY" tools/oracle_v2.py verify --module rebar
PYTHONPATH=. "$PY" tools/cpython_re_oracle.py verify --module rebar
PYTHONPATH=. "$PY" tools/replacement_controls.py --output /tmp/replacement-controls.json
PYTHONPATH=. "$PY" tools/collection_controls.py --output /tmp/collection-controls.json
PYTHONPATH=. "$PY" tools/perf_v2.py verify
PYTHONPATH=. "$PY" tools/perf_v3.py verify
PYTHONPATH=. "$PY" tools/engine_pilot.py --output /tmp/engine-pilot.json --module candidates.ast_candidate --module candidates.rust_candidate
```
