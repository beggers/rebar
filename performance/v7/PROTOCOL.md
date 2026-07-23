# Larger independent performance test

This test asks one question: is a from-scratch replacement really faster than the Python `re` module over a broad range of everyday and difficult uses?

It preserves all **12,432** tasks and exact expected-result bytes from the separately frozen version 6. It then adds **64 new types of work**, each with **64 independently generated practice examples** and **64 independently generated unseen examples**. The result is **20,624 tasks: 10,312 practice and 10,312 unseen**. Every task has the same weight. Existing results are not reclassified or discarded.

The baseline is the unchanged `re` module in the pinned stable **CPython 3.14.6**. The competitors are the independently implemented Python, C, Rust, and Zig replacements. Production matching must not call Python `re`, `_sre`, a third-party regular-expression package, or another candidate. Normal language runtimes, system byte-search primitives, and the project's own Python bindings are not regular-expression engines.

The [from-scratch audit](evidence/delegation-audit.jsonl) guards **10** candidate and native source paths against forbidden Python and external-engine imports, exercises each engine while those imports are blocked, verifies Rust's locked offline package has **zero external dependencies**, and inspects both rebuilt Rust libraries for external regular-expression links. All **13** recorded audit checks pass.

## What the larger test includes

The complete patterns and inputs are in [suite.py](suite.py). They cover internet and application logs; programming, data, and configuration formats; short and long searches; success and failure; text and byte buffers; narrow, wide, multilingual, and non-BMP Unicode; accents and case-insensitive matching; ordinary and zero-length matches; named and unnamed captures; word and line boundaries; lookarounds and backreferences; conditional, atomic, and possessive expressions; replacement strings and callbacks; splitting; scanners; match details; bounded input windows; warm module calls; and fresh compilation.

Each practice and unseen family is balanced at exactly **64** tasks. Separate fixed seeds prevent practice inputs from becoming holdout inputs. The older fixture is checked as an exact byte-for-byte prefix. Zero, one, few, and many results; `str`, `bytes`, `bytearray`, and `memoryview`; all **12** established calls; compiled, module-level, and fresh-compile lifecycles; unlimited and limited splits; and zero, one, two, and four permitted replacements are recorded in the frozen manifest.

Seeds alone are not accepted as proof of independence. The fixture rejects any repeated executable scenario within a family and any intersection between the practice and unseen scenarios, ignoring task names and operation counts. An earlier prototype failed this check in **1,216** cases across **19** families; the rejected result is preserved in [the seed-collision audit](evidence/seed-collision-audit.json).

The unseen half must never be used to choose an algorithm, tune a compiler flag, optimize a special pattern, or select a candidate. Development and profiling use independently labeled practice tasks. The complete unseen measurement is made only after the fixture, protocol, and candidate correctness checks have been committed.

## Correctness comes first

CPython generates the entire expected result twice, and both results must agree exactly. The first **12,432** encoded records must exactly equal `performance/v6/expected.jsonl`. The frozen file pins the immutable objective, the **44,084-case** established correctness oracle, Python version, old fixture hash, source hashes, cases, weights, seeds, operation counts, and trial rules.

All five engines must agree with the expected result on all **20,624** tasks before timing. That is **103,120** direct baseline comparisons. Every timed candidate result is checked again immediately before its timed trial and immediately after its timed batch. A mismatch, unexpected exception, crash, missing case, changed denominator, changed result, or changed fixture fails the run.

The larger test does not replace the **35,840-case** correctness holdout, all runnable official CPython `re` tests, focused public-surface checks, sanitizer checks, or zero-delegation audits. Every one of those separate gates still applies.

## Timing and memory rules

- **13 paired trials** and **4 untimed warmups** per task and candidate.
- Candidate order is shuffled by the frozen deterministic task and trial seed.
- The baseline and each candidate receive the exact same pattern, subject, flags, operation count, lifecycle, and Python/native boundary work.
- Each raw row records elapsed time, operations, peak Python-traced memory, process resident memory, process memory high-water mark, trial, order, and frozen expected-result digest.
- The full five-engine run must contain exactly **1,340,560** rows. A separate baseline-versus-Rust rerun must contain exactly **536,224** rows.
- Each task uses **2,000** seeded paired bootstrap samples for its 95% confidence range. Overall speed uses the equally weighted geometric mean of every task in the relevant cohort and the same frozen confidence protocol.
- `1×` means the speed of Python `re`. Larger means faster. A task is counted as clearly faster only when its entire 95% range is above `1×`.
- Every task taking more than **20% longer** than Python remains in the results and graphs. Because speed is `Python time / replacement time`, the exact cutoff is **less than `1 / 1.2`**, approximately **0.83333×**, not `0.8×`. Values of `0.80×`, `0.81×`, and `0.833×` are slowdowns; exactly `1 / 1.2` and `0.84×` are not. No task, failure, regression, memory observation, or candidate may be silently removed.

The original success rule remains unchanged: a fully compatible candidate must be at least **1.5× faster overall** on all **10,312** unseen tasks, be clearly faster on at least **60%** of them, have zero unexplained correctness failures, crashes, or undefined behavior, and explain every slowdown greater than **20%**.

Until a complete, correctness-gated measurement is actually performed, all version-7 candidate speed, confidence, memory, ranking, and slowdown results are **NOT MEASURED**.

## Reproduce

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

PYTHONPATH=. "$PY" tools/perf_v7_seed_audit.py \
  --output performance/v7/evidence/seed-collision-audit.json
PYTHONPATH=. "$PY" tools/perf_v7.py freeze
head -n 12432 performance/v7/expected.jsonl | cmp performance/v6/expected.jsonl -
PYTHONPATH=. "$PY" tools/perf_v7.py self-test
PYTHONPATH=. "$PY" tools/perf_v7.py verify \
  --output performance/v7/evidence/initial-correctness.json
PYTHONPATH=. "$PY" tools/perf_v7_delegation_audit.py \
  --output performance/v7/evidence/delegation-audit.jsonl
PYTHONPATH=. "$PY" tools/perf_v7_coverage.py \
  --result performance/v7/evidence/initial-correctness.json \
  --output performance/v7/evidence/coverage.svg

# Run these only after the frozen protocol and all correctness gates are committed.
PYTHONPATH=. "$PY" tools/perf_v7.py measure --output /tmp/rebar-v7-all-raw.jsonl
PYTHONPATH=. "$PY" tools/perf_v7.py analyze \
  --input /tmp/rebar-v7-all-raw.jsonl --output /tmp/rebar-v7-all-summary.json
PYTHONPATH=. "$PY" tools/rust_perf_v7.py self-test
PYTHONPATH=. "$PY" tools/rust_perf_v7.py measure --output /tmp/rebar-v7-rust-raw.jsonl
PYTHONPATH=. "$PY" tools/rust_perf_v7.py analyze \
  --input /tmp/rebar-v7-rust-raw.jsonl --output /tmp/rebar-v7-rust-summary.json
PYTHONPATH=. "$PY" tools/rust_merge_v7.py --self-test
PYTHONPATH=. "$PY" tools/rust_merge_v7.py \
  --initial /tmp/rebar-v7-all-summary.json \
  --rust /tmp/rebar-v7-rust-summary.json \
  --output /tmp/rebar-v7-combined-summary.json
PYTHONPATH=. "$PY" tools/performance_v7_charts.py \
  --summary /tmp/rebar-v7-combined-summary.json --prefix /tmp/rebar-v7
```
