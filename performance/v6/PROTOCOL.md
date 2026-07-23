# Broader performance holdout v6

This version expands the performance comparison to **6,216 unseen holdout tasks** and **6,216 matching practice tasks**. All **6,288** v5 records are preserved byte-for-byte; the **6,144** new tasks add **48** balanced workload families with **64** deterministic variations in each set. Every task has weight 1, so the holdout denominator is always **6,216**.

The completed five-engine run finds Zig / `rebar` **1.5825×** as fast overall (95% range **1.5812–1.5837×**), clearly faster on **5,333/6,216** holdout tasks, with **243** explained large slowdowns. Native C reaches **1.2830×**, Rust **0.1344×**, and Python **0.0207×**. The readable result, every family, and every Zig slowdown are in [INITIAL.md](evidence/INITIAL.md).

The baseline is the pinned, unmodified CPython **3.14.6** `re` module. The independently written Python, native C, Rust, and Zig engines are included; production code does not wrap or delegate matching to an external package or Python's regex engine. The fixture is generated twice with stdlib and agrees exactly, preserves the complete v5 prefix, and is pinned to the **44,084-case** correctness oracle. Fixture SHA-256: `c8e32e879cc7a134748f8f3f29fed49678895745fdecebe63ceec46b6a3b5335`.

![Broader performance coverage and pre-timing status](evidence/coverage.svg)

## What is tested

The new holdout adds web requests/headers, error stacks, markup/Markdown/SQL/config/source text, shell variables, identifiers/hashes/versions/money/dates/files/paths, quoted CSV/values/email, multilingual/case-folded/accented/emoji/CJK text, non-ASCII and mutable byte buffers, dense collection, empty/boundary positions, chained lookarounds, named references/conditionals, controlled/bounded/shared-prefix alternatives, negative sets, anchors/local modes, long hits/misses, short/full matches, warm module calls, cold compilation, escaping, input windows, scanners, and full match details.

Practice and holdout inputs vary independently with stable seeds (`1985072211` and `1985072229`). Each family includes short and longer inputs, different result counts, flags/input forms, and representative hits and misses. Long scans reach **262,144** characters; collection cases reach hundreds of results. The exact patterns, inputs, flags, operation counts, weights, and stable IDs are in [suite.py](suite.py).

Across all **12,432** tasks there are **1,242** `search`, **330** `match`, **332** `fullmatch`, **3,860** `findall`, **3,572** `finditer`, **424** `split`, **638** `sub`, **676** `subn`, **646** scanner, **292** compile, **194** escape, and **226** detailed-match tasks. Lifecycles include **11,396** compiled calls, **582** module-level calls, and **454** fresh compilations/searches; **987** tasks use bytes, bytearray, or memoryview.

## How timings are kept honest

Every engine result is compared with the frozen stdlib output immediately **before every timed trial** and the final result is checked again **after every timed batch**. A mismatch, crash, or exception stops measurement. Nothing incorrect is timed or included in a summary.

- **13 paired trials** and **4 untimed warmups** for every task and engine.
- Engine order is shuffled deterministically for each task/trial with seed `1985072201`.
- Garbage collection is disabled only for the timed batch and restored immediately afterward. Time uses `perf_counter_ns`.
- Every raw row records task, engine, trial, order, operation count, elapsed time, traced Python peak memory, process RSS/high-water observations, and the expected-result digest, including Python/native boundary costs.
- A complete run contains exactly **808,080 raw rows** (12,432 tasks × 5 engines × 13 trials). Missing, duplicate, incorrect, or mismatched rows fail analysis.

## How results are summarized

Each task compares paired times as `Python re time / engine time`: **1× means the same speed; higher is faster**. Measured ranges use **2,000** deterministic bootstrap samples with seed `1985072202`. Overall speed combines every task with equal weight using the geometric mean. An engine is clearly faster only when the lower end of the measured 95% range is above 1×. Every result below 0.8× is kept and reported as a large slowdown.

The committed streaming analyzer validates all raw IDs, metadata, result digests, and duplicates, then uses a small dependency-free C helper for the exact same seeded draws as Python's `random.Random(seed).randrange(13)`. Its self-test compares draws, task ranges, and overall ranges with the Python reference. This keeps the frozen **2,000-sample** protocol practical without changing any sample or denominator.

The success threshold remains: at least **1.5× overall on holdout**, clearly faster on at least **60%** of holdout tasks, zero unexplained correctness failures/crashes/undefined behavior, and an explanation for every slowdown greater than 20%.

## Pre-timing correctness check

The fixture is deterministic, preserves all earlier records, and passes stdlib-vs-stdlib twice. The pre-timing check of stdlib and all four independent engines completes **62,160/62,160** comparisons with zero failures; the complete result is [initial-correctness.json](evidence/initial-correctness.json). The [six source/import delegation audits](evidence/delegation-audit.jsonl) report zero forbidden markers or blocked imports and all smoke checks pass.

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHONPATH=. "$PY" tools/perf_v6.py freeze
head -n 6288 performance/v6/expected.jsonl | cmp performance/v5/expected.jsonl -
PYTHONPATH=. "$PY" tools/perf_v6.py verify --output /tmp/v6-correctness.json
PYTHONPATH=. "$PY" tools/perf_v6.py measure --output /tmp/v6-raw.jsonl
PYTHONPATH=. "$PY" tools/perf_v6_analyze_fast.py --self-test
PYTHONPATH=. "$PY" tools/perf_v6_analyze_fast.py --input /tmp/v6-raw.jsonl --output /tmp/v6-summary.json
PYTHONPATH=. "$PY" tools/performance_v6_charts.py --summary /tmp/v6-summary.json --prefix /tmp/v6
```

The preserved raw file expands to SHA-256 `a6fefab9e97c21e1ea17d258860fd05dbbc9adc3bb2154b66935abe3d3d84907` and exactly **808,080** rows; the expanded summary SHA-256 is `808e79c4c2ababa56075bfa0c6b059acbab53fb48d2e44d997da59ef75f767fd`. Their deterministic gzip files have SHA-256 `ec5d7f3e77b070cb335d0dc71963a70ee7e1acf9c7daebfb0d6706d7b6b83450` and `22dc707132dea304cc518ea867cfcf4f489f4df9d1d3d336b0dbac9435c20be4` respectively.
