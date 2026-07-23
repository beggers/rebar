# Rust experiment: reuse native attribute names

This is a complete **624-case practice-only** experiment. The final **12,288-case** holdout has not been opened.

The fully compatible Rust implementation was repeatedly converting the same six Python attribute names at its native method boundary. Its native bridge now interns those six ordinary names once when the owned extension is initialized, then uses genuine Python attribute lookup with the existing object, conversion, error, reference, and garbage-collection semantics. No match result is cached, no test is detected, and no Python or third-party regex engine is used.

| Practice result | Previous fully compatible Rust | Interned native names |
| --- | ---: | ---: |
| Overall speed relative to Python | 0.7543× | **0.9290×** |
| 95% confidence interval | 0.7225–0.7911× | 0.8931–0.9668× |
| Clearly faster cases | 132/624 | **211/624** |
| More than 20% slower | 347/624 | **243/624** |
| Cases | 624 | 624 |
| Paired trials per case | 7 | 7 |
| Raw observations | 8,736 | 8,736 |
| Before-, during-, and after-timing correctness checks | 26,208 | 26,208 |

The improvement is descriptive: the two architectures were measured in separate randomized sessions, each paired directly against Python, not directly against each other. The improved result is still below **1×** and is not called a speedup over Python.

| Operation | Cases | Interned-name speed | More than 20% slower |
| --- | ---: | ---: | ---: |
| Compile | 48 | 2.368× | 0 |
| Escape | 48 | 0.995× | 1 |
| Find all | 80 | 0.844× | 36 |
| Find iterator | 67 | 0.897× | 26 |
| Full match | 47 | 0.822× | 24 |
| Match | 48 | 0.742× | 42 |
| Match-object access | 48 | 0.345× | 48 |
| Scanner | 48 | 0.869× | 19 |
| Search | 48 | 0.922× | 30 |
| Split | 47 | 1.101× | 13 |
| Replace | 48 | 1.188× | 4 |
| Replace and count | 47 | 1.141× | 0 |

All twelve operations, all **260** practice categories, every original slowdown, and all **243** new substantial slowdowns remain recorded. The complete **22-stage** correctness campaign passes all **223,198** matching checks, **393** real-user checks, **479** tracing checks, **8,862** standard and **11,266** deep replacement checks, and **4,494,555** Unicode checks. A separate, fresh **134-check** source and native-library audit independently verifies the exact optimized engine, including **125** deliberately corrupted controls and every original anti-delegation check. The independent performance integrity audit verifies all five actual Rust artifacts, all mapped native libraries, every raw row, all **625** recalculated confidence intervals, and all **39** poisoned-result controls.

- [Complete practice rows](rust-v7-calibration-native-heap-interned-attributes-raw.jsonl.gz).
- [Every practice case, confidence interval, and slowdown](rust-v7-calibration-native-heap-interned-attributes-summary.json).
- [Independent complete performance and native-library audit](rust-v7-calibration-native-heap-interned-attributes-integrity.json).
- [Frozen matching proof](../../../candidates/evidence/rust-v7-edge-oracle-rust-native-interned-attributes.json.gz).
- [Full real-user object proof](../../../candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-INTERNED-ATTRIBUTES.json.gz).
- [Full tracing and unusual-argument proof](../../../candidates/evidence/rust-v8-observability-rust-qualified-interned-attributes.json.gz).
- [Independent 134-check from-scratch source and native-library audit](../../../candidates/audits/RUST-V8-INTERNED-ATTRIBUTES-FROM-SCRATCH.json).
- [Complete 22-stage correctness campaign](../../../candidates/evidence/rust-v8-rust-interned-attributes-sealed-campaign.json).
- [Original and current practice performance](rust-v7-calibration-overall.svg).
- [All twelve public operations](rust-v7-calibration-api.svg).
- [Every faster case and slowdown](rust-v7-calibration-win-loss.svg).
- [Every slowdown over 20%](rust-v7-calibration-regressions.svg).
- [Python-traced temporary memory](rust-v7-calibration-memory.svg).

Final speed: **NOT MEASURED**. Final holdout: **NOT ACCESSED**.
