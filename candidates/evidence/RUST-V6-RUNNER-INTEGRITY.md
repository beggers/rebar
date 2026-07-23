# Rust benchmark integrity check

The Rust-only benchmark was verified against the original five-engine measurement before using it to report any optimization. This is a check of existing timing data, not a new performance result.

The verifier reads every **808,080** original raw rows, preserves the frozen **12,432** tasks, extracts exactly **323,232** stdlib/Rust paired rows, and runs the unchanged **13-trial**, **2,000-sample** analyzer. Every individual speed ratio, traced-memory ratio, case denominator, and **11,784** combined large slowdowns agrees with the original. The complete [machine-readable check](rust-v6-runner-integrity.json) preserves the source and extracted-row hashes, exact result counts, all confidence-range details, and each negative test.

| Check | Result |
| --- | --- |
| Archived five-engine rows | 808,080 validated |
| Frozen cases | 12,432/12,432 |
| Extracted Rust/stdlib rows | 323,232/323,232 |
| Rust speed/memory mismatches | 0 |
| Large-slowdown mismatches | 0 |
| Intentionally corrupted inputs rejected | 15/15 |
| Unchanged non-Rust results in merge | 37,296/37,296 |
| Preserved complete engine/task results | 49,728/49,728 |

The original Rust holdout speed is **0.13442162253182238×**; the extracted paired calculation returns **0.1344216225318228×**, agreeing to ordinary floating-point precision. The pinned fixture SHA-256 is `c8e32e879cc7a134748f8f3f29fed49678895745fdecebe63ceec46b6a3b5335`. Extracted paired-raw SHA-256 is `97099e08f9dda95dc02f00cb1feb0ee4d5df0ae98466539630c079671cb2744c`; the original five-engine expanded-raw SHA-256 remains `a6fefab9e97c21e1ea17d258860fd05dbbc9adc3bb2154b66935abe3d3d84907`.

## Important confidence-range difference

The frozen bootstrap algorithm and seed are unchanged, but the original analyzer drew samples for four candidates per case while the Rust-only analyzer draws samples for one. Their random-number streams therefore reach subsequent tasks at different positions. All measured point speeds and memory values remain identical; confidence ranges need not.

For example, the original five-engine Rust holdout range was **0.1343451707–0.1344990799×** with **229** significantly faster cases. Correct Rust-only extraction yields **0.1343443394–0.1345012646×** and **228** significantly faster cases. The single changed significance decision is an escape task near the **1×** boundary, not a missing task or a changed timing. Future Rust results must report the confidence interval and significance counts produced by their own complete paired run.

```sh
PY=/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
PYTHONPATH=. "$PY" tools/rust_perf_v6.py self-test
PYTHONPATH=. "$PY" tools/rust_merge_v6.py --self-test
```

No candidate is selected from this integrity check. Optimized Rust holdout performance remains **NOT MEASURED**.
