# Rust native-allocation checkpoint

This is a reproducible diagnostic comparison of the original Rust engine with its first rewritten execution engine. It is **not** the full performance result and does not claim Rust is faster than Python's `re` overall.

The comparison uses **137 matched tasks from 28 frozen workload families**, including both cheap and expensive inputs. Every action is checked against the pinned CPython 3.14.6 answer. The original and rewritten Rust libraries are fingerprinted immediately before and after each measurement; neither library changed during its run.

## What the first rewrite improved

| Measurement across the same 137 tasks | Original Rust | First rewritten Rust | Change |
| --- | ---: | ---: | ---: |
| Native allocation calls | 11,279,427 | 31,868 | 99.72% fewer |
| Requested native allocation bytes | 1,902,421,190 | 138,886,574 | 92.70% fewer |
| Relative running time | 1× | 3.610× | 3.610× faster than the original Rust |
| Normalized thread CPU time | 1× | 3.539× | 3.539× faster than the original Rust |
| Sampled tasks improved over original Rust | — | 124/137 | 13 did not improve |

The diagnostic running-time range is **2.900–4.537×** and the normalized thread-CPU range is **2.831–4.413×**, using five paired trials and 2,000 deterministic resamples with seed `1985072202`. These ranges describe only the selected 137 tasks. They are not the confidence intervals for the full 6,216-task holdout.

Selected examples make the cause visible:

| Kind of work | Original native allocations | Rewritten native allocations | Speed improvement over original Rust |
| --- | ---: | ---: | ---: |
| Quoted captures | 484,979 | 2 | 11.57× |
| Unicode case-insensitive matches | 16,286 | 19 | 120.88× |
| Configuration lines | 51,758 | 2 | 23.22× |
| HTML tags | 1,240 | 1 | 28.07× |
| Quoted CSV splitting | 1,261,470 | 3,149 | 3.76× |

The allocation columns in this table are family medians, not totals. The rewritten Rust engine avoids eagerly building and copying every possible match. Case-insensitive Unicode collection prepares the input once instead of rebuilding it separately for each result.

## What was still slower

The first rewrite was **not** a qualified winner. **100/137** sampled tasks still ran more than 20% slower than CPython. Comparing the first rewrite with the original Rust, there were **13** slower tasks, including these **six** slowdowns greater than 20%. Nothing is removed from the denominator.

| Frozen task | Original speed relative to CPython | Rewritten speed relative to CPython | Rewritten speed relative to original Rust |
| --- | ---: | ---: | ---: |
| `hold.deeper.dense-literal-findall.63` | 3.564× | 1.005× | 0.282× |
| `hold.deeper.dense-literal-findall.15` | 3.366× | 1.013× | 0.301× |
| `hold.deeper.dense-literal-findall.07` | 2.956× | 0.925× | 0.313× |
| `hold.deeper.dense-literal-findall.31` | 3.004× | 1.010× | 0.336× |
| `hold.deeper.search-long-miss.63` | 5.233× | 3.060× | 0.585× |
| `hold.deeper.search-long-hit.31` | 0.349× | 0.221× | 0.634× |

Dense literal collection regressed from one native allocation to 12 because the original one-call literal collector was not yet preserved. Wide-character iteration still prepared large subject strings repeatedly: `hold.deeper.combining-wide.07` required **657** native allocations and approximately **18.49 MB**, despite 640 results. CSV splitting still performed approximately **3,149** allocations and requested approximately **14 MB** per long action. Those are remaining optimization targets, not waived results.

Cold compilation improved in every sampled compile family. Median improvements over the original Rust are **1.52×**, **1.58×**, and **1.61×** for expanded, deeper, and large cold-compilation tasks respectively. This diagnostic does not establish final full-holdout compile performance.

## What these measurements do and do not cover

The allocation counter observes glibc `malloc`, `calloc`, `realloc`, and `free`, including allocations made by Rust. CPython can reuse its internal small-object allocator without making a fresh glibc call. Native allocation counts therefore are not a complete measure of Python allocations; the recorded Python traced-memory values must be considered separately.

The measurement contains **28 workload families**, **137** fixed task IDs, five paired timing trials, three allocation samples per engine and case, stable engine ordering, the frozen result hash, and before/after native-binary fingerprints. The sampled variation indexes are `0`, `7`, `15`, `31`, and `63`, where available. The fixture SHA-256 is `c8e32e879cc7a134748f8f3f29fed49678895745fdecebe63ceec46b6a3b5335`.

**NOT MEASURED by this report:** the rewritten Rust engine's speed on all 6,216 holdout tasks; the 13-trial holdout confidence interval; its percentage of statistically faster holdout tasks; its final ranking against Zig, C, or Python; and whether the rewritten engine satisfies every expanded correctness and safety gate. Those claims require the separate complete performance and correctness oracles.

## Preserved evidence

- [Original Rust native allocations](rust-v6-native-allocator-baseline.json): SHA-256 `2a7d3800d340afa1ce5e401fed1a89c31db12b3cb2db2d7163f8db9a8f9d1493`.
- [First rewritten Rust native allocations](rust-v6-native-allocator-first-vm.json): SHA-256 `1e1e71c38f534f707ce11e318a2cb56da28756f2c1aa896cf5f57a79fa54d6cf`.
- [Matched-case comparison, diagnostic confidence intervals, every family, and every regression](rust-v6-native-allocator-comparison.json).
- [Original Python/native execution profile](rust-v6-native-cprofile-baseline.json) and [first rewritten execution profile](rust-v6-native-cprofile-first-vm.json).
- [Live preloaded-allocation self-test](rust-v6-native-allocator-self-test.json) and [safe no-preload self-test](rust-v6-native-allocator-no-preload-self-test.json).
- [Comparator self-test](rust-v6-native-comparator-self-test.json): an exact 1× self-comparison and six deliberate rejections covering changed frozen fixtures, sample selection, denominators, metadata, native-library drift, and duplicate tasks.
- [All-category baseline execution profile](rust-v6-baseline-profile.json): **568** checked inputs covering all **196** frozen holdout categories.

## Reproduce

Run from the project root using the pinned Python:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

cc -std=c11 -O3 -fPIC -shared -Wall -Wextra -Werror \
  tools/rust_native_allocator_v6.c \
  -o /tmp/rebar-rust-native-allocator-v6.so

LD_PRELOAD=/tmp/rebar-rust-native-allocator-v6.so PYTHONPATH=. \
  "$PY" tools/rust_native_allocator_v6.py self-test \
  --output /tmp/rebar-rust-native-allocator-self-test.json

LD_PRELOAD=/tmp/rebar-rust-native-allocator-v6.so PYTHONPATH=. \
  "$PY" tools/rust_native_allocator_v6.py families \
  --trials 5 --max-ops 16 --allocation-samples 3 \
  --max-seconds 180 \
  --output /tmp/rebar-rust-native-allocator-current.json

cp candidates/evidence/rust-v6-native-allocator-baseline.json \
  /tmp/rebar-rust-readonly-allocator-v6.json

PYTHONPATH=. "$PY" tools/rust_native_allocator_compare_v6.py \
  --before /tmp/rebar-rust-readonly-allocator-v6.json \
  --after /tmp/rebar-rust-native-allocator-current.json \
  --bootstrap-samples 2000 --bootstrap-seed 1985072202 \
  --output /tmp/rebar-rust-native-allocator-current-comparison.json

PYTHONPATH=. "$PY" tools/rust_native_allocator_compare_v6.py \
  --before /tmp/rebar-rust-readonly-allocator-v6.json \
  --self-test \
  --self-test-output /tmp/rebar-rust-native-comparator-self-test.json

PYTHONPATH=. "$PY" tools/rust_native_allocator_v6.py python-profile \
  --profile-variant 7 --profile-ops 8 --top 14 \
  --output /tmp/rebar-rust-native-cprofile-current.json
```

The original baseline is preserved in the linked evidence above; rerunning `families` measures whatever Rust binary is currently built. The comparator refuses a changed fixture, cohort, family selection, variation list, case, result metadata, incomplete run, failed native allocation, or a binary that changed during measurement.
