# Zig: a smaller match buffer did not produce a speedup

**Outcome: compatibility checks passed; the performance design is REJECTED.** The Zig implementation remained compatible with Python's `re`, but its public practice result does not show that it is faster. The complete **624-case** practice run compared Zig, Rust, and C with Python in the same process. The sealed **24,576-case** final benchmark is **NOT MEASURED** and **NOT ACCESSED**.

| Engine | Overall speed against Python | 95% confidence interval | Clearly faster cases | More than 20% slower |
| --- | ---: | ---: | ---: | ---: |
| C | 1.319119695× | 1.27268333–1.37268864× | 440/624 | 48/624 |
| Rust | 1.146317870× | 1.10018190–1.19147998× | 266/624 | 112/624 |
| Zig | 1.000634803× | 0.95529848–1.04552108× | 225/624 | 242/624 |

Here **1× is Python's speed**. Zig's confidence interval includes **1×**, so the apparent **1.000634803×** result does **not** establish that Zig is faster. Only **225 of 624** Zig cases are clearly faster, while **242** take strictly more than 20% longer. All **402** substantial slowdowns are retained: C **48**, Rust **112**, and Zig **242**. The experiment is rejected as an overall speed improvement, not as a correctness failure.

## What was tried

We reduced the owned Zig bridge's local match-span buffer from **514 to 256 pointer-sized words**: **4,112 bytes to 2,048 bytes**. The independent Zig parser, compiler, matching engine, and Python interface were not replaced or delegated to another package. Patterns with up to **127 capture groups** continue using the smaller stack buffer. Larger patterns retain the checked, exact-size heap fallback; no capture groups or supported patterns were discarded.

Direct inspection of the native machine code shows a genuine structural change. Before this experiment, the `bridge_pattern_match`, `zig_scanner_match`, and `bridge_match` entry points each contained a `sub $0x1000,%rsp; orq $0,(%rsp)` stack-page probe. Their new stack allocations are, respectively, **`0x8f8`**, **`0x868`**, and **`0x8b8`**, with no 4,096-byte page probe at those entries. This demonstrates a change in generated code, **not** a proven cause of any timing difference or an overall Zig speedup.

## Full compatibility was independently checked

The exact changed bridge source is SHA-256 `cb14210092d9ec92a2ac8c458d7b713342c8662bcf3318f954e0c520bc7b1589`; its actually loaded native bridge is SHA-256 `4d1eb307eabc8b254ac0724aeb8ba106105d9879b7d46054b2355621fb330a92`. The owned Zig matcher source remains SHA-256 `4deca5a442cccd02bebfcecd4ceeb73de62a68837c5a3bdadee4dcaf84cf0ee3`; the independently loaded Zig engine remains SHA-256 `70bafca56a3f48477b2011f016a81b625e5f40a772af6a986d32b9098269f614`.

Before timing, that exact implementation passed:

- [223,198 frozen matching checks](../../../candidates/evidence/rust-v8-edge-oracle-zig-deep-stage-12.json.gz).
- [393 Python object and method-behavior checks](../../../candidates/audits/RUST-V8-DEEP-CONTRACT-ZIG-STAGE-12.json.gz).
- [479 observable Python behavior checks](../../../candidates/evidence/rust-v8-observability-zig-qualified-stage-12.json.gz).
- [All 22 stages of the original independent correctness campaign](../../../candidates/evidence/rust-v8-zig-stage-12-sealed-campaign.json), including the complete **4,494,555-case Unicode comparison**, replacement, callbacks, and isolated crash and recursion checks.
- [The original from-scratch source and actually loaded native-library audit](../../../candidates/audits/FROM-SCRATCH-AUDIT.json); SHA-256 `d68a14b5a2c4f181871afbc23c2d6e90150e7eb4752e9d636f035a8ad9cdf796`.

The complete passing campaign has SHA-256 `f89fe9081421d28a291feab1b664c21a7c372762a548569856c6572e4a23eba6`. Its performance field is **NOT MEASURED**; it does not access the final benchmark. Passing compatibility does not convert an inconclusive speed result into a successful performance experiment.

## What the practice run measured

Python and all three qualified candidates were measured in the same run using **624 cases**, **7 paired trials** per case, **4 warmups**, and **499 preselected confidence resamples.** All **17,472 timing rows**, **52,416 correctness checks**, and **402 substantial slowdowns** are recorded. The native-library and source hashes were checked before and after the run.

- [Every public case, confidence interval, and substantial slowdown](three-qualified-engines-public-practice-v4-summary.json); SHA-256 `e23164b077b2bfa1abccaf8cce93a068bc7ea9b7ef444ef55905cc2fbd573e0c`.
- [All original paired observations](three-qualified-engines-public-practice-v4-raw.jsonl.gz); compressed SHA-256 `628b23d7797312fce35436a4709bb278995f1513b381c9cc302ee6caf5bda6fe`; uncompressed SHA-256 `1639451c8167062e0b7d847c969c6a1c4d613e784d86c7ca09044e9786085da0`.

The previous [smaller Rust-buffer experiment](RUST-FINDALL-CAPACITY-16.md) and its [original public measurements](three-qualified-engines-public-practice-v3-summary.json) remain unchanged. The earlier run reported Zig at **1.010909001×**, with **229** clearly faster cases and **232** substantial slowdowns. The new Zig result is **1.000634803×**, with **225** and **242**. These are separate runs. Their results have **no paired confidence interval across runs**, and the difference is not attributed to the source change.

Recorded memory values describe **Python-traced temporary allocations only**. The implementations shared a measurement process. Independently isolated native or whole-process memory for each candidate is **NOT MEASURED**.

## Independent verification and graphs

The following are the exact version-four integrity, self-check-tool, and graph filenames. Linking a destination does not claim it has already been generated or verified. The version-four tools are responsible for their own self-checks; no separate nonexistent self-test reports are implied.

- [Independent verification of every observation and source hash](three-qualified-engines-public-practice-v4-integrity.json).
- [Version-four independent verifier and self-checks](../../../tools/rust_v7_multi_candidate_practice_v4_audit.py).
- [Version-four graph generator and self-checks](../../../tools/rust_v7_multi_candidate_practice_v4_charts.py).
- [Overall speeds and confidence intervals](three-qualified-engines-public-practice-v4-overall.svg).
- [Candidate rankings against Python](three-qualified-engines-public-practice-v4-rankings.svg).
- [Results by regular-expression operation](three-qualified-engines-public-practice-v4-api.svg).
- [Faster, slower, and inconclusive cases](three-qualified-engines-public-practice-v4-outcomes.svg).
- [Every substantial slowdown](three-qualified-engines-public-practice-v4-regressions.svg).
- [Python-traced temporary allocations and memory limitations](three-qualified-engines-public-practice-v4-memory.svg).

Zig design: **CORRECTNESS QUALIFIED; PERFORMANCE REJECTED**. Final **24,576-case** benchmark: **NOT MEASURED**. Final benchmark access: **NOT ACCESSED**. Final winner: **NOT SELECTED**.
