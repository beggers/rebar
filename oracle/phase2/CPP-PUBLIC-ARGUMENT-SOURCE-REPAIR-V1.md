# Freeze the observed C++ public argument correction

This is a source-only repair for a regular-expression engine implemented in
this repository. It neither changes nor runs the actual C++ candidate. A
published source freeze, a passing source self-test, and a matching source hash
do not mean the corrected engine has passed its compatibility test.

## The failure actually seen

The genuine Python 3.14.6 test is
`ReTests.test_qualified_re_sub`, at lines 240–256 of
`oracle/cpython-3.14.6/test_re.py`. Its source SHA-256 is
`879c8b562a5bddb413e73ad6d026a6199785bd08fa1c2c5db1ef831b4e1c47e2`.
The authenticated method's own source SHA-256 is
`16c182d4d8a4ea9e346f38d11aa3fc7db4a89415528b009b5f3b134fa5efabad`.

The actual upstream failure, recorded at line 253, is:

```text
C++:    sub() takes at most 5 arguments
Python: sub() takes from 3 to 5 positional arguments but 6 were given
```

The original failure archive is
`owned-six-family-original-p0-campaign-v1-cpp-phase2-v1-failures.json.gz`,
SHA-256 `0462adbd6ee7bafb274578462117513669de9b849473a2e1ada441407bc814a2`.
An earlier investigation read exactly one 1,048,576-byte uncompressed prefix,
SHA-256 `66cb4ec2f314213676486261e170e8109190b3029553509de637beaa6038bb53`.
This source freeze does not reopen, decompress, or reinterpret that archive.
It authenticates only the existing, separately published failure receipt.

## One change, three related public functions

The original C++ public adapter is exactly 27,488 bytes:

```text
candidates/cpp_candidate.py
8dcece29b1a194eea023143148af37bb679a9df4c39c01153f5ee23f778e16d5
```

One uniquely anchored in-memory block repairs `split`, `sub`, and `subn`.
It follows the actual pinned CPython argument order: reject a duplicate
argument first, report the exact actual number of excessive positional
arguments, and issue the positional-argument deprecation warning only after
all argument validation succeeds. Preserve the exact Python warning category,
message, and caller filename.

The same three functions receive the exact user-visible text signatures
explicitly defined by Python 3.14.6:

```text
split: (pattern, string, maxsplit=0, flags=0)
sub:   (pattern, repl, string, count=0, flags=0)
subn:  (pattern, repl, string, count=0, flags=0)
```

A source-only synthetic check compares 336 deterministic text and byte
argument examples against the genuine pinned Python standard library. The
synthetic candidate uses an in-memory, first-party literal witness; it does
not import a C++ candidate, load a native library, or call Python's
regular-expression engine on behalf of a candidate. Python's standard
regular-expression engine runs only as the reference inside the explicitly
isolated, pinned oracle process.

The corrected complete adapter is derived only in memory:

```text
aa4256725c75635d4e4e932b173d6d74ccd059bd867461ad6b0f5939306891c1
28,109 bytes
```

The unchanged original 1,951-byte argument block has SHA-256
`74d6f41c879661d9c3fde96da6368ceb42d57e39587a082a83e2242c13269462`.
The derived 2,572-byte argument block has SHA-256
`1423ca2cf876b5979d174933365b34f82a2049c6ec8d711e2f6efc7a17270928`.
The canonical adapter, native C++ parser, compiler, executor, header, and
bridge remain unchanged. No external regular-expression package, CPython
regex wrapper, fallback, other candidate, compiler, or benchmark is used.

## Keep all published failures and counts visible

The historical version-31 graph genuinely has **151** evidence owners and
**156** authenticated references. C++ completed all 13 suites: **one passing
suite**, **128 verified passing checks**, **2,308 semantic mismatches in seven
suites**, and **five infrastructure-failed suites**. There are **12 failing
suites in total**, not 12 infrastructure failures or crashes. The actual C++
crash and timeout counts are both zero.

The newer published corrected Rust matching run added exactly two actual
evidence owners. Current history therefore has **153** evidence owners and
**158** references. The actual Rust result remains **FAIL**: **1,036
mismatches**, **8,965 verified passing checks**, 13 matching workers, all 13
suites completed, and zero infrastructure failures. Its compressed failure
archive is authenticated as raw bytes only:

```text
2ab266d193728e1297382ed233a813c7ef62c0aa407355cf44fef6aaeffa134f
3,663,299 compressed bytes

201b7edc94d54f9ea2054f2eab98a68c83850def841ceade6a14c8db7d05cdd3
4,674 receipt bytes
```

C still has 1,230 mismatches. Zig still has 2,172. No candidate is qualified.
The original denominator remains exactly **31,237 checks, 13 suites, and 13
named private waivers**. The separately frozen 50 callable-signature checks
are not added to that denominator; their two-reference baseline and every
candidate result are **NOT RUN**.

The planned 4,194,304-case holdout is **NOT GENERATED** and **NOT OPENED**.
Speed, memory, confidence intervals, undefined behavior, and corrected C++
candidate correctness are **NOT MEASURED**. No winner has been selected.

## Four independently pinned source gates

Use exactly this stable, isolated, bytecode-free Python:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B
```

Independently calculate and supply the SHA-256 values of the repair tool,
this protocol, and the canonical machine contract:

```text
sha256sum tools/apply_owned_cpp_public_argument_source_repair_v1.py \
  oracle/phase2/CPP-PUBLIC-ARGUMENT-SOURCE-REPAIR-V1.md \
  oracle/phase2/cpp-public-argument-source-repair-v1.json
```

Run `--self-test` and `--verify-frozen-context`, each in the ordinary
environment and in `env -i PATH=/usr/bin:/bin LC_ALL=C`. Every invocation
must provide all three independent hashes:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/apply_owned_cpp_public_argument_source_repair_v1.py \
  --self-test \
  --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/apply_owned_cpp_public_argument_source_repair_v1.py \
  --verify-frozen-context \
  --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256
```

The synthetic source wall physically rejects file access, writes, processes,
candidate imports, networking, threads, clocks, native libraries, locks,
signals, and decompression. Hostile controls also reject false signatures,
wrong warning order, duplicate source blocks, regex wrappers, stale 151/156
history presented as current, hidden failures, opened holdouts, and fabricated
candidate passes.

## Any actual application is a separate chunk

Do not run `--apply` as part of this source freeze. Only a future explicitly
authorized, independently hash-pinned application may create one fresh
owner-only snapshot at a path of this exact form:

```text
/tmp/rebar-phase2-cpp-public-argument-source-build-v1-PRIVATE/
  reference-a/source/candidates/cpp_candidate.py
```

`reference-b` is the only other permitted phase. Both existing phase trees
must have distinct directory identities and mode `0700`. The destination
must be a fresh mode-`0600` file created with
`O_CREAT | O_EXCL | O_NOFOLLOW`, fully synchronized, and verified by exact
source readback. The original worktree source and all native owners must
remain unchanged. Compiling, activating, running the full original test,
updating a graph, and measuring performance are separately gated future
chunks.
