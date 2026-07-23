# Rust experiment: read checked native pattern data directly

This is a complete **624-case practice-only** experiment. The **24,576-case** final benchmark has not been created or opened.

The Rust engine continues to parse, compile, match, and replace using its own implementation. Its Python bridge now reads ordinary compiled-pattern data directly when it has verified that the exact original Python object layout is still valid. It checks the type and its version on every access, verifies the actual member descriptors and their offsets, owns a fresh reference to each value, and safely uses the ordinary Python path for subclasses, changed classes, deleted attributes, and unsupported interpreter builds. It does not retain pattern objects, regex answers, or native handles; it does not import or delegate to a regex engine.

| Practice result | Previous native expansion | Checked direct pattern access |
| --- | ---: | ---: |
| Overall speed relative to Python | 0.9705× | **1.0171×** |
| 95% confidence interval | 0.9376–1.0066× | 0.9822–1.0540× |
| Clearly faster cases | 212/624 | **237/624** |
| More than 20% slower | 230/624 | **172/624** |
| Match-object operation speed | 0.6192× | 0.6261× |
| Match-object slowdowns over 20% | 31/48 | 29/48 |
| Paired trials per case | 7 | 7 |
| Raw timing observations | 8,736 | 8,736 |
| Before-, during-, and after-timing correctness checks | 26,208 | 26,208 |

Each design was independently paired against pinned Python 3.14.6. The two designs were not directly paired against one another. The new overall confidence interval still crosses **1×**, so this result does not establish that Rust is faster overall. It does not predict the unseen final benchmark.

| Operation | Cases | Speed relative to Python | Clearly faster | More than 20% slower |
| --- | ---: | ---: | ---: | ---: |
| Compile | 48 | 2.390× | 48 | 0 |
| Escape | 48 | 1.002× | 0 | 0 |
| Find all | 80 | 0.880× | 27 | 31 |
| Find iterator | 67 | 0.927× | 22 | 21 |
| Full match | 47 | 0.887× | 11 | 22 |
| Match | 48 | 0.831× | 0 | 26 |
| Match-object access | 48 | 0.626× | 0 | 29 |
| Scanner | 48 | 0.908× | 6 | 9 |
| Search | 48 | 0.994× | 14 | 21 |
| Split | 47 | 1.189× | 35 | 11 |
| Replace | 48 | 1.246× | 40 | 2 |
| Replace and count | 47 | 1.166× | 34 | 0 |

The unchanged **39,000-case** direct replacement comparison passes all **13,000** Rust cases and retains **504** genuine failures in a separate public prototype. The Rust engine also passes all **8,862** standard replacements, all **11,266** deeper replacements, all **223,198** frozen matching checks, all **393** object checks, all **479** tracing and argument checks, and its complete **22-stage** compatibility campaign, including **4,494,555** Unicode comparisons. The independent timing audit recalculates all **625** confidence intervals and rejects **39** deliberate raw-data, native-code, hidden-test, denominator, and missing-loss corruptions.

- [Complete direct replacement evidence, including the separate prototype's failures](../../../candidates/evidence/rust-v8-rust-native-slot-fastpath-direct-replacement-controls.json).
- [All standard replacements](../../../candidates/evidence/rust-v8-replacement-rust-native-slot-fastpath.json.gz).
- [All deeper replacements](../../../candidates/evidence/rust-v8-replacement-rust-native-slot-fastpath-deep.json.gz).
- [All frozen matching checks](../../../candidates/evidence/rust-v7-edge-oracle-rust-native-slot-fastpath.json.gz).
- [Native-object and lifetime checks](../../../candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-NATIVE-SLOT-FASTPATH.json.gz).
- [Tracing, unusual arguments, and engine-independence checks](../../../candidates/evidence/rust-v8-observability-rust-qualified-native-slot-fastpath.json.gz).
- [Complete 22-stage compatibility campaign](../../../candidates/evidence/rust-v8-rust-native-slot-fastpath-sealed-campaign.json).
- [All raw timing observations](rust-v7-calibration-native-slot-fastpath-raw.jsonl.gz).
- [Every measured case, confidence interval, and slowdown](rust-v7-calibration-native-slot-fastpath-summary.json).
- [Independent 39-control timing and native-library integrity audit](rust-v7-calibration-native-slot-fastpath-integrity.json).
- [Overall speed of all five recorded Rust designs](rust-v7-calibration-overall.svg).
- [Speed across every operation and recorded design](rust-v7-calibration-api.svg).
- [Every clearly faster and slower case](rust-v7-calibration-win-loss.svg).
- [Every slowdown exceeding 20%](rust-v7-calibration-regressions.svg).
- [Temporary allocations visible to Python](rust-v7-calibration-memory.svg).

Final performance: **NOT MEASURED**. Final benchmark: **NOT ACCESSED**.
