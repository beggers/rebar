# Zig experiment: implement large repeated patterns from scratch

Python can compile patterns such as `(?:ab){4294967294}` without constructing billions of instructions. The previous independent Zig engine [incorrectly rejected this valid pattern](rust-v8-zig-stage-06-extended-path-first-mismatch.json). Its separately written Zig parser, compiler, and execution engine now represent a general fixed-width repeated motif compactly, validate Python's actual maximum repetition, check arithmetic and subject boundaries, and preserve existing capture and search-window behavior. The implementation does not wrap a regex package or call another candidate.

The first three focused attempts honestly exposed two empty-match and unusual-window errors and one repetition-overflow error. All three original failures remain preserved. The corrected engine passes **39,512** targeted comparisons, covering valid huge patterns, the rejected maximum, text and bytes, Unicode, nested groups, captures, scoped flags, and empty matches.

| Frozen compatibility gate | Actual result |
| --- | ---: |
| Large-repeat and unusual-window comparisons | 39,512/39,512 |
| Matching | 223,198/223,198 |
| Independent parser | 20,480/20,480 |
| Object and lifetime behavior | 393/393 |
| Tracing and native binding | 479/479 |
| Standard replacements | 8,862/8,862 |
| Deep replacements and callbacks | 11,266/11,266 |
| Extended Python compatibility | **308 differences in 72,248 checks** |
| Complete 22-stage campaign | **FAIL** |

The [first complete campaign](rust-v8-zig-stage-07-sealed-campaign-failure.json) fails before testing while the all-engine native-code audit is unstable. Once every independent source and actual library is frozen and the audit separately passes all **76** controls, the [one corrected campaign](rust-v8-zig-stage-07-sealed-campaign-attempt-02-failure.json) reaches the actual unchanged extended Python suite. It reports **72,248** checks and **308** differences. Its frozen child reports aggregate results only, so individual failed cases are **NOT REPORTED**, not invented. The complete Unicode step is **NOT MEASURED** because the campaign correctly stops at the preceding failure.

- [Preserved initial large-repeat incompatibility](rust-v8-zig-stage-06-extended-path-first-mismatch.json).
- [First genuine empty-match failure](rust-v8-zig-stage-07-repeat-motif-controls-attempt-01-failure.json).
- [Second genuine unusual-window failure](rust-v8-zig-stage-07-repeat-motif-controls-attempt-02-failure.json).
- [Actual repetition-overflow failure](rust-v8-zig-stage-07-repeat-motif-controls-attempt-03-failure.json).
- [All repaired large-repeat and unusual-window comparisons](rust-v8-zig-stage-07-repeat-motif-controls.json).
- [All independent matching checks](rust-v8-edge-oracle-zig-deep-stage-07.json.gz).
- [All independent parser checks](rust-v7-grammar-zig-v8-deep-stage-07.json.gz).
- [Object and lifetime checks](../audits/RUST-V8-DEEP-CONTRACT-ZIG-STAGE-07.json.gz).
- [Tracing, native-binding, and engine-independence checks](rust-v8-observability-zig-qualified-stage-07.json.gz).
- [Standard replacements](rust-v8-replacement-zig-stage-07-from-scratch-failures.json.gz).
- [Deep replacements and callbacks](rust-v8-replacement-zig-stage-07-from-scratch-deep-failures.json.gz).
- [Preserved first full-campaign failure](rust-v8-zig-stage-07-sealed-campaign-failure.json).
- [Preserved 72,248-check full-campaign failure](rust-v8-zig-stage-07-sealed-campaign-attempt-02-failure.json).

Full compatibility: **NOT QUALIFIED**. Final benchmark: **NOT ACCESSED**. Final speed: **NOT MEASURED**.
