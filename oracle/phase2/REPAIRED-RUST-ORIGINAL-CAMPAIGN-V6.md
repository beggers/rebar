# Freeze the complete corrected from-scratch Rust correctness run

This is a source freeze, not a successful correctness run. The Rust replacement
is first-party code, built from its own Rust engine and Python bridge. It may
not wrap a regex package, call Python's `re` or `_sre`, fall back to another
matcher, borrow another candidate's engine, or skip an original test.

The current overview is the already committed and pushed version 41. Its source
is `c0ab9b19acd895a122a171ca1d9df9010de0ec732b81b0f52f29b96cbc88f87a`;
its inputs, summary, and chart are respectively
`3abaa207a8d25f03c59bd9f7443dcd0bfb5fd6934c7f1fa388e2abf636893fc4`,
`e2835917d55d654a6d4c167298737c51f5f3b299ab7e2bc2c2eba60f9bff4f9f`,
and `882e8ddb4e233a1c569c0330bbbf618f65f54bcf3d0bb59dc1c99542677dd2b7`.
Preserve overview 40 as its immediate authenticated history and overview 39
as earlier history. Neither previous overview is current.

Version 41 freezes exactly one runnable general test-runner family: C. The
worker, runner, protocol, and contract are respectively
`78634bbcb5f55c560ea4b38c81ca395f4d4d5385c285bd0a3c25b395e3dd5ee1`,
`c114b578ac7ebfe28b45aa3b3407b81d05333f4470fa3047fd338ed3541c185a`,
`2d773fc55fe7c0a61e044a0e7deef81c8e36ffa0a9a744f4e60901f7a953c2ae`,
and `8eb72f1d94af85db1f1b282dda4d6ce1839f51f492ed2c7436c666d792f9b737`.
The six first-party languages are a source inventory, not six runnable
families. Corrected C matching is **NOT RUN**. This separately dedicated Rust
version-6 freeze was **UNCOMMITTED** when overview 41 was published and must
not be claimed to run through the C-only worker.

## Preserve the real Python baseline and every original case

Use only the committed version-4, six-family case producer:

- Source: `e0bab3833f6b8274b79e19b1dd7ca28c45931ef3efea8eefcc5cdfb0505af3d8`.
- Protocol: `e82b3469853406bf36812f016688aa3e6403b8d98d025a29fb9d0a9704ea2aa5`.
- Machine contract:
  `c22ff77b4947659510634e3fb802f82b559b8938dd26ba2d58552f3e761fa1d5`.

Retain all 31,237 original cases, all 13 suites, and only the original 13
individually named private waivers. The 13 suite counts in source order are
151, 864, 1,024, 768, 1,024, 2,854, 6,912, 5,120, 10,240, 1,376,
128, 264, and 512.

The public-type suite uses both independently executed, complete CPython
3.14.6 reference vectors, with distinct actual process IDs 81 and 82. Each
reference contains all 6,912 original cases. The complete records are
`6b26ac4eff9ec64cc3ae79872b3195b303a12bf40b96b55850b627857e614aa2`.
Preserve every one of the 96 original text- and bytes-subclass cache cases;
their corrected records are
`587cf35555472940522d6ae3a73053fb7e98492befe581cc024444bed8e264ad`.

The actual reference receipt
`ff8ddfaa14ff2eb09bde02ecb3566c84d204a41373c6b842eb34598c4de2f966`
says both **reference PASS** and **publication PASS**. A source-only contract
that says the reference was not yet run is historical, not the present actual
result. Preserve the earlier genuinely falsified 96-case script-context
record `df849727d5aa74cbec19950c2d56764bd592404b76c49abe87418bccd3a5013a`.
Do not alter the original denominator or create an equality waiver.

The additional 50 callable-signature cases remain separately counted. Their
two Python reference processes passed; no replacement has run them. They do
not silently become part of the 31,237-case denominator.

## Preserve what has and has not been observed

The previously tested Rust, C, and Zig engines genuinely failed with 1,036,
1,230, and 1,764 mismatches. Retain their failures and complete evidence.
Their durable publication receipts are not compatibility passes.

The first-party Rust version-13 build genuinely passed, with two independent
build phases and 28 real compiler and binary-inspection processes. Its build
receipt is
`4d4c927640c6e8c1b1e02c53350e1517b98255284218f49c2cefb53d647e9805`.
The corrected public Rust source is
`d47a976771206da468168ec22683e6d0204905a0f5b7e9e328fc1234b38f210e`;
the first-party bridge source is
`4436bbb8ad180ee8f02dd4418187506ec0d5a33bdb5a79c424fc736253fa0257`.
A passing build establishes only that the owned native code was built.

Preserved version 40 also freezes an unapplied first-party Zig scanner correction. All
1,024 original scanner cases remain; 960 are preserved and 64 are
prospective. The correction is **NOT APPLIED**, corrected Zig matching is
**NOT RUN**, and compatibility or speed improvements are **NOT MEASURED**.

There are at least 164 authenticated evidence owners and 169 authenticated
history references. These are lower bounds, not a full-repository count.

## Preserve the independently reviewed, superseded draft

Before the pushed version-41 overview was available, the same three Rust
version-6 paths held an independently reviewed version-40 source draft. Its
source, protocol, and contract fingerprints were, respectively,
`e1dbad33e0e6ee323f6110559d797fb91eb1610b63b639e217b04485dc60fefd`,
`6a8f086fa80c938c8f6c5e9521d5933c23de70e7f26c05893a30c472a40e5ef8`,
and `6ec627e4ffd380e8620642578327b95025dafb7e9ef553bd27bd2a072e2dc4ee`.
It was independently reviewed but **never committed or pushed**. The present
version-41 source, protocol, and contract replace those same paths. Preserve
the earlier fingerprints as a superseded audit only; never authenticate them
as current filesystem owners, published history, or candidate execution.

## Recover and measure all 13 real workers only when authorized

A future, separately authorized actual Rust run owns exactly four existing
target roles: the bridge source, public adapter, Rust engine, and Python
bridge. Authenticate their exact original hashes, device numbers, inodes,
sizes, permissions, ownership, and link counts before changing anything.

Use only the independently locked version-6 recovery directory. Persist,
fsync, read back, and announce the complete recovery journal before the first
target change. Preserve adjacent original-inode hardlinks and durable
per-role mutation intentions. Mask graceful signals during each individual
replacement. On failure or interruption, restore and verify all four exact
original inodes in reverse order. Recovery is not group-atomic and cannot
promise automatic recovery after `SIGKILL` or power loss.

Attempt all 13 independently isolated workers even if earlier workers fail.
Record each attempt before spawning, preserve each genuine started process ID
before collecting output, and distinguish attempted, started, timed-out,
crashed, failed, and completely observed workers. Retain the actual complete
stdout and stderr hash and size; explicitly mark bounded oversized prefixes
as truncated. Never count a truncated or partial observation as complete.

An actual candidate is compatible only if 13 distinct real workers verify
all 31,237 unchanged cases with zero mismatches and infrastructure failures.
If any suite is missing, the overall mismatch count is **NOT MEASURED**.
Do not extrapolate, suppress failures, or interpret durable publication as
candidate success. Preserve a truthful activated-run effect ledger even if
recovery or archive and receipt publication fails.

## Verify the source freeze without running matching

Independently hash and pin this source, this protocol, and the canonical
machine contract. Run `--self-test` and `--verify-frozen-context` using
pinned CPython 3.14.6 with `-I -B`, both ordinarily and with
`env -i PATH=/usr/bin:/bin LC_ALL=C`.

Read-only verification authenticates the small actual Python reference and
Rust build receipts, the complete current version-41 graph, the actual four
C-only runner owners, preserved version-40 and version-39 graphs, the
corrected six-family producer, and the immutable goal. It does not open,
read, or decompress any build, candidate-matching, or Python-reference
archive. It starts zero candidate, reference, compiler, or benchmark
processes.

Physically block direct imports, `builtins.__import__`, source and native
extension loaders, `_imp`, `ctypes`, direct process creation, filesystem
changes, networking, threads, clocks, recovery, and archive-file access.
Exercise fully in-memory failures for worker launch, missing or duplicated
process IDs, timeout, crash, malformed records, oversized output, partial
results, source-owner substitution, stale graphs and reference vectors, and
failure of archive or receipt publication.

Current Rust matching: **NOT RUN**. Runtime no-delegation:
**NOT ESTABLISHED**. Speed, memory use, confidence intervals, and undefined
behavior: **NOT MEASURED**. The 4,194,304-case performance holdout:
**NOT OPENED**.
