# Independently build the first-party Rust exact-literal engine V34

Status: **SOURCE FROZEN; OFFLINE NATIVE BUILD NOT RUN; EXACT-LITERAL
COMPATIBILITY, SPEED, AND QUALIFICATION NOT MEASURED.**

This experiment evaluates another from-scratch Rust execution architecture.
For proven two-to-32-byte, capture-free, exact-case literal expressions, it
uses this repository's existing bounded byte-search primitive. All other
patterns continue through the same independently written first-party parser,
compiler, execution engine, scanner, and Python binding. No Python regular
expression engine, third-party regex package, other candidate, fallback,
benchmark detection, or hardcoded answer performs matching.

## Preserve verified correctness and every unsuccessful experiment

The latest corrected Rust architecture genuinely passed all **31,237** original
Python checks in **13** suites and then all **10,434** independently frozen
wider public checks. These are independently authenticated V26 and V33
results for their previously tested architecture; they do **not** establish
correctness for this new exact-literal engine.

The previously measured 416-case architectures remain visible: accelerated
search **1.2521×**, low-allocation compilation **0.7968×**, and the combined
design **1.2298×** relative to Python. Every unsuccessful case and every
slowdown is retained; none is a final holdout result. The prior 1,145 wider
mismatches, their scanner/replacement/comment/scoped-Unicode partition, the
V25 1,352-case original mismatch, and safely rejected V32 build are preserved.

## Four exact, exclusively materialized private overlays

Each of two owner-only source phases contains nine independently created
first-party owners: five unchanged canonical files and these four exact
private overlays:

1. Exact-literal Rust engine:
   `candidates/rust/variants/exact_literal_fastpath_v1/lib.rs`,
   SHA-256 `7ec7dc9815bec10c3149123ddc5045f575c3cd45731531bd81e0b888362a9136`,
   **194,276 bytes**.
2. Existing optimized first-party search source:
   `4d332a2af446550e29ac81369f8629b47be344f8274b0e83d6d1e2f44ebb8ae7`,
   **24,305 bytes**.
3. Complete scanner/substitution/safe-buffer Rust bridge:
   `f6253fbecc76b64750a22dc9393180d3ea6e3f2e29aace006c0479543e94342e`,
   **178,472 bytes**.
4. Corrected public/comment adapter:
   `f7ad42db903e7f9f096f9c9460eb6605ac42932a40323a9ff9eb47e88a386227`,
   **34,039 bytes**.

The exact-literal engine is independently reconstructed from the committed
189,493-byte scoped-Unicode parent. The frozen transformer validates its
1,009,125 bounded match cases, 1,345,500 collection cases, all conservative
eligibility restrictions, non-ASCII text handling, group-zero positions,
leftmost matching, and existing byte-search provenance. Its actual exclusive
application receipt and complete previous V33 source/build/public-correctness
receipts are independently authenticated.

Both private phases run the already authenticated V16/V9/V7/V4 first-party
compiler and ELF-audit kernel. Exactly **28** individually recorded, successful
processes compile and inspect two complete engines and two complete bridges;
both engine files and both bridge files must be byte-identical. Cargo runs
`build --release --locked --offline --frozen`, with one first-party package,
**zero external dependencies**, no network, and no loaded candidate library.
Canonical source files and installed native outputs remain unchanged.

## SOURCE-ONLY WALL

An irreversible, deny-default source wall is installed before any predecessor
is read. Only complete, no-follow, single-link, owner-only, explicitly pinned
source and plaintext evidence files can be opened. Candidate execution/import,
native files/loading, private roots, timing, entropy, compiler processes,
network, final proposals/cases, archive contents, descriptor aliases, broad
enumeration, and workspace mutation are forbidden. No final proposal metadata
or contents are inspected.

The historical V2 holdout remains **INVALIDATED; REKEYED SUCCESSOR REQUIRED**.
The public V3 replacement plan is **PROPOSAL_NOT_FROZEN_NOT_GENERATED**;
its future secret seed and final cases do not exist. Neither proposal is opened.

Independently pin source and protocol before rendering the contract:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B -S \\
  tools/reproduce_owned_rust_exact_literal_source_build_v34.py \\
  --render-contract --source-sha256 SOURCE_SHA256 \\
  --protocol-sha256 PROTOCOL_SHA256
```

Both ordinary and sterile environments must independently pass the frozen
`--verify-frozen-context` and `--self-test` modes with separately supplied
source, protocol, and contract SHA-256 values.

Only root may run the actual dual build after all three V34 files are verified,
committed, and pushed. Matching frozen/pushed commit identities, all nine
canonical owner pins, exact overlay hashes and byte counts, independent
exact-literal source/protocol/contract/application pins, previous V33
source/protocol/contract/build/root/public-correctness pins, historical
V25/V26/V27/V28/V30/V32 evidence, and explicit root authorization are required
before the first compiler starts. Native publication proves only reproducible
first-party compilation: this exact-literal architecture's compatibility,
runtime no-delegation, speed, memory, confidence, undefined behavior, and
qualification remain **NOT MEASURED** until separate authorized experiments.

