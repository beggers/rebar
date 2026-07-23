# Zig experiment: fix Unicode and expose extreme-input failures

Zig is an independently written regular-expression engine. This change does not wrap Python `re`, another candidate, or an external regular-expression package. It does not access or measure the hidden **24,576-case** final test.

The previous Zig version recorded [308 differences](rust-v8-zig-stage-07-extended-path-failures.json.gz) on Python's frozen extended tests. Its Unicode character comparison was already correct, but two initial-character filters could skip a high-Unicode case-insensitive character that is equivalent to an ordinary byte. Both filters now use the Zig engine's own Unicode-aware character comparison.

| Frozen compatibility check | Result |
| --- | ---: |
| Extended Python behavior | [72,248/72,248](rust-v8-zig-stage-08-extended-path-failures.json.gz) |
| Difficult repeat patterns | [39,512/39,512](rust-v8-zig-stage-08-repeat-motif-controls.json) |
| Matching and search | [223,198/223,198](rust-v8-edge-oracle-zig-deep-stage-08.json.gz) |
| Parser and pattern errors | [20,480/20,480](rust-v7-grammar-zig-v8-deep-stage-08.json.gz) |
| Objects and lifetimes | [393/393](../audits/RUST-V8-DEEP-CONTRACT-ZIG-STAGE-08.json.gz) |
| Tracing and unusual arguments | [479/479](rust-v8-observability-zig-qualified-stage-08.json.gz) |
| Replacements and callbacks | [8,862/8,862](rust-v8-replacement-zig-stage-08-from-scratch-failures.json.gz) |
| Deeper replacements and callbacks | [11,266/11,266](rust-v8-replacement-zig-stage-08-from-scratch-deep-failures.json.gz) |

The [complete one-shot 22-stage campaign](rust-v8-zig-stage-08-sealed-campaign-failure.json) nevertheless fails its isolated extreme-input safety check:

| Frozen failing category | Actual failures |
| --- | ---: |
| Deep nesting | 8 |
| Reversed surrogate ranges | 8 |
| Seeded malformed patterns | 3 |
| Extreme repetition | 2 |
| Allocation boundary | 1 |
| Total | 22/254 |

The genuine campaign records **three native crashes**, **zero timeouts**, and **zero** standard-Python self-test failures. Its unchanged safety runner emitted aggregate category totals, not individual failing cases; individual failed-case records are **NOT MEASURED**. The campaign stopped before its full-Unicode stage, so the full-Unicode result is also **NOT MEASURED**. The failed campaign was not rerun or presented as a pass.

The [current four-engine independence audit](../audits/FROM-SCRATCH-AUDIT.json) verifies the exact Zig source, both loaded Zig libraries, all other engine families, and all **76** anti-delegation controls. The [preceding audit](../audits/FROM-SCRATCH-AUDIT-BEFORE-ZIG-STAGE-08.json) and every original failure remain preserved.

Zig qualification: **FAILED**. Final performance: **NOT MEASURED**. Hidden final test: **NOT ACCESSED**.
