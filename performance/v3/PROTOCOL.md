# Broader performance oracle v3

This oracle expands the performance holdout while preserving every earlier task and result. It compares the pinned, unmodified CPython 3.14.6 `re` module with the three independently written engines. The suite is frozen before tuning or timing; an incorrect task is never measured.

## What is tested

There are **144 tasks**: 72 practice tasks and 72 distinct holdout tasks. Every task has weight 1, so the holdout denominator is always 72. The first 56 records are byte-for-byte identical to the v2 fixture; the other 88 records add 44 balanced practice/holdout pairs.

The earlier tasks cover common calls, text and bytes, compilation and caching, groups/replacements/splitting, iterators and scanners, Unicode, empty matches, references, conditionals, and controlled branches. The new pairs add:

- **15 everyday examples:** request logs, URLs, email-like addresses, dates/times, versions, identifiers, IPv4-like values, paths, configuration lines, comments, whitespace/line cleanup, simple markup, quoted values, and comma-separated fields;
- **11 pattern and matching shapes:** shared-prefix and missing alternatives, nested repeats, multiline records, multi-line blocks, readable/verbose patterns, ASCII and Unicode modes, astral characters, and negative lookarounds;
- **10 API and input shapes:** byte replacement/scanning/views, complex cold compilation, warm module replacement, empty boundaries, dense iteration, optional captures, limited split/replacement;
- **8 boundary and short-call shapes:** four `pos`/`endpos` windows, literal and repeated-template replacement, and quick `match`/`fullmatch` misses.

The exact patterns, inputs, flags, operation counts, weights, and IDs are in [suite.py](suite.py). The fixture is generated twice with stdlib and must be identical. Fixture SHA-256: `f3ab490e351648118e522035c8624976203c777d9c1a7f7d44ad98233f2056bf`.

## How timings are kept honest

Every engine result is checked against the frozen stdlib result immediately before every timed trial. A mismatch, crash, or exception aborts measurement. Nothing incorrect is timed or included in raw data.

- **13 paired trials** per task and **4 untimed warmups** per engine.
- Engine order is shuffled deterministically for each task and trial with seed `1979121403`.
- Garbage collection is disabled only for the timed batch and restored immediately afterward. Time uses `perf_counter_ns`.
- Each trial records traced Python peak memory and process RSS/high-water observations, including boundary costs. Every raw row retains the task, engine, trial, order, operation count, elapsed time, memory, and expected-result digest.
- The complete run contains exactly **7,488 raw rows** (144 tasks × 4 engines × 13 trials); missing or duplicate rows fail analysis.

## How results are summarized

Each task compares paired times as `Python re time / engine time`: **1× means the same speed, higher is faster**. Measured ranges use 5,000 deterministic bootstrap samples with seed `1979121404`. Overall speed combines every task with equal weight using the geometric mean; the denominator cannot change silently.

An engine is clearly faster only when the lower bound of the measured 95% range is above 1×. Every result below 0.8× is reported as a large slowdown. Generated graphs will show the overall comparison, every holdout task, memory, all wins/losses, and rankings.

The success threshold remains: at least **1.5× overall on holdout**, clearly faster on at least **60%** of holdout tasks, zero unexplained correctness failures/crashes/undefined behavior, and an explanation for every slowdown greater than 20%.

## Pre-timing correctness check

The frozen fixture is deterministic, preserves all earlier records, and passes stdlib-vs-stdlib. The first check of all engines completes **568/576 checks** and exposes eight mismatches; the complete result is [initial-correctness.json](evidence/initial-correctness.json).

- All three engines reject the new windowed-scanner calls (`Pattern.scanner(string, pos, endpos)`): two tasks each, six checks total.
- Native C misses the first configuration line under multiline matching in both practice and holdout: two checks.

These are useful compatibility findings, not timing results. **Performance is NOT MEASURED for v3 until these cases and the official CPython correctness gate are clean.**

Reproduce the freeze and checks with:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHONPATH=. "$PY" tools/perf_v3.py freeze
head -n 56 performance/v3/expected.jsonl | cmp performance/v2/expected.jsonl -
PYTHONPATH=. "$PY" tools/perf_v3.py verify --output /tmp/v3-correctness.json
```
