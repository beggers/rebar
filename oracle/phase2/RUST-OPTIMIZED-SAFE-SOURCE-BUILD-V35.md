# Independently rebuild the optimized, lifetime-safe Rust candidate V35

Status: **SOURCE FROZEN; OFFLINE NATIVE BUILD NOT RUN; CORRECTNESS,
INDEPENDENCE, SPEED, AND QUALIFICATION NOT MEASURED.**

This experiment combines two independently implemented, already materialized
first-party improvements in a genuine fresh Rust build:

- the exact-literal Rust execution engine,
- the optimized Python-facing literal bridge with safe native-engine ownership,
- and the complete, compatibility-corrected Python adapter.

The engine, search implementation, C bridge, and adapter are all written in
this repository. No installed regular-expression package, CPython matching
engine, Python regular-expression operation, other candidate, fallback, or
benchmark detector supplies production behavior.

## Preserve previous results and distinguish old audits

The exact previous Rust build passed all **31,237** original Python checks
and all **10,434** wider compatibility checks. Its **416**-case public
measurement was **1.2424347186648022×** Python, faster in **252** cases,
slower in **164**, with every one of its **14** substantial slowdowns and all
**1,664** paired observations preserved. These are historical facts about
the previously tested build; they are not results for this new architecture.

The existing successful static source/ELF audit examined the older V30 engine
`3c952a1a9eee234f646bdbd119978d8fb18c223ac71b63db1ed0eada9aed1237` and bridge
`ee63273fe7fc79934004db26a5c8df5b94ec3d0083837aed4bee701a7ed52256`.
It does not cover the exact previous V33 build or this proposed V35 output.
The older strict V4 private-inspection failure also remains preserved.
Current exact static and live independence, and V35 source/ELF and live
independence, are **NOT ESTABLISHED** until separate same-build audits.

## Four exact, owner-only first-party overlays

Each of two independent private phases retains five unchanged canonical
source files and creates exactly these four fresh, owner-only overlays:

1. The independently written exact-literal Rust engine,
   `candidates/rust/variants/exact_literal_fastpath_v1/lib.rs`, SHA-256
   `7ec7dc9815bec10c3149123ddc5045f575c3cd45731531bd81e0b888362a9136`,
   **194,276 bytes**.
2. The independently written optimized search implementation,
   `candidates/rust/variants/combined_search_compiler_fastpath_v2/search.rs`,
   SHA-256
   `4d332a2af446550e29ac81369f8629b47be344f8274b0e83d6d1e2f44ebb8ae7`,
   **24,305 bytes**.
3. The actually materialized optimized, ownership-safe C bridge,
   `candidates/rust/variants/native_handle_lease_v1/py_bridge.c`, SHA-256
   `c9b22c4443c36cc6e653af18fcd829561b7987df312368b30dfcbade254538f8`,
   **182,459 bytes**. Its authentic application receipt is SHA-256
   `8f3ad6bffcbbb2129a4a95bc12a0b9865b39f08d2c953ba5ce303a4a77743764`.
4. The fully corrected first-party Python adapter,
   `candidates/rust/variants/corrected_comment_adapter_v2/rust_candidate.py`,
   SHA-256
   `f7ad42db903e7f9f096f9c9460eb6605ac42932a40323a9ff9eb47e88a386227`,
   **34,039 bytes**.

The bridge retains adaptive first/last-byte literal acceleration while using
one owning Python capsule per compiled native engine. Active operations,
replacement callbacks, scanners, and iterators hold strong ownership leases;
failed ownership transfer frees exactly once, and private capsules do not
change externally visible garbage-collection referents. All ownership proofs,
32,768 callback sequences, 103,184 callback finalizations, and both exact
source-application receipts are independently authenticated.

Both private phases run the already authenticated V16/V9/V7/V4 offline
first-party compiler and ELF-inspection kernel. Exactly **28** successful,
individually verified compiler and native-inspection processes build and
inspect two complete engines and bridges. Both independently built engine
ELFs and both bridge ELFs must be byte-identical. Cargo uses
`build --release --locked --offline --frozen`, one first-party package,
**zero external dependencies**, and no candidate loading or execution.
Canonical workspace sources and installed native outputs remain unchanged.

## SOURCE-ONLY WALL

A permanent deny-default source wall is installed before any predecessor is
read. Only complete, no-follow, single-link, owner-only, explicitly pinned
source and plaintext public evidence owners are allowed. Native binaries,
private build roots, compiler processes, candidate execution/import, archive
contents, timing, entropy, hidden tests, final proposal metadata/contents,
descriptor aliases, network access, and workspace mutations are forbidden.

The historical final is **INVALIDATED; REKEYED SUCCESSOR REQUIRED**. Its
replacement remains **PROPOSAL_NOT_FROZEN_NOT_GENERATED**; no proposal,
secret seed, or held-out case is created, inspected, or opened.

Independently pin source and protocol before rendering the machine contract:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B -S \\
  tools/reproduce_owned_rust_optimized_safe_source_build_v35.py \\
  --render-contract --source-sha256 SOURCE_SHA256 \\
  --protocol-sha256 PROTOCOL_SHA256
```

Both ordinary and sterile environments must pass `--verify-frozen-context`
and `--self-test` with independently supplied source, protocol, and contract
SHA-256 values. Only root may perform the actual two-phase build after all
three V35 files are committed and pushed, every source/application/evidence
owner is separately pinned, frozen and pushed commit identities match, and
explicit build authorization is present.

A successful build proves reproducible first-party compilation only. Actual
V35 compatibility, runtime behavior, undefined behavior, same-build static
and live independence, speed, confidence, memory, final holdout results,
and qualification remain **NOT MEASURED** pending separately authorized
correctness, independence, and performance experiments.
