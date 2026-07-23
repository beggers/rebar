# Rust: initialize match captures once

**Outcome: all 22 compatibility stages passed; the proposed change is not a demonstrated end-to-end optimization.** In one four-way public practice run, the independently implemented Rust engine was **1.149988885×** as fast as Python, with a 95% interval of **1.103878921–1.195661517×**. It remained slower than the independent C and Zig engines overall and had **119** substantial slowdowns. The separate **24,576-case** final benchmark is **NOT ACCESSED** and **NOT MEASURED**.

| Implementation | Speed relative to Python | 95% confidence interval | Clearly faster cases | More than 20% slower |
| --- | ---: | ---: | ---: | ---: |
| C | 1.328250333× | 1.282155687–1.381582025× | 441/624 | 46/624 |
| Zig | 1.283308061× | 1.237542089–1.331120963× | 363/624 | 96/624 |
| Rust | 1.149988885× | 1.103878921–1.195661517× | 274/624 | 119/624 |

Here **1× means Python's unchanged `re`**. Each confidence interval compares an implementation with Python in this **same** public run. The complete results retain all **261** substantial slowdowns: **46 C**, **96 Zig**, and **119 Rust**. A substantial slowdown means taking strictly more than **20% longer** than Python on the same case.

Rust did not reach either the experiment's **1.5×** overall-speed target or its **60%** clearly-faster-case target on public practice. Practice results do not establish whether any implementation meets those targets on the untouched final benchmark.

## What changed

Rust's own matching engine records where each captured group begins and ends, together with the last participating group. Previously, its search loop cleared all of these values immediately before **every attempted starting position**:

```rust
begins.fill(-1);
ends.fill(-1);
*last = -1;
```

The change moves these same three statements before the loop, after the existing early rejection of an impossible search. Capture values are therefore initialized **once per search**, not repeatedly for each candidate starting position. The parser, compiler, match instructions, search ordering, Python bridge, C engine, and Zig engine do not change.

The existing Rust matching machine records every changed capture in its undo history. If an attempted start fails, `undo_captures(..., 0)` restores every capture and the last-group value before the next start is tried. Backtracking restores its precise capture checkpoint. Capturing lookarounds snapshot and correctly restore or merge their captures; repeated captures, backreferences, conditionals, and empty-match continuation keep the original behavior.

There is one explicit exceptional path worth disclosing: an atomic-end instruction without a matching atomic-begin returns without ordinary capture undo. It is unreachable for a production Rust program: the instruction sequence is private, the compiler emits balanced atomic and possessive regions, failed compilation does not produce an engine, and the matcher discards backtracking choices within completed atomic regions. This reasoning concerns real compiler-produced programs; it does not assert safety for forged or memory-corrupted bytecode.

Python callers inspect capture values only after a successful match. A no-match result does not expose the working capture arrays. Replacement callbacks first receive a separate match object containing copied spans, preserving reentrant Python calls and garbage collection.

The exact source and loaded production artifacts are:

| Production artifact | SHA-256 |
| --- | --- |
| Rust matching-engine source | `4b89d916e4c33e2b516be570ff3e75694f03dcea5eccf9320cedf07471b07dac` |
| Loaded Rust matching engine | `e7177c97070b2d0073a721044c4d23bb93e0d0883c1f2ccaa07c41eda8b96255` |
| Unchanged Rust native bridge source | `83afb5a709a6d0ea1701dfd64db30644edbf2cb0276c2db731a8119cfd52d8ed` |
| Unchanged loaded Rust native bridge | `1f072e81ba9339a8b2e52a7e93b7bcde791c4d518620b6bd760af67c7c89af34` |
| Unchanged public Rust Python interface | `80812459261edb9585bdf703f137af3e0e788638af2ad7183d00b6d357e8a926` |

The implementation does not wrap an external regular-expression package, call Python's regex engine, or delegate matching to the other candidates.

## Correctness was established before timing

Pinned CPython **3.14.6** was the reference. The freshly generated evidence binds to the actual new Rust source, loaded matching engine, unchanged Python bridge, and public interface:

- [223,198 frozen matching checks across 49 categories](../../../candidates/evidence/rust-v7-edge-oracle-rust-owned-capture-init-hoist.json.gz), with zero mismatches; compressed SHA-256 `397f8940b7b98c454241cd00290ec67dbf2592c6f95096e811de0771b98eebbd`.
- [393 Python object, method, descriptor, and exception-behavior checks](../../../candidates/audits/RUST-V8-DEEP-CONTRACT-RUST-OWNED-CAPTURE-INIT-HOIST.json.gz), with zero public mismatches; compressed SHA-256 `6a04536315e0f2af9ca129179b539b629614dcdd707f62ac61c5f24fe05a5a33`.
- [479 observable Python-behavior checks](../../../candidates/evidence/rust-v8-observability-rust-qualified-owned-capture-init-hoist.json.gz), including all **479** reference self-checks and **34** binding checks, with zero failures; compressed SHA-256 `6a2d4ec435109e0f96092d65c27092c9e6b1c3eea21b21f4962aae10a0a9cb8e`.
- [All 22 fresh, sealed correctness stages](../../../candidates/evidence/rust-v8-rust-owned-capture-init-hoist-sealed-campaign.json), including Python's own tests, callback behavior, isolated crash and recursion checks, and **4,494,555 full-Unicode comparisons**; SHA-256 `9ddbab81b16f0440ca19bffb8a539ea08d4a7ff33606ee3019eaf85977c2249a`.
- [The independent from-scratch and no-delegation audit](../../../candidates/audits/FROM-SCRATCH-AUDIT.json), confirming **three independent engine families** and **four distinct implementation pipelines**; SHA-256 `55ab21dfa78193c96551f5d3d95a51251f30e535cdb37c24df3d2e6044166854`.

The 22-stage correctness campaign explicitly records performance **NOT MEASURED**, does not access the final benchmark, and binds the same production artifacts that were subsequently measured. The public timing run recorded **zero correctness failures**.

## Every Rust operation, including the losses

The public practice run includes **12 operations**, **624 cases per candidate**, **7 paired trials** per case, **4 warmups**, **499 predetermined confidence resamples**, **17,472 original timing rows**, **52,416 correctness checks**, and all **1,872 candidate-by-case results**.

| Rust operation | Public cases | Clearly faster | More than 20% slower |
| --- | ---: | ---: | ---: |
| Compile a pattern | 48 | 48 | 0 |
| Escape pattern text | 48 | 4 | 2 |
| Find all matches | 80 | 25 | 31 |
| Iterate over matches | 67 | 28 | 21 |
| Match a complete string | 47 | 19 | 17 |
| Match at the start | 48 | 3 | 10 |
| Inspect match objects | 48 | 23 | 1 |
| Scanner | 48 | 9 | 8 |
| Search | 48 | 16 | 16 |
| Split | 47 | 27 | 11 |
| Replace matches | 48 | 38 | 2 |
| Replace and count | 47 | 34 | 0 |
| **All public Rust cases** | **624** | **274** | **119** |

This table retains every recorded substantial Rust slowdown instead of reporting only favorable search cases. In particular, finding all matches, iterating, full matches, searching, and splitting remain meaningful weaknesses. The practice observations do not identify a measured cause for any individual slowdown.

- [Every version-eight practice case, confidence interval, ranking, and slowdown](three-qualified-engines-public-practice-v8-summary.json); SHA-256 `77d3aa8ac970e126d11c9e9aad832f480670aceda1778966d16a4a768ca5a4c3`.
- [Every original four-way timing observation](three-qualified-engines-public-practice-v8-raw.jsonl.gz); compressed SHA-256 `f67cd7ddc0dff0cd256b156e23bfc8efc39546df8a4aec909cd9034261c91289`; independently verified uncompressed SHA-256 `32a265fa68ce82e76572c33696f41a605c2ea1b572d31411badbe78ff3cff8d4`.

## Preserve previous results and report limitations

The [version-seven four-way practice run](three-qualified-engines-public-practice-v7-summary.json), SHA-256 `89cf98bee40bb8e3ecc95861e07f302eff6c5f6288130854ea806578e8b76d79`, remains unchanged. Its Rust result was **1.141205743×**, with **264/624** clearly faster cases and **116/624** substantial slowdowns. It recorded **259** substantial slowdowns across all three candidates. Version eight separately records Rust at **1.149988885×**, **274/624**, and **119/624**, with **261** slowdowns across all candidates.

These are **different measurement runs**. There is no paired confidence interval comparing version seven with version eight, no statistically demonstrated Rust improvement, and no evidence that moving capture initialization caused the numerical difference. The change is **correctness qualified**, but it is **not a statistically established end-to-end optimization**.

The [earlier Rust common-prefix experiment](RUST-OWNED-MANDATORY-COMMON-PREFIX.md) and [its original, independently bound 22-stage correctness campaign](../../../candidates/evidence/rust-v8-rust-owned-mandatory-common-prefix-sealed-campaign.json), SHA-256 `9543fbbb39bbf42f5329a051b8441e69c756a495287a06c2f877c757b3ec5688`, remain separate and unchanged. The [previous Zig experiment](ZIG-STAGE-13-INTERNED-DISPATCH.md) and all preceding public practice results remain historical evidence, not current same-run Rust comparisons.

The existing incident records are preserved rather than replaced:

- [Earlier Rust verification and reviewer incident](RUST-OWNED-MANDATORY-COMMON-PREFIX-VERIFIER-INCIDENTS.md); SHA-256 `f26eddbe3902cefb343d7ca6eea13a1d649ea5edfddee0277606388e84340a92`.
- [C independence-audit retry](C-STAGE-20-INDEPENDENCE-AUDIT-RETRY.md); SHA-256 `0ee24eabfe369328c3dcd03c2dabab80f46a3851e82b6dbf4b390a72667149c4`.
- [Zig verification and reviewer-isolation incident](ZIG-STAGE-13-VERIFIER-INCIDENTS.md); SHA-256 `84efcdbd0059ab430c84322695bf472f66fdc1cc05efd74e383b62114efcedff`.

Practice memory figures describe **Python-traced temporary allocations only**. Per-engine native allocation and independently isolated whole-process memory are **NOT MEASURED**.

Capture-initialization change: **CORRECTNESS QUALIFIED; NO DEMONSTRATED END-TO-END OPTIMIZATION**. Final **24,576-case** benchmark: **NOT MEASURED**. Final benchmark access: **NOT ACCESSED**. Final winner: **NOT SELECTED**.
