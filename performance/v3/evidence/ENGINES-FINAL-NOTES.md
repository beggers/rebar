# Optimized-engine follow-up: what changed and why tasks are still slow

The frozen broader run contains **144** tasks, four modules, **13** paired trials, and **7,488** correctness-gated timing rows. Every task, memory observation, confidence range, and slowdown is in the [full report](ENGINES-FINAL.md), [summary](engines-final-summary.json), and [raw rows](engines-final-raw.jsonl).

## Overall result

| Engine | Previous holdout | Current holdout | Improvement | Clearly faster | Large slowdowns |
| --- | ---: | ---: | ---: | ---: | ---: |
| Native C | 1.557× | **1.568×** (1.560–1.576×) | 1.01× | **68/72** | **0/72** |
| Rust | 0.014× | **0.178×** (0.177–0.178×) | **13.03×** | 4/72 | 68/72 |
| Python | 0.011× | **0.027×** (0.027–0.028×) | **2.38×** | 3/72 | 69/72 |

Native C remains the only fully compatible engine that is faster overall. It exceeds the **1.5×** target, is clearly faster on **94%** of holdout tasks, and has no task more than 20% slower. The four close/uncertain native tasks are absent-branch search (**1.031×**, 0.965–1.071×), windowed search (**0.965×**, 0.932–1.022×), windowed match (**1.002×**, 0.993–1.011×), and failed match (**1.087×**, 0.975–1.155×).

Rust improves about **13×** overall after removing repeated Python/`ctypes` conversion, batching collections, and simplifying common matching paths. Python improves about **2.4×** after adding safe start skipping, reusable matching state, and cheaper common paths. Their remaining costs are most visible on short calls, where constructing Python results dominates the actual match.

## Every large slowdown is accounted for

The full report retains all **274** results more than 20% slower. They fall into three public-facing groups; the counts below sum exactly to **138 Python + 136 Rust = 274**. Native C has none.

| What the task does | Python slowdowns | Rust slowdowns | Why it remains slower |
| --- | ---: | ---: | --- |
| One match or search | 52 | 52 | Short calls still create matching state and Python `Match` objects; this fixed per-call cost is larger than the small input being searched. |
| Build multiple results | 84 | 84 | `findall`, `finditer`, `split`, replacement, scanners, and match-surface access construct many Python values and repeatedly cross or execute the public-object layer. |
| Compile and immediately search | 2 | 0 | Python pays its parser/compiler and first-match setup together; Rust's optimized compiler path is faster on these tasks. |
| **Total** | **138** | **136** | **274/274 explained** |

This is consistent with the fastest remaining cases: Rust is clearly faster for compile-only, complex compile, cold compile/search, and bytes escaping; Python is clearly faster for both compile-only tasks and bytes escaping. The detailed speed, memory, and regression graphs keep the losses visible rather than averaging them away.

## Reproduce

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHON="$PY" sh tools/build_vm.sh
PYTHON="$PY" RUSTFLAGS='-D warnings' sh tools/build_rust.sh
PYTHONPATH=. "$PY" tools/perf_v3.py verify
PYTHONPATH=. "$PY" tools/perf_v3.py measure --output /tmp/engines-raw.jsonl
PYTHONPATH=. "$PY" tools/perf_v3.py analyze --input /tmp/engines-raw.jsonl --output /tmp/engines-summary.json
"$PY" tools/performance_report.py --summary /tmp/engines-summary.json --output /tmp/ENGINES.md --title 'Optimized engines — broader performance report'
"$PY" tools/performance_charts.py --summary /tmp/engines-summary.json --prefix /tmp/engines
```
