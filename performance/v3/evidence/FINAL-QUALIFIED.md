# Final native execution and collection result

The final experiment meets every success criterion. All three independent, from-scratch candidates are correctness-qualified and measured against unmodified CPython 3.14.6. The native C bytecode engine is the simplest compatible winner and is exposed as `import rebar as re`.

| Required result | Final result |
| --- | --- |
| Holdout speed | **1.5572×** geometric mean, measured range **1.5475–1.5670×** |
| Clearly faster cases | **70/72 (97.2%)** |
| Large holdout slowdowns | **0/72** |
| Correctness-gated timing | **7,488/7,488 rows** |
| Correctness-qualified candidates | **3/3** independent implementations |
| Unexplained mismatches, crashes, or unsafe behavior | **0** |

The only two holdout cases not clearly faster are short windowed search/match calls: **0.978×** (0.950–1.026×) and **1.005×** (0.988–1.021×). They are near parity and within uncertainty. There are no regressions over 20% to explain or omit. Every Rust/Python slowdown, memory observation, and confidence range remains visible in the [complete report](FINAL.md).

## What changed

Profiling showed that small repeated costs affected many workloads. The final native paths address them generally:

- Character-class tables now initialize only the needed case mode; direct run loops handle repeated classes, dots, and literals without a function call per character. This also removes unnecessary first-character table construction and improves cold compilation/search.
- Iterators and scanners retain a validated subject view, avoiding repeated Python/native boundary setup. Literal and three-character alternative starts skip impossible positions safely.
- Structured line records, configuration, paths, mixed separators, match expansion, literal replacement, and escaping use direct native operations with the same captures, limits, windows, and error behavior.
- A new **6,720-comparison** collection differential suite exposed two edge cases during development—final-newline consumption and optional-prefix backtracking at a shortened window—which were fixed before timing.

Representative holdout gains from the previous full run:

| Task | Before | Final | Final measured range |
| --- | ---: | ---: | ---: |
| Compile and search from cold | 0.813× | **1.333×** | 1.316–1.350× |
| Find a web or file address | 0.872× | **1.420×** | 1.282–1.570× |
| Find email-like addresses | 0.808× | **1.312×** | 1.299–1.324× |
| Find file paths | 0.951× | **3.297×** | 3.163–3.514× |
| Read configuration lines | 1.067× | **2.985×** | 2.888–3.071× |
| Read repeated line records | 1.088× | **1.771×** | 1.655–1.852× |
| Find all text tokens | 1.611× | **2.200×** | 2.026–2.312× |
| Iterate over captured pairs | 1.436× | **2.155×** | 2.027–2.267× |
| Search for one of many words (absent) | 0.815× | **1.061×** | 1.010–1.114× |
| Escape special byte characters | 0.997× | **4.646×** | 4.536–4.775× |
| Find a readable formatted field | 2.386× | **3.189×** | 3.147–3.237× |

The full raw timing rows are [final-raw.jsonl](final-raw.jsonl), SHA-256 `7e8872eec672c5cf2a285ec97dc21dae04a5b3372016c7404cf3c70517c2f6e3`; the analyzed summary is [final-summary.json](final-summary.json), SHA-256 `69c262d0bd9fcd4e644e5f45e6a35f64a73f756dcbdf7581bf7bca0758f8a38a`. All intermediate pilots are preserved alongside the report.

## Final gates

| Gate | Result |
| --- | --- |
| Original and expanded correctness matrices | **PASS** — all 2,048 and 8,244 cases in every engine |
| Focused differential checks | **PASS** — 66,033/66,033 replacement, buffer, long-input, lookaround, structured, and collection comparisons |
| Official CPython `re` suite | **PASS** — 144/144 runnable methods in every engine; zero failures, crashes, or timeouts |
| Native address/undefined-behavior checks | **PASS** — expanded suite, all performance cases, and all new controls |
| Delegation audit | **PASS** — zero forbidden markers or blocked imports in all three production candidates |
| Pre-timing check | **PASS** — 576/576 comparisons |
| Full paired performance | **PASS** — 7,488/7,488 correctness-gated rows |

The final collection-control output is [collection-controls.json](collection-controls.json), SHA-256 `aa44dbb4421ee74f0dd38aae7ef8fd67ba9974e56f9252dc8515ee142a1d5ef6`, seed `20260727`.

Reproduce the final checks and analysis:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHON="$PY" sh tools/build_vm.sh
RUSTFLAGS='-D warnings' sh tools/build_rust.sh
PYTHONPATH=. "$PY" tools/oracle_v2.py verify --module rebar
PYTHONPATH=. "$PY" tools/cpython_re_oracle.py verify --module rebar
PYTHONPATH=. "$PY" tools/replacement_controls.py --output /tmp/replacement-controls.json
PYTHONPATH=. "$PY" tools/look_path_controls.py --output /tmp/look-controls.json
PYTHONPATH=. "$PY" tools/structured_path_controls.py --output /tmp/structured-controls.json
PYTHONPATH=. "$PY" tools/collection_controls.py --output /tmp/collection-controls.json
PYTHONPATH=. "$PY" tools/perf_v3.py verify
PYTHONPATH=. "$PY" tools/perf_v3.py analyze --input performance/v3/evidence/final-raw.jsonl --output /tmp/final-summary.json
```
