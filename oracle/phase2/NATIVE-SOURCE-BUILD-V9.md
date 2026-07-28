# V9 first-party Rust source-build freeze

Status: source freeze only. No V9 Rust compiler has run, no repaired bridge
has been written, and no candidate has been imported, tested, or activated.

This experiment concerns our own independent Rust engine and its own native C
Python bridge. It does not wrap a regular-expression package, borrow another
candidate, call Python's regular-expression engine, download a dependency, or
modify any original candidate source.

## Frozen baseline

The unchanged oracle is CPython 3.14.6: 13 complete suites, 31,237 counted
cases, and 13 named private upstream waivers. Performance, memory, final
comparisons, and the hidden holdout are NOT MEASURED or NOT OPENED.

The original Rust family has exactly nine separately pinned source owners:
its Python adapter, five Rust source files, the Rust manifest and lock, and
the C bridge. Cargo has exactly one local package and zero external
dependencies. The manifest fixes the release profile, and the one-package
lock is preserved.

The unchanged bridge is candidates/rust/py_bridge.c: 175,676 bytes and
SHA-256 f8a0918aaf8a78f363f6d755770636d26acd45fb83c9abcf997a6e052748ea8b.
The separately frozen, unique private bridge repair is 176,118 bytes and
SHA-256 4436bbb8ad180ee8f02dd4418187506ec0d5a33bdb5a79c424fc736253fa0257.
The unchanged adapter is candidates/rust_candidate.py: 31,151 bytes and
SHA-256 6fb66ef6c3f143475426dd3d5b97c52dbe251f8d2ddd0ef3d5de7ec553a0351b.

Only the independently committed Rust repair's apply_private may ever
materialize the derived bridge. Read-only verification computes and audits
its bytes in memory without applying, compiling, loading, or testing them.

The independent C V8 source freeze is authenticated but is not built or
activated by this Rust experiment.

## Future explicit build

A real build is a separate, fully pinned --build operation. Its unique root
must match /tmp/rebar-phase2-native-build-v9-rust-*. Both reference-a and
reference-b, including their source/candidates/rust directories, must be
genuine, distinct, owner-only mode-0700 directories before either application.

Each phase exclusively copies all eight unchanged Rust owners and then calls
the exact frozen Rust apply_private once to create its one derived bridge.
The bridge must not already exist; O_CREAT, O_EXCL, and O_NOFOLLOW create
its owner-only mode-0600 inode. All nine original repository files are
rechecked without mutation.

The pinned Cargo command is exactly an own-crate release build with
--locked, --offline, and --frozen; Cargo has an isolated phase-private
CARGO_HOME and target directory, and CARGO_NET_OFFLINE is true. The pinned
GCC bridge retains the V7 warning, hardening, linkage, and origin-relative
runtime-path flags. Nothing substitutes a prebuilt binary or an external
regular-expression implementation.

There are exactly 14 planned genuine processes per future phase: four
pinned compiler and inspector version checks, the Rust engine build, the
native bridge build, dynamic and exported-symbol checks for both ELF
outputs, and section and note inspections for both outputs. A completed
future build has 28 actual, separately identified processes. None has run.
The original completed V2 Rust build had 16 actual processes; its history
does not constitute execution of this future 28-process V9 build.

Both private source closures, both engine ELF files, and both bridge ELF
files must have distinct genuine phase identities. Their complete raw
bytes are independently inspected and compared before reproducibility can
pass. The original-source-only V4 reproducibility verifier is never used
for the repaired bridge.

Any separately authorized real pass or failure receives its own canonical,
exclusive, synchronized archive and receipt. A successfully written receipt
never converts a failed build or an untested candidate into a success.

## History and boundaries

The freeze retains the 76 digest-addressed V19 history references and the
distinct authoritative count of 71 evidence owners. It preserves all 169
actual historical compiler processes without reporting them as V9 results.
The original Rust result remains 2,042 mismatches. The complete Go result
remains a failure: 4,518 mismatches and four infrastructure failures;
restoration passed.

A source-only self-test:

    /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
      -I -B tools/reproduce_owned_native_source_build_v9.py --self-test

Independently pinned read-only verification:

    /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
      -I -B tools/reproduce_owned_native_source_build_v9.py --verify-context \
      --source-sha256 V9_SOURCE_SHA256 \
      --protocol-sha256 V9_PROTOCOL_SHA256 \
      --contract-sha256 V9_CONTRACT_SHA256

Neither command writes source, snapshots, compiles, runs a candidate,
activates Rust or C, opens the holdout, samples a clock, measures
performance, or selects a winner.
