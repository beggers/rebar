# Performance oracle v1

Performance is measured only after the three candidate families pass correctness v1.1. The baseline is the unmodified, pinned CPython 3.14.6 `re`; candidates are `candidates.ast_candidate`, `candidates.vm_candidate`, and `candidates.rust_candidate`. No winner is selected during this phase.

## Frozen matrix and weights

The suite has **32 cases**: 16 calibration and 16 holdout. Each cohort covers the same balanced categories with different patterns/subjects: four search cases (hit, miss, long boundary, class/anchor), one `match`, one `fullmatch`, captures/lookarounds, `findall`, `finditer`, `split`, `sub`, callable `subn`, bytes, Unicode, cold compile/call, and warm module call. Every case has weight 1; both cohort denominators are exactly 16. The case IDs, patterns, inputs, flags, operation counts, and weights are frozen in [suite.py](suite.py) and hashed in `manifest.json`.

Representative lifecycles are explicit:

- `compiled`: compile once outside timing and measure the bound operation, including result construction and Python/native boundary cost.
- `module`: exercise the public module-level API with its warm cache.
- `cold`: purge then compile and execute for every operation, including parser/compiler and cache cost.

The holdout is a distinct set of patterns and subjects. It is not used to guide candidate design or optimization before its first measurement.

## Correctness and protocol

`freeze` records a normalized result for every case using stdlib in an isolated baseline process and validates deterministic regeneration. `verify` checks every candidate against these exact values before timing. `measure` repeats that check immediately before each timed case; a mismatch, crash, or exception aborts measurement, so no invalid timing enters the raw data.

The frozen trial protocol is:

- 9 paired trials per case, 2 untimed warmups per module, fixed case-specific operation counts.
- Candidate/baseline order is deterministically shuffled for each `(case, trial)` with seed `1979120921`; every module receives identical inputs and operation counts.
- Garbage collection is disabled only during a timed batch and restored immediately afterward. Wall-clock time is `perf_counter_ns`.
- One correctness-gated operation is measured with `tracemalloc` per trial for Python peak bytes. `/proc/self/status` records RSS/HWM snapshots to expose native/boundary memory effects; these are reported as observations, not precise per-operation allocations.
- Raw JSONL contains every case, module, trial, order, operation count, elapsed nanoseconds, peak traced bytes, RSS/HWM, and the frozen expected digest. No rows are discarded.

## Analysis and success test

For each candidate/case, analysis uses the paired ratio `stdlib_ns / candidate_ns` and a deterministic 95% percentile-bootstrap confidence interval (2,000 resamples, seed `1979120922`). The cohort score is the weighted geometric mean of all case ratios; its interval preserves case weights and pairing. A case is statistically faster only when its lower confidence bound is greater than 1. Regressions greater than 20% are every case with speedup below 0.8 and are listed without filtering. Memory, speed/confidence, regressions, and rankings are generated from raw data.

The objective's success thresholds are evaluated only after optimization/falsification: holdout geomean at least 1.5x, statistically faster on at least 60% of all holdout cases, zero unexplained correctness failures/crashes/UB, and an explanation for every regression greater than 20%.
