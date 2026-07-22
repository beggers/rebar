# Zig direct-scanning follow-up

The independent Zig engine is now **1.683×** as fast as Python `re` on the **3,144-task** expanded holdout (95% range **1.660–1.705×**), clearly faster on **2,931/3,144 (93.2%)**, with **zero** tasks more than 20% slower. Every timing row, check, interval, memory result, pilot, and rejection is preserved. Matching uses no external regular-expression engine or package.

![Overall speed compared with Python re](zig-exec-overall.svg)

## What changed

Profiles showed that several ordinary expressions repeatedly entered the general capture/backtracking executor even when their structure permits a direct scan. The from-scratch Zig compiler and executor now recognize conservative shapes and retain the general path for everything else:

- **Compact safe empty and lookaround work.** A lazy, unbounded, capture-free repeat whose only other choice is empty becomes a compact run. One-character assertions, fixed literal assertions, a run followed by an atom, and a boundary-or-assertion choice use small direct instructions. Programs containing no remaining references use the lighter executor, and a root zero-width choice scans positions directly. Greedy nullable repeats are deliberately excluded because their iteration behavior differs.
- **Scan balanced quoted fields once.** Capture-free lookaheads made from repeated pairs of a single excluded quote and a final excluded-quote run are recognized structurally. Splitting or finding a literal separator then tracks quote parity in a linear scan instead of restarting the lookahead at each separator. Quote and separator values are general, text/bytes/wide inputs are supported, and incompatible flags or sets stay on the general path.
- **Scan common captured fields directly.** Lazy quoted captures with a repeated closing delimiter, two-part key/value fields, readable fields with optional space, and three-part delimited fields now fill capture spans during one scan. Bounded/lazy runs, flags, windows, and suffix backtracking are preserved. Simple uncaptured two/three-run expressions and excluded-prefix word searches receive the same treatment.

These are general syntax-based transformations in [mini_regex.zig](../zig/mini_regex.zig), not special answers or wrappers. The new [executor differential probe](../../tools/zig_executor_probe.py) covers all paths with stable seed `2026072203`, text/bytes/Unicode, windows, flags, `search`/`match`/`fullmatch`, collection, splitting, and replacements.

## Final performance

The frozen fixture remains SHA-256 `67a4d07ee260bc58456290d76e040b78ba769d1b63cd3b21f0879daa063c2f92`. The complete run uses all **6,288** practice/holdout tasks, 13 paired trials, 2,000 bootstrap samples, and **163,488** raw rows. All **176,064** before/after timing checks pass.

| Task set | Overall speed | 95% range | Clearly faster | Large slowdowns |
| --- | ---: | ---: | ---: | ---: |
| Practice (3,144) | 1.651× | 1.628–1.674× | 2,848 | 5 |
| Holdout (3,144) | **1.683×** | **1.660–1.705×** | **2,931** | **0** |
| All (6,288) | 1.667× | 1.651–1.683× | 5,779 | 5 |

The targeted holdout families improve broadly on the identical frozen tasks:

| Kind of task | Previous | Current | Clearly faster | Large slowdowns |
| --- | ---: | ---: | ---: | ---: |
| Quoted comma-separated fields | 0.736× | **3.316×** | 1/1 | 0 |
| Lazy empty alternatives | 0.965× | **2.818×** | 48/48 | 0 |
| Empty-position iterator | 0.929× | **2.306×** | 32/32 | 0 |
| Readable formatted field | 1.137× | **3.113×** | 1/1 | 0 |
| Verbose/multi-line patterns | 1.934× | **2.557×** | 32/32 | 0 |
| Structured text | 1.486× | **1.681×** | 32/32 | 0 |
| Text scanners | 1.033× | **1.227×** | 24/32 | 0 |
| Byte scanners | 1.035× | **1.255×** | 27/32 | 0 |
| Windowed captured fields | 0.992× | **1.287×** | 34/48 | 0 |
| Email-like values | 0.917× | **1.186×** | 1/1 | 0 |

![Zig speed across all balanced holdout families](zig-exec-v5-family.svg)

The separate successful-match control passes all **192** checks and reaches **1.061×** on its 48 unseen hits (1.054–1.068×), clearly faster on 42, with zero large slowdowns. Its **1,248** raw rows and summary are [here](zig-exec-match-hit-summary.json). The capture-returning core passes **5,214** checks and reaches **3.454×** overall across eight paired tasks; every task is faster. The complete result is [zig-exec-capture-perf.json](zig-exec-capture-perf.json).

Temporary memory is at or below Python `re` on **3,014/3,144** unseen tasks; medians are **864 B** for Zig and **2,046 B** for stdlib. Compiled programs use **18,608–47,588 B**, median **23,316 B**, across all 6,288 tasks.

![Zig temporary memory across the expanded holdout](zig-exec-v5-memory.svg)

![Compiled Zig program memory across the expanded holdout](zig-exec-program-memory.svg)

![Zig wins and losses across the expanded holdout](zig-exec-v5-regressions.svg)

There are no holdout tasks below 0.8×. The generated [large-slowdown report](zig-exec-regressions.md) confirms that no result is omitted or reclassified. Short module-level searches and literal calls remain close to the baseline and are useful targets for later boundary work.

The correctness-gated executor profile explains the changes. Median calls/steps fall **12/268→0/0** for quoted fields, **7/119→0/0** for readable fields, **26/55→0/0** for excluded-prefix words, **8/52→0/0** for scanners, **4/48→0/0** for windowed fields, and **102/241→0/0** for empty iterators. Lazy empty alternatives fall **672 capture calls, 3,064 steps, 684 splits → 0 capture calls, 763 steps, 80 splits**. Complete rows and counters are [zig-exec-profile.json.gz](zig-exec-profile.json.gz).

## Correctness and safety

The release build passes **8,244/8,244** expanded cases, **35,840/35,840** unseen correctness cases, **6,288/6,288** expanded performance tasks, all **144/144** runnable official CPython methods, **109,848/109,848** established focused checks, **190/190** public-surface comparisons, **163,960/163,960** dispatch comparisons, and **156,484/156,484** new executor comparisons. The new probe's stdlib-vs-stdlib control passes **20,292/20,292** checks. There are zero unexplained mismatches, crashes, or timeouts.

Zig Debug plus AddressSanitizer/UndefinedBehaviorSanitizer passes **142,982** frozen/focused checks, including **78,660** executor and **41,080** dispatch checks. Both production-source audits report zero forbidden markers or blocked calls. The objective remains unchanged; `GOAL.md` SHA-256 is `e5935060b44fe5f6b4e19ac2d01f3ce63182cf6a1d3b416502a4441cde345b62`.

## Pilots and rejected designs

Each pilot uses all **6,288** tasks, five paired trials, **62,880** rows, and **75,456** correctness checks. The complete raw rows and summaries are in [zig-exec-pilots.tar.gz](zig-exec-pilots.tar.gz). Short pilots vary; the 13-trial final run above is the headline result.

| Experiment | Holdout speed | 95% range | Clearly faster | Large slowdowns |
| --- | ---: | ---: | ---: | ---: |
| Current-code baseline | 1.619× | 1.595–1.641× | 2,713 | 34 |
| Short index conversion — rejected | 1.603× | 1.579–1.624× | 2,711 | 29 |
| CPU-specific build — rejected | 1.645× | 1.620–1.667× | 2,747 | 25 |
| Smaller binary build — rejected | 1.338× | 1.316–1.357× | 2,391 | 192 |
| Portable link-time build — not selected | 1.655× | 1.631–1.678× | 2,740 | 30 |
| Compact lazy empty repeat | 1.633× | 1.610–1.655× | 2,787 | 22 |
| One-character assertion | 1.641× | 1.619–1.663× | 2,810 | 33 |
| Literal assertion | 1.646× | 1.622–1.668× | 2,837 | 32 |
| Run-plus-atom assertion | 1.645× | 1.623–1.666× | 2,820 | 30 |
| Boundary/assertion choice | 1.649× | 1.626–1.670× | 2,823 | 21 |
| Remove unnecessary capture path | 1.643× | 1.619–1.664× | 2,804 | 22 |
| Direct zero-width scan | 1.659× | 1.636–1.681× | 2,834 | 24 |
| Quoted-field recognizer inactive | 1.666× | 1.644–1.688× | 2,811 | 31 |
| Correct internal-flag comparison | 1.661× | 1.638–1.682× | 2,824 | 24 |
| Direct quoted capture | 1.638× | 1.616–1.660× | 2,740 | 20 |
| Direct captured fields | 1.685× | 1.662–1.707× | 2,828 | 9 |
| Direct uncaptured runs | 1.665× | 1.643–1.686× | 2,839 | 7 |
| Direct three-part fields | **1.709×** | **1.687–1.731×** | **2,908** | **2** |

The final raw timing rows are [zig-exec-v5-raw.jsonl.gz](zig-exec-v5-raw.jsonl.gz) (uncompressed SHA-256 `299ee1c1eaddaf776a3df8d62278f5077a7a1073264d0050db5dae33b8b9298c`), with the complete [summary](zig-exec-v5-summary.json), [compiled-memory rows](zig-exec-program-memory.json.gz), and successful-match [raw rows](zig-exec-match-hit-raw.jsonl.gz). Correctness, safety, and audit results are the `zig-exec-*` files in this directory.

Reproduce with:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHON="$PY" sh tools/build_zig_probe.sh
PYTHONPATH=. "$PY" tools/oracle_v3.py verify --module rebar --cohort holdout --output /tmp/zig-correctness.json
PYTHONPATH=. "$PY" tools/cpython_re_oracle.py verify --module rebar --output /tmp/zig-official.json
PYTHONPATH=. "$PY" tools/zig_dispatch_probe.py --module rebar --seeded-cases 16384 --output /tmp/zig-dispatch.json
PYTHONPATH=. "$PY" tools/zig_executor_probe.py --module rebar --seeded-cases 8192 --output /tmp/zig-executor.json
PYTHONPATH=. "$PY" tools/perf_v5.py verify --module rebar --output /tmp/zig-performance-check.json
PYTHONPATH=. "$PY" tools/zig_perf_v5_pilot.py --raw /tmp/zig-performance.jsonl --output /tmp/zig-performance.json --chart /tmp/zig-speed.svg --memory-chart /tmp/zig-memory.svg --regression-chart /tmp/zig-regressions.svg --trials 13 --bootstraps 2000
PYTHONPATH=. "$PY" tools/zig_regressions_report.py --summary /tmp/zig-performance.json --output /tmp/zig-losses.md
```
