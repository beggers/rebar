# Current-build correctness proofs: V8

This protocol adds new evidence. It does not edit, retry, overwrite, or
reclassify an earlier experiment. A current-build result is about actual,
independently implemented native code, not a wrapper around Python `re`, `_sre`,
a package, another candidate, or a previously tested binary.

## Freeze

Use exactly CPython 3.14.6 and Unicode 16.0.0. Keep the original frozen
correctness producers, source seeds, categories, cases, and expected answers
unchanged.

- Original edge producer: `tools/rust_v7_edge_oracle.py`, SHA-256
  `fe6a263a48f243ea02faaa78fc3bbd051233a2b2221967a5f76dd1bb79d242ca`.
  Run all **223,198** actual observations across **49** categories, with seed
  `2026072329`, all six independent original source seeds, eight seeded edge
  cases, and Unicode stride `4099`. The complete expected observation SHA-256 is
  `b34c2fcd36396c3373308d80889c4e855603bfb34bf5c0ce52725d2bda032526`.
- Original deep contract: `tools/rust_v8_deep_contract_oracle.py`, SHA-256
  `ba4b640d12444a5346d918a039d8a7a9fef0c78a54f6b66c6f0eb0c9dddbe978`.
  Run all **393** observations, including **64** seeded cases, with seed
  `2026072347`. The expected observation SHA-256 is
  `b184f3388320909b3c28fbd3ce9c15cefc992d3e852e9495ad8fb503d1cbaad8`.
- Original isolated deep producer:
  `tools/rust_v8_multi_candidate_contract.py`, SHA-256
  `167f9d9114f95cd9c9821465339264f8b6eca9bf7f70b84774f4108f62f11a70`.
  Keep both separate CPython reference workers, the complete actual candidate
  observations, the native poison worker, all 13 Python matching guards, the
  cross-family and third-party import guards, every mismatch, and the original
  canonical gzip bytes.

The three actually observed earlier edge failures remain failures:

| Independently implemented engine | Genuine failures | Complete original failure archive SHA-256 |
| --- | ---: | --- |
| Rust | 16 | `3ffdb21d10f40deabd70fa1f408fa38ff2b027a2d269c4b75e607a05cefde3b8` |
| C | 33 | `2cce7c26d2487c8e400d2fd6b8cfbc81d4b734b08f7a8f356def910a9cbb385c` |
| Zig | 16 | `5fa7283942994139d531593cc1bdf25f5da48f6de424d7604ce2ce569100788a` |

Authenticate all three complete archives and all original failure rows before
any new candidate run. In particular, preserve all 17 original C
`Pattern.groupindex` descriptor failures. An earlier archive never qualifies a
new source or binary.

No V7 or V8 campaign report is a prerequisite. The acyclic order is: freeze and
pass the actual V8 native-ownership audit; freeze and pass the independently
verified V8 no-delegation audit; run these original complete edge and deep
correctness proofs; run an additive official CPython V5 correctness oracle
using the unchanged official 152-case source, applicability rules, complete
support tree and V8 audit provenance; only then begin a new sealed campaign.
Earlier single-engine diagnostics may help repair a native candidate, but
cannot advance or bypass any later gate.

## Single-engine diagnosis is not qualification

A rebuilt Rust, C, or Zig engine may be diagnosed immediately. Record the
SHA-256 of every source file and actual ELF for that one family. Execute the
genuine isolated V8 native-owner worker immediately before and immediately
after the unchanged original edge suite. The pre-edge worker must actually
**pass all 16 ordinary public pickle checks** and verify that the worker really
matches using its own native owner while persistently blocking Python `re`,
`_sre`, external regex packages, the other candidates, and foreign native
loaders. If the owner fails or crashes, preserve its complete real failure
exactly once, do not start the original edge suite, do not publish any passing
archive, and do not retry. Require the same genuine passing ownership checks
after the original suite and before publishing edge evidence.

Use a distinct, deterministic, exclusively created complete failure archive:

```text
candidates/evidence/rust-v7-edge-oracle-{rust,vm,zig}-postfinal-current-build-v8-diagnostic-native-owner-failure.json.gz
candidates/evidence/rust-v7-edge-oracle-{rust,vm,zig}-postfinal-current-build-v8-qualified-native-owner-failure.json.gz
```

Include every actual ordinary pickle observation, the bounded complete crash
output where applicable, all independently hashed sources and ELFs, and whether
an original producer had already started. Never fabricate a missing worker
observation or label a failure `campaign_qualified`.

If the original producer itself crashes, times out, exceeds the frozen stream
limits, or finishes without a complete original archive, preserve a separate
exclusive deterministic record. Record the actual exit code or signal, timeout,
complete observed stream lengths and SHA-256 values, reversibly encoded bounded
stream previews, the genuine passing pre-run owner, the exact source and ELF
fingerprints, and that complete correctness observations were not produced.
Never manufacture missing cases or overwrite an original-suite archive.

```text
candidates/evidence/rust-v7-edge-oracle-{rust,vm,zig}-postfinal-current-build-v8-{diagnostic,qualified}-producer-crash.json.gz
candidates/audits/RUST-V8-DEEP-CONTRACT-{RUST,C,ZIG}-POSTFINAL-CURRENT-BUILD-V8-PRODUCER-CRASH.json.gz
```

If the producer finishes but the subsequent native-owner check genuinely fails,
preserve both the complete unchanged original producer bytes and the complete
separate native-owner failure. The original bytes are explicitly invalidated,
not passing evidence and not campaign-qualified:

```text
candidates/evidence/rust-v7-edge-oracle-{rust,vm,zig}-postfinal-current-build-v8-{diagnostic,qualified}-invalidated-after-owner-failure.json.gz
candidates/audits/RUST-V8-DEEP-CONTRACT-{RUST,C,ZIG}-POSTFINAL-CURRENT-BUILD-V8-INVALIDATED-AFTER-OWNER-FAILURE.json.gz
```

Preflight every pass, failure, crash, and invalidated destination for exclusive
creation before launching any candidate or original-suite worker. Refuse any
pre-existing target; do not overwrite or retry.

The original edge suite intentionally invokes the CPython reference and the
candidate in the same differential process. Do not falsely claim that Python
`re` is disabled inside that original reference process. Its adjacent,
separately isolated native-owner workers provide the actual poison-guard
observations.

Publish the unchanged, full original producer gzip only once, exclusively, to
the appropriate fresh path:

```text
candidates/evidence/rust-v7-edge-oracle-{rust,vm,zig}-postfinal-current-build-v8-diagnostic-pass.json.gz
candidates/evidence/rust-v7-edge-oracle-{rust,vm,zig}-postfinal-current-build-v8-diagnostic-failures.json.gz
```

The summary schema is `rebar-postfinal-current-build-proofs-v8-edge-diagnostic`.
It always states `campaign_qualified: false`, even if the rebuilt engine has
zero observed edge failures. It publishes no all-family audit claim. These
diagnostic paths cannot satisfy the qualified edge or deep prerequisites.

## All-family qualification fails closed

Before starting any campaign-qualified edge or deep candidate worker, require
all four genuinely frozen, distinct SHA-256 values:

1. `tools/postfinal_from_scratch_audit_v8.py`.
2. Its exclusively generated, actually passing
   `candidates/audits/POSTFINAL-FROM-SCRATCH-AUDIT-V8.json`.
3. `tools/postfinal_no_delegation_audit_v8.py`.
4. Its exclusively generated, actually passing
   `candidates/audits/POSTFINAL-NO-DELEGATION-AUDIT-V8.json`.

Missing values are `None`, not predicted fingerprints. Authenticate the actual
V8 native-ownership protocol, both complete audit reports, all **12** owned
source files, all **five** real native ELF roles, the **three** independently
executed native owners, all **48** actual public pickle checks, all **six**
genuine public match representations, all **13** Python matching guards per
owner, all cross-family and external-engine guards, all protected native-loader
aliases, and all three real historical failures. Recheck the complete graph
and all report fingerprints after each original-suite run.

Qualified original edge gzip has separate exclusive destinations:

```text
candidates/evidence/rust-v7-edge-oracle-{rust,vm,zig}-postfinal-current-build-v8-qualified-pass.json.gz
candidates/evidence/rust-v7-edge-oracle-{rust,vm,zig}-postfinal-current-build-v8-qualified-failures.json.gz
```

The summary schema is `rebar-postfinal-current-build-proofs-v8-qualified-edge`.
A passing original edge can only state `campaign_qualified: true` after both
actual all-family V8 audits independently pass. A real original failure is
recorded in the `failures` archive with all **223,198** observations, all **49**
categories, and every actual failure; it is never a qualifying pass.

## Genuine full deep contract

The deep run requires the exact passing **qualified** edge archive for the same
source and native ELFs. A diagnostic archive, a previous V7 result, a different
candidate, or an edited document is not sufficient. Run the unchanged original
deep producer through its genuine isolated workers and preserve its complete
original canonical gzip, all **393** observations, all **64** seeded cases,
both independent CPython references, every active guard, native provenance, and
every public mismatch. A private direct `/tmp` destination lets the genuine
producer finish before the actual result determines the exclusive final path.

```text
candidates/audits/RUST-V8-DEEP-CONTRACT-{RUST,C,ZIG}-POSTFINAL-CURRENT-BUILD-V8-PASS.json.gz
candidates/audits/RUST-V8-DEEP-CONTRACT-{RUST,C,ZIG}-POSTFINAL-CURRENT-BUILD-V8-FAILURES.json.gz
```

The summary schema is `rebar-postfinal-current-build-proofs-v8-qualified-deep`.
Record and reject every genuine public mismatch. Never publish a failure under
a passing filename.

## Candidate-free source gate

`tools/postfinal_current_build_proofs_v8.py --self-test` may authenticate only
the approved frozen source files and this protocol. It cannot import a
candidate, run a native worker, inspect a historical evidence archive, read a
performance fixture or holdout, read an unrelated file, write, create a
temporary directory, start a subprocess or thread, or sample a clock. Enforce
those restrictions using reversible guards and explicit rejected-effect
controls. Exercise deterministic canonical gzip, full edge denominators,
historical failure fingerprints, distinct diagnostic and qualified destinations,
and missing, duplicated, or fabricated qualification inputs using only
in-memory synthetic controls. A synthetic control is never evidence.

Performance: **NOT MEASURED**. Holdout: **NOT ACCESSED**. No benchmark,
performance fixture, enlarged holdout, ranking, timing, memory claim, or
release is authorized by this correctness-only protocol.
