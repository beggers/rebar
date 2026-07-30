# First-party Rust no-external-introspection source freeze V1

This append-only Phase 2 source freeze corrects exactly the single genuine V4
static-policy failure without claiming to establish runtime non-delegation. The
complete, independently authenticated actual V4 root audit receipt is
`oracle/phase2/evidence/runtime-non-delegation-v4-actual-source-audit-failure.json`,
SHA-256 `c3020fe067ad06c2bf7309a73b960884572addd9e984d01d2cf27d5cd9d61f19`.
It contains exactly one candidate-owned failure:

```
CANDIDATE_NATIVE_INSPECT_TRANSITIVE_RE
candidates/rust/py_bridge.c:4403
candidate native bridge -> inspect -> tokenize -> re -> re.compile
PRIVATE_BRIDGE_BIND_GETTER; PUBLIC_MATCHING_DELEGATION_NOT_PROVEN
```

The actual receipt explicitly establishes that public Rust pattern methods use
`PyDescr_NewMethod` native descriptors, the Rust adapter has zero `_NATIVE_BIND`
calls, the private bridge getter is latent, and public matching delegation is
not proven. Authentic first-party Zig FFI and its same-family facade passed the
V4 audit and must remain permitted. V2 and V3 failures, six candidate families,
zero candidate executions, and unopened holdouts remain visible in the complete
actual V4 evidence. No V4 audit is rerun by this frozen transformer.

The predecessor is the complete first-party V25 dual-phase offline source build,
whose actual publication and root provenance receipts have SHA-256
`55cdccb1114e0cc7e4bdcecb8311b3c80c4e020dcfdabd1d8597cf3cececeefc` and
`e8633ac1224235db9f8ea48c683c833fba3015cd73f071cd2488fa0b13a117a2`.
That independently authenticated evidence contains 28 real compiler processes,
two byte-identical native build phases, a first-party bridge depending only on
`_rust_engine.so` and `libc.so.6`, zero external regular-expression or
cross-family dependencies, 13 original suites, 31,237 original cases, 13 named
private waivers, and the previous real candidate failure of 1,352 semantic
mismatches with 15,877 verified passing cases. A successful native build is not
a successful correctness run or a proof of runtime non-delegation.

The only future input source is
`candidates/rust/variants/capture_clamp_semantics_v1/py_bridge.c`, exactly
178,805 bytes, SHA-256
`a127ef85945a4dfa40a1b6c98f6c1a73ca7e1a487e190e8dde1d5aa2be47bb54`, device
2064, inode 526064, mode `0600`, one link. Its identity is established by
public V25 evidence in frozen verification mode without opening the candidate
source itself. The separate, root-only materialization mode may subsequently
open that complete pinned C source exactly once.

The sole correction removes these exact contiguous bytes and nothing else:

1. The complete private `rust_bound_get_signature` function, including its
   trailing blank line: 1,541 bytes. This removes its complete imports of
   `functools` and `inspect` and thus the transitive `tokenize -> re` path.
2. Its one exact `__signature__` entry in `rust_bound_getsets`: 118 bytes.

The immutable predicted corrected source is
`candidates/rust/variants/no_external_introspection_v1/py_bridge.c`, 177,146
bytes, SHA-256
`2dd040dc0337f205134431ebeaafe56ee4fe63cc77c1bb6cb5434742549884b7`. The
correction is byte-exactly reversible at the two sites. It retains native bound
calls, `__self__`, `__name__`, `__qualname__`, `__doc__`, representation,
`bridge.bind`, public `PyDescr_NewMethod` pattern descriptors and their
docstrings, the `signature` struct field, both `Py_CLEAR(method->signature)`
sites, `Py_VISIT(method->signature)`, and the already corrected capture-clamp
logic. Normal `inspect.signature(Pattern.search)` remains available through the
unchanged real public native descriptor; this surface is compared statically,
not executed. No matching engine, candidate adapter, public behavior, canonical
source, or preexisting variant is edited.

The source-only verifier imports no regular-expression engine, candidate,
compiler, subprocess, network client, timer, or native loader. A deny-default
audit-hook wall is installed before any owner read. Every owned pathname is
resolved from the exact workspace root using component-by-component
descriptor-relative `O_NOFOLLOW` opens. Source verification authenticates only
the three new frozen owners and fourteen pinned public tools, protocols,
contracts, and existing publication receipts. It never opens a candidate source,
native binary, compressed archive, private root, benchmark, expanded-holdout
proposal, hidden case, or Git metadata, and performs zero workspace mutations.
The zero-owner self-test uses only synthetic bytes and hostile isolation
controls. Runtime non-delegation remains **NOT ESTABLISHED**.

The sole writer is the root coordinator after the immutable source, protocol,
and contract are committed and pushed. It requires explicit complete SHA-256
values for all three frozen files, `--root-authorized`, and identical complete
40-character `--frozen-commit` and `--pushed-commit` values. Only this mode
authenticates and reads the one pinned V25 bridge. It creates the exact new
variant directory with mode `0700`, then creates its new `py_bridge.c` with
descriptor-relative `O_CREAT | O_EXCL | O_NOFOLLOW`, mode `0600`, writes the
predicted exact bytes, fsyncs the file and directory, and verifies complete
descriptor-relative readback. An existing target directory or file is rejected;
no overwrite, canonical mutation, additional source read, build, audit,
candidate execution, holdout access, performance measurement, or winner
selection is authorized.

Commands use the pinned project Python with `-I -B -S`:

```
python3.14 -I -B -S tools/apply_owned_rust_no_external_introspection_v1.py --self-test
python3.14 -I -B -S tools/apply_owned_rust_no_external_introspection_v1.py \
  --verify-source --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
python3.14 -I -B -S tools/apply_owned_rust_no_external_introspection_v1.py \
  --apply --root-authorized --frozen-commit PUSHED_FROZEN_COMMIT \
  --pushed-commit PUSHED_FROZEN_COMMIT --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 --contract-sha256 CONTRACT_SHA256
```

The final command is root-only and is not run when freezing or independently
verifying these three files.
