# rebar: building a faster Python `re`

`rebar` is an experiment to build a compatible, faster replacement for Python's regular-expression module. Use it with `import rebar as re`. Four independent engines were written from scratch and checked against the latest stable CPython; none wraps or delegates matching to an external package or Python's regex engine.

The immutable objective is [GOAL.md](GOAL.md), SHA-256 `e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62`. Scope notes are in [AMENDMENTS.md](AMENDMENTS.md), and the complete chronological record is in the [experiment log](docs/EXPERIMENT-LOG.md).

## Headline results

The expanded holdout contains **3,144 separate, unseen tasks** spanning everyday text and byte processing, every common API, compilation, Unicode, captures, replacements, scanners, windows, structured data, source/config parsing, addresses, cleanup, hits, misses, and short/long inputs. **1× means the same speed as Python `re`; higher is faster.**

The native C engine is the fastest candidate at **1.351× as fast overall** (1.349–1.352× measured range) and clearly faster on **2,482/3,144** tasks (**79%**). The larger holdout exposes **226** large slowdowns and falsifies the earlier 1.5× success claim. Empty matches, quoted/CSV data, many alternatives, paths, controlled repeats, long scans, and email collection account for all of them; they are retained, profiled, and explained.

![Overall speed compared with Python re](performance/v5/evidence/initial-overall.svg)

| Engine | Overall speed | Clearly faster | Large slowdowns |
| --- | ---: | ---: | ---: |
| Native C / `rebar` | **1.351×** | **2,482/3,144** | **226/3,144** |
| Zig | 0.481× | 370/3,144 | 2,486/3,144 |
| Rust | 0.149× | 167/3,144 | 2,948/3,144 |
| Python | 0.024× | 86/3,144 | 3,021/3,144 |

The [complete results](performance/v5/evidence/INITIAL.md) retain all **408,720** paired timing rows, every task, memory observation, measured range, and all **17,416** practice/holdout slowdowns. The [plain-language notes](performance/v5/evidence/INITIAL-NOTES.md) explain the profiled native losses and the remaining Zig/Rust/Python costs. Every timed batch is checked against frozen CPython output both before and after timing.

![Expanded performance holdout coverage](performance/v5/evidence/coverage.svg)

All three engines pass the frozen **44,084-case** correctness matrix, including **35,840** previously unused cases across deeper patterns, everyday inputs, Unicode/bytes/buffers, scanner sequences, properties, and invalid inputs. They also pass **155,313** focused checks and all **144** runnable official CPython `re` tests, with zero unexplained failures, crashes, or release-build timeouts. The [qualification report](oracle/v3/evidence/QUALIFIED.md) preserves the compatibility gaps the larger suite found and their fixes.

![Large correctness holdout coverage and results](oracle/v3/evidence/qualified-correctness.svg)

The separate from-scratch Zig engine is under active development. It passes **all 44,084 frozen correctness cases**, **all 6,288 expanded performance tasks**, and **135/144** runnable official CPython methods, with zero crashes or timeouts. On the expanded holdout it is **0.481×** as fast as Python `re`; fresh compilation, cleanup, and splitting can win, while scanners, captures, references, and empty matches remain slow. The [Zig compatibility report](candidates/evidence/ZIG-SYNTAX.md) and [expanded performance notes](performance/v5/evidence/INITIAL-NOTES.md) keep every result and explain the remaining gaps.

![Zig compatibility gained from common syntax](candidates/evidence/zig-syntax-correctness.svg)

![Overall Zig speed and the main holdout families](candidates/evidence/zig-syntax-v4-family.svg)

## Detailed graphs

The family view makes the expanded benchmark readable: each row combines the matching variations of one kind of task. The all-case plots then show every individual holdout result and its measured range or memory use. Green indicates clearly faster, red indicates a slowdown greater than 20%, and grey indicates close or uncertain.

![Speed by kind of holdout task](performance/v5/evidence/initial-family-speed.svg)

![Speed and confidence on every holdout task](performance/v5/evidence/initial-speed-cloud.svg)

![Memory on every holdout task](performance/v5/evidence/initial-memory-cloud.svg)

![Where each engine wins and loses](performance/v5/evidence/initial-regressions.svg)

![Overall results across all task sets](performance/v5/evidence/initial-rankings.svg)

The Zig experiment's detailed memory and win/loss views retain every legacy and generated holdout task family:

![Zig temporary memory across the large holdout](candidates/evidence/zig-syntax-v4-memory.svg)

![Zig wins and losses across the large holdout](candidates/evidence/zig-syntax-v4-regressions.svg)

## Current status

The baseline is [CPython 3.14.6](oracle/v1/BASELINE.md). The public import selects the correctness-qualified native C winner. The independently written [Zig experiment](candidates/evidence/ZIG-SYNTAX.md) now supports Unicode, scoped flags, exact pattern errors, lookbehind references, long/nested repeats, comments, literal braces, octal escapes, and forward references while avoiding large temporary allocations for long misses or sparse results; nine official large-pattern/compiler cases remain before it can be ranked with the qualified engines. Earlier language/FFI experiments, optimizations, rejections, and raw evidence are linked from the [experiment log](docs/EXPERIMENT-LOG.md).

| Check | Status |
| --- | --- |
| Large correctness matrix | **PASS** — stdlib, native C, Python, and Rust each pass all 44,084 cases |
| Focused checks | **PASS** — 155,313 replacement, buffer, long-input, lookaround, collection, separator, newline, and locale checks |
| Official CPython tests | **PASS** — all three engines pass 144/144 runnable methods; zero failures, crashes, or timeouts |
| Earlier large holdout | **PASS / HISTORICAL** — native C reaches 1.56× on the preserved 1,224 tasks; its 10 remeasured large slowdowns are explained |
| Expanded performance holdout | **BELOW TARGET** — native C reaches 1.351× on 3,144 unseen tasks, clearly faster on 79%; all 226 large slowdowns are profiled/explained |
| Zig experiment | **IN PROGRESS** — all 44,084 frozen cases and 6,288 performance tasks pass; 135/144 official methods; 0.481× holdout speed; valid large-pattern/compiler gaps remain |
| Public import | **AVAILABLE / WINNER** — `import rebar as re` uses the independent native C engine |

The [expanded performance protocol](performance/v5/PROTOCOL.md) preserves every earlier task and records the larger unseen set, fixed seeds, weights, timing rules, correctness gate, and complete result. The [earlier v4 protocol/result](performance/v4/PROTOCOL.md) remains available for comparison.

## Try it or reproduce the checks

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHON="$PY" sh tools/build_vm.sh
PYTHON="$PY" RUSTFLAGS='-D warnings' sh tools/build_rust.sh
PYTHON="$PY" sh tools/build_zig_probe.sh

PYTHONPATH=. "$PY" -c 'import rebar as re; print(re.findall(r"[A-Za-z]+", "a faster python re"))'
PYTHONPATH=. "$PY" tools/oracle_v3.py verify --module rebar
PYTHONPATH=. "$PY" tools/cpython_re_oracle.py verify --module rebar
PYTHONPATH=. "$PY" tools/holdout_regression_controls.py --output /tmp/holdout-regression.json
PYTHONPATH=. "$PY" tools/perf_v5.py verify
PYTHONPATH=. "$PY" tools/perf_v5.py measure --output /tmp/rebar-performance.jsonl
PYTHONPATH=. "$PY" tools/perf_v5.py analyze --input /tmp/rebar-performance.jsonl --output /tmp/rebar-summary.json
```
