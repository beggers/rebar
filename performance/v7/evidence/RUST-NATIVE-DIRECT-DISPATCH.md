# Rust experiment: call the native matcher directly

This is a complete **624-case practice-only** experiment. The **24,576-case** final benchmark has not been created or opened.

When an ordinary compiled Rust pattern receives a valid positional `search`, `match`, or `fullmatch` call, its Python bridge can call the independently written native matcher directly. The previous bridge instead created a temporary argument list, copied the public arguments, called another bridge method, and parsed the already-known search window again. The new path keeps the existing checked pattern attributes, native handle validation, real Python error behavior, match construction, and safe handling of keywords, overrides, subclasses, unusual windows, and unsupported layouts. No regex result is cached; no Python or external regex engine is called.

| Practice result | Previous checked pattern access | Direct native matcher |
| --- | ---: | ---: |
| Overall speed relative to Python | 1.0171× | **1.0257×** |
| 95% confidence interval | 0.9822–1.0540× | 0.9916–1.0635× |
| Clearly faster cases | 237/624 | **241/624** |
| More than 20% slower | 172/624 | **155/624** |
| Match operation | 0.8311× | 0.8851× |
| Match slowdowns over 20% | 26/48 | 11/48 |
| Full-match operation | 0.8873× | 0.9180× |
| Search operation | 0.9936× | 1.0227× |
| Paired trials per case | 7 | 7 |
| Raw timing observations | 8,736 | 8,736 |
| Before-, during-, and after-timing correctness checks | 26,208 | 26,208 |

Each architecture was independently paired against pinned Python 3.14.6; the two architectures were not directly paired against one another. The new overall confidence interval still includes **1×**. This is not a statistically established overall speedup or a final-benchmark result.

| Operation | Cases | Speed relative to Python | Clearly faster | More than 20% slower |
| --- | ---: | ---: | ---: | ---: |
| Compile | 48 | 2.412× | 48 | 0 |
| Escape | 48 | 0.995× | 1 | 1 |
| Find all | 80 | 0.867× | 23 | 31 |
| Find iterator | 67 | 0.923× | 24 | 21 |
| Full match | 47 | 0.918× | 16 | 22 |
| Match | 48 | 0.885× | 0 | 11 |
| Match-object access | 48 | 0.642× | 0 | 24 |
| Scanner | 48 | 0.897× | 6 | 12 |
| Search | 48 | 1.023× | 15 | 19 |
| Split | 47 | 1.170× | 31 | 11 |
| Replace | 48 | 1.254× | 40 | 3 |
| Replace and count | 47 | 1.176× | 37 | 0 |

The original complete-campaign attempt failed honestly because other candidate native libraries changed during its all-engine from-scratch audit; the [entire actual failure](../../../candidates/evidence/rust-v8-rust-native-direct-dispatch-sealed-campaign-failure.json) is preserved. After independently verifying and freezing all four engine families and all **76** malicious controls, one unchanged campaign passes **22/22** actual stages, including all **4,494,555** Unicode comparisons. The **39,000-case** direct replacement suite passes all **13,000** Rust cases and preserves **504** unrelated public-prototype failures. Both replacement suites, all **223,198** matching checks, all **393** object checks, and all **479** tracing and native-independence checks pass.

The [first practice command](rust-v7-calibration-native-direct-dispatch-preflight-failure.json) also failed safely before candidate import or timing because Python's baseline must be explicitly named first. No row or partial measurement was produced. The preserved corrected run explicitly pairs `re` with `candidates.rust_candidate`. An independent audit recomputes all **625** confidence intervals, retains all **155** substantial slowdowns, and rejects **39** deliberate corruption controls.

- [Preserved complete-campaign audit failure](../../../candidates/evidence/rust-v8-rust-native-direct-dispatch-sealed-campaign-failure.json).
- [Complete, successful 22-stage compatibility campaign](../../../candidates/evidence/rust-v8-rust-native-direct-dispatch-sealed-campaign.json).
- [Complete direct replacement matrix and preserved unrelated failures](../../../candidates/evidence/rust-v8-rust-native-direct-dispatch-direct-replacement-controls.json).
- [All standard replacements](../../../candidates/evidence/rust-v8-replacement-rust-native-direct-dispatch.json.gz).
- [All deeper replacements](../../../candidates/evidence/rust-v8-replacement-rust-native-direct-dispatch-deep.json.gz).
- [All frozen matching checks](../../../candidates/evidence/rust-v7-edge-oracle-rust-native-direct-dispatch.json.gz).
- [Native-object, subclass, and lifetime checks](../../../candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-NATIVE-DIRECT-DISPATCH.json.gz).
- [Tracing, unusual arguments, and anti-delegation checks](../../../candidates/evidence/rust-v8-observability-rust-qualified-native-direct-dispatch.json.gz).
- [Preserved failed baseline-first preflight](rust-v7-calibration-native-direct-dispatch-preflight-failure.json).
- [All raw practice timing observations](rust-v7-calibration-native-direct-dispatch-raw.jsonl.gz).
- [Every practice case, confidence interval, and slowdown](rust-v7-calibration-native-direct-dispatch-summary.json).
- [Independent timing, confidence, and loaded-library integrity audit](rust-v7-calibration-native-direct-dispatch-integrity.json).
- [Overall results for all six recorded Rust designs](rust-v7-calibration-overall.svg).
- [Every public operation and design](rust-v7-calibration-api.svg).
- [Every faster and slower practice case](rust-v7-calibration-win-loss.svg).
- [Every slowdown greater than 20%](rust-v7-calibration-regressions.svg).
- [Temporary allocations visible to Python](rust-v7-calibration-memory.svg).

Final performance: **NOT MEASURED**. Final benchmark: **NOT ACCESSED**.
