# Zig allocation, execution, and Python-boundary optimization

The from-scratch Zig engine is now almost three times faster on the expanded holdout than its previous complete version. It stays fully compatible, reduces compiled memory, and moves many common workloads ahead of Python `re`. Every regression and rejected experiment remains available.

![Overall speed compared with Python re](zig-opt-overall.svg)

![Zig speed across all balanced holdout families](zig-opt-v5-family.svg)

## Headline result

The full paired rerun covers **3,144 practice + 3,144 unseen holdout tasks**, the frozen operation counts, 13 trials, memory, and **163,488** timing rows. Every result is checked before and after timing.

| Task set | Speed vs Python `re` | Clearly faster | Large slowdowns |
| --- | ---: | ---: | ---: |
| Practice | 1.364× (1.341–1.388×) | 2,248/3,144 | 288/3,144 |
| Holdout | **1.381× (1.358–1.403×)** | **2,290/3,144 (73%)** | **259/3,144** |
| All | 1.372× (1.357–1.388×) | 4,538/6,288 | 547/6,288 |

The previous complete Zig result was **0.462×** on the same holdout. This is a **2.99× improvement**, but still below the experiment's 1.5× overall target. Bytes replacement now reaches **1.59×**, generated replacement workloads **1.19–1.38×**, generated splitting **2.14×**, generated scanners **1.14×**, and long literal searches **2.07×**. Short calls, references, verbose/lazy matching, many alternatives, and result-heavy scanning remain the main losses.

[Every one of the 259 large holdout slowdowns](zig-opt-regressions.md) is listed with its range, median time, and cause. Nothing was removed or reclassified.

## What changed

The optimization began by reading the regular-expression implementation bundled in the configured Zig distribution (musl's TRE source) and Zig's arena-allocation code. TRE pools compiler allocations, keeps one contiguous per-operation workspace, and separates paths that do and do not need captures. Those are useful allocation patterns; **none of its code or API is called or linked**. The parser, compiler, executor, character rules, result types, and bridge here remain independently written.

- The executor now compiles compact runs for all safe, flattenable repeat atoms, caches exact ASCII class membership, scans repeated literals/classes/dots directly, skips to a unique first byte, and avoids the capture executor when no captures are needed. Active captures and lookaround copies are right-sized. Packed backtracking/capture state and stack-first growth reduce the normal matching frame from roughly **2.1 MB to 20 KB** while retaining safe growth for deep expressions.
- A small, uncorrelated second-byte filter replaces the expensive full prefix-pair table. The program header falls **25,800→17,640 B**; measuring all **6,288** tasks gives **18,600–47,580 B**, median **23,308 B**, down from **30,966 B** and far below the original fixed **423,960 B**.
- A dependency-free native bridge now builds real match objects, validates calls/windows, handles immutable and writable buffers correctly, batches immutable iterators/scanners, performs Unicode and byte replacement construction directly, runs callbacks in one native loop, and returns compiler metadata in one crossing. Byte replacements use one exact-size output allocation instead of many fragments. Warm templates and module-cache hits avoid repeated Python validation and rescanning.
- Exact one-byte-kind literal search uses `memmem`. This removes a measured pathological long-text case in the generic Unicode finder: the affected 8–32 KB searches improve from tens of microseconds to hundreds of nanoseconds while preserving Unicode and window behavior. Literal replacement uses its own native path.

The capture-only control reaches **3.14×** overall (seven paired trials); structured, URL, line, and conditional captures are **3.55–5.29×**. Its one remaining clear loss is alternatives (**0.614×**), consistent with the full-holdout branch results.

![Compiled Zig program memory across the expanded holdout](zig-opt-program-memory.svg)

## Correctness and safety

Zig passes **8,244/8,244** expanded cases, **35,840/35,840** unseen correctness cases, **6,288/6,288** performance tasks, **144/144** runnable official CPython methods, and all **109,848** focused checks covering large programs/sets/groups, syntax, nullable/long repeats, lookbehind/references, exact errors, scoped flags, every Unicode code point, spans, and captures. Debug, address, and undefined-behavior checks pass **21,457/21,457** additional comparisons. Static/import/linkage audits report zero delegation or forbidden symbols; production links only the local Zig engine and C runtime.

The gates found and fixed three real optimization regressions, preserved in [the findings record](zig-opt-found-findings.json): 21 unsafe assertion-repeat flattenings, two stale writable-buffer scanner sequences, and four official resize/type/verbose boundary cases. An additional 63 cross-API invalid-subject comparisons match CPython exactly. There are zero unexplained mismatches, crashes, timeouts, or sanitizer findings.

![Zig correctness coverage](zig-opt-correctness.svg)

## Experiments and rejected paths

The correctness-gated pilot sequence used the same **6,288** tasks, five paired trials, and **75,456** checks per run. Its complete raw rows and summaries are in [zig-opt-pilots.tar.gz](zig-opt-pilots.tar.gz).

| Experiment | Holdout speed | Clearly faster | Large slowdowns |
| --- | ---: | ---: | ---: |
| Initial native boundary | 0.486× | 249 | 2,633 |
| Boundary batching | 0.492× | 254 | 2,635 |
| General compact runs | 0.509× | 250 | 2,615 |
| Safe compact runs | 0.542× | 393 | 2,453 |
| ASCII membership cache | 0.630× | 651 | 2,076 |
| Smaller stack workspace | 0.636× | 623 | 2,061 |
| Native match objects | 0.689× | 727 | 1,884 |
| Native match refinements | 0.738× | 845 | 1,724 |
| Native pattern calls | 0.820× | 943 | 1,518 |
| Batched iterator/scanner | 0.887× | 1,084 | 1,305 |
| Guard allocation | 0.885× | 1,083 | 1,350 |
| No-capture path | 0.886× | 1,090 | 1,308 |
| Smaller capture workspace | 0.997× | 1,462 | 828 |
| Unicode output writer | 1.012× | 1,521 | 806 |
| Native callback loop | 1.052× | 1,652 | 656 |
| Remove full prefix table | 1.129× | 1,674 | 685 |
| Small prefix filter | 1.117× | 1,670 | 647 |
| Group prefix control | 1.136× | 1,696 | 649 |
| Direct repeat scanning | 1.234× | 1,972 | 505 |
| Surface refinements | 1.231× | 1,961 | 489 |
| Recursive literal choice — rejected | 1.226× | 1,900 | 531 |
| Packed state | 1.223× | 1,931 | 521 |
| Smaller packed state | 1.229× | 1,944 | 524 |
| Flat literal choice — rejected | 1.181× | 1,858 | 588 |
| Wide direct runs | 1.237× | 1,943 | 514 |
| Exact-size replacement | 1.261× | 1,999 | 467 |
| Native boundaries and fast literal search | **1.390×** | **2,278** | **260** |
| Lazy-repeat shortcut — rejected | 1.384× | 2,262 | 216 |
| Branch-first shortcut — rejected | 1.368× | 2,224 | 258 |

Both literal-choice architectures and the branch/lazy shortcuts were correctness-clean in their pilots but made the broader workload mix slower. They are removed. The profile in [zig-opt-profile.json.gz](zig-opt-profile.json.gz) explains why: generated alternatives take a median **78 splits/199 steps** per call, nullable work **684 splits/3,064 steps**, scanners **46 splits/256 steps**, and email collection **229 class checks**. Optimizing a single branch shape at the cost of every executor dispatch did not pay off.

## Detailed graphs and evidence

![Zig temporary memory across the expanded holdout](zig-opt-v5-memory.svg)

![Where Zig wins and loses across the expanded holdout](zig-opt-v5-regressions.svg)

The full raw timing rows are [zig-opt-v5-raw.jsonl.gz](zig-opt-v5-raw.jsonl.gz) (uncompressed SHA-256 `de1588f45afdcb72adb111717955c4eaf25c46644073a3ffff389e8e7c22b5e5`), with the complete summary in [zig-opt-v5-summary.json](zig-opt-v5-summary.json), compiled-memory rows in [zig-opt-program-memory.json.gz](zig-opt-program-memory.json.gz), and the capture result in [zig-opt-capture-perf.json](zig-opt-capture-perf.json). Correctness, safety, and audit results are the `zig-opt-*` files in this directory.

Reproduce with:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHON="$PY" sh tools/build_zig_probe.sh
PYTHONPATH=. "$PY" tools/oracle_v3.py verify --module candidates.zig_candidate --cohort holdout --output /tmp/zig-correctness.json
PYTHONPATH=. "$PY" tools/cpython_re_oracle.py verify --module candidates.zig_candidate --output /tmp/zig-official.json
PYTHONPATH=. "$PY" tools/perf_v5.py verify --module candidates.zig_candidate --output /tmp/zig-performance-check.json
PYTHONPATH=. "$PY" tools/zig_program_memory_probe.py --output /tmp/zig-program-memory.json
PYTHONPATH=. "$PY" tools/zig_perf_v5_pilot.py --raw /tmp/zig-performance.jsonl --output /tmp/zig-performance.json --chart /tmp/zig-speed.svg --memory-chart /tmp/zig-memory.svg --regression-chart /tmp/zig-regressions.svg --trials 13 --bootstraps 2000
PYTHONPATH=. "$PY" tools/zig_regressions_report.py --summary /tmp/zig-performance.json --output /tmp/zig-losses.md
PYTHONPATH=. "$PY" tools/zig_headline_chart.py --initial performance/v5/evidence/initial-summary.json --zig /tmp/zig-performance.json --output /tmp/zig-overall.svg
```
