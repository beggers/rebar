# Expanded performance holdout v5

This version expands the performance comparison to **3,144 unseen holdout tasks** and **3,144 matching practice tasks**. All **2,448** v4 records are preserved byte-for-byte; the **3,840** new tasks add **40** everyday workload families with **48** deterministic variations in each set. Every task has weight 1, so the holdout denominator is always **3,144**. Performance was **NOT MEASURED** in the freeze chunk; the first fully gated result is recorded below.

The baseline is the pinned, unmodified CPython **3.14.6** `re` module. The independently written native C, Python, Rust, and Zig engines are included; production code does not wrap or delegate matching to an external package or Python's regex engine. The fixture is generated twice with stdlib and agrees exactly, preserves the complete v4 prefix, and is pinned to the **44,084-case** correctness oracle. Fixture SHA-256: `67a4d07ee260bc58456290d76e040b78ba769d1b63cd3b21f0879daa063c2f92`.

![Expanded performance coverage and pre-timing status](evidence/coverage.svg)

## What is tested

The new holdout covers long present/absent phrases, log/status lines, JSON-like fields, markup, Markdown links, code tokens/comments, URLs/email/IP/versions/dates/numbers/phones/postcodes, text and byte paths, CSV/quoted data, whitespace/newline cleanup, splitting with and without separators, secret redaction, template and callback replacement, multilingual words/case/accents/emoji, ASCII boundaries, byte buffers, lookaround, references, conditionals, atomic/possessive and empty matches, many alternatives, character-set-heavy input, windows, scanners, fresh compilation/module calls, and full match details.

Inputs vary independently between practice and holdout using stable seeds (`1984073111` and `1984073129`). Each family includes short and longer inputs, different result counts, flags and input forms, and representative hits and misses. Long scans reach **32,768** characters; collection cases range from one to dozens of results. The exact patterns, inputs, flags, operation counts, weights, and stable IDs are in [suite.py](suite.py).

Across all **6,288** tasks there are **826** `search`, **138** `match`, **140** `fullmatch`, **1,652** `findall`, **1,716** `finditer`, **296** `split`, **510** `sub`, **420** `subn`, **262** scanner, **164** compile, **66** escape, and **98** detailed-match tasks. Lifecycles include **5,764** compiled calls, **198** module-level calls, and **326** fresh compilations/searches; **539** tasks use bytes, bytearray, or memoryview.

## How timings are kept honest

Every engine result is compared with the frozen stdlib output immediately **before every timed trial** and the final result is checked again **after every timed batch**. A mismatch, crash, or exception stops measurement. Nothing incorrect is timed or included in a summary.

- **13 paired trials** and **4 untimed warmups** for every task and engine.
- Engine order is shuffled deterministically for each task/trial with seed `1984073101`.
- Garbage collection is disabled only for the timed batch and restored immediately afterward. Time uses `perf_counter_ns`.
- Every raw row records task, engine, trial, order, operation count, elapsed time, traced Python peak memory, process RSS/high-water observations, and the expected-result digest, including Python/native boundary costs.
- A complete run contains exactly **408,720 raw rows** (6,288 tasks × 5 engines × 13 trials). Missing, duplicate, incorrect, or mismatched rows fail analysis.

## How results are summarized

Each task compares paired times as `Python re time / engine time`: **1× means the same speed; higher is faster**. Measured ranges use **2,000** deterministic bootstrap samples with seed `1984073102`. Overall speed combines every task with equal weight using the geometric mean. An engine is clearly faster only when the lower end of the measured 95% range is above 1×. Every result below 0.8× is kept and reported as a large slowdown.

The success threshold remains: at least **1.5× overall on holdout**, clearly faster on at least **60%** of holdout tasks, zero unexplained correctness failures/crashes/undefined behavior, and an explanation for every slowdown greater than 20%.

## Pre-timing correctness check

The fixture is deterministic, preserves all earlier records, and passes stdlib-vs-stdlib twice. The pre-timing check of stdlib and all four independent engines completes **31,440/31,440** comparisons with zero failures; the complete result is [initial-correctness.json](evidence/initial-correctness.json). The [six source/import delegation audits](evidence/delegation-audit.jsonl) report zero forbidden markers or blocked imports and all smoke checks pass.

## Initial expanded result

The first full paired run retains all **408,720** correctness-gated rows in [initial-raw.jsonl.gz](evidence/initial-raw.jsonl.gz), decompressed SHA-256 `c905fa024c5ee6990cf4af7145af9a06432e9f22667e434c728e571de6334308`, and every result/slowdown in [INITIAL.md](evidence/INITIAL.md). The independent [post-run check](evidence/final-correctness.json) again passes **31,440/31,440** comparisons. Native C reaches **1.3507x** on the **3,144-task** holdout (1.3494--1.3520x), is clearly faster on **2,482/3,144 (79%)**, and has **226** large holdout slowdowns; it no longer reaches the 1.5x overall target. Zig reaches **0.4807x** (370 clearly faster, 2,486 losses), Rust **0.1492x** (167 clearly faster, 2,948 losses), and Python **0.0241x** (86 clearly faster, 3,021 losses). The [plain-language notes](evidence/INITIAL-NOTES.md), readable graphs, eight correctness-checked native profiles, memory observations, every interval, and all **17,416** practice/holdout slowdowns are retained.

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHONPATH=. "$PY" tools/perf_v5.py freeze
head -n 2448 performance/v5/expected.jsonl | cmp performance/v4/expected.jsonl -
PYTHONPATH=. "$PY" tools/perf_v5.py verify --output /tmp/v5-correctness.json
PYTHONPATH=. "$PY" tools/perf_v5.py measure --output /tmp/v5-raw.jsonl
PYTHONPATH=. "$PY" tools/perf_v5.py analyze --input /tmp/v5-raw.jsonl --output /tmp/v5-summary.json
```
