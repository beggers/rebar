# Rust native-allocation second checkpoint

This is a diagnostic follow-up to the [first Rust native-allocation checkpoint](RUST-V6-NATIVE-PROFILE.md). It measures the next complete Rust execution and Python-boundary build using the same **137 frozen tasks in 28 workload families**. It does not overwrite the first result and is **not** the 6,216-task holdout ranking.

The new build retains the lazy Rust instruction engine and adds persistent, single-preparation Unicode iterators, a restored direct literal collector, and the combined native Python boundary. All **137/137** outputs agree with pinned CPython 3.14.6. The run records **3,014** correctness checks and observes no change to either native binary during measurement.

## Measured diagnostic results

| Measurement on the same 137 tasks | Original Rust | First rewritten Rust | Second rewritten Rust |
| --- | ---: | ---: | ---: |
| Native allocation calls | 11,279,427 | 31,868 | 26,181 |
| Requested native allocation bytes | 1,902,421,190 | 138,886,574 | 55,390,882 |
| Speed relative to original Rust | 1× | 3.610× | 5.481× |

Relative to the original Rust, the second checkpoint removes **99.77%** of observed native allocations and **97.09%** of requested native-allocation bytes. The **sample-only** five-trial, 2,000-resample running-time range is **4.320–6.975×**; normalized thread CPU is **5.335×**, with range **4.241–6.756×**. These intervals use seed `1985072202` and describe only these 137 diagnostic tasks.

The largest first-checkpoint regression is corrected: dense literal tasks again reach **3.27–3.47×** CPython speed while making exactly one observed native allocation of 3,072 bytes. Wide Unicode iteration also improves: `hold.deeper.combining-wide.07` decreases from **657 allocations and 18,492,823 requested bytes** at the first checkpoint to **16 allocations and 37,792 requested bytes**. The wide-character family improves **84.50×** over the original Rust.

The second checkpoint improves **129/137** sampled tasks over the original Rust. Cold compilation remains faster in each sampled cold-compilation family. All task-level results, allocation counts, timing trials, deterministic diagnostic intervals, family results, and binary fingerprints are preserved in the [second-checkpoint comparison](rust-v6-native-allocator-second-comparison.json).

## Every large remaining regression

Five sampled tasks still run more than 20% slower than the **original Rust engine**. The ratios below compare the second checkpoint with that original engine; values below 1× mean the new Rust is slower on that task.

| Frozen task | Second checkpoint relative to original Rust |
| --- | ---: |
| `hold.deeper.search-long-miss.63` | 0.617× |
| `hold.deeper.search-long-hit.31` | 0.646× |
| `hold.deeper.unicode-word-lines.63` | 0.671× |
| `hold.deeper.unicode-word-lines.31` | 0.741× |
| `hold.deeper.unicode-word-lines.07` | 0.771× |

These are not removed or waived. The two long literal tasks require further boundary and scanning measurements. The Unicode word-line tasks do not have a large allocation problem; their remaining cost is matching, Unicode classification, and line scanning.

Importantly, **96/137** sampled tasks are still more than 20% slower than CPython. Quote collection, source comments, and Markdown remain among the slowest. Some large CSV cases still require approximately **3,147** allocations and approximately **15 MB**. The second checkpoint is progress, **not a fully compatible or statistically qualified winner**.

## Scope and evidence

The allocation counter observes glibc `malloc`, `calloc`, `realloc`, and `free`. It does not count Python objects satisfied by CPython's internal small-object allocator; traced Python memory and execution profiles are recorded separately. Both the original and second-checkpoint measurements use the same 137 task IDs, variation indexes, frozen answers, random order, and five timing trials. The fixture SHA-256 remains `c8e32e879cc7a134748f8f3f29fed49678895745fdecebe63ceec46b6a3b5335`.

- [Original native-allocation baseline](rust-v6-native-allocator-baseline.json).
- [Preserved first rewritten engine](rust-v6-native-allocator-first-vm.json) and [complete first-checkpoint report](RUST-V6-NATIVE-PROFILE.md).
- [Second rewritten engine allocation evidence](rust-v6-native-allocator-second-vm.json): SHA-256 `235a3b23cd1eb44d8a593701859d69bdee496561619708ce8e79ec83ea980c5d`.
- [Complete original-to-second comparison](rust-v6-native-allocator-second-comparison.json): SHA-256 `549f1e9a496614061edfaf5cce7d461556082e2981730453df314df510b8308b`.
- Second-checkpoint engine SHA-256: `01339378bf955b3db816025f2e2e1e4410b5379595802a3b11257bc5092bc706`.
- Second-checkpoint bridge SHA-256: `a4be8246bde010c4b8464da38439a3b18d8150c9667a91a4a7d73922f2ed91dd`.

**NOT MEASURED:** the complete 6,216-case rewritten-Rust holdout; a 13-trial full-holdout confidence interval; final ranking against Zig, native C, or CPython; qualification of all safety, crash, and extended-correctness oracles; and a post-second-checkpoint Python execution profile. Those claims require their own independently completed gates.

## Reproduce

Run from the project root:

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14

cc -std=c11 -O3 -fPIC -shared -Wall -Wextra -Werror \
  tools/rust_native_allocator_v6.c \
  -o /tmp/rebar-rust-native-allocator-v6.so

cp candidates/evidence/rust-v6-native-allocator-baseline.json \
  /tmp/rebar-rust-readonly-allocator-v6.json

LD_PRELOAD=/tmp/rebar-rust-native-allocator-v6.so PYTHONPATH=. \
  "$PY" tools/rust_native_allocator_v6.py families \
  --trials 5 --max-ops 16 --allocation-samples 3 \
  --max-seconds 180 \
  --output /tmp/rebar-rust-native-allocator-current.json

PYTHONPATH=. "$PY" tools/rust_native_allocator_compare_v6.py \
  --before /tmp/rebar-rust-readonly-allocator-v6.json \
  --after /tmp/rebar-rust-native-allocator-current.json \
  --bootstrap-samples 2000 --bootstrap-seed 1985072202 \
  --output /tmp/rebar-rust-native-allocator-current-comparison.json
```

The command profiles whichever Rust binary is currently installed. The comparator refuses changed frozen answers, task selections, denominators, task metadata, failed native allocations, incomplete runs, and binaries that changed during timing.
