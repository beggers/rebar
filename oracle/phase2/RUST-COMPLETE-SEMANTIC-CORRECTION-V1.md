# First-party Rust complete semantic correction source freeze V1

Status: **SOURCE FROZEN; VARIANT NOT MATERIALIZED; NOT BUILT; NOT RUN.**

This append-only Phase 2 correction composes the two separately committed,
pushed, and root-materialized first-party repairs without opening any compressed
failure archive, native object, final holdout, proposal, Git metadata, timer, or
candidate during source-only verification.

The actual materialized expansion/probe predecessor is:

```text
input   candidates/rust/variants/expand_probe_semantics_v1/py_bridge.c
sha256  d0f0422a08592390619138d072cb831d6d446f38e2b67750798a221e7693d822
bytes   178081
device  2064
inode   525501
mode    0600
```

Its complete immutable root-application receipt is authenticated by SHA-256
`9eaff0631cb6aed1e8231d8dc9e1a346d2efb1cab88cb5b5cd686689f5a092b1`.
The separately materialized substitution-event-order V2 predecessor and its
complete application receipt are also authenticated without opening their
candidate:

```text
ordering source       50489f3ce64e254364ab416c132045c1bdcafed8bf5393efc6afb4727323658e
ordering protocol     d1c30f4bf11682a09ed7a67d368585daf51168079cdbb22816f19889bd8d8cae
ordering contract     de964c871ce364dce87e88fb97e151d0e8307199a50e24b35a8cbb4830fd7d00
ordering application  51d783da90847820cff44fe0cdaf329200e35948798c34aa2fe9d371c7ca2fac
ordering target       c69e24a87c251a332b79c4f4b5ed1a9f232847e446518930473a2ec871f020ab
ordering target bytes 177335
```

The expansion predecessor's source/protocol/contract triple is independently
pinned to `849a38fed6508b4e69ca049e46e932be65a98cbc49c0c3096e5edaf55ae75957`,
`e9eecf30afff954bfa1ceee79bef551f0cd31215de24e0d55a9f704adde559bf`, and
`e739146385553032f6f5705b4b43f230f4fe72070a0d4f636b86bbb66e4c1e14`.

## Authentic complete original failure and exact disjoint repair ownership

The complete, public, immutable V25 publication receipt is authenticated by
SHA-256 `d2926ae0d08e8c17ef07232c916166946678b764bfed7c5176ce6f6d7fc33c59`.
Publication succeeded but the candidate failed. The authentic denominator is
31,237 original cases in 13 suites and 13 actual candidate workers, with 15,877
verified passes and 1,352 semantic mismatches:

```text
substitution_v2  240 / 5120
shape_v2        1112 / 10240

disjoint correction ownership:
  240  substitution exporter ordering
 1024  shape-changing substitution exporter ordering
   56  shape trailing-escape outer-length probes
   32  malformed named-template Match.expand validation
 ----
 1352  complete original known semantic mismatch denominator
```

An additional 32 both-direct substitution probe witnesses overlap the ordering
correction and are explicitly modeled separately. They are **not** included in
the disjoint denominator; `240 + 1024 + 56 + 32 = 1352` is not inflated to 1384.
The historical shape partition remains `1024 + 56 + 32 = 1112`.

Synthetic controls exhaustively enumerate all 240 substitution cases, all 1,024
shape ordering cases, all 56 trailing-probe cases, all 32 malformed expansion
cases, and the separately reported 32 overlap witnesses. They preserve all 48
failing substitution replacements, 512 shape `BufferError` failures that never
touch a subject, exactly 32 fixed hashes, exactly 32 `PyBUF_FULL_RO` escaped
replacements, malformed visible lengths 13 and 19, zero malformed outer length
probes, and zero malformed subject reacquisitions. The disjoint ordered-record
projection SHA-256 is
`3f60354ffd19483b2419185637590f723b56ccb254fcf41405ddeb696d37db6d`; the
separate overlap projection SHA-256 is
`50376b3356be2fc5c8151b78fd87e6011029f31c556dd577f9c103dfa2f63ae3`.

## Exact complete first-party source correction

The existing expansion/probe bridge already has exactly two correction sites:

1. The exact `bad escape (end of pattern)` message conditionally probes the
   replacement's outer `__len__`; failure supersedes the saved `PatternError`.
   Other malformed messages perform zero probes and retain their nested position.
2. The non-bytes exporter branch of `Match.expand` invokes the existing owned
   helper with exactly three arguments and `Py_True` to validate before capture
   lookup. Malformed named templates do not reacquire their subject.

Both sites remain byte-for-byte unchanged. Exactly four new reversible edits,
all inside `rust_substitute_core`, apply the already authenticated V2 ordering
correction to that expansion successor:

1. Validate noncallable replacements through the existing replacement cache
   **before** acquiring the subject, using the unchanged adapter's safe
   zero-length validate-only dummy `Match`.
2. Copy the deferred tail, release the noncallback subject, and only then allow
   `PyBytes_Join` to reacquire replacement exporters.
3. Guard successful cleanup using the one-bit subject-ownership flag.
4. Guard error cleanup with the same flag, preventing every duplicate release.

The genuine `Match.expand` forward declaration and its complete definition are
independently distinguished and preserved. The existing safe capture clamp,
`PyBUF_FULL_RO`, first-party replacement cache, native descriptors, callback
lifetimes, and no-external-introspection correction are preserved. No private
`inspect`/`functools` import, stdlib regex matching delegation, third-party regex
engine, native engine mutation, canonical source mutation, or existing-variant
mutation is authorized.

The frozen byte-exact composed successor is:

```text
target  candidates/rust/variants/complete_semantic_correction_v1/py_bridge.c
sha256  254a8cea354556789496ce9dbfe70b4fed73ed9ee8e3b7f1c107dfe8662d7f55
bytes   178270
delta   +189 bytes relative to the materialized expansion successor
sites   2 preserved expansion sites + 4 reversible substitution-core sites
```

No corrected candidate has been built, imported, executed, qualified, or
benchmarked by this source freeze. Complete modeled historical coverage is not
an actual post-correction candidate result: candidate correctness, runtime
non-delegation, undefined behavior, memory, and performance remain **NOT
MEASURED** until independently authorized later phases.

## Physical source wall and four ordinary/sterile gates

The final holdout remains **INVALIDATED; REKEYED SUCCESSOR REQUIRED**. Its
contents, any proposal, final evidence, archive bytes, native objects, clocks,
networks, subprocesses, `.git`, hidden roots, and workspace writes are denied
before the first approved owner read.

Source verification authenticates exactly 12 public plaintext files: this
source/protocol/contract triple, the expansion source/protocol/contract triple
and application receipt, the ordering V2 source/protocol/contract triple and
application receipt, and the sole complete original V25 receipt. Each
predecessor owner is pinned by pathname, complete SHA-256, bytes, device, inode,
mode, owner, link count, and descriptor-relative no-follow identity. Neither
candidate bridge is opened during self-test or verification.

Run the ordinary and sterile gates with the pinned project CPython:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_complete_semantic_correction_v1.py --self-test

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_complete_semantic_correction_v1.py \
  --verify-frozen-context --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

env -i PATH=/usr/bin:/bin LC_ALL=C \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_complete_semantic_correction_v1.py --self-test

env -i PATH=/usr/bin:/bin LC_ALL=C \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_complete_semantic_correction_v1.py \
  --verify-frozen-context --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
```

Only the root coordinator may apply this correction after committing and pushing
the exact three-file freeze. The complete lowercase 40-character frozen and
pushed commits must match, and explicit root authorization plus all three
independent owner SHA-256 pins are mandatory:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B -S tools/apply_owned_rust_complete_semantic_correction_v1.py \
  --apply --root-authorized --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256 \
  --frozen-commit PUSHED_COMMIT --pushed-commit PUSHED_COMMIT
```

Root-only application opens exactly the authenticated expansion source once,
creates only the new target directory with mode `0700`, exclusively creates its
sole `py_bridge.c` with `O_CREAT | O_EXCL | O_NOFOLLOW` and mode `0600`, fsyncs
the file and directory, and verifies the complete durable readback SHA-256.
Existing targets are rejected. No build, candidate execution, native access,
holdout access, winner, or qualification is permitted.
