# First-party Rust source repair, version 1

This is a source-only repair freeze. It does not change a checked-in Rust or C
candidate, build or load a native library, activate a candidate, execute a
regex, run an oracle, measure performance, or open the final holdout. The
reference remains isolated CPython 3.14.6, all 13 original suites, all 31,237
original cases, and the same 13 named private exclusions.

## The exact proposed change

The authentic original first-party Rust bridge remains unchanged:
`candidates/rust/py_bridge.c`, 175,676 bytes, SHA-256
`f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b`.
Its independently owned adapter, its Rust engine, its empty external dependency
graph, its one-package Cargo lock, and all nine original Rust source owners
remain unchanged.

The source tool derives exactly one replacement inside the existing
`rust_substitute_core` function. State and compiled-group validation still run
first. For a non-callable replacement, the existing, unchanged
`rust_replacement_cache` prepares and releases the replacement before the
subject is acquired. Its existing replacement hash, cache, exception,
`PyBUF_SIMPLE` request, and nested full-read-only buffer behavior remain
unchanged.

An ordinary Unicode, bytes, or bytearray subject has its exact length read
directly from its built-in native layout. Every opaque or exporter subject uses
zero solely as the temporary validation-only match endpoint. In particular, the
repair never calls `_subject_length`, `PyObject_Length`, a new
`PyObject_GetBuffer`, or `memoryview` to discover an arbitrary subject length.
The actual subject is still acquired exactly once, after template validation.
The existing native validation-only `Match` does not acquire its subject.

A replacement error occurs before any subject is acquired. If subsequent
subject acquisition fails, the already prepared raw template and token
references are each released exactly once; no unopened subject is released.
Callable replacements retain their subject-first behavior. The successful and
error cleanup paths, `match.expand`, the independent Rust matching engine, and
all other candidate families are byte-for-byte untouched.

The unique original block contains 437 bytes and has SHA-256
`164afc04529a2e1b3dbd112ed907bd89d6e7a870fd6fa6ccdfef7b36e72a08de`.
The unique derived block contains 879 bytes and has SHA-256
`e73571d971682ff2167e2338b044eda2bc46566dcb6b90af78db85d592e01d0b`.
The complete derived source has 176,118 bytes and SHA-256
`4436bbb8ad180ee8f02dd4418187506ec0d5a33bdb5a79c424fc736253fa0257`.
No derived source is materialized by source-only verification.

## Preserved original evidence

The original version-19 graph counts 71 real historical evidence owners, while
its complete independently hashed reference closure contains 76 files. Those
different denominators are both preserved. All six first-party families and
all 25 independent source owners remain authentic. The separate blind-reviewed
C source-repair tool, protocol, and canonical contract remain unchanged.

The preserved Rust shape-changing suite recorded 1,392 mismatches out of
10,240 cases; 1,216 involved the four substitution APIs and 176 involved
`match.expand`. The preserved replacement suite recorded 336 mismatches out of
5,120 cases. At most 1,552 historically witnessed substitution cases could
be affected by the proposed ordering. This is a hypothesis, **NOT TESTED**.
The `match.expand` mismatches, public-type failures, public-surface failures,
and interpreter failures must not be represented as fixed.

## Private-only future application

Only an explicit `--apply --snapshot-root` may create the derived source. The
root must be a fresh, owner-only `0700` path under
`/tmp/rebar-phase2-native-build-v9-rust-*/reference-a/source` or its distinct
`reference-b/source` peer. The existing `candidates` and `rust` subdirectories
must be owner-only; both phase roots must be distinct. The sole permitted new
file is the previously absent `candidates/rust/py_bridge.c` within that
private snapshot. It uses descriptor-relative, exclusive, no-follow creation,
mode `0600`, one unaliased inode, complete original-byte verification, file
and directory synchronization, and reauthentication of the unchanged checked-
in Rust source. Workspace, reused, foreign, symlinked, hardlinked, C-builder,
or non-Rust destinations are forbidden.

Normal and empty-environment `--self-test` runs are wholly synthetic and block
all actual file access, writes, candidate and reference imports, processes,
compilers, networking, clocks, temporary roots, and threads. They attack
nonunique blocks, missing state guards, subject-before-template behavior,
callback changes, unsafe opaque lengths, exception cleanup, altered flags,
foreign dependencies, and hostile source paths.

Normal and empty-environment `--verify-frozen-context` operations are strictly
read-only. They authenticate the immutable original reference, the 25 source
owners, all nine Rust owners, the 71 preserved historical evidence owners, all
76 published evidence references, the unchanged separate C repair, both
original Rust failure receipts, the unique complete derived source, and the
unopened 4,194,304-case final holdout. Neither gate applies the repair.

The proposed Rust repair is **NOT TESTED**. Correctness, speed, memory,
confidence intervals, and undefined behavior are **NOT MEASURED**. The
performance holdout is **NOT OPENED**. No winner is selected.
