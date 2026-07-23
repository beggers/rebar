# Rust: fewer steps between Python and the matcher

This is a result from the **624-case public practice test**, not the final speed test. Rust, C, Zig, and Python's unchanged `re` were measured together in the same run after their regular-expression engines passed the frozen compatibility checks. The sealed **24,576-case** final benchmark is **NOT MEASURED** and has **NOT BEEN ACCESSED**.

| Engine | Overall speed against Python | 95% confidence interval | Clearly faster cases | More than 20% slower |
| --- | ---: | ---: | ---: | ---: |
| C | 1.3155× | 1.2688–1.3708× | 428/624 | 49/624 |
| Rust | 1.1362× | 1.0897–1.1834× | 252/624 | 112/624 |
| Zig | 1.0034× | 0.9575–1.0496× | 230/624 | 240/624 |

Here **1× means the speed of Python's `re`**; a larger number is faster. The interval describes each candidate's comparison with Python **within this run**. It is not a comparison between candidates or between separate experiments. All **401 substantial slowdowns** are included: C 49, Rust 112, and Zig 240. The unchanged definition is a task taking **strictly more than 20% longer** than Python.

## What changed

The Rust regular-expression parser, compiler, matching engine, and public Python module did not change. The small, from-scratch change is in the bridge between Python and Rust: pattern attributes needed for a call are gathered together, safely cached when eligible, and passed directly to the existing native operations. This reduces repeated Python attribute lookups, temporary argument construction, and indirect calls. Ordinary Python-compatible method binding, positional and keyword arguments, error handling, object lifetimes, match objects, iteration, scanners, splitting, and replacement remain subject to the full frozen test suite.

This is our own implementation. It does not call Python's regular-expression engine, wrap another regular-expression package, or delegate matching to the C or Zig candidates. The [independent from-scratch and native-library audit](../../../candidates/audits/FROM-SCRATCH-AUDIT.json) has SHA-256 `ee98f2098223585e4cc3d484d97d36a33c358ccdfd133e6db78c8dad89d1a355`.

## Compatibility before measurement

The measured Rust source and native library passed:

- [223,198 frozen matching checks](../../../candidates/evidence/rust-v7-edge-oracle-rust-fused-vectorcall.json.gz).
- [393 Python object and method-behavior checks](../../../candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-FUSED-VECTORCALL.json.gz).
- [479 observable Python behavior checks](../../../candidates/evidence/rust-v8-observability-rust-qualified-fused-vectorcall.json.gz).
- [All 22 compatibility stages](../../../candidates/evidence/rust-v8-rust-fused-vectorcall-sealed-campaign.json), including the full **4,494,555-case Unicode comparison**, replacement and callback behavior, and crash and recursion checks.

The 22-stage report has SHA-256 `d54d11835e6fd1d4b6bf81d6bdd9f72d219265fbd48142cb923274bf5b6f681e`. None of those correctness runs accessed or timed a final benchmark.

## What the practice result actually measured

All four implementations used the same **624 public cases**, **7 paired trials** per case, **4 warmups**, and **499 preselected confidence resamples.** The run records **17,472 timing rows** and **52,416 correctness checks**. The measured Rust bridge source is SHA-256 `88a8a6b086061da69022a978eba3a0f0317a378f0a758c44ec84fb9c1c0b3c65`; its actually loaded native bridge is SHA-256 `8a413cce5dde126fbcdeba269a4ee766f20ba80396db460a160864df4d8c6434`. Both were checked before and after measurement.

- [Every public case, confidence interval, and slowdown](three-qualified-engines-public-practice-v2-summary.json); SHA-256 `db3cc7f4704df7b0a6b1283818d0dfdf96947d83d44752bf633a640a3e721cab`.
- [All recorded same-run observations](three-qualified-engines-public-practice-v2-raw.jsonl.gz); compressed SHA-256 `81b1a8c99f8f460539d9b212127d2ba9c76720987d4dde49c5c0186f31c05e76`.

The older, separately recorded [practice run](three-qualified-engines-public-practice-v1-summary.json) reported **1.121192×** for Rust and **139** substantial Rust slowdowns. The new run reports **1.136192×** and **112**. Both results remain available. Because these are different measurement runs, the difference has **no paired confidence interval** and is not presented as proof that the code change alone caused the difference.

Temporary Python allocation measurements do not isolate each engine's native memory: the four implementations share a measurement process. Independent total native-memory comparisons are **NOT MEASURED**.

## Independent verification and charts

The independent verifier checks all five native libraries, replays all **17,472** timing rows, recomputes all **1,875** confidence intervals, preserves all **401** slowdowns, and passes **44** synthetic corruption controls. The chart generator passes **45** additional controls and produces all six views directly from the verified same-run data. Neither verification tool runs a regular-expression engine or opens the final benchmark.

- [Independent check of all recorded cases and source hashes](three-qualified-engines-public-practice-v2-integrity.json).
- [Verifier and 44 reproducible self-checks](../../../tools/rust_v7_multi_candidate_practice_v2_audit.py).
- [Chart generator and 45 reproducible self-checks](../../../tools/rust_v7_multi_candidate_practice_v2_charts.py).
- [Overall speeds and confidence intervals](three-qualified-engines-public-practice-v2-overall.svg).
- [Candidate rankings against Python](three-qualified-engines-public-practice-v2-rankings.svg).
- [Results by Python operation](three-qualified-engines-public-practice-v2-api.svg).
- [Faster, slower, and inconclusive cases](three-qualified-engines-public-practice-v2-outcomes.svg).
- [All substantial slowdowns](three-qualified-engines-public-practice-v2-regressions.svg).
- [Python-traced temporary allocations and their limitations](three-qualified-engines-public-practice-v2-memory.svg).

Final **24,576-case** benchmark: **NOT MEASURED**. Final benchmark access: **NOT ACCESSED**. Final winner: **NOT SELECTED**.
