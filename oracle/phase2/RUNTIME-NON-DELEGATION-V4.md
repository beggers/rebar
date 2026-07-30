# First-party non-delegation audit V4

V4 is an immutable, additive correction to V2 and V3. It retains both prior
source freezes and their authentic public failure evidence. No predecessor
source, receipt, candidate, or native binary is modified by V4 source-only
work. Runtime non-delegation is still **NOT ESTABLISHED**.

The real V2 root-authorized attempt failed before completing candidate-source
inspection: `candidates/rust/src/lib.rs:252: unterminated native literal`. Its
411-byte public receipt has SHA-256
`7f30581baf5b47adf7c2d21f0baf2218bc78e14a72aeba90355140519dbadf1a`.
The real V3 root-authorized static audit completed and **FAILED** with seven
findings. Its 20,583-byte public receipt has SHA-256
`8afe74eeaaa2cab4a1138366d6d2d088de16e31cee5c855827a4efdee97a10db`.
Both attempts executed zero candidates, loaded zero native libraries, and left
the holdout unopened. V4 authenticates both exact receipts, including their
device, inode, mode, byte count, and complete recorded failures.

V3's Rust finding is genuine: a private native bridge `bind` capability exposes
a custom `__signature__` getter that imports `inspect`, whose pinned CPython
dependency chain reaches `tokenize` and two import-time `re.compile` calls.
It remains a **forbidden latent candidate-owned escape hatch** until removed or
separately proved safe. This is not proof that ordinary Rust public matching
delegates; normal public methods use native descriptors.

The other six V3 findings were policy false positives. The user's actual
restriction forbids wrapping or using an **external regular-expression
package/engine**; it does not forbid a foreign-function interface to an engine
implemented from scratch in the candidate's own language, and does not forbid
a public facade over one selected first-party candidate.

V4 therefore allows precisely one unaliased `ctypes` import inside the owned Zig
adapter and precisely this fixed operation in `candidates/zig_candidate.py`
inside `_Native.__init__`:

```text
path = os.path.join(os.path.dirname(__file__), "_zig_probe.so")
self.library = ctypes.CDLL(path)
```

The path must be a single literal, file-anchored assignment; mutable names,
extra path components, traversal, symlinks, borrowed candidate binaries,
environment-controlled expressions, aliasing, substituted libraries, loader
keywords, multiple loads, and dynamic attribute dispatch are rejected. The root
static audit also independently authenticates all three Zig source owners and
both separate native owners with descriptor-relative no-follow reads, distinct
same-device inodes, exact regular-file modes and digests, allowed ELF
`DT_NEEDED` owners, owned export sets, and `$ORIGIN` bridge linkage. External
regex packages, CPython `re`/`_sre`, other candidate engines, dynamic engine
resolution, and subprocess/package-install dispatch remain forbidden.

The public `rebar.py` facade may select only its one independently owned Zig
candidate. It is an entrypoint, **not a seventh candidate family**, and does
not establish candidate correctness or runtime independence.

Only three files are V4-owned:

- `tools/audit_candidate_runtime_non_delegation_v4.py`.
- `oracle/phase2/RUNTIME-NON-DELEGATION-V4.md`.
- `oracle/phase2/runtime-non-delegation-v4.json`.

`--self-test` performs only in-memory positive and hostile controls and reads
no files. `--verify-source` authenticates exactly 11 public owners: three V4
owners, three V2 owners, three V3 owners, and two precisely pinned public
failure receipts. Neither source-only mode reads a candidate source or binary,
stdlib source, archive, hidden case, holdout, benchmark, private data, or Git
metadata. The effect wall forbids subsequent imports, candidate execution,
native loading, subprocesses, compilers, threads, network, clocks, and
workspace mutation.

Use the pinned CPython normally and under an empty environment:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/audit_candidate_runtime_non_delegation_v4.py --self-test

env -i /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/audit_candidate_runtime_non_delegation_v4.py --self-test

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/audit_candidate_runtime_non_delegation_v4.py --verify-source \
  --source-sha256 PUBLISHED_V4_SOURCE_SHA256 \
  --protocol-sha256 PUBLISHED_V4_PROTOCOL_SHA256 \
  --contract-sha256 PUBLISHED_V4_CONTRACT_SHA256
```

`--audit` remains **root-agent-only**, after an independently verified source
commit and push, and requires
`--root-authorized --pushed-source-sha256 EXACT_PUSHED_V4_SOURCE_SHA256`.
The expected current static result is **FAIL solely for the latent Rust
candidate-owned introspection escape hatch**. First-party Zig FFI and the
same-family facade are allowed, but neither is yet a correctness-qualified
candidate. A future actual runtime audit remains unimplemented, fail-closed,
and separately root-authorized.

Candidate family count: **6**. Public facade count: **0 candidate families**.
Runtime non-delegation: **NOT ESTABLISHED**. Public Rust matching delegation:
**NOT PROVEN**. Candidate execution: **NOT RUN**. Candidate qualification:
**NOT ESTABLISHED**. Holdout: **NOT OPENED**. Performance: **NOT MEASURED**.
Winner: **NOT SELECTED**.
