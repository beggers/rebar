# First-party non-delegation audit V3

V3 is an immutable, additive successor to the published V2 source freeze. None
of the V2 source, protocol, contract, or actual failure evidence is modified.
The exact authenticated predecessor owners are:

- `tools/audit_candidate_runtime_non_delegation_v2.py`:
  `23862f929d7b875cbc16059cb8c1d5c60df7aaba7379e17b57fe943a7d77bf6f`.
- `oracle/phase2/RUNTIME-NON-DELEGATION-V2.md`:
  `bd8a393d8f385ea9ff55570b1a222a9baed347e9f238ec89534fc46a85127802`.
- `oracle/phase2/runtime-non-delegation-v2.json`:
  `456439d8b0467b17bd40ee78b5de0f00ace6e0f01e5d558590fabb592dd49729`.

The first root-authorized V2 static audit really **FAILED** before completing
candidate source inspection:

```text
AuditError: candidates/rust/src/lib.rs:252: unterminated native literal
```

Its exact public failure receipt is
`oracle/phase2/evidence/runtime-non-delegation-v2-actual-source-lexer-failure.json`,
SHA-256 `7f30581baf5b47adf7c2d21f0baf2218bc78e14a72aeba90355140519dbadf1a`,
411 bytes, device 2064, inode 525976, and mode `0600`. Its status is **FAIL**;
actual candidate executions, candidate workers, and native library loads were
all zero. The holdout remained unopened. A failure receipt is evidence of a
real lexer failure, not evidence that any candidate passed or delegated.

V2's generic native lexer incorrectly interpreted the Rust lifetime apostrophe
in forms such as `struct BorrowedText<'a>` and `&'a [u8]` as the beginning of
an unterminated character literal. V3 replaces that lexer with an explicit
Rust-aware lexical layer covering named and static lifetimes, `'_`, loop
labels, Unicode and escaped character literals, byte characters and strings,
normal and arbitrarily hash-delimited raw strings, byte/raw C strings, raw
identifiers, doc comments, and nested block comments. Lifetimes and comments
cannot conceal subsequent executable imports. Unterminated or malformed
literals are still rejected. External regex crates, native engine symbols,
dynamic loading, dangerous macro concatenation/inclusion, and disguised link
attributes remain forbidden.

The six-family V2 policy is unchanged: Rust's native `inspect` import is a
forbidden **latent private bridge escape hatch**, not proof that ordinary Rust
public `Pattern` matching delegates. The real public methods use native
descriptors. Zig's candidate-owned `ctypes` loader is forbidden even though its
present `_zig_probe.so` target is first-party, and public `rebar.py` inherits
that wrapper. Caller-owned warning formatting and enum introspection remain
ordinary host plumbing, not candidate-owned matching delegation.

The only V3-owned files are:

- `tools/audit_candidate_runtime_non_delegation_v3.py`.
- `oracle/phase2/RUNTIME-NON-DELEGATION-V3.md`.
- `oracle/phase2/runtime-non-delegation-v3.json`.

`--self-test` uses only in-memory positive and hostile fixtures. It reads no
candidate, predecessor, receipt, archive, stdlib, hidden case, or holdout.
`--verify-source` authenticates exactly seven public files: the three pinned V3
owners, the three pinned immutable V2 owners, and the single exact V2 failure
receipt. The receipt exception is exact and cannot authorize another evidence
file. Both source-only modes physically block imports after the effect wall,
candidate reads, candidate execution, native loads, compiler/process creation,
clocks, threads, network, Git, private data, archive access, and workspace
mutation.

Use pinned CPython both normally and with an empty environment:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/audit_candidate_runtime_non_delegation_v3.py --self-test

env -i /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/audit_candidate_runtime_non_delegation_v3.py --self-test

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/audit_candidate_runtime_non_delegation_v3.py --verify-source \
  --source-sha256 PUBLISHED_V3_SOURCE_SHA256 \
  --protocol-sha256 PUBLISHED_V3_PROTOCOL_SHA256 \
  --contract-sha256 PUBLISHED_V3_CONTRACT_SHA256
```

`--audit` remains root-agent-only and must follow an independently verified
source commit and push. It requires
`--root-authorized --pushed-source-sha256 EXACT_PUSHED_V3_SOURCE_SHA256`.
Only that separately authorized static mode may read the real canonical V24
Rust source, remaining candidate sources, pinned stdlib files, or native ELF
binaries. It never executes, imports, builds, or loads any candidate. The
expected policy result remains **FAIL**, honestly reporting the Rust private
escape hatch, the Zig candidate-owned loader, and the public wrapper.

`--run-runtime-audit` remains unimplemented, fails closed, and is reserved for
a future independently frozen, explicitly root-authorized runtime protocol.

Runtime non-delegation: **NOT ESTABLISHED**. Public Rust matching delegation:
**NOT PROVEN**. Candidate execution: **NOT RUN**. Candidate qualification:
**NOT ESTABLISHED**. Holdout: **NOT OPENED**. Performance: **NOT MEASURED**.
Winner: **NOT SELECTED**.
