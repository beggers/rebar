# Fully compatible Rust: sealed-practice starting point

This is not the final speed test. The independently generated **12,288-case** final holdout has not been opened.

The genuine from-scratch Rust engine first passed its complete **22-stage** correctness campaign, all **223,198** frozen matching cases, **20,480** parser cases, **393** object cases, **479** tracing cases, both frozen replacement suites, and **4,494,555** Unicode checks. The pinned Python 3.14.6 baseline and the exact same qualified Rust source and loaded native libraries were then measured on the unchanged **624-case** practice plan.

| Practice-only measure | Fully compatible Rust |
| --- | ---: |
| Overall speed relative to Python | **0.7543×** |
| 95% confidence interval | **0.7225–0.7911×** |
| Clearly faster practice cases | **132/624** |
| Cases taking more than 20% longer | **347/624** |
| Paired trials per case | **7** |
| Correctness checks surrounding measurements | **26,208** |
| Recorded timing rows | **8,736** |

A value below **1×** means slower than Python. The entire confidence interval is below **1×**; this measurement is a negative result, not a speedup or a final-test claim. Every case and slowdown is preserved.

| Operation | Cases | Speed relative to Python | More than 20% slower |
| --- | ---: | ---: | ---: |
| Compile | 48 | 2.420× | 0 |
| Escape | 48 | 0.992× | 0 |
| Find all | 80 | 0.689× | 53 |
| Find iterator | 67 | 0.801× | 40 |
| Full match | 47 | 0.563× | 38 |
| Match | 48 | 0.426× | 48 |
| Match-object access | 48 | 0.313× | 48 |
| Scanner | 48 | 0.749× | 30 |
| Search | 48 | 0.615× | 33 |
| Split | 47 | 0.932× | 19 |
| Replace | 48 | 0.980× | 13 |
| Replace and count | 47 | 0.843× | 25 |

The twelve rows contain exactly **624** cases and **347** substantial slowdowns. Temporary memory remains Python-traced memory, not native Rust process memory. Confidence intervals use the prospectively fixed **499** practice bootstrap samples; the separate final test uses its own fixed **9,999** samples.

The first independently recorded practice attempt used the correct unchanged matching evidence under its version-eight filename. It measured **0.7683×** with **344** substantial slowdowns, but the older architecture-audit tool deliberately accepts only a `rust-v7-edge-oracle-rust-` filename. The matching report was therefore independently regenerated under the required version-seven name; its complete deterministic SHA-256 is identical to the version-eight report. The second complete practice run above is the one whose **39-check** independent architecture, actual loaded-library, all-case, all-confidence, and historical-slowdown audit passes. Both original measurements remain available; separately measured runs are not described as directly paired.

- [Complete certified raw timing rows](rust-v7-calibration-native-heap-certified-baseline-raw.jsonl.gz).
- [Every certified case, confidence interval, and slowdown](rust-v7-calibration-native-heap-certified-baseline-summary.json).
- [Independent 39-control full-result and native-library audit](rust-v7-calibration-native-heap-certified-baseline-integrity.json).
- [Complete first-run raw rows](rust-v7-calibration-native-heap-qualified-baseline-raw.jsonl.gz).
- [Complete first-run summary](rust-v7-calibration-native-heap-qualified-baseline-summary.json).
- [Independently regenerated matching proof](../../../candidates/evidence/rust-v7-edge-oracle-rust-native-heap-qualified.json.gz).
- [Comparison of both corrected Rust architectures](rust-v7-calibration-overall.svg).
- [Every operation](rust-v7-calibration-api.svg).
- [Every faster, slower, and unresolved case](rust-v7-calibration-win-loss.svg).
- [Every slowdown above 20%](rust-v7-calibration-regressions.svg).
- [Python-traced temporary memory](rust-v7-calibration-memory.svg).

Final holdout: **NOT ACCESSED**. Final speed: **NOT MEASURED**.
