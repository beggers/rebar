# Rejected C experiment: compatibility passes, independence fails

The [Stage 14 C design](C-STAGE-14-REJECTED-INDEPENDENCE.patch) fixes large repeats, preserves empty captures and lazy matching, reports Python-compatible Unicode range errors, and commits possessive repetitions correctly. Every independently run standalone correctness gate passes.

| Frozen check | Actual result |
| --- | ---: |
| Isolated crashes and extreme inputs | [254/254](rust-v8-vm-stage-14-isolated-safety.json) |
| Full extended Python behavior | [72,248/72,248](rust-v8-vm-stage-14-extended-path-failures.json.gz) |
| Matching and search | [223,198/223,198](rust-v8-edge-oracle-vm-deep-stage-14.json.gz) |
| Independently generated parser cases | [20,480/20,480](rust-v7-grammar-vm-v8-deep-stage-14.json.gz) |
| Public objects and lifetimes | [393/393](../audits/RUST-V8-DEEP-CONTRACT-C-STAGE-14.json.gz) |
| Scanner, tracing, and native arguments | [479/479](rust-v8-observability-vm-qualified-stage-14.json.gz) |
| Replacement and callback cases | [8,862/8,862](rust-v8-replacement-vm-stage-14.json.gz) |
| Deep replacement and callback cases | [11,266/11,266](rust-v8-replacement-vm-deep-stage-14.json.gz) |

The implementation nevertheless imports `sys` to calculate `sys.maxsize`. The [unchanged four-engine audit](../audits/FROM-SCRATCH-AUDIT-C-STAGE-14-FAILURE.json) forbids this interpreter-introspection import and correctly fails with `forbidden_indirection_import`. Consequently, the native runtime is not accepted, the full 22-stage campaign is not started, and this source is not merged into the production candidate.

The complete rejected Python-source SHA-256 is `00eba5cdeff9f4288c8fef035a9396e9b4fa13a5cf437f6c95fbee677f68b387`; the independent native source is `892696cbf35a146c4da3e9e677058c3873199a4d9053b7ba9e7b4a34d5908ee5`; its actual native library is `6520023f79cc69afed8e0fd8a95d3822e458774eb79a65ded262f76014302e47`. The [exact rejected source patch](C-STAGE-14-REJECTED-INDEPENDENCE.patch), [full audit failure](../audits/FROM-SCRATCH-AUDIT-C-STAGE-14-FAILURE.json), and every passing report remain preserved.

Qualification: **FAILED**. Final performance: **NOT MEASURED**. Hidden final test: **NOT ACCESSED**.
