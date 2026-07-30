# Fully corrected first-party Rust comment adapter V2

Status: **SOURCE FROZEN; VARIANT NOT MATERIALIZED; NOT BUILT; NOT RUN.**

This source-only Phase 2 experiment closes the gap between the existing,
independently built Rust adapter and its standalone comment fix. The faster
V26, V27, V28, and fully corrected V30 builds already use a private adapter
containing four earlier public-interface fixes. Applying the standalone
comment variant directly would discard those four fixes. This experiment
instead proves that all seven first-party corrections commute and freezes the
single complete result without running a candidate.

V1's actual application failed safely before opening or creating its candidate:

```text
failure receipt
    oracle/phase2/evidence/rust-corrected-comment-adapter-v1-preapplication-failure.json
SHA-256
    7bc692fcf17780ed05ca49c982536849212e1909f73337764b2392ea3ee9a37b
failure phase
    PREAPPLICATION_SOURCE_HOSTILE_CONTROL
candidate target created
    false
candidate source materialized
    false
candidate executions
    0
```

The deterministic cause: V1 added its canonical candidate to the root-mode
allowlist before hostile controls asserted candidate access was forbidden. V2
authenticates the complete V1 source, protocol, contract, and failure history,
keeps its candidate excluded through every owner read and all 98 controls, and
then grants one explicit, one-shot canonical-source authorization. No earlier
history is edited, hidden, or reclassified.

## Two exact, independently frozen predecessors

The canonical first-party adapter is never modified:

```text
path     candidates/rust_candidate.py
SHA-256  6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b
bytes    31151
device   2064
inode    428100
mode     0600
```

The existing four-repair private adapter is reconstructed solely from that
canonical source and the authenticated first-party V3 public-contract repair
transformer. No private build directory is opened:

```text
repair source    tools/apply_owned_rust_public_contract_source_repair_v3.py
repair source    5e57da2379e736bba75eacdb57f84710dc144c0d4088d5827b3139a6b71d8859
repair protocol  2aeb81e55548b46011c75815465d2bc2fa461d57ba7b990fc7a7b87d2d687a34
repair contract  82bce0066181dd16f3de52d88f31e930f25706b5ff3da2ba18b10c8b31b4f6a1

four-repair adapter SHA-256
    d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e
four-repair adapter bytes
    31934
```

Those four exact reversible edits preserve standalone flag order, pattern error
metadata, compiled-pattern flag representation, pattern equality, and hashing.
Their independently built V30 provenance is authenticated in full:

```text
V30 publication receipt
    c29361f0436f73ada037ba497a0eb008eeadac6ebb41c50019521c0212448abd
V30 root-provenance receipt
    26445b833ac0e846538a1f648059a1c8a224e4e2f1acd58f82e9458dcc142404

independent build phases               2
actual authenticated compiler runs    28
external Cargo dependencies            0
V30 candidate correctness      NOT MEASURED
runtime non-delegation         NOT ESTABLISHED
```

The separate, exclusively materialized standalone comment adapter contains
three additional lexical fixes but does not contain the four existing private
repairs:

```text
standalone source       cb2dc59dbe973f0ef33606a32ba0d475d8e3617fa1d435fe867fcaf2007132f2
standalone protocol     e3707659283373c432717d1c8356ce5cb045a63361b7e971f58bceb0d5a60cac
standalone contract     3198c323841cf3dbde87179270a4afd714d321cda7ca785748e8778a261dad57
standalone application  2d194cecca898a23c3515ffc69cd8aefc8b16fd5f1d205c5dcd84ff6113d9b90

standalone adapter SHA-256
    c1d150d467d5732eab4cc589f7e18583e59892592fb48d7d6f37700c00dccda0
standalone adapter bytes
    33256
```

## Seven exact commuting first-party corrections

The three new lexical corrections affect only `_Native.compile`,
`_Native.compile_scanner`, and the existing `_named_escapes` helper. They
forward effective flags and ignore unknown or malformed Unicode names within
inline comments and enabled verbose line comments. Nested scoped flag changes,
character classes, escaped punctuation, active Unicode lookups, original
`PatternError` text and positions, and byte patterns are preserved.

Applying the four previous public-interface repairs followed by the three
comment repairs gives exactly the same bytes as applying the three comment
repairs first and the four previous repairs second:

```text
canonical adapter                 31151 bytes
existing private four repairs     +783 bytes
new first-party comment repairs  +2105 bytes
                                 -----
complete composed adapter         34039 bytes

target
    candidates/rust/variants/corrected_comment_adapter_v2/rust_candidate.py
target SHA-256
    f7ad42db903e7f9f096f9c9460eb6605ac42932a40323a9ff9eb47e88a386227
```

The adapter continues to call only its independently written first-party Rust
bridge. It imports neither standard-library `re` nor an existing regex
package, starts no process, and introduces no other candidate engine.

## Complete public mismatch accounting

The frozen V26, V27, and V28 publication receipts all preserve the same
**10,434-case public comparison** and **1,145 observed mismatches**. The exact
comment-related rows are:

```text
inline named-Unicode comment             108
global verbose named-Unicode comment     108
scoped verbose named-Unicode comment     108
                                        ----
gross lexical rows                       324

independent comment-only rows            297
rows overlapping scanner correction       15
rows overlapping substitution correction  12
                                        ----
same gross lexical rows                  324
```

These are modeled corrections, not a measured composed-candidate result. The
original **31,237-case** denominator, previous **1,352 observed original
mismatches**, named private waivers, all failed runs, all timing results, and
all substantial regressions remain unchanged. Full composed-adapter
correctness, matching, memory, speed, runtime no-delegation, and qualification
are **NOT MEASURED** or **NOT ESTABLISHED**.

## Physical source isolation and mandatory gates

The irreversible deny-default wall is installed before the first owner read.
Self-tests read no workspace files. Source verification reads exactly three
current freeze owners and 20 authenticated public plaintext predecessors.
Candidate source, native objects, compressed archives, private build roots,
final proposals, holdout cases, `.git`, dynamic code, imports, processes,
network, clocks, and writes are physically rejected.

At least 90 hostile controls and more than 900 independent lexical witnesses
cover every frozen public comment row, nested flag scopes, classes, escaped
comments, byte patterns, error offsets, all four previous repairs, all three
comment repairs, and both exact correction orders.

Run these four gates using the pinned official interpreter and independently
computed full SHA-256 digests:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_corrected_comment_adapter_v2.py --self-test

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_corrected_comment_adapter_v2.py \
  --verify-frozen-context --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

env -i PATH=/usr/bin:/bin LC_ALL=C \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_corrected_comment_adapter_v2.py --self-test

env -i PATH=/usr/bin:/bin LC_ALL=C \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_corrected_comment_adapter_v2.py \
  --verify-frozen-context --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
```

Only the root coordinator may materialize the new target after committing and
pushing exactly the frozen source, protocol, and contract. Explicit root
authorization, three full owner hashes, and identical complete pushed/frozen
commits are required:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_corrected_comment_adapter_v2.py \
  --apply --root-authorized --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256 \
  --frozen-commit PUSHED_COMMIT --pushed-commit PUSHED_COMMIT
```

Root-only materialization keeps the immutable canonical adapter forbidden
through all authenticated owners and hostile controls. Only then does one
explicit authorization admit that adapter exactly once. It reconstructs all
seven corrections entirely in memory, proves both correction
orders produce identical frozen bytes, and creates exactly one fresh `0700`
variant directory and one exclusive `0600` adapter. The existing standalone
variant, native artifacts, canonical sources, all public evidence, and the
hidden holdout are never modified or opened. File and directory are fsynced;
the durable readback must match the complete predicted digest.

The retired final proposal remains **INVALIDATED**. Its successor remains a
**proposal only**, with no generated or opened final case. No claim is made
that the retired proposal remained globally unopened.
