# Expanded performance oracle v2

This oracle compares the unmodified, pinned CPython 3.14.6 `re` module with the three independently written, correctness-qualified engines. It is frozen only after all three pass the expanded 8,244-case correctness suite. No new winner is selected before measurement.

## What is tested

There are **56 tasks**: 28 practice tasks and 28 separate holdout tasks. Every task has weight 1, so each set has a fixed denominator of 28. Practice and holdout cover the same categories with different patterns and inputs:

- finding present, absent, anchored, formatted, captured, empty-position, controlled-branch, named-Unicode, and case-insensitive matches;
- `match`, `fullmatch`, backreferences, conditionals, repeated results, `findall`, `finditer`, splitting, template replacement, callable replacement, scanning, and match-object access/expansion;
- text, bytes, byte arrays, memory views, escaping, cold compilation, cold compile-and-search, warm module calls, and precompiled calls.

The exact patterns, inputs, flags, operation counts, weights, and task IDs are in [suite.py](suite.py). The fixture is generated twice with stdlib and must be identical. Fixture SHA-256: `ec2f7194e8bfb4f5438a61abc3d893e18e5fcada13d2de583801b7e28e7b8f1a`.

## How timings are kept honest

Every engine result is checked against the frozen stdlib result immediately before every timed trial. A mismatch, crash, or exception aborts measurement. Nothing incorrect is timed or included in the raw data.

- **11 paired trials** per task and **3 untimed warmups** per engine.
- Engine order is shuffled deterministically for each task and trial with seed `1979121303`.
- Garbage collection is disabled only for the timed batch and restored immediately after it. Time is measured with `perf_counter_ns`.
- Each trial records traced Python peak memory and process RSS/high-water observations, including boundary costs. RSS observations are useful context, not precise per-call allocation counts.
- Every raw row records the task, engine, trial, order, operation count, elapsed time, memory, and expected-result digest. No rows are discarded.

## How results are summarized

Each task compares paired times as `Python re time / engine time`: **1× means the same speed, higher is faster**. Measured ranges use 3,000 deterministic bootstrap samples with seed `1979121304`. Overall speed combines all tasks with equal weight using the geometric mean; the denominator never changes silently.

An engine is clearly faster on a task only when the lower bound of the measured 95% range is above 1×. Every result below 0.8× is listed as a large slowdown. The generated charts show the overall comparison first, followed by every holdout task, memory, all wins/losses, and rankings.

The success threshold remains: at least **1.5× overall on holdout**, clearly faster on at least **60%** of holdout tasks, zero unexplained correctness failures/crashes/undefined behavior, and an explanation for every slowdown greater than 20%.
