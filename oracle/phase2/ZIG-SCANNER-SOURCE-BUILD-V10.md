# Freeze the next first-party Zig build before running it

We are trying to build a faster, fully compatible replacement for Python's
`re`. This step does not claim that the Zig candidate is correct or fast. It
freezes one reproducible way to compile the already published, first-party Zig
scanner correction in two independent private directories. No external regular
expression package, CPython matching engine, other candidate, or prebuilt
matching library may do the work.

The unchanged baseline is CPython 3.14.6, with 13 frozen test suites, 31,237
counted case executions, and 13 separately named private waivers. The current
V21 historical record contains 103 distinct evidence files and 108 authenticated
history references. A later, genuinely failed C correctness run published two
additional evidence files, giving **105 actual current evidence owners and 110
authenticated history references**. Its one failed entry process started no
candidate worker; neither C correctness nor passing case counts were measured,
and its original native file was restored. The failure remains a failure. There
are six independent first-party implementation
families and 25 implementation source owners, including exactly three original
Zig sources. The original Zig implementation still has 1,764 recorded matching
differences, including 620 verbose-scanner differences. Zero candidates are
qualified. A proposed repair is not a passing test.

## What this freeze permits

Only a later, explicitly requested `--build`, using the exact published SHA-256
of this tool, this document, and the V10 machine contract, may create a new
private root. The root must be a fresh, unpredictable directory under `/tmp`
whose name begins with the **already frozen overlay prefix**
`rebar-phase2-zig-scanner-capture-source-build-v1-`. Substituting a V7 or V10
prefix would violate the separately published overlay and must fail.

The build first creates both `reference-a` and `reference-b`. Each phase and its
source, native output, temporary directory, and two Zig caches must be separate
owner-only, mode-0700 directories. Each original Zig engine and Python adapter is
copied into a fresh, separate, mode-0600 snapshot. The original C bridge must
**not** be copied: the private `source/candidates/zig/py_bridge.c` destination
must still be absent in both phases.

Only after both complete phase trees exist may the build load the exact,
hash-authenticated, separately published scanner overlay in-process. It calls
the overlay's existing `verify_context` and then calls its unchanged
`apply_private` exactly once for each phase. The resulting bridge must be
173,082 bytes, with SHA-256
`a5ab490d0cfcbba295b68f3f738a1c6371ef3314e9a6c01cdcc0bb5978e3b148`.
Exclusive, no-follow creation prevents replacement, reuse, symlink traversal, or
an accidental repository edit. Every original Zig source is authenticated
before and after any actual build.

Each future phase has exactly 13 direct, pinned processes: official stable Zig
0.16.0, GCC 13, and GNU `readelf` version checks; one first-party Zig engine
compile; one strict C bridge compile; and four complete ELF inspections for
each of the two actual outputs. The compiler environment has only the frozen
locale, `PATH`, reproducibility setting, private temporary directory, and two
private Zig caches. Both source roots are mapped to the same canonical V7 path.
There is no shell, package fetch, network access, candidate import, dynamic
library load, stdlib matching, external regex library, or timing.

**Twenty-six processes are an expectation, not a result.** The current actual
build-process count is zero. The current actual overlay-application count is
zero. Binary hashes, byte sizes, native reproducibility, correctness, undefined
behavior, memory use, and speed are **NOT MEASURED**. The final holdout is
**NOT OPENED**. The V21 history, the additional recovered C failure, and all
1,764 original Zig failures remain unchanged.

A later actual build must record each process's complete argument list, clean
environment, private working directory, real process ID, exit status, and every
stdout and stderr byte. The already frozen first-party V7 ELF parser must
authenticate both complete phase-native binaries. The genuine Zig engine must
export its own matching functions and may use only the original seven CPython
Unicode classification and casing helpers; these helpers are data operations,
not delegation to CPython's regex engine. The bridge must link only to its own
adjacent `_zig_probe.so` and libc, export `PyInit__zig_bridge`, and use exactly
`$ORIGIN`. Foreign regular-expression engines, `_sre`, cross-family symbols,
dynamic loaders, network symbols, and legacy `RPATH` are rejected.

The build can pass only if both independently created engine files and both
independently created bridge files are genuinely byte-identical, with distinct
phase file identities and all 26 real processes preserved. Any actual compiler,
ownership, linking, or reproducibility failure must be preserved in its own
fresh canonical compressed report and independent durable receipt. Success or
failure publications each use exclusive, mode-0600 files, complete same-inode
readback, and file and parent-directory synchronization. A publication receipt
is not a correctness pass.

## Safe source-only verification

Use the exact pinned CPython 3.14.6 executable with `-I -B`. Substitute the
independently calculated complete SHA-256 values of the V10 source, this
protocol, and `oracle/phase2/zig-scanner-source-build-v10.json`.

```sh
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/reproduce_owned_zig_scanner_source_build_v10.py --self-test \
  --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256

env -i PATH=/usr/bin:/bin \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/reproduce_owned_zig_scanner_source_build_v10.py --self-test \
  --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256

/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/reproduce_owned_zig_scanner_source_build_v10.py --verify-context \
  --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256

env -i PATH=/usr/bin:/bin \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 -I -B \
  tools/reproduce_owned_zig_scanner_source_build_v10.py --verify-context \
  --source-sha256 SOURCE_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 \
  --contract-sha256 CONTRACT_SHA256
```

Both self-tests are entirely in-memory and deliberately block filesystem,
compiler, native-library, candidate-import, network, thread, and clock effects.
Both context checks only authenticate already committed first-party sources,
tools, original correctness evidence, the independent scanner overlay, and the
current complete V21 historical record. None of these four commands applies a
repair, builds an engine, runs a candidate, creates evidence, measures speed, or
opens the holdout.
