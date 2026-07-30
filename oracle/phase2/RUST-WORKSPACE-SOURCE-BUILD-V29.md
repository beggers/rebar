# Independently reproduce the first-party Rust matching workspace

Status: **SOURCE FROZEN; OFFLINE NATIVE BUILD NOT RUN; CANDIDATE CORRECTNESS
NOT MEASURED; FINAL HOLDOUT INVALIDATED; REKEYED SUCCESSOR REQUIRED.**

This version-29 experiment isolates one first-party Rust architecture: reuse
the root-match-local guard, repetition, and lookaround workspace. It does not
combine the separately built anchor-search or parser-allocation variants. The
original Rust search implementation, its single offline Cargo package, and its
zero external dependencies remain unchanged.

## Preserve every observed predecessor

The immutable original denominator is **31,237 cases in 13 suites**. The latest
complete V25 candidate run was **FAIL, with 1,352 mismatches**: 240
substitution differences and 1,112 changing-buffer differences. All 13 actual
workers completed; 15,877 cases were observed passing. Its publication passed,
but the candidate failed, remains unqualified, and is not interchangeable with
Python's matcher.

Authenticate the complete frozen source triples and genuine, independent
two-phase native-build publication/root receipts for V25, V26, and V27. Each
historical build genuinely executed 28 pinned compiler or ELF-inspection roles.
The historical V4 first-party non-delegation audit remains **FAIL with one
finding**. Removing its private bridge import chain is not a new audit; runtime
non-delegation remains **NOT ESTABLISHED**.

Authenticate the complete separate public profile: 416 public cases, 1,664
paired observations, and 984 VM allocation events. Exactly **408 guard/repeat
allocations total 120,768 bytes**; 576 capture-undo allocations total 276,480
bytes and are intentionally unchanged by this variant. Function-level CPU
time remains **NOT MEASURED**: the genuine profiler log says its timer could
not be set.

## Exactly three first-party private overlays

The exclusively materialized, standalone workspace architecture is:

```text
candidates/rust/variants/vm_workspace_reuse_v1/lib.rs
0bd199957ed96cbf67109d4621698a6be300cb5c88d0ae30d25402f51777ba36
178647 bytes
```

The unchanged, canonical search source is:

```text
candidates/rust/src/search.rs
4612c86424b9cbcb193d7ace521f359d7e3507281e83d3bf7e7ef7d189dd68fe
```

The separately materialized corrected first-party bridge removes the historical
private `inspect`/`functools` chain while retaining capture clamping and public
native method descriptors:

```text
candidates/rust/variants/no_external_introspection_v1/py_bridge.c
2dd040dc0337f205134431ebeaafe56ee4fe63cc77c1bb6cb5434742549884b7
177146 bytes
```

The existing corrected first-party public adapter is independently rederived
from its original source; its hash is
`d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e`
and its length is 31,934 bytes. The workspace and corrected-bridge frozen
source/protocol/contract triples and their real exclusive application receipts
must all authenticate.

Only an actual, explicitly root-authorized build may create two fresh private
`0700` phase trees. Each receives nine independently created `0600` first-party
owners: six unchanged canonical sources and exactly three overlays (workspace
`lib.rs`, corrected bridge, and corrected adapter). The original `search.rs`
must remain byte-identical. Cargo runs `build --release --locked --offline
--frozen`; GCC 13 and Rust 1.95.0 use deterministic source-prefix remapping.
All 14 pinned process roles must complete separately in each phase. The
complete native engine files must be byte-identical across both phases, and the
complete bridges must also be byte-identical. Native libraries are inspected,
never loaded; no candidate is imported or executed.

## Final-proposal incident and fail-closed boundary

The historical V2 final proposal is **COMPROMISED; RETIRED** after unintended
broad tracked-oracle enumeration elsewhere. Its previously pinned hash and
141,557,760-case historical count remain provenance only. Source gates perform
at most one `lstat` metadata check; they never open or read its contents. The
current final status is exactly:

```text
INVALIDATED; REKEYED SUCCESSOR REQUIRED
```

No hidden cases have been generated or accessed by this controller. No successor
is created, frozen, opened, or evaluated here. Final comparison, qualification,
confidence, memory, undefined behavior, and performance remain unavailable.

The ordinary and sterile source gates run both modes below with the exact pinned
CPython and independently frozen owner digests:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/reproduce_owned_rust_workspace_source_build_v29.py \
  --verify-frozen-context --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/reproduce_owned_rust_workspace_source_build_v29.py \
  --self-test --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
```

Both gates install an irreversible deny-default wall before reading predecessors.
Candidate execution/imports, native opens or metadata, clocks, compiler starts,
network, filesystem writes, directory enumeration, private roots, compressed
archives, hidden cases, final contents, and successor discovery are rejected.

Root separately verifies that this exact source/protocol/contract triple was
committed and pushed. Actual `--build`/`--run` additionally requires explicit
`--root-authorized --frozen-committed-pushed`, identical full
`--frozen-commit`/`--pushed-commit` identities, the three V29 owner digests, all
four workspace lineage digests, all four corrected-bridge lineage digests, both
overlay byte counts and digests, the original search digest, the adapter digest
and byte count, and all six V25/V26/V27 publication/root digests. A successful
build establishes only reproducible native compilation; it never qualifies a
candidate or repairs the invalidated final holdout.
