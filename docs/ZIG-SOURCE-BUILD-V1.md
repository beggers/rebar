# Rebuilding our Zig engine from source

The Zig candidate must use this project's own regular-expression
parser, compiler, and matching engine. It must not wrap Python's
matcher or an external regular-expression package.

## Pinned compiler

Use the official stable Zig **0.16.0** Linux x86-64 release listed
in the [official Zig release index](https://ziglang.org/download/index.json).

| Item | Exact value |
| --- | --- |
| Release | `0.16.0` |
| Official archive | `https://ziglang.org/download/0.16.0/zig-x86_64-linux-0.16.0.tar.xz` |
| Archive size | `55478392` bytes |
| Archive SHA-256 | `70e49664a74374b48b51e6f3fdfbf437f6395d42509050588bd49abe52ba3d00` |
| Extracted compiler SHA-256 | `2317bbb91798556d9d0f38aabdac23db83f0979b25f767259ae474546724087c` |
| Verified compiler version | `0.16.0` |

The downloaded archive's **20,832** entries were checked to remain
inside the single `zig-x86_64-linux-0.16.0/` directory before
extraction. The compiler is installed only in `/tmp`; no existing
project source or candidate was replaced.

```sh
curl --fail --location --proto '=https' --tlsv1.2 \
  --output /tmp/rebar-zig-0.16.0-x86_64-linux.tar.xz \
  https://ziglang.org/download/0.16.0/zig-x86_64-linux-0.16.0.tar.xz

printf '%s  %s\n' \
  70e49664a74374b48b51e6f3fdfbf437f6395d42509050588bd49abe52ba3d00 \
  /tmp/rebar-zig-0.16.0-x86_64-linux.tar.xz |
  sha256sum --check

tar --extract \
  --file /tmp/rebar-zig-0.16.0-x86_64-linux.tar.xz \
  --directory /tmp \
  --no-same-owner \
  --no-same-permissions

/tmp/zig-x86_64-linux-0.16.0/zig version
```

## Pinned project sources

| Owned file | SHA-256 |
| --- | --- |
| Zig regular-expression engine, `candidates/zig/mini_regex.zig` | `539bf5d378e0c2845c01519fcce62f1ef5e68610f477912c44a03027fb67a346` |
| Native Python binding, `candidates/zig/py_bridge.c` | `f4900d04734a7c02bd766aee81c1d64114803dbefcf6f4591bfb667262658fea` |
| Python-compatible adapter, `candidates/zig_candidate.py` | `07e9fa19af8fe9938dc8ed5170e30a478ff56f0d04cd2488a0bd1869e28201cc` |

The baseline is the pinned CPython **3.14.6** interpreter and its own
headers at
`/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/include/python3.14`.
Its extension suffix is `.cpython-314-x86_64-linux-gnu.so`.

## Frozen source-build controller

The independently reviewed build controller is
`tools/reproduce_owned_zig_source_build_v1.py`, with SHA-256
`53df4260eee56a143d2cd9134e5c0dc336b412758218c681f59acee0a8b8644e`.
Its synthetic self-test passes **14** valid controls and rejects
**87** forged archives, paths, engine symbols, native dependencies,
or unsafe outputs under both ordinary and empty environments.

```sh
/tmp/rebar-cpython/cpython-3.14.6-linux-x86_64-gnu/bin/python3.14 \
  -I -B tools/reproduce_owned_zig_source_build_v1.py --self-test
```

The self-test runs no compiler or candidate and creates no build or
evidence files. An actual build remains an explicit, separate step.
When authorized, the controller will compile only these authenticated
owned sources into a fresh `/tmp` directory, retain complete compiler
output, validate native exports and `$ORIGIN` dependencies, and
publish a complete success or failure without overwriting any
existing candidate.

The Zig engine legitimately refers to Python-owned Unicode helpers;
the exact source build must permit those authenticated host-Python
symbols with `-fallow-shlib-undefined`. This is a Python interface,
not an external regular-expression implementation.

## What is and is not proved

The official compiler archive, extracted compiler version, owned
source hashes, and Python header and extension versions are
**VERIFIED**.

Compiling the engine with this compiler, rebuilding its Python
extension, reproducing a native binary from the owned sources,
matching the existing native binaries, and passing any Zig
correctness or speed test are **NOT YET RUN**. Source-to-binary
reproducibility and Zig performance remain **NOT ESTABLISHED**.

Run the separately frozen original Python correctness suite and
from-scratch audit before qualifying any rebuilt Zig candidate. Do
not use a final or hidden performance case to guide the build.
