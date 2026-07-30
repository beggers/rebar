# Preserve the real Rust failures and freeze one smaller source change

Status: **SOURCE FROZEN; NOT BUILT; NOT RUN; NOT BENCHMARKED.**

This is an evidence-based proposal for the from-scratch Rust implementation,
not a wrapper around another regular-expression engine. It changes no existing
candidate, source, test, holdout, benchmark, or build.

## What the real test found

Authenticate the complete published Rust V22 original-test receipt:

    SHA-256  7013c42f6309d94e094dd89cc8e9f24fe245c0cba5ca4791d35ffe5fa2b7dad7
    bytes    47336
    device   2064
    inode    525371

The receipt records a successful publication of an unsuccessful candidate.
All 13 original groups started in 13 real worker processes. Twelve groups
completed, nine passed completely, and only **14,725** original cases can be
counted as passing. The completely observed differences were:

    managed buffers          42 of 1,024
    replacement handling    352 of 5,120
    changing buffer shape  1,624 of 10,240

These establish a **2,018-difference lower bound**, not the total: the
128-case subinterpreter group failed before it could finish. The complete
number of differences is **NOT MEASURED**. Do not subtract failing-group
differences from their group sizes to invent passing cases.

The genuine failing worker was process 188. It created no native child
interpreters. Its complete error contains one remaining-interpreters warning
and 16 destructor warnings. Those counts apply **only to that one worker**.
Keep the original 31,237-case denominator and 13 named private waivers. Keep
the frozen 8,244-case supplemental reference and the distinct 6,912-case
reference vector separate; neither is added to the original denominator.

Preserve the full V22 source, protocol, and 435-field machine contract:

    source   e88f242835781e9b70efa18e68a7b06b0b9368e91320ed596995ef0e16370c61
    protocol c6a2a5db9c9c27974c29af01b3d7f7042bae73e254c638fe27813505ef11f396
    contract f1c021049e4bb173be8d47339920354e02c8c0194aead877b8474a128b5e158a

Preserve, separately, all 402 inherited V21 obligations and the real V20
predecessor. V20 tested the original `a0b9…` bridge, passed 15,749 cases, and
observed 240 replacement and 1,056 shape differences. Its total also remains
**NOT MEASURED** because its child group did not complete.

## The smallest source-only proposal

The frozen V1 source publishes the complete exact original and corrected C
branch anchors. Use those public bytes; never read a candidate C file. The
actually tested V22 bridge was `f9bd…` and contained a 384-byte failed
replacement branch. Replace that branch exactly once with its authenticated
97-byte original `a0b9…` predecessor. This removes only the 287-byte
over-broad early-return guard from `rust_replacement_cache`.

Retain the separately authenticated 660-byte removal of the erroneous outer
`PyObject_Length(replacement)` block. The unchanged matcher, parser, native
engine, and two-capture optimization are established by frozen public source
metadata only. Pure arithmetic gives a conditional expected source length:

    original a0 source        179,520
    outer-length removal        −660
    conditional V2 length     178,860

Equivalently, the measured V22 source length is 179,147 and the one guard
removes 287 bytes. **The complete proposed source is not publicly available,
not read, and not materialized. Its actual length and SHA-256 are NOT
MEASURED.** The arithmetic is not an observed complete-file hash. The exact
cases the proposal might fix, its actual exception behavior, correctness,
build, performance, and memory remain **NOT MEASURED**.

Use only a synthetic, in-memory event ledger to verify acquisition flags
`0, 0, 284` and replacement-first, last-in-first-out release order. Synthetic
events are not real matching or proof of actual buffer behavior.

## Reproduce the public-only freeze

The verifier installs a new deny-by-default audit wall **before** reading any
frozen owner. It never executes the V22 controller, V1 `load_context`, a
candidate, a build, a native library, or a benchmark. It reads only exactly
pinned public plaintext through no-follow, owned, tracked descriptors.
Physically reject `builtins.open`, `_io.open`, `_io.FileIO`, foreign file
descriptors, `os.stat`, candidate and historical bridge paths, traversal,
private roots, compressed evidence, all phase-3 proposals, clocks, entropy,
subprocesses, matching engines, and writes.

For the pinned CPython 3.14.6, independently supply the three frozen source,
protocol, and contract SHA-256 values to each mode:

    python3.14 -I -B -S tools/apply_owned_rust_capture_shape_semantics_v2.py
      --self-test --source-sha256 SOURCE_SHA256
      --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

    python3.14 -I -B -S tools/apply_owned_rust_capture_shape_semantics_v2.py
      --verify-frozen-context --source-sha256 SOURCE_SHA256
      --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

Repeat both modes with the absolute pinned interpreter and
`env -i PATH=/usr/bin:/bin LC_ALL=C`. No private candidate, native file,
holdout, archive, build, actual test, or timing may be accessed. The proposed
14,155,776-case holdout is **NOT FROZEN, NOT GENERATED, and NOT OPENED**.
