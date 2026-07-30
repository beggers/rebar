# First-party Rust capture clamping on a freshly changing exported buffer

Status: **SOURCE FROZEN; VARIANT NOT MATERIALIZED; NOT BUILT; NOT RUN.**

The complete actual V24 original campaign is a candidate failure even though
its durable publication succeeded. Its authenticated public receipt is:

    SHA-256  5acd8dee2a515af56306e61f6ae8774c567f1f47e0ef1930a17e6809c2aafa09
    bytes    11832
    device   2064
    inode    525952

All 13 independent workers completed the original 31,237-case denominator.
The exact complete mismatch count is **1,352**: 240 in `substitution_v2` and
**1,112 in `shape_v2`**. Only 15,877 cases belong to completely passing suites;
do not invent passing cases inside either failing suite. The 13 named private
waivers, separate 8,244-case supplemental reference, and separate 6,912-case
corrected reference remain unchanged and are not added to the denominator.

The actual first-party V24 C bridge is frozen at:

    path    candidates/rust/variants/buffer_shape_pickle_findall_captures_semantics_v2/py_bridge.c
    SHA-256 1adb6bcecfa0b2fa80403e1c2caf372916466e8b9d0516980e60aef6a9ac08f0
    bytes   178860

Its `rust_output_capture` correctly reacquires a fresh non-bytes buffer but
incorrectly raises `BufferError` when the original capture end exceeds the
new export length. The original canonical bridge has no safe bounds check at
all and must never be exercised against changing exporters before repair.

CPython's public witness is:

    first export:   b"az12 bz34"
    second export:  b"X"
    re.sub(rb"([a-z]+)\d+", br"\1", exporter) == b"X "

The proposed one-site first-party C correction preserves the existing bytes
and text fast path, exactly one fresh buffer acquisition, and exactly one
release. After successful `rust_subject_open`, its complete changed core is:

```c
size_t first = begin > capture.length ? capture.length : begin;
size_t finish = end > capture.length ? capture.length : end;
if (finish < first) finish = first;
int result = rust_output_subject(writer, &capture, first, finish);
rust_subject_release(&capture);
return result;
```

The deterministic complete transformed bridge is:

    target  candidates/rust/variants/capture_clamp_semantics_v1/py_bridge.c
    SHA-256 a127ef85945a4dfa40a1b6c98f6c1a73ca7e1a487e190e8dde1d5aa2be47bb54
    bytes   178805

The source-only verifier authenticates the entire V24 bridge and complete V24
failure receipt, replaces exactly one anchored complete function in memory,
proves the transformation reversible, checks exhaustive synthetic hostile
size bounds and aliased byte views, and validates the explicit public witness
without importing or executing any matching engine. It installs a physical
deny-default descriptor and audit wall before reading evidence. Exactly one
V24 candidate **source file** is read; no candidate is imported or run.

The 141,557,760-case V2 holdout proposal is authenticated by its pinned path,
size, device, inode, and independently known SHA-256; its contents are never
opened. The proposal is **NOT FROZEN, NOT GENERATED, and NOT OPENED**. Native
binaries, compressed archives, private roots, hidden cases, workers, timing,
clocks, subprocesses, and other candidate sources are physically forbidden.

For each frozen-context and self-test mode, pass independently frozen SHA-256
pins for this source, this protocol, and the complete machine contract:

    python3.14 -I -B -S tools/apply_owned_rust_capture_clamp_semantics_v1.py \
      --verify-frozen-context --source-sha256 SOURCE_SHA256 \
      --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

    python3.14 -I -B -S tools/apply_owned_rust_capture_clamp_semantics_v1.py \
      --self-test --source-sha256 SOURCE_SHA256 \
      --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

Repeat both with the absolute pinned CPython 3.14.6 interpreter and with
`env -i PATH=/usr/bin:/bin LC_ALL=C`.

Only the root coordinator may materialize the bridge, after committing and
pushing all three frozen source/protocol/contract owners. Supply that same
40-character pushed commit as both independent explicit attestations:

    python3.14 -I -B -S tools/apply_owned_rust_capture_clamp_semantics_v1.py \
      --apply --source-sha256 SOURCE_SHA256 \
      --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256 \
      --frozen-commit PUSHED_COMMIT --pushed-commit PUSHED_COMMIT

The destination directory must not already exist. Application creates exactly
the stated private source file once with `O_NOFOLLOW | O_CREAT | O_EXCL`; it
does not build, import, execute, qualify, benchmark, or open a holdout.
