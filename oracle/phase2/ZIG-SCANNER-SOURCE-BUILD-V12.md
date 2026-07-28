# Freeze a from-scratch corrected Zig build

Status: **SOURCE FROZEN; BUILD NOT RUN.**

This experiment freezes a reproducible way to compile the project's own Zig
regular-expression engine and its own Python bridge. Both are first-party source
files. No external regular-expression library, wrapper, Python `re` or `_sre`,
another candidate, fallback, prebuilt matching engine, or network is permitted.

The previous Zig build used a scanner fix that changed the complete token
`alpha42` into its nested capture `alpha`. This build uses only the independently
frozen V2 correction. Its Python bridge exactly matches the 173,026-byte original
first-party source:

    67edae144290254ba25f67f73350ff5d52ccfb2a209e3fbcc555fc4b3d4efd4b

The old 173,082-byte V1 conditional bridge is forbidden. Neither the original
engine nor the original Python-facing adapter is changed.

## What has actually happened

Stable CPython 3.14.6 remains the sole correctness reference. The frozen original
denominator is 31,237 checks across 13 named suites with 13 named private
waivers. A separate 50-case callable-introspection extension is frozen but its
Python reference and every candidate remain **NOT RUN**; those 50 cases have not
been added to the denominator.

The signed V31 headline graph is preserved as historical evidence: 151 evidence
owners and 156 references. It includes a genuinely completed, reproducible Rust
source build with 28 actual compiler processes. A later complete Rust matching
run created exactly two more genuine evidence owners. The current totals are
therefore 153 evidence owners and 158 references.

That corrected Rust candidate **FAILS** its complete original compatibility
gate: 1,036 mismatches, 8,965 individually passing checks, all 13 matching
workers and test groups completed, zero infrastructure failures, and all four
original native targets restored. The older Rust result of 1,087 mismatches and
7,438 individually passing checks is retained separately. Successful source
building and successful durable evidence publication do not mean matching
passed. The tested C engine still has 1,230 mismatches. The tested Zig engine
still has 2,172 mismatches, 2,847 individually passing checks, and all 13
workers and suites completed. The original zero-worker Zig setup failure is
also retained. No candidate is qualified.

The Rust build's two independent, authenticated owners are:

    840a6403699fec44d4f725f737fc9538c997b818a48d167398ad1b95cbb9828d
    1cd7e538098711ddac017ee3375d302d4b1ba4e6da52d10d2a524103db500a2f

The 108,325-byte source-build archive is authenticated as raw compressed bytes;
its separate publication receipt is 2,109 bytes. The corrected Rust matching
run additionally produced:

    2ab266d193728e1297382ed233a813c7ef62c0aa407355cf44fef6aaeffa134f
    201b7edc94d54f9ea2054f2eab98a68c83850def841ceade6a14c8db7d05cdd3

Its matching-failure archive is 3,663,299 compressed bytes; its independent
receipt is 4,674 bytes. Both compressed archives are hashed without inflation.
Their real, distinct files establish V30 at 149/154, historical V31 at 151/156,
and the current evidence at 153/158. No unpublished graph or guessed result
is used.

## The independently reproducible future build

The sole stable Zig compiler is:

    /tmp/zig-x86_64-linux-0.16.0/zig
    2317bbb91798556d9d0f38aabdac23db83f0979b25f767259ae474546724087c

Both references use separate, fresh mode-0700 trees:

    /tmp/rebar-phase2-zig-scanner-capture-source-build-v2-PRIVATE/reference-a/
    /tmp/rebar-phase2-zig-scanner-capture-source-build-v2-PRIVATE/reference-b/

Each reference receives separately owned mode-0600 copies of the exact Zig
engine, exact adapter, and V2-derived corrected bridge. Both phase trees must
exist before either bridge is created. Source destinations are exclusive,
no-follow, inode-verified, and synchronized. Source inodes, caches, native
output inodes, and phase directories must be distinct.

Each future phase has exactly 13 compiler and inspection roles: version checks,
one optimized native Zig engine build, one CPython C-bridge build, and full
dynamic-symbol, dependency, section, and note inspections for both native
artifacts. The total is exactly 26 **future** processes, not processes already
run. The bridge can link only to its adjacent `_zig_probe.so`. Complete ELF64
forensics reject external regular-expression engines, Python's matching engine,
dynamic loading, other candidate engines, omitted source bytes, and unexpected
symbols. Both independently built engines and bridges must be byte-identical.

The historical V11 private-build and ELF mechanics are individually
authenticated and rebound exclusively to the corrected V2 bridge and V2 phase
root. V11's overlay, root, historical evidence counts, source-build controller,
and matching results are never reused as current evidence.

## Source-only gates

Replace the three placeholders with the independent SHA-256 of this source,
this document, and the canonical V12 contract. Use the exact pinned interpreter:

    /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
      tools/reproduce_owned_zig_scanner_source_build_v12.py \
      --self-test \
      --source-sha256 SOURCE_SHA256 \
      --protocol-sha256 PROTOCOL_SHA256 \
      --contract-sha256 CONTRACT_SHA256

Repeat with `--verify-frozen-context`. Run both commands once in the normal
environment and once prefixed with `env -i PATH=/usr/bin:/bin LC_ALL=C`.

The synthetic gate physically blocks filesystem, candidate, compiler, worker,
archive, network, and clock effects. Its hostile controls reject historical
151/156 evidence presented as current, missing or duplicated Rust matching
owners, a forged successful Rust match, unrun extra cases silently included in
the original total, old V1 roots or scanner overlays, cross-phase commands,
unauthorized archives, replaced compilers, external matching engines, holdout
access, and early winners.

`--build --label LABEL` is a separately authorized future operation. It is not a
source-only gate and has not been run. A future run must retain both successful
and failed outcomes in fresh, exclusive mode-0600 compressed reports and
distinct publication receipts. A successful compilation never counts as
successful matching.

Corrected Zig build: **NOT RUN.** Corrected Zig compatibility, speed, memory,
confidence, and undefined behavior: **NOT MEASURED.** The planned 4,194,304-case
holdout remains **NOT GENERATED** and **NOT OPENED**. Winner: **NOT SELECTED.**
