# API-boundary paths: correctness and performance follow-up

Profiling the broader holdout identified three avoidable boundary costs. This focused experiment removes them without changing the frozen workloads, weights, or denominators and keeps all three engines from scratch.

- Escaping built and joined one Python object per input character. Each engine now uses an independently owned translation table; text/byte behavior and errors remain CPython-compatible.
- Every native `Match.expand` call reparsed its replacement template in Python. Native expansion now reuses the compiled-pattern template cache and writes captures/literals directly, including bytes and mutable-buffer templates.
- Native compiled-pattern scanning wrapped a native iterator in Python and called `start`/`end` for every result. A small native scanner now performs `search` and `match` directly. The differential controls also exposed incorrect mixed-call/empty-match progression in every engine; each implementation now follows CPython's state transitions.

The focused before/after probe found native costs of about **3.8→0.7 µs** for byte escaping, **4.1→1.0 µs** for match expansion/surface access, and **1.8→0.9 µs** for repeated scanning. The full paired holdout confirms the gains:

| Holdout task | Native speed before | Native speed after | Native traced-memory ratio after |
| --- | ---: | ---: | ---: |
| Escape special byte characters | 0.184× | **0.966×** | 0.68× (from 24.36×) |
| Read groups and expand a match | 0.267× | **1.090×** | 0.32× |
| Scan repeated matches | 0.520× | **1.062×** | 0.36× |
| Scan repeated byte pairs | 0.541× | **1.257×** | 0.38× |
| Scan values in a text window | 0.509× | **1.066×** | 0.30× |

Overall native holdout speed improves from **0.8997× to 0.9735×** (0.9676–0.9795× measured range), clearly faster on **37/72** tasks with **19** remaining large slowdowns. Python/Rust escaping also moves from about 0.18× to about 0.99× and drops traced memory from 24.36× to 0.68×; other short matching calls remain dominated by their execution/FFI architecture. The [complete result](BOUNDARY.md) retains every case, confidence range, and slowdown.

## Gate results

| Gate | Result |
| --- | --- |
| Original seeded oracle | **PASS** — 2,048/2,048 for native, Python, and Rust |
| Expanded seeded oracle | **PASS** — 8,244/8,244 for native, Python, and Rust |
| Broader pre-timing check | **PASS** — 576/576 comparisons |
| Full official CPython suite | **PASS** — 144/144 runnable methods in every engine; zero failures, crashes, or timeouts |
| Boundary differential controls | **PASS** — 2,223/2,223 comparisons, seed `20260722` |
| Long-pattern differential controls | **PASS** — 3,060/3,060 comparisons, seed `20260721` |
| Native address/undefined-behavior checks | **PASS** — expanded oracle, all 144 tasks, and all boundary controls |
| Rust address/overflow checks | **PASS** — expanded oracle, all 144 tasks, and all boundary controls |
| Delegation audit | **PASS** — zero forbidden markers or blocked import attempts in all three engines |
| Paired performance rows | **PASS** — 7,488/7,488 correctness-gated rows |

The complete deterministic control output is [boundary-controls.json](boundary-controls.json), SHA-256 `821e4bea47b266a04b74a362378b9343abc4f3b284cddd0f566ba09a51129f82`. Raw paired rows are [boundary-raw.jsonl](boundary-raw.jsonl), SHA-256 `5754989a48db93cc5e31688595352bfb1457b466baac78ca2c92db4bdb8d1c14`.

Reproduce the checks and analysis:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHON="$PY" sh tools/build_vm.sh
RUSTFLAGS='-D warnings' sh tools/build_rust.sh
PYTHONPATH=. "$PY" tools/boundary_controls.py --output /tmp/boundary-controls.json
PYTHONPATH=. "$PY" tools/perf_v3.py verify
PYTHONPATH=. "$PY" tools/perf_v3.py analyze --input performance/v3/evidence/boundary-raw.jsonl --output /tmp/boundary-summary.json
```
