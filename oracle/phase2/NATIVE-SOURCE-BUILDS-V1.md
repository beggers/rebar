# Build each regular-expression engine from its own source

The Python correctness standard was completed and published before this
build protocol. Its independently verified inventory is
[`../phase1/p0-completeness-v1.json`](../phase1/p0-completeness-v1.json),
SHA-256
`cc703915bf08b4a4d3caf399729d6afd4b583287633bd5db25db3a20671cd47f`.
All **31,237** original Python-reference checks across **13** suites pass.
Building a replacement proves its source and native provenance; it does not
prove that the replacement passes those checks or runs faster.

The sole recorder is
[`../../tools/reproduce_phase2_native_builds_v1.py`](../../tools/reproduce_phase2_native_builds_v1.py).
Freeze, commit, and push this source and protocol **before** starting an actual
reproducibility build, linking or publishing a native library, importing a
candidate, or qualifying a candidate. Previously documented compiler
syntax-only checks did not link a native library or run a candidate; they are
not a reproducibility build. The synthetic `--self-test` is not a build.

## Three genuinely separate source families

| Implementation | Complete independently owned source closure | Fresh native outputs |
| --- | --- | --- |
| C | `candidates/vm_candidate.py`; `candidates/_vm_native.c` | `_vm_native.cpython-314-x86_64-linux-gnu.so` |
| Rust | `candidates/rust_candidate.py`; `candidates/rust/py_bridge.c`; `candidates/rust/Cargo.toml`; `candidates/rust/Cargo.lock`; and `candidates/rust/src/{lib,newline,search,stack,unicode_tables}.rs` | `_rust_engine.so`; `_rust_bridge.cpython-314-x86_64-linux-gnu.so` |
| Zig | `candidates/zig_candidate.py`; `candidates/zig/mini_regex.zig`; `candidates/zig/py_bridge.c` | `_zig_probe.so`; `_zig_bridge.cpython-314-x86_64-linux-gnu.so` |

Pass the exact **current** SHA-256 for every source in the selected family as
a separate `--owned-source-sha256 RELATIVE/PATH=SHA256`. The recorder rejects
missing, duplicate, stale, malformed, or cross-family pins. It authenticates
every source before and after the build, and copies only those complete,
independently owned bytes into each fresh private source tree. The evolving C
native source and Rust Python bridge must not be pinned to an old revision.
Existing `.so` files are never build inputs.

The native and Python sources must not import Python `re`, `_sre`, an
external regular-expression package, another candidate, or a dynamically
selected matcher. The Rust lockfile must contain its one owned package and
**zero** external dependencies, registries, build scripts, or plugins. The
separately frozen Phase-2 candidate audit supplies the additional guarded
runtime verification; a source build alone is not that runtime audit.

## Exact offline compilers and Python ABI

All extensions target the independently pinned CPython **3.14.6** executable:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14
255e900f44ce87c630e83b637a79435f9ae7778dd72f6e2a2f18a486e501d016
```

The exact Python headers are under
`/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/include/python3.14`.
The extension suffix is `.cpython-314-x86_64-linux-gnu.so`. Authenticate
the executable, `Python.h`, `patchlevel.h`, immutable objective, published
correctness inventory and its explanation and verifier before each build.

Use Rust **1.95.0** directly; never use the mutable `rustup` shim or the
`PATH` Rust **1.97.1**:

```text
/home/dev-user/.rustup/toolchains/1.95.0-x86_64-unknown-linux-gnu/bin/rustc
bff349e72704ff70bc08a234a3847338e797065bbedde5e556808bc87b7bf7c6

/home/dev-user/.rustup/toolchains/1.95.0-x86_64-unknown-linux-gnu/bin/cargo
841072d1d92f9e841d9ba5b0814182a0adf064acf4527cd120967b7bc49dcb66

/home/dev-user/.rustup/toolchains/1.95.0-x86_64-unknown-linux-gnu/lib/librustc_driver-6108105cd7e839cf.so
ae69468875215df490fde685ec1f1b969743482ba7e0251f4074a222606a5484
```

The authenticated compiler must report release `1.95.0`, host
`x86_64-unknown-linux-gnu`, and commit
`59807616e1fa2540724bfbac14d7976d7e4a3860`. Cargo must report version
`1.95.0` and commit `f2d3ce0bd`. Invoke the absolute pinned cargo with
`build --release --locked --offline --frozen`, the fresh source's exact
manifest, a fresh target directory, `CARGO_NET_OFFLINE=true`, a fresh
`CARGO_HOME`, the absolute pinned `RUSTC`, and reproducible source-prefix
maps. Independently authenticate the actual **153,621,360**-byte compiler
driver loaded by `rustc`, not just the small Rust launcher. Recheck every
compiler, driver, header, source, and frozen Python input before and after
both builds. No registry or network is permitted.

Use the actual official stable Zig **0.16.0** release:

```text
/tmp/zig-x86_64-linux-0.16.0/zig
2317bbb91798556d9d0f38aabdac23db83f0979b25f767259ae474546724087c

/tmp/rebar-zig-0.16.0-x86_64-linux.tar.xz
70e49664a74374b48b51e6f3fdfbf437f6395d42509050588bd49abe52ba3d00
```

Independently validate the complete committed
[`../../toolchains/zig-0.16.0.lock.json`](../../toolchains/zig-0.16.0.lock.json),
SHA-256
`a0f105b47dd60bab9c3136a7b7a44ab417bc034e680bf2d30693cc954422b3cd`,
the **55,478,392**-byte official archive, the **172,641,672**-byte official
compiler, the original official download metadata, and the actual
`0.16.0` compiler version. Both Zig caches must be fresh and private to the
selected build phase.

The C compiler and Python bridges use the pinned host GCC executable
`/usr/bin/x86_64-linux-gnu-gcc-13`, SHA-256
`1b99826121ae6682a634e5efe09bd3e3df58ce58e0b28f849114ab5b89139c26`.
Inspect the complete fresh ELF files with the pinned
`/usr/bin/x86_64-linux-gnu-readelf`, SHA-256
`64c58e15274bbbb5153f31078e455e9e77ee5f51489e709bba5bb788ce9df2b0`.
No command is resolved through the ambient environment.

## Two actual builds, not one reused library

For each separately authorized family, create one new mode-0700 temporary
root under `/tmp/rebar-phase2-native-build-v1-FAMILY-`. Build the same
complete frozen sources separately in **two** distinct private source,
target, cache, and output directories. Fix locale, release mode, source-date
epoch, and source-prefix mappings. Preserve every actual compiler and ELF
inspector command, environment, real process ID, complete output, error,
exit status, and output SHA-256.

Require both independently produced native outputs to have byte-for-byte
matching hashes, sizes, exported symbols, sonames, direct dependencies, and
Python entry points. The Rust bridge may load only its adjacent
`_rust_engine.so`; the Zig bridge may load only its adjacent `_zig_probe.so`.
Both use exactly `$ORIGIN`. Reject foreign regular-expression symbols,
foreign dynamic libraries, cross-candidate references, invented process
records, unsafe paths, symlinks, partial files, stale compiler versions, and
missing Python 3.14 entry points.

An actual build writes only its fresh source trees and exactly one new
non-overwriting report and receipt under `oracle/phase2/evidence/`:

```text
native-source-build-v1-FAMILY-LABEL.json.gz
native-source-build-v1-FAMILY-LABEL-publication-receipt.json
```

A real compiler or validation failure instead preserves its complete logs
and observed prefix, without overwriting the passing filenames:

```text
native-source-build-v1-FAMILY-LABEL-failures.json.gz
native-source-build-v1-FAMILY-LABEL-failures-publication-receipt.json
```

Every report and receipt is created once using exclusive, no-follow file
descriptors, complete writes, file synchronization, full same-inode
readback, and directory synchronization. A receipt must not claim that its
own publication was complete before it was written.

## Exact reproduction and phase boundary

The following command is synthetic and may run before source publication.
Run it in both an ordinary and an empty environment. It reads **zero**
workspace files, starts **zero** processes or compilers, creates **zero**
build directories, imports **zero** candidates, accesses **zero** hidden
cases, and samples **zero** clocks:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/reproduce_phase2_native_builds_v1.py --self-test

env -i PATH=/usr/bin:/bin \
  /tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/reproduce_phase2_native_builds_v1.py --self-test
```

Only **after this recorder and protocol have been committed and pushed**, get
their actual hashes with:

```text
sha256sum tools/reproduce_phase2_native_builds_v1.py \
  oracle/phase2/NATIVE-SOURCE-BUILDS-V1.md
```

Independently obtain the SHA-256 of **every** then-current owner in the
selected family. Run one family and one fresh label per focused experiment:

```text
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/reproduce_phase2_native_builds_v1.py \
  --build --family FAMILY --label LABEL \
  --source-sha256 RECORDER_SHA256 \
  --protocol-sha256 PROTOCOL_SHA256 \
  --owned-source-sha256 EXACT/RELATIVE/OWNER=ACTUAL_SHA256 \
  --owned-source-sha256 NEXT/RELATIVE/OWNER=ACTUAL_SHA256
```

Supply one `--owned-source-sha256` for **each** of the **2** C, **9** Rust,
or **3** Zig owners; the displayed two-owner form is complete only for C.
Do not reuse a failed or previously published label. Commit and push each
family's evidence as its own focused chunk before starting the next family.

**Candidate correctness: NOT MEASURED. Performance: NOT MEASURED. Memory:
NOT MEASURED. Expanded holdout: NOT OPENED. No winner is selected.**
