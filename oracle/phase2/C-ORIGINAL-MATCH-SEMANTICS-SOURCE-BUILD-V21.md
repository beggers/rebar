# First-party C Match native build, version 21

Status: first-party source frozen only. C21 has not compiled or loaded a
native extension, created a private root, generated random bytes, run a
candidate, opened a holdout, or measured performance. Candidate compatibility,
speed, memory, and undefined behavior are NOT MEASURED.

## Preserve both genuine earlier failures

The pushed C19 preactivation failure exposed a wrong installed-original
identity. It started no compiler and created no root. C20 corrected that
mistake: the real original native extension has SHA-256
`075350a17d4909cd6f8dbe5e808e7b6444760f54bb60af013e0f812e22cfb7fd`,
149,976 bytes, device 2064, inode 430300, mode `0755`, and one hard link. The
C18 `f379` artifact remains a separately proven private build output, not the
installed original.

The subsequently pushed real C20 attempt correctly authenticated all five
native build tools and the actual original native extension. It then stopped
before creating a private directory because official pinned CPython 3.14.6
does not expose `os.getrandom`. Its private-root call was
`os.getrandom(16)`; the same unavailable API would also have broken the first
atomic recovery journal at `os.getrandom(12)`.

The exact C20 failure is the immutable, separately published small owner
`oracle/phase2/evidence/c-original-match-semantics-source-build-v20-preactivation-failure.json`,
SHA-256
`88bc4bf0b1037a00bc426f0121dac601a9433e0d0090aae483d03a620b995d47`.
It records all 26 genuinely supplied authority pins, five authenticated
toolchains, zero compiler processes, zero roots, zero journals, zero receipts,
and the unchanged original-native identity before and after. Preserve this
actual failure and the earlier independently published C19 failure; do not
retry, relabel, overwrite, or hide either.

## Exact portable first-party correction

Authenticate the complete committed C20 and C19 source-freeze triplets,
both actual small failure receipts, the independent C Match semantic source,
the unchanged phase-one oracle, the six-family original producer, the strict
runtime guard, all four original-native provenance text owners, and the two
actual C18 receipts.

Derive the complete existing first-party C20/C19 native compiler in memory.
Make exactly two portable cryptographic-randomness changes to the real build
code:

```text
private root:     os.getrandom(16) -> os.urandom(16)
recovery journal: os.getrandom(12) -> os.urandom(12)
```

Pinned CPython 3.14.6 provides callable `os.urandom`. No extra dependency,
Python regex implementation, candidate, wrapper engine, deterministic random
number, time-based seed, shell, or subprocess wrapper is introduced.
Physically deny both `os.urandom` lengths during every source-only gate; only
a separately authorized actual build may request unpredictable bytes.

Preserve the entire unchanged independently written C parser, compiler, and
matching executor. The complete corrected C source remains exactly 221,647
bytes, SHA-256
`fe5bd423cb93b982bce79c584f19ad6eb254ab927008b21b37427de9e6ecf3c2`.
Preserve the six-protocol Match fix, original Match copy identity, exact
numeric protocol validation, nested PEP-688 acquisition flags `(0, 0, 284)`,
last-in-first-out release, and released-buffer error behavior.

Preserve all 31,237 frozen original case executions, 13 original suites,
13 named private waivers, and the separate 8,244 reference cases. The last
actual C candidate remains FAIL and its 236 observed differences are only a
lower bound. Fixing build portability does not measure candidate correctness.

## Physical source-only gates

Use exclusively isolated CPython 3.14.6 `-I -B -S`. Install the cumulative
first-party source wall before reading any input. Its complete allowlist
contains only exact pinned immutable source, protocol, machine contract, and
small real failure owners. It excludes the installed native, current C
source or adapter, private `/tmp` roots, compressed archives, overview
graphs, holdout or benchmark files, native loading, candidate imports,
compiler processes, clock, network, and workspace mutation.

The wall separately patches and rejects `os.urandom` itself. Hostile controls
must independently reject both actual-only 12-byte and 16-byte entropy
requests, deletion or alteration of either original vulnerable call,
invented C20 compiler or root creation, omitted C20 authority pins, false
failure phase, changed installed-original metadata, reopening hidden tests,
an actual compiler, and a regex engine.

Replace each placeholder with the independently calculated exact V21 owner
hash:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B -S \
  tools/reproduce_owned_c_original_match_semantics_source_build_v21.py \
  --self-test --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B -S \
  tools/reproduce_owned_c_original_match_semantics_source_build_v21.py \
  --verify-frozen-context --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
```

Repeat both under `env -i PATH=/usr/bin:/bin`. Require all four gates to
pass, with exactly zero source-only random-byte requests, compilers, roots,
journals, candidate workers, native loads, clocks, holdout reads, and
workspace mutations. An independent blind reviewer must reproduce the
results before the three new owners are committed and pushed.

## Later root-authorized actual build

No actual compilation is authorized by this source freeze. A later actual
build requires an independent commit, successful push, explicit
`--authorize-first-party-native-build-v21`, separate hashes for the V21,
C20, C19, and semantic owners, both pushed C19/C20 failure receipts, every
original P0, guard, producer, and C18 receipt pin, and the authentic
original-native hash. Preserve every earlier genuine authority rather than
replacing or weakening the 26-pin C20 audit.

Only after that authorization, request first-party operating-system entropy
to create one unpredictable owner-only `0700` root. Publish its recovery
journal through an unpredictably named, exclusive `0600` temporary file and
atomic replacement with file and directory synchronization. Build two
independent `0700` phases, four distinct `0600` exact C/adapter source
owners, and two distinct byte-identical native ELF files. Require all five
real toolchains and 14 distinct genuinely spawned compiler/inspection
processes. Verify the complete original `075350` native identity, including
its inode and mode, both before and after. Never replace, activate, or load
the installed candidate.

Only a fully successful actual build may publish fresh, exclusive, durable
small build and root-provenance receipts. Preserve a real failure and its
private journal; never delete roots or rewrite earlier evidence. Native
compilation, even if successful, is not candidate correctness. The expanded
holdout remains NOT GENERATED and NOT OPENED; performance remains NOT
MEASURED.
